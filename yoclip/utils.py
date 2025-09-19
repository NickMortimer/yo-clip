"""CLI utilities and helper functions."""

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

console = Console()


def show_spinner(description: str = "Working..."):
    """Create a spinner context manager."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def format_output(data: Any, format_type: str = "table") -> None:
    """Format and display output in various formats."""
    if format_type == "json":
        import json
        console.print_json(json.dumps(data, indent=2))
    elif format_type == "table":
        # Handle table formatting
        console.print(data)
    else:
        console.print(data)


def validate_input(value: str, validation_type: str = "email") -> bool:
    """Validate input based on type."""
    if validation_type == "email":
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    return True


def find_closest_vectors(
    query_embeddings: np.ndarray,
    reference_embeddings: np.ndarray,
    reference_labels: List[str],
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """Find closest vectors using cosine similarity."""
    # Compute cosine similarity between query embeddings and reference embeddings
    similarities = cosine_similarity(query_embeddings, reference_embeddings)
    
    results = []
    for i, query_similarities in enumerate(similarities):
        # Get top-k most similar references
        top_indices = np.argsort(query_similarities)[-top_k:][::-1]
        
        query_result = {
            "query_id": i,
            "matches": []
        }
        
        for rank, idx in enumerate(top_indices):
            query_result["matches"].append({
                "rank": rank + 1,
                "class_name": reference_labels[idx],
                "similarity": float(query_similarities[idx]),
                "reference_idx": int(idx)
            })
        
        results.append(query_result)
    
    return results


def load_clip_model(model_name: str = "ViT-B/32", device: str = "cuda"):
    """Load CLIP model with error handling."""
    try:
        import clip
        import torch
        
        device = device if torch.cuda.is_available() else "cpu"
        console.print(f"📱 Using device: {device}")
        console.print(f"🤖 Loading CLIP model: {model_name}")
        
        model, preprocess = clip.load(model_name, device=device)
        return model, preprocess, device
    except Exception as e:
        console.print(f"❌ Error loading CLIP model: {e}")
        raise


def validate_paths(*paths) -> bool:
    """Validate that all provided paths exist."""
    from pathlib import Path
    
    for path in paths:
        path_obj = Path(path)
        if not path_obj.exists():
            console.print(f"❌ Path not found: {path}")
            return False
    return True
