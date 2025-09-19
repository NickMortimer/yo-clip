"""YOLO to CLIP conversion functionality."""

import torch
import clip
import pickle
import numpy as np
from pathlib import Path
from PIL import Image
import pandas as pd
from typing import List, Tuple, Dict, Any
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from yoclip.utils import console


def collect_crops_and_metadata(
    labels_dir: Path, 
    images_dir: Path, 
    class_prompts: List[str]
) -> Tuple[List[Image.Image], List[Dict[str, Any]]]:
    """Collect all crops and their metadata in a single pass."""
    crops = []
    metadata = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        label_files = list(labels_dir.glob("*.txt"))
        task = progress.add_task("Collecting crops...", total=len(label_files))
        
        for label_path in label_files:
            # Find corresponding image
            image_path = images_dir / (label_path.stem + ".jpg")
            if not image_path.exists():
                image_path = images_dir / (label_path.stem + ".png")
            if not image_path.exists():
                console.print(f"⚠️ No matching image found for {label_path.stem}")
                progress.advance(task)
                continue
                
            # Load full image
            full_image = Image.open(image_path).convert("RGB")
            W, H = full_image.size
            
            # Read YOLO label file
            with open(label_path, "r") as f:
                for i, line in enumerate(f):
                    parts = line.strip().split()
                    if not parts:
                        continue
                        
                    class_id = int(parts[0])
                    if class_id >= len(class_prompts):
                        console.print(f"⚠️ Invalid class_id {class_id} in {label_path}")
                        continue
                        
                    class_name = class_prompts[class_id]
                    
                    # Convert YOLO bbox (normalized) to pixel coords
                    x_center, y_center, w, h = map(float, parts[1:])
                    x_center, y_center, w, h = x_center * W, y_center * H, w * W, h * H
                    x1 = int(max(0, x_center - w / 2))
                    y1 = int(max(0, y_center - h / 2))
                    x2 = int(min(W, x_center + w / 2))
                    y2 = int(min(H, y_center + h / 2))
                    
                    # Skip invalid bboxes
                    if x2 <= x1 or y2 <= y1:
                        continue
                    
                    # Crop the object
                    crop = full_image.crop((x1, y1, x2, y2))
                    
                    crops.append(crop)
                    metadata.append({
                        "image": str(image_path),
                        "object_id": i,
                        "class_id": class_id,
                        "class_name": class_name,
                        "bbox": (x1, y1, x2, y2),
                    })
            
            progress.advance(task)
    
    return crops, metadata


def process_crops_in_batches(
    crops: List[Image.Image], 
    metadata: List[Dict[str, Any]],
    model: torch.nn.Module,
    preprocess,
    text_features: torch.Tensor,
    device: str,
    batch_size: int = 32
) -> List[Dict[str, Any]]:
    """Process crops in batches for efficient GPU utilization."""
    records = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        total_batches = (len(crops) + batch_size - 1) // batch_size
        task = progress.add_task("Processing batches...", total=total_batches)
        
        for i in range(0, len(crops), batch_size):
            batch_crops = crops[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            
            # Preprocess batch
            batch_tensors = []
            for crop in batch_crops:
                try:
                    tensor = preprocess(crop)
                    batch_tensors.append(tensor)
                except Exception as e:
                    console.print(f"⚠️ Error preprocessing crop: {e}")
                    # Use a dummy tensor for failed crops
                    batch_tensors.append(torch.zeros(3, 224, 224))
            
            # Stack into batch tensor
            batch_tensor = torch.stack(batch_tensors).to(device)
            
            # Process batch
            with torch.no_grad():
                batch_features = model.encode_image(batch_tensor)
                batch_features /= batch_features.norm(dim=-1, keepdim=True)
            
            # Add results to records
            for j, (features, meta) in enumerate(zip(batch_features, batch_metadata)):
                record = meta.copy()
                record["image_embedding"] = features.cpu().numpy()
                record["text_embedding"] = text_features[meta["class_id"]].cpu().numpy()
                records.append(record)
            
            progress.advance(task)
    
    return records


def run_yolotoclip(
    root_dir: Path,
    output_file: Path,
    batch_size: int = 32,
    model_name: str = "ViT-B/32",
    prompt_template: str = ""
) -> None:
    """
    Encode YOLO images and bounding box crops into CLIP embeddings and save them for classification.
    Uses batch processing for efficient GPU utilization.
    """
    console.print(f"🚀 Starting YOLO to CLIP processing with batch size {batch_size}")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"📱 Using device: {device}")
    
    # Load CLIP model
    console.print(f"🤖 Loading CLIP model: {model_name}")
    model, preprocess = clip.load(model_name, device=device)

    images_dir = root_dir / "images"
    labels_dir = root_dir / "labels"
    classes_file = root_dir / "classes.txt"

    # Validate paths
    if not images_dir.exists():
        console.print(f"❌ Images directory not found: {images_dir}")
        raise ValueError(f"Images directory not found: {images_dir}")
    
    if not labels_dir.exists():
        console.print(f"❌ Labels directory not found: {labels_dir}")
        raise ValueError(f"Labels directory not found: {labels_dir}")

    if not classes_file.exists():
        console.print(f"❌ Could not find classes.txt in root directory: {classes_file}")
        raise ValueError(f"Could not find classes.txt in root directory: {classes_file}")

    # Load YOLO classes (prompts)
    with open(classes_file, "r") as f:
        class_prompts = [line.strip() for line in f.readlines()]
    
    console.print(f"📝 Loaded {len(class_prompts)} classes")

    # Encode text prompts once
    console.print("🔤 Encoding text prompts...")
    
    # Apply prompt template if provided
    if prompt_template:
        console.print(f"[cyan]Using prompt template: '{prompt_template}'[/cyan]")
        formatted_prompts = []
        for prompt in class_prompts:
            if '{class}' in prompt_template:
                # Handle hierarchical class names (major;minor;specific)
                if ';' in prompt:
                    # For hierarchical classes, convert semicolons to commas for better readability
                    class_name = prompt.replace(';', ', ')
                    formatted_prompt = prompt_template.replace('{class}', class_name)
                else:
                    formatted_prompt = prompt_template.replace('{class}', prompt)
                formatted_prompts.append(formatted_prompt)
            else:
                # If no {class} placeholder, just append the label
                formatted_prompts.append(f"{prompt_template} {prompt}")
    else:
        formatted_prompts = class_prompts
    
    text_tokens = clip.tokenize(formatted_prompts).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features /= text_features.norm(dim=-1, keepdim=True)

    # Collect all crops and metadata
    crops, metadata = collect_crops_and_metadata(labels_dir, images_dir, class_prompts)
    
    if not crops:
        console.print("❌ No valid crops found!")
        raise ValueError("No valid crops found!")
    
    console.print(f"📦 Collected {len(crops)} crops from {len(set(m['image'] for m in metadata))} images")

    # Process crops in batches
    records = process_crops_in_batches(
        crops, metadata, model, preprocess, text_features, device, batch_size
    )

    # Save embeddings to a dataframe
    console.print("💾 Saving results...")
    df = pd.DataFrame(records)
    
    # Save pickle with embeddings
    pickle_file = output_file.with_suffix(".pkl")
    df.to_pickle(pickle_file)
    
    # Save CSV without embeddings for readability
    csv_df = df.drop(columns=["image_embedding", "text_embedding"])
    csv_df.to_csv(output_file, index=False)

    console.print(f"✅ Saved CLIP embeddings to {output_file} and {pickle_file}")
    console.print(f"📊 Processed {len(records)} objects across {len(set(r['image'] for r in records))} images")
