#!/usr/bin/env python3
"""
RESTORED YoClip Workflow with Batch Processing

This shows your original workflow but with added batch processing capabilities.
"""

def show_restored_workflow():
    print("🔄 RESTORED YoClip Workflow with Batch Processing")
    print("=" * 55)
    print()
    
    print("📁 Your Original Data Structure:")
    print("   ├── yolo_tiles/")
    print("   │   ├── images/          # Your training tile images")
    print("   │   ├── labels/          # YOLO format labels")
    print("   │   └── classes.txt      # Class names")
    print("   └── query_vector.npy     # From your few-shot training")
    print()
    
    print("🚀 Step 1: Create embeddings from YOLO tiles (with batch processing)")
    print("-" * 70)
    yolo_cmd = """python -m yoclip.main yolotoclip \\
    /path/to/yolo_tiles \\
    --output-file tile_embeddings.csv \\
    --batch-size 64 \\
    --model-name ViT-B/32"""
    print(yolo_cmd)
    print()
    print("   Creates:")
    print("   ├── tile_embeddings.csv    # Human readable")
    print("   └── tile_embeddings.pkl    # Full embeddings + metadata")
    print()
    
    print("🎯 Step 2: Create query vector from specific class (NEW!)")
    print("-" * 60)
    query_cmd = """python -m yoclip.main create-query \\
    tile_embeddings.pkl \\
    "building" \\
    --output-file building_query.npy \\
    --method mean"""
    print(query_cmd)
    print()
    print("   Creates:")
    print("   └── building_query.npy       # Query vector for 'building' class")
    print()
    
    print("🎯 Step 3: Apply to GeoTIFF with your query vector (with batch processing)")
    print("-" * 80)
    process_cmd = """python -m yoclip.main process \\
    satellite_image.tif \\
    building_query.npy \\
    tile_embeddings.pkl \\
    --batch-size 32 \\
    --tile-size 512 \\
    --top-k 10 \\
    --shapefile \\
    --geojson"""
    print(process_cmd)
    print()
    print("   Creates:")
    print("   ├── similarity_results.csv     # Similarity matches")
    print("   ├── similarity_results.shp     # For QGIS visualization")
    print("   └── similarity_results.geojson # For web mapping")
    print()
    
    print("🔧 Key Improvements Added:")
    print("   ✅ Batch processing for GPU efficiency")
    print("   ✅ Configurable batch sizes (--batch-size)")
    print("   ✅ Maintained original pickle format")
    print("   ✅ Added spatial outputs (shapefile/GeoJSON)")
    print("   ✅ NEW: Query vector creation from class embeddings")
    print("   ✅ Preserved your few-shot training workflow")
    print()
    
    print("💡 Performance Tips:")
    print("   • Increase batch size for better GPU utilization")
    print("   • Larger tile sizes capture more context")
    print("   • Use --shapefile for QGIS visualization")
    print("   • Adjust --top-k based on your analysis needs")
    print("   • Try different methods (mean/median/centroid) for query creation")
    print()
    
    print("🎯 Query Vector Creation Methods:")
    print("   • mean: Average of all class embeddings (default)")
    print("   • median: Median of all class embeddings (robust to outliers)")
    print("   • centroid: Normalized mean (good for cosine similarity)")
    print()
    
    print("🔍 Your Complete Workflow:")
    print("   1. Create embeddings from YOLO tiles")
    print("   2. Create query vector for target class")
    print("   3. Apply to GeoTIFF to find similar areas")

if __name__ == "__main__":
    show_restored_workflow()
