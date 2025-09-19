#!/usr/bin/env python3
"""Test script for the updated process command with batch processing (restored format)."""

from pathlib import Path
import numpy as np
import pandas as pd

def create_test_data():
    """Create minimal test data for the process command using original pickle format."""
    
    # Create test query vector
    query_vector = np.random.rand(512).astype(np.float32)  # CLIP ViT-B/32 embedding size
    np.save("test_query.npy", query_vector)
    print("✅ Created test_query.npy")
    
    # Create test embeddings directory and files
    embeddings_dir = Path("test_embeddings")
    embeddings_dir.mkdir(exist_ok=True)
    
    # Create test data in original DataFrame format (like yolotoclip output)
    test_records = []
    for i in range(10):
        test_records.append({
            "image": f"test_image_{i}.jpg",
            "object_id": i,
            "class_id": i % 3,
            "class_name": f"class_{i % 3}",
            "bbox": (i * 10, i * 10, (i + 1) * 10, (i + 1) * 10),
            "image_embedding": np.random.rand(512).astype(np.float32),
            "text_embedding": np.random.rand(512).astype(np.float32),
        })
    
    # Save as pickle (original format)
    df = pd.DataFrame(test_records)
    embeddings_file = embeddings_dir / "embeddings.pkl"
    df.to_pickle(embeddings_file)
    print(f"✅ Created {embeddings_file}")
    
    print(f"\nTest data created! You can now test with:")
    print(f"python -m yoclip.main process test.tif test_query.npy test_embeddings/embeddings.pkl --batch-size 4 --top-k 3")
    print(f"\nNote: You'll need a real GeoTIFF file named 'test.tif' for the full test.")

if __name__ == "__main__":
    create_test_data()
