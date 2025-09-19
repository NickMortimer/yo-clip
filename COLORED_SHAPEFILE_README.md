# Colored Shapefile Implementation

## Overview
The shapefile creation functions have been enhanced to automatically generate color-coded visualizations for QGIS. This solves the issue where shapefiles appeared as single-colored polygons without clear classification visualization.

## New Features

### 1. Automatic Color Assignment
- **Unique Color per Class**: Each classification class gets a distinct, visually appealing color
- **HSV Color Space**: Uses HSV color generation for maximum visual distinction
- **Fallback Colors**: Predefined color palette if HSV generation fails
- **RGB & Hex Values**: Stores both RGB components and hex color codes in the shapefile attributes

### 2. Enhanced Shapefile Attributes
The shapefile now includes these additional fields:
- `red`, `green`, `blue`: RGB color values (0-255)
- `color_hex`: Hex color code (e.g., "#FF5733")
- `best_class`: Classification result
- `similarity`: Confidence score
- Original fields: `tile_id`, `tile_x`, `tile_y`, etc.

### 3. QGIS Style File (QML)
- **Automatic Style Generation**: Creates a `.qml` file alongside the shapefile
- **Categorized Symbology**: Automatically sets up categorized styling based on `best_class`
- **Color Coordination**: Uses the same colors as stored in the shapefile attributes
- **Auto-loading**: QGIS will often automatically apply the style when loading the shapefile

### 4. GeoJSON Enhancement
The GeoJSON output has been similarly enhanced with color information for web mapping applications.

## Usage in QGIS

### Automatic Method (Preferred)
1. Load the `.shp` file in QGIS
2. The `.qml` style file should automatically apply colored styling
3. Each class will appear in a different color with proper legend

### Manual Method (If needed)
1. Right-click the layer → Properties → Symbology
2. Change from "Single Symbol" to "Categorized"
3. Set Column to "best_class"
4. Click "Classify" to generate categories
5. Colors should be automatically assigned

### Custom Styling
- Use the `red`, `green`, `blue` fields for custom color expressions
- Use `color_hex` field for web-compatible color codes
- Use `similarity` field for transparency/opacity based on confidence

## Technical Implementation

### Color Generation Algorithm
```python
def generate_color_palette(n_colors):
    colors = []
    for i in range(n_colors):
        hue = i / n_colors  # Distribute hues evenly
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)  # High saturation, high value
        rgb = tuple(int(c * 255) for c in rgb)
        colors.append(rgb)
    return colors
```

### Key Benefits
- **Visual Clarity**: Immediate identification of different classification zones
- **Legend Generation**: Automatic legend with class names and colors
- **Spatial Analysis**: Easy visual assessment of classification patterns
- **Export Ready**: Styled maps ready for publication or presentation

## Example Output
```
🎨 Found 4 unique classes: ['substrate;rock;boulder', 'vegetation;seagrass;sparse', 'vegetation;seagrass;dense', 'substrate;sand;fine']
📋 Class distribution:
   substrate;rock;boulder: 1 tiles (RGB: (229, 45, 45))
   substrate;sand;fine: 1 tiles (RGB: (137, 45, 229))
   vegetation;seagrass;dense: 2 tiles (RGB: (45, 229, 229))
   vegetation;seagrass;sparse: 1 tiles (RGB: (137, 229, 45))
```

## Files Created
When using `create_shapefile=True`, the following files are generated:
- `output.shp` - Main shapefile with enhanced attributes
- `output.shx` - Spatial index
- `output.dbf` - Attribute database (with color information)
- `output.prj` - Coordinate reference system
- `output.cpg` - Character encoding
- `output.qml` - QGIS style file for automatic color styling

This enhancement transforms the shapefile from a basic geometric representation into a rich, immediately visualizable classification map suitable for analysis and presentation in QGIS.
