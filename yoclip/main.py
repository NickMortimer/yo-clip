import typer
from pathlib import Path

from yoclip.yolotoclip import run_yolotoclip
from yoclip.process import run_process
from yoclip.utils import console


app = typer.Typer()


@app.command()
def yolotoclip(
    root_dir: Path = typer.Argument(..., help="Root YOLO dataset directory (with images/ and labels/ subfolders)"),
    output_file: Path = typer.Option("clip_embeddings.csv", help="Output CSV file for embeddings"),
    batch_size: int = typer.Option(32, help="Batch size for processing images"),
    model_name: str = typer.Option("ViT-B/32", help="CLIP model to use"),
    prompt_template: str = typer.Option("", help="Template for class prompts (e.g., 'a photo of {class}' or 'aerial view of {class}')")
):
    """
    Encode YOLO images and bounding box crops into CLIP embeddings and save them for classification.
    Uses batch processing for efficient GPU utilization.
    """
    try:
        run_yolotoclip(root_dir, output_file, batch_size, model_name, prompt_template)
    except Exception as e:
        console.print(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def create_query(
    embeddings_file: Path = typer.Argument(..., help="Path to embeddings pickle file (.pkl)"),
    class_name: str = typer.Argument(None, help="Specific class name to create query vector for (optional - if not provided, creates vectors for all classes)"),
    output_file: Path = typer.Option("query_vector.npy", help="Output query vector file (used only when class_name is specified)"),
    output_dir: Path = typer.Option("query_vectors", help="Output directory for query vectors (used when processing all classes)"),
    method: str = typer.Option("mean", help="Method to create query vector: 'mean', 'median', or 'centroid'"),
):
    """Create query vector(s) from embeddings. If no class is specified, creates vectors for all classes."""
    from yoclip.process import create_query_vector, create_query_vectors_auto
    
    if class_name:
        # Create query vector for specific class
        console.print(f"🎯 Creating query vector for class: {class_name}")
        console.print(f"📁 From embeddings: {embeddings_file}")
        console.print(f"🔢 Method: {method}")
        
        try:
            create_query_vector(embeddings_file, class_name, output_file, method)
            console.print(f"✅ Saved query vector to: {output_file}")
        except Exception as e:
            console.print(f"❌ Error: {e}")
            raise typer.Exit(1)
    else:
        # Create query vectors for all classes automatically
        console.print(f"🚀 Creating query vectors for ALL classes found in embeddings")
        console.print(f"📁 From embeddings: {embeddings_file}")
        console.print(f"📂 Output directory: {output_dir}")
        console.print(f"🔢 Method: {method}")
        
        try:
            create_query_vectors_auto(embeddings_file, output_dir, method)
            console.print(f"✅ Created query vectors for all classes in: {output_dir}")
        except Exception as e:
            console.print(f"❌ Error: {e}")
            raise typer.Exit(1)


@app.command()
def process(
    geotiff_path: Path = typer.Argument(..., help="Path to GeoTIFF file"),
    query_vector_path: Path = typer.Argument(..., help="Path to query vector (.npy file) or directory containing query vectors"),
    embeddings_file: Path = typer.Argument(..., help="Path to embeddings pickle file (.pkl)"),
    output_file: Path = typer.Option("similarity_results.csv", help="Output CSV file"),
    tile_size: int = typer.Option(512, help="Size of tiles to extract"),
    overlap: int = typer.Option(0, help="Overlap between tiles in pixels"),
    batch_size: int = typer.Option(32, help="Batch size for processing tiles"),
    top_k: int = typer.Option(5, help="Number of top similar images to return per tile"),
    create_shapefile: bool = typer.Option(False, "--shapefile", help="Create shapefile for QGIS"),
    create_geojson: bool = typer.Option(False, "--geojson", help="Create GeoJSON for web mapping"),
    use_grid: bool = typer.Option(False, "--grid", help="Use fast grid-based shapefile instead of individual tile polygons (much faster for large datasets)"),
    color_csv: Path = typer.Option(None, "--color-csv", help="CSV file mapping habitat types to color hex codes (for custom QGIS coloring)"),
):
    """Process GeoTIFF and find similar images using CLIP embeddings. Can use single query vector or directory of vectors for multi-class classification."""
    console.print(f"🌍 Processing GeoTIFF: {geotiff_path}")
    console.print(f"🔍 Query vector: {query_vector_path}")
    console.print(f"📁 Embeddings: {embeddings_file}")
    console.print(f"📏 Tile size: {tile_size}x{tile_size}")
    console.print(f"🔄 Overlap: {overlap} pixels")
    console.print(f"📦 Batch size: {batch_size}")
    console.print(f"🎯 Top K matches: {top_k}")
    
    if create_shapefile:
        if use_grid:
            console.print("🗺️ Will create fast grid-based shapefile for QGIS")
        else:
            console.print("🗺️ Will create detailed shapefile for QGIS")
    if create_geojson:
        console.print("🌐 Will create GeoJSON for web mapping")
    
    run_process(
        geotiff_path=geotiff_path,
        query_vector_path=query_vector_path,
        embeddings_file=embeddings_file,
        output_file=output_file,
        tile_size=tile_size,
        overlap=overlap,
        batch_size=batch_size,
        top_k=top_k,
        create_shapefile=create_shapefile,
        create_geojson=create_geojson,
        use_grid=use_grid,
        color_csv=color_csv,
    )


if __name__ == "__main__":
    app()