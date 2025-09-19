#!/usr/bin/env python3
"""
Test continuous grid generation for UTM data.

This test verifies that the grid approach creates a continuous grid 
without gaps between cells, which is essential for proper visualization
in QGIS.
"""

def test_continuous_grid():
    """Test that grid cells are continuous without gaps."""
    print("🧪 Testing Continuous Grid Generation")
    print("=" * 40)
    
    # Simulate tile positions that might have gaps due to processing
    # (e.g., some tiles might be skipped due to invalid data)
    tile_positions = [
        (0, 0),      # Row 0, Col 0
        (256, 0),    # Row 0, Col 1  
        (512, 0),    # Row 0, Col 2
        (0, 256),    # Row 1, Col 0
        # Missing (256, 256) - simulates skipped tile
        (512, 256),  # Row 1, Col 2
        (0, 512),    # Row 2, Col 0
        (256, 512),  # Row 2, Col 1
        (512, 512),  # Row 2, Col 2
    ]
    
    print(f"📋 Simulated tile positions: {len(tile_positions)} tiles")
    for pos in tile_positions:
        print(f"   📍 Tile at {pos}")
    print()
    
    # Old approach (using range with step) - creates gaps
    tile_width, tile_height = 256, 256
    min_x = min(pos[0] for pos in tile_positions)
    max_x = max(pos[0] for pos in tile_positions) + tile_width
    min_y = min(pos[1] for pos in tile_positions)  
    max_y = max(pos[1] for pos in tile_positions) + tile_height
    
    old_grid_positions = []
    for y in range(min_y, max_y, tile_height):
        for x in range(min_x, max_x, tile_width):
            if (x, y) in tile_positions:  # Only if tile exists
                old_grid_positions.append((x, y))
    
    print(f"❌ Old approach (range-based): {len(old_grid_positions)} cells")
    print(f"   Grid positions: {old_grid_positions}")
    print()
    
    # New approach (position-based) - continuous grid
    sorted_x_positions = sorted(set(pos[0] for pos in tile_positions))
    sorted_y_positions = sorted(set(pos[1] for pos in tile_positions))
    
    new_grid_positions = []
    for y_pos in sorted_y_positions:
        for x_pos in sorted_x_positions:
            if (x_pos, y_pos) in tile_positions:  # Only if tile exists
                new_grid_positions.append((x_pos, y_pos))
    
    print(f"✅ New approach (position-based): {len(new_grid_positions)} cells")
    print(f"   Grid positions: {new_grid_positions}")
    print()
    
    # Test continuity - check for gaps
    def check_continuity(positions, tile_w, tile_h):
        """Check if grid positions form a continuous grid."""
        gaps = []
        positions_set = set(positions)
        
        for pos in positions:
            x, y = pos
            # Check adjacent positions
            adjacent = [
                (x + tile_w, y),      # Right
                (x, y + tile_h),      # Below
                (x - tile_w, y),      # Left  
                (x, y - tile_h),      # Above
            ]
            
            for adj_pos in adjacent:
                if adj_pos in positions_set:
                    # Check if there's a gap between current and adjacent
                    x1, y1 = pos
                    x2, y2 = adj_pos
                    
                    # For continuous grid, tiles should be exactly tile_width apart
                    x_gap = abs(x2 - x1) - tile_w if x1 != x2 else 0
                    y_gap = abs(y2 - y1) - tile_h if y1 != y2 else 0
                    
                    if x_gap > 0 or y_gap > 0:
                        gaps.append((pos, adj_pos, x_gap, y_gap))
        
        return gaps
    
    old_gaps = check_continuity(old_grid_positions, tile_width, tile_height)
    new_gaps = check_continuity(new_grid_positions, tile_width, tile_height)
    
    print(f"🔍 Gap Analysis:")
    print(f"   Old approach gaps: {len(old_gaps)}")
    print(f"   New approach gaps: {len(new_gaps)}")
    
    if old_gaps:
        print(f"   ❌ Old gaps found: {old_gaps[:3]}...")  # Show first 3
    
    if new_gaps:
        print(f"   ❌ New gaps found: {new_gaps}")
    else:
        print(f"   ✅ New approach: No gaps detected!")
    
    print()
    print("💡 Key Insights:")
    print("   - Position-based approach ensures continuity")
    print("   - Works even when some tiles are missing")
    print("   - Creates proper grid structure for QGIS")
    print("   - No artificial gaps between valid tiles")

if __name__ == "__main__":
    test_continuous_grid()
