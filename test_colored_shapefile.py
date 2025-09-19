#!/usr/bin/env python3
"""
Test script demonstrating the new colored shapefile functionality.
This shows how the shapefile now includes color information and creates a QGIS style file.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from yoclip.process import create_shapefile_from_results

# Create sample results data
sample_results = [
    {
        'tile_id': 0,
        'best_class': 'vegetation;seagrass;dense',
        'query_similarity': 0.85,
    },
    {
        'tile_id': 1,
        'best_class': 'substrate;sand;fine',
        'query_similarity': 0.78,
    },
    {
        'tile_id': 2,
        'best_class': 'vegetation;seagrass;sparse',
        'query_similarity': 0.82,
    },
    {
        'tile_id': 3,
        'best_class': 'substrate;rock;boulder',
        'query_similarity': 0.91,
    },
    {
        'tile_id': 4,
        'best_class': 'vegetation;seagrass;dense',
        'query_similarity': 0.88,
    },
]

# Create sample tile metadata with simple coordinate transform
sample_metadata = []
for i in range(5):
    # Simple linear transform for demonstration
    x_offset = (i % 3) * 512  # 3 columns
    y_offset = (i // 3) * 512  # 2 rows
    
    # Create a simple affine transform (identity + translation)
    from rasterio.transform import Affine
    transform = Affine(1.0, 0.0, x_offset, 0.0, -1.0, y_offset + 512)
    
    metadata = {
        'tile_x': x_offset,
        'tile_y': y_offset,
        'tile_width': 512,
        'tile_height': 512,
        'row': i // 3,
        'col': i % 3,
        'transform': transform,
        'crs': 'EPSG:4326',  # WGS84
        'source_file': 'test_geotiff.tif'
    }
    sample_metadata.append(metadata)

def main():
    print("🧪 Testing colored shapefile creation...")
    
    # Create output path
    output_path = Path("test_colored_output.shp")
    
    # Test the shapefile creation
    try:
        create_shapefile_from_results(
            results=sample_results,
            tile_metadata=sample_metadata,
            output_shapefile=output_path,
            crs='EPSG:4326'
        )
        
        print("\n✅ Test completed successfully!")
        print("\n📁 Created files:")
        
        # List all created files
        base_name = output_path.stem
        for ext in ['.shp', '.shx', '.dbf', '.prj', '.qml']:
            file_path = output_path.with_suffix(ext)
            if file_path.exists():
                print(f"   {file_path}")
        
        print("\n🎨 Color Information:")
        print("The shapefile now includes these additional fields:")
        print("   - red, green, blue: RGB color values (0-255)")
        print("   - color_hex: Hex color code for web use")
        print("   - best_class: Classification result")
        print("   - similarity: Confidence score")
        
        print("\n🗺️ QGIS Usage:")
        print("1. Load the .shp file in QGIS")
        print("2. The .qml style file should automatically apply color styling")
        print("3. If not automatic, right-click layer → Properties → Symbology → Load Style")
        print("4. Select the .qml file to apply categorized colors")
        
        print("\n📊 Alternative manual styling in QGIS:")
        print("1. Layer Properties → Symbology")
        print("2. Change from 'Single Symbol' to 'Categorized'")
        print("3. Set Column to 'best_class'")
        print("4. Click 'Classify' to auto-generate categories")
        print("5. Optionally use the RGB fields for custom colors")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    main()
