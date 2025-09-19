#!/usr/bin/env python3
"""Debug script to test yolotoclip function by importing it."""

from pathlib import Path
from yoclip.yolotoclip import run_yolotoclip

def main():
    """Run yolotoclip function with debug parameters."""
    root_dir = Path("/media/mor582/ASHMORE_02/Seagrass/yolo")
    output_file = Path("/media/mor582/ASHMORE_02/Seagrass/features.csv")
    batch_size = 32
    model_name = "ViT-B/32"
    
    print(f"🔧 Debug: Calling yolotoclip function with:")
    print(f"   root_dir: {root_dir}")
    print(f"   output_file: {output_file}")
    print(f"   batch_size: {batch_size}")
    print(f"   model_name: {model_name}")
    
    # Call the function directly
    run_yolotoclip(
        root_dir=root_dir,
        output_file=output_file,
        batch_size=batch_size,
        model_name=model_name
    )

if __name__ == "__main__":
    main()
