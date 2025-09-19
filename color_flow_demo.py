#!/usr/bin/env python3
"""
Demonstration of alphabetical color assignment for QGIS visualization.
Shows how colors are assigned in a predictable flow based on class names.
"""

import colorsys

def demonstrate_color_flow():
    """Show how colors are assigned alphabetically."""
    
    # Example hierarchical seagrass classes (typical for marine mapping)
    example_classes = [
        'substrate;rock;boulder',
        'substrate;sand;coarse', 
        'substrate;sand;fine',
        'substrate;silt;organic',
        'vegetation;algae;brown',
        'vegetation;algae;green',
        'vegetation;seagrass;dense',
        'vegetation;seagrass;moderate',
        'vegetation;seagrass;sparse',
        'water;clear;shallow',
        'water;turbid;deep'
    ]
    
    # Sort alphabetically (this is what the code now does)
    sorted_classes = sorted(example_classes)
    
    print("🎨 Color Assignment Flow (Alphabetical Order)")
    print("=" * 60)
    
    # Generate colors using same algorithm as the code
    def generate_color_palette(n_colors):
        colors = []
        for i in range(n_colors):
            hue = i / n_colors  # Evenly distribute hues around color wheel
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)  # High saturation, high value
            rgb = tuple(int(c * 255) for c in rgb)
            colors.append(rgb)
        return colors
    
    colors = generate_color_palette(len(sorted_classes))
    
    # Show the mapping
    for i, (class_name, rgb) in enumerate(zip(sorted_classes, colors)):
        hue_degrees = int((i / len(sorted_classes)) * 360)
        hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        print(f"{i+1:2d}. {class_name:<30} → {hex_color} RGB{rgb} (Hue: {hue_degrees}°)")
    
    print("\n📊 Color Distribution Pattern:")
    print("- Colors flow smoothly around the HSV color wheel")
    print("- Each class gets an evenly spaced hue (360° / number_of_classes)")
    print("- Alphabetical sorting ensures consistent color assignment")
    print("- Same class names will always get the same colors")
    
    print("\n🎯 Benefits of Alphabetical Sorting:")
    print("- Predictable: 'substrate' classes always come before 'vegetation'")
    print("- Consistent: Same class always gets same color across different runs")
    print("- Logical: Related classes (same hierarchy) appear near each other")
    print("- Professional: Clean color progression in QGIS legend")

if __name__ == "__main__":
    demonstrate_color_flow()
