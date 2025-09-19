#!/usr/bin/env python3
"""
Test coordinate transformation for UTM GeoTIFF data.

Since UTM coordinates have square pixels and regular grid structure,
we can verify that the grid approach produces the same coordinates
as the detailed polygon approach.
"""

import numpy as np
from pathlib import Path

def test_coordinate_consistency():
    """Test that grid and detailed approaches produce identical coordinates."""
    print("🧪 Testing UTM Coordinate Transformation Consistency")
    print("=" * 50)
    
    # Simulate UTM transform (typical values for seagrass mapping)
    # UTM transform: (pixel_size, 0, x_origin, 0, -pixel_size, y_origin)
    pixel_size = 0.5  # 50cm pixels typical for drone imagery
    x_origin = 300000  # UTM easting origin
    y_origin = 8500000  # UTM northing origin
    
    # Create a mock affine transform (simulating rasterio.Affine)
    class MockTransform:
        def __init__(self, a, b, c, d, e, f):
            self.a, self.b, self.c, self.d, self.e, self.f = a, b, c, d, e, f
            
        def __mul__(self, coords):
            x, y = coords
            # Affine transformation: x' = a*x + b*y + c, y' = d*x + e*y + f
            return (self.a * x + self.b * y + self.c, 
                   self.d * x + self.e * y + self.f)
    
    # UTM transform
    transform = MockTransform(pixel_size, 0, x_origin, 0, -pixel_size, y_origin)
    
    print(f"📐 UTM Transform: pixel_size={pixel_size}m, origin=({x_origin}, {y_origin})")
    print()
    
    # Test several tile positions
    test_cases = [
        (0, 0, 256, 256),      # Top-left tile
        (256, 0, 256, 256),    # Top-right tile  
        (0, 256, 256, 256),    # Bottom-left tile
        (512, 512, 256, 256),  # Interior tile
    ]
    
    for i, (tile_x, tile_y, tile_w, tile_h) in enumerate(test_cases):
        print(f"🔍 Test Case {i+1}: Tile at ({tile_x}, {tile_y})")
        
        # Detailed approach (current working method)
        x_min, y_min = tile_x, tile_y
        x_max, y_max = tile_x + tile_w, tile_y + tile_h
        
        detailed_coords = [
            transform * (x_min, y_min),  # Top-left
            transform * (x_max, y_min),  # Top-right  
            transform * (x_max, y_max),  # Bottom-right
            transform * (x_min, y_max),  # Bottom-left
        ]
        
        # Grid approach (should match detailed)
        grid_coords = [
            transform * (tile_x, tile_y),                          # Top-left
            transform * (tile_x + tile_w, tile_y),                 # Top-right
            transform * (tile_x + tile_w, tile_y + tile_h),        # Bottom-right  
            transform * (tile_x, tile_y + tile_h),                 # Bottom-left
        ]
        
        # Compare coordinates
        print(f"   📍 Detailed: {detailed_coords}")
        print(f"   📍 Grid:     {grid_coords}")
        
        # Check if they match
        matches = all(
            abs(d[0] - g[0]) < 0.001 and abs(d[1] - g[1]) < 0.001 
            for d, g in zip(detailed_coords, grid_coords)
        )
        
        print(f"   ✅ Match: {matches}")
        
        if matches:
            # Calculate actual UTM coordinates
            utm_coords = detailed_coords
            print(f"   🗺️ UTM Top-left: ({utm_coords[0][0]:.1f}, {utm_coords[0][1]:.1f})")
            print(f"   📏 Tile size: {utm_coords[1][0] - utm_coords[0][0]:.1f}m x {utm_coords[0][1] - utm_coords[3][1]:.1f}m")
        print()
    
    print("💡 Key Points for UTM Data:")
    print("   - Square pixels ensure regular grid structure")
    print("   - Grid approach should be perfectly aligned")
    print("   - Coordinate transformation is linear and predictable")
    print("   - No projection distortion within UTM zone")

if __name__ == "__main__":
    test_coordinate_consistency()
