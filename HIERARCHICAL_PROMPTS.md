# Hierarchical Class Names and Prompt Templates

## Overview

YoClip now supports hierarchical class names and prompt templates to improve CLIP embedding quality. This is particularly useful for aerial and satellite imagery where objects have natural hierarchies.

## Hierarchical Class Names

Class names can use a three-level hierarchy separated by semicolons:

```
major_category;subcategory;specific_type
```

### Examples:
- `vehicle;car;sedan`
- `vehicle;truck;pickup`
- `building;residential;house`
- `building;commercial;office`
- `vegetation;tree;oak`
- `vegetation;grass;lawn`

## Prompt Templates

Prompt templates help CLIP better understand the context and relationships in your class names.

### Template Format

Use `{class}` as a placeholder in your template:

```bash
yoclip yolotoclip /path/to/dataset output.csv --prompt-template "aerial view of {class}"
```

### Recommended Templates for Aerial/Satellite Imagery

1. **Aerial Context**: `"aerial view of {class}"`
2. **Satellite Context**: `"satellite image showing {class}"`
3. **Overhead Perspective**: `"overhead photograph of {class}"`
4. **General Photo**: `"a photo of {class}"`

## How It Works

1. **Hierarchical Processing**: Semicolons (`;`) in class names are converted to commas (`,`) for better natural language understanding
2. **Template Application**: The `{class}` placeholder is replaced with the processed class name
3. **CLIP Encoding**: The formatted prompts are encoded by CLIP instead of raw class names

### Example Transformation

```
Raw class name: "vehicle;car;sedan"
Template: "aerial view of {class}"
Result: "aerial view of vehicle, car, sedan"
```

## Usage Examples

### Basic Usage
```bash
# Without prompt template (uses raw class names)
yoclip yolotoclip /path/to/dataset output.csv

# With prompt template
yoclip yolotoclip /path/to/dataset output.csv --prompt-template "aerial view of {class}"
```

### Complete Workflow
```bash
# 1. Process YOLO dataset with hierarchical prompts
yoclip yolotoclip /path/to/yolo_dataset embeddings.csv --prompt-template "satellite image showing {class}"

# 2. Create query vector for a specific class
yoclip create-query embeddings.pkl "vehicle;car;sedan" query_vector.npy

# 3. Process GeoTIFF to find similar objects
yoclip process satellite.tif query_vector.npy embeddings.pkl results.csv --shapefile
```

## Benefits

1. **Better Context**: Templates provide spatial and viewing context that CLIP understands
2. **Natural Language**: Converts technical class names into natural language descriptions
3. **Improved Accuracy**: Better embeddings lead to more accurate similarity matching
4. **Hierarchical Understanding**: CLIP can better understand object relationships and categories

## Best Practices

1. **Match Your Data**: Use templates that match your imagery type (aerial, satellite, drone, etc.)
2. **Consistent Templates**: Use the same template for training and inference
3. **Test Different Templates**: Experiment with different templates to find what works best for your use case
4. **Clear Hierarchies**: Use clear, logical hierarchies in your class names
