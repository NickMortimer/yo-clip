#!/usr/bin/env python3
"""
Test grid cell sizing for UTM data.

This test verifies that grid cells are the correct size and properly aligned.
The issue was that we were using tile pixel dimensions instead of the 
actual coordinate spacing between tiles.
"""

def test_grid_cell_sizing():
    """Test that grid cells are correctly sized."""
    print("🧪 Testing Grid Cell Sizing")
    print("=" * 35)
    
    # Simulate tile metadata for a regular grid
    # Tiles are 256x256 pixels at positions that are 256 pixels apart
    tile_metadata = [
        {'tile_x': 0, 'tile_y': 0, 'tile_width': 256, 'tile_height': 256},
        {'tile_x': 256, 'tile_y': 0, 'tile_width': 256, 'tile_height': 256},
        {'tile_x': 512, 'tile_y': 0, 'tile_width': 256, 'tile_height': 256},
        {'tile_x': 0, 'tile_y': 256, 'tile_width': 256, 'tile_height': 256},
        {'tile_x': 256, 'tile_y': 256, 'tile_width': 256, 'tile_height': 256},
        {'tile_x': 512, 'tile_y': 256, 'tile_width': 256, 'tile_height': 256},
    ]
    
    print(f"📋 Input tiles: {len(tile_metadata)} tiles")
    for meta in tile_metadata:
        print(f"   📍 Tile at ({meta['tile_x']}, {meta['tile_y']}) size {meta['tile_width']}x{meta['tile_height']}")
    print()
    
    # Old approach (incorrect - using tile pixel dimensions)
    first_tile = tile_metadata[0]
    old_tile_width = first_tile['tile_width']   # 256 pixels
    old_tile_height = first_tile['tile_height'] # 256 pixels
    
    print(f"❌ Old approach (pixel dimensions):")
    print(f"   Cell size: {old_tile_width}x{old_tile_height} pixels")
    print(f"   Problem: Uses pixel dimensions, not coordinate spacing")
    print()
    
    # New approach (correct - calculate actual grid spacing)
    tile_positions = [(meta['tile_x'], meta['tile_y']) for meta in tile_metadata]
    x_positions = sorted(set(pos[0] for pos in tile_positions))
    y_positions = sorted(set(pos[1] for pos in tile_positions))
    
    print(f"✅ New approach (coordinate spacing):")
    print(f"   X positions: {x_positions}")
    print(f"   Y positions: {y_positions}")
    
    # Calculate grid spacing
    if len(x_positions) > 1:
        grid_cell_width = min(x_positions[i+1] - x_positions[i] for i in range(len(x_positions)-1))
    else:
        grid_cell_width = tile_metadata[0]['tile_width']
        
    if len(y_positions) > 1:
        grid_cell_height = min(y_positions[i+1] - y_positions[i] for i in range(len(y_positions)-1))
    else:
        grid_cell_height = tile_metadata[0]['tile_height']
    
    print(f"   Grid cell size: {grid_cell_width}x{grid_cell_height} pixels")
    print(f"   Correctly uses spacing between tiles!")
    print()
    
    # Test coordinate transformation
    print(f"🔍 Coordinate Transformation Test:")
    
    # Simulate UTM transform (0.5m/pixel)
    class MockTransform:
        def __init__(self, pixel_size):
            self.pixel_size = pixel_size
            self.x_origin = 300000
            self.y_origin = 8500000
            
        def __mul__(self, coords):
            x, y = coords
            return (self.x_origin + x * self.pixel_size, 
                   self.y_origin - y * self.pixel_size)
    
    transform = MockTransform(0.5)  # 0.5 meters per pixel
    
    # Test a grid cell at position (256, 256)
    test_x, test_y = 256, 256
    
    # Old approach (incorrect)
    old_corners = [
        transform * (test_x, test_y),
        transform * (test_x + old_tile_width, test_y),
        transform * (test_x + old_tile_width, test_y + old_tile_height),
        transform * (test_x, test_y + old_tile_height),
    ]
    
    # New approach (correct)
    new_corners = [
        transform * (test_x, test_y),
        transform * (test_x + grid_cell_width, test_y),
        transform * (test_x + grid_cell_width, test_y + grid_cell_height),
        transform * (test_x, test_y + grid_cell_height),
    ]
    
    print(f"   Test cell at pixel position ({test_x}, {test_y}):")
    print(f"   Old approach corners: {old_corners}")
    print(f"   New approach corners: {new_corners}")
    
    # Calculate cell sizes in meters
    old_width_m = abs(old_corners[1][0] - old_corners[0][0])
    old_height_m = abs(old_corners[0][1] - old_corners[3][1])
    new_width_m = abs(new_corners[1][0] - new_corners[0][0])
    new_height_m = abs(new_corners[0][1] - new_corners[3][1])
    
    print()
    print(f"📏 Cell sizes in meters:")
    print(f"   Old approach: {old_width_m}m x {old_height_m}m")
    print(f"   New approach: {new_width_m}m x {new_height_m}m")
    print(f"   Expected: 128.0m x 128.0m (256 pixels * 0.5 m/pixel)")
    
    if abs(new_width_m - 128.0) < 0.1 and abs(new_height_m - 128.0) < 0.1:
        print(f"   ✅ New approach produces correct cell size!")
    else:
        print(f"   ❌ New approach still has sizing issues")
    
    print()
    print("💡 Key Insight:")
    print("   Grid cell size should match the spacing between tile positions,")
    print("   not the pixel dimensions of individual tiles!")

if __name__ == "__main__":
    test_grid_cell_sizing()
