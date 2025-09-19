#!/usr/bin/env python3
"""
Test script to demonstrate the new automatic query vector creation functionality.
"""

def test_create_query_usage():
    """Show the different ways to use the create-query command."""
    
    print("🚀 YoClip Create-Query Command Usage Examples\n")
    
    print("📋 Option 1: Create query vectors for ALL classes automatically (RECOMMENDED)")
    print("   Command: yoclip create-query /path/to/embeddings.pkl")
    print("   Result:  Creates query vectors for every class found in the embeddings")
    print("   Output:  query_vectors/ directory with individual .npy files for each class")
    print("   Benefits: No need to know class names, processes everything at once")
    print()
    
    print("📋 Option 2: Create query vector for a specific class")
    print("   Command: yoclip create-query /path/to/embeddings.pkl 'seagrass' --output-file seagrass_query.npy")
    print("   Result:  Creates query vector only for the 'seagrass' class")
    print("   Output:  Single seagrass_query.npy file")
    print("   Benefits: Focused on one class, custom output filename")
    print()
    
    print("🔧 Advanced Options:")
    print("   --output-dir:  Specify custom directory for auto-generated vectors")
    print("   --method:      Choose aggregation method (mean, median, centroid)")
    print()
    
    print("💡 Typical Workflow:")
    print("   1. yoclip yolotoclip /dataset output.csv --prompt-template 'aerial view of {class}'")
    print("   2. yoclip create-query output.pkl  # Creates vectors for ALL classes automatically")
    print("   3. yoclip process satellite.tif query_vectors/query_seagrass.npy output.pkl results.csv")
    print()
    
    print("✅ Benefits of Automatic Query Vector Creation:")
    print("   - No need to manually specify class names")
    print("   - Creates vectors for ALL classes at once")
    print("   - Provides summary of what was created")
    print("   - Safe filename handling for hierarchical classes (vehicle;car;sedan → query_vehicle_car_sedan.npy)")
    print("   - Easy to use any class for subsequent processing")


def show_output_structure():
    """Show what the automatic output structure looks like."""
    
    print("\n📁 Output Structure for Automatic Query Vector Creation:")
    print("query_vectors/")
    print("├── query_seagrass.npy")
    print("├── query_sand.npy") 
    print("├── query_rock.npy")
    print("├── query_vehicle_car_sedan.npy      # Hierarchical class: vehicle;car;sedan")
    print("├── query_building_residential_house.npy  # Hierarchical class: building;residential;house")
    print("└── query_vectors_summary.csv        # Summary with class info")
    print()
    print("📊 Summary CSV contains:")
    print("   - class_name: Original class name (with semicolons for hierarchical)")
    print("   - file_path: Path to the generated .npy file")
    print("   - num_embeddings: Number of embeddings used to create the vector")
    print("   - method: Aggregation method used (mean, median, centroid)")


if __name__ == "__main__":
    test_create_query_usage()
    show_output_structure()
