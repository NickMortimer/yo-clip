#!/usr/bin/env python3
"""
Example workflow for using yoclip with batch processing.

This shows the complete pipeline:
1. Convert YOLO dataset to CLIP embeddings (with new format)
2. Process GeoTIFF with batch processing and spatial outputs
"""

import subprocess
import sys
from pathlib import Path

def run_yolotoclip_example():
    """Example of running yolotoclip with batch processing."""
    
    print("🚀 Step 1: Convert YOLO dataset to CLIP embeddings")
    print("=" * 50)
    
    # Example command - adjust paths as needed
    yolo_root = "path/to/your/yolo/dataset"  # Contains images/ and labels/ subdirectories
    output_file = "my_dataset_embeddings.csv"
    batch_size = 64  # Adjust based on GPU memory
    
    cmd = [
        "python", "-m", "yoclip.main", "yolotoclip",
        yolo_root,
        "--output-file", output_file,
        "--batch-size", str(batch_size),
        "--model-name", "ViT-B/32"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("\nThis will create:")
    print(f"  📄 {output_file} (CSV summary)")
    print(f"  🗃️ {Path(output_file).with_suffix('.pkl')} (full data)")
    print(f"  🔢 {Path(output_file).stem}_embeddings.npy (for process command)")
    print(f"  📋 {Path(output_file).stem}_metadata.pkl (for process command)")
    print()


def run_process_example():
    """Example of running process with batch processing and spatial outputs."""
    
    print("🚀 Step 2: Process GeoTIFF with similarity search")
    print("=" * 50)
    
    # Example command - adjust paths as needed
    geotiff_file = "satellite_image.tif"
    query_vector = "query_embedding.npy"  # Your query CLIP embedding
    embeddings_dir = Path("my_dataset_embeddings.csv").parent  # Same dir as step 1 output
    embeddings_file = "my_dataset_embeddings_embeddings.npy"  # Generated in step 1
    metadata_file = "my_dataset_embeddings_metadata.pkl"     # Generated in step 1
    
    cmd = [
        "python", "-m", "yoclip.main", "process",
        geotiff_file,
        query_vector,
        str(embeddings_dir),
        "--embeddings-file", embeddings_file,
        "--metadata-file", metadata_file,
        "--output-file", "results.csv",
        "--tile-size", "512",
        "--batch-size", "32",
        "--top-k", "10",
        "--shapefile",  # Create shapefile for QGIS
        "--geojson"     # Create GeoJSON for web mapping
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("\nThis will create:")
    print(f"  📄 results.csv (similarity results)")
    print(f"  🗺️ results.shp (+ .shx, .dbf, .prj for QGIS)")
    print(f"  🌐 results.geojson (for web mapping)")
    print()


def create_query_vector_example():
    """Example of creating a query vector from a sample image."""
    
    print("🚀 Step 0: Create query vector from sample image")
    print("=" * 50)
    
    example_code = '''
import torch
import clip
import numpy as np
from PIL import Image

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load and preprocess your query image
image = Image.open("example_query_image.jpg")
image_tensor = preprocess(image).unsqueeze(0).to(device)

# Get CLIP embedding
with torch.no_grad():
    image_features = model.encode_image(image_tensor)
    image_features /= image_features.norm(dim=-1, keepdim=True)

# Save as numpy array
query_embedding = image_features.cpu().numpy().squeeze()
np.save("query_embedding.npy", query_embedding)
print(f"Saved query embedding with shape: {query_embedding.shape}")
'''
    
    print("Python code to create query vector:")
    print(example_code)


if __name__ == "__main__":
    print("🎯 YoClip Batch Processing Workflow")
    print("=" * 40)
    print()
    
    create_query_vector_example()
    run_yolotoclip_example()
    run_process_example()
    
    print("💡 Tips:")
    print("- Adjust batch sizes based on your GPU memory")
    print("- Larger tile sizes give more context but use more memory")
    print("- Use --shapefile for QGIS visualization")
    print("- Use --geojson for web-based mapping")
    print("- The query vector should be from a CLIP embedding of your target image/concept")
