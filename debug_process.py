#!/usr/bin/env python3
"""Debug script to test process function by importing it."""

from pathlib import Path
from yoclip.process import run_process

def main():
    """Run process function with debug parameters."""
    geotiff_path = Path("/path/to/your/geotiff.tif")  # Update this path
    embeddings_file = Path("/media/mor582/ASHMORE_02/Seagrass/features.pkl")
    output_file = Path("/media/mor582/ASHMORE_02/Seagrass/geotiff_analysis.csv")
    tile_size = 256
    overlap = 0
    batch_size = 16
    top_k = 3
    model_name = "ViT-B/32"
    
    print(f"🔧 Debug: Calling process function with:")
    print(f"   geotiff_path: {geotiff_path}")
    print(f"   embeddings_file: {embeddings_file}")
    print(f"   output_file: {output_file}")
    print(f"   tile_size: {tile_size}")
    print(f"   overlap: {overlap}")
    print(f"   batch_size: {batch_size}")
    print(f"   top_k: {top_k}")
    print(f"   model_name: {model_name}")
    
    # Call the function directly
    run_process(
        geotiff_path=geotiff_path,
        embeddings_file=embeddings_file,
        output_file=output_file,
        tile_size=tile_size,
        overlap=overlap,
        batch_size=batch_size,
        top_k=top_k,
        model_name=model_name
    )

if __name__ == "__main__":
    main()
