"""GeoTIFF processing and CLIP similarity matching functionality."""

import torch
import clip
import pickle
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import rasterio
from rasterio.windows import Window
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
import geopandas as gpd
from shapely.geometry import Polygon

from yoclip.utils import console, find_closest_vectors


def create_qgis_style_file(shapefile_path: Path, unique_classes: List[str], class_to_color: Dict[str, Tuple[int, int, int]]):
    """Create a QGIS style file (QML) for automatic classification styling."""
    qml_path = shapefile_path.with_suffix('.qml')
    
    # Create QML content for categorized styling
    qml_content = '''<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0" styleCategories="AllStyleCategories">
  <renderer-v2 type="categorizedSymbol" symbollevels="0" enableorderby="0" forceraster="0" attr="best_class">
    <categories>
'''
    
    # Add category for each class
    for i, class_name in enumerate(unique_classes):
        rgb_color = class_to_color[class_name]
        
        qml_content += f'''      <category render="true" symbol="{i}" value="{class_name}" label="{class_name}"/>
'''
    
    qml_content += '''    </categories>
    <symbols>
'''
    
    # Add symbol for each class
    for i, class_name in enumerate(unique_classes):
        rgb_color = class_to_color[class_name]
        
        qml_content += f'''      <symbol alpha="0.7" type="fill" name="{i}" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="{rgb_color[0]},{rgb_color[1]},{rgb_color[2]},255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="{rgb_color[0]},{rgb_color[1]},{rgb_color[2]},255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
'''
    
    qml_content += '''    </symbols>
    <source-symbol>
      <symbol alpha="1" type="fill" name="0" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" class="SimpleFill" enabled="1" locked="0">
          <Option type="Map">
            <Option type="QString" name="border_width_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="color" value="145,82,45,255"/>
            <Option type="QString" name="joinstyle" value="bevel"/>
            <Option type="QString" name="offset" value="0,0"/>
            <Option type="QString" name="offset_map_unit_scale" value="3x:0,0,0,0,0,0"/>
            <Option type="QString" name="offset_unit" value="MM"/>
            <Option type="QString" name="outline_color" value="35,35,35,255"/>
            <Option type="QString" name="outline_style" value="solid"/>
            <Option type="QString" name="outline_width" value="0.26"/>
            <Option type="QString" name="outline_width_unit" value="MM"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="145,82,45,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="randomcolors" name="[source]">
      <Option/>
    </colorramp>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontCapitals="0" fontFamily="Ubuntu" fontSize="10" textOpacity="1" fontWeight="50" multilineHeight="1" fontWordSpacing="0" fontSizeMapUnitScale="3x:0,0,0,0,0,0" allowHtml="0" namedStyle="Regular" fontLetterSpacing="0" fontStrikeout="0" fontSizeUnit="Point" textOrientation="horizontal" blendMode="0" fontUnderline="0" textColor="50,50,50,255" fontItalic="0" useSubstitutions="0" fontKerning="1" previewBkgrdColor="255,255,255,255" isExpression="0" fieldName="best_class">
        <families/>
        <text-buffer bufferSize="1" bufferOpacity="1" bufferSizeUnits="MM" bufferColor="250,250,250,255" bufferBlendMode="0" bufferJoinStyle="128" bufferDraw="0" bufferNoFill="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0"/>
        <text-mask maskJoinStyle="128" maskSize="1.5" maskOpacity="1" maskType="0" maskEnabled="0" maskedSymbolLayers="" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskSizeUnits="MM"/>
        <background shapeRadiiY="0" shapeBorderColor="128,128,128,255" shapeRadiiX="0" shapeFillColor="255,255,255,255" shapeOffsetY="0" shapeSizeX="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeBorderWidth="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeSizeY="0" shapeDraw="0" shapeBlendMode="0" shapeJoinStyle="64" shapeOffsetX="0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeOpacity="1" shapeSVGFile="" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeRotation="0" shapeSizeType="0" shapeBorderWidthUnit="Point" shapeRadiiUnit="Point" shapeSizeUnit="Point" shapeOffsetUnit="Point" shapeType="0"/>
        <shadow shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowColor="0,0,0,255" shadowOffsetDist="1" shadowOffsetGlobal="1" shadowRadius="1.5" shadowRadiusAlphaOnly="0" shadowOpacity="0.69999999999999996" shadowScale="100" shadowBlendMode="6" shadowRadiusUnit="MM" shadowDraw="0" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOffsetUnit="MM"/>
        <dd_properties>
          <Option type="Map">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format autoWrapLength="0" useMaxLineLengthForAutoWrap="1" rightDirectionSymbol=">" addDirectionSymbol="0" leftDirectionSymbol="&lt;" formatNumbers="0" reverseDirectionSymbol="0" decimals="3" multilineAlign="3" wrapChar="" placeDirectionSymbol="0" plussign="0"/>
      <placement centroidWhole="0" rotationAngle="0" maxCurvedCharAngleOut="-25" dist="0" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" geometryGenerator="" priority="5" overrunDistance="0" lineAnchorPercent="0.5" placementFlags="10" offsetUnits="MM" repeatDistanceUnits="MM" lineAnchorClipping="0" centroidInside="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" fitInPolygonOnly="0" layerType="2" lineAnchorType="0" distUnits="MM" repeatDistance="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" distMapUnitScale="3x:0,0,0,0,0,0" polygonPlacementFlags="2" preserveRotation="1" xOffset="0" quadOffset="4" placement="0" overrunDistanceUnit="MM" offsetType="0" maxCurvedCharAngleIn="25" rotationUnit="AngleDegrees" yOffset="0" geometryGeneratorType="PointGeometry"/>
      <rendering obstacle="1" fontMaxPixelSize="10000" scaleVisibility="0" drawLabels="0" unplacedVisibility="0" limitNumLabels="0" fontMinPixelSize="3" mergeLines="0" scaleMax="0" maxNumLabels="2000" obstacleType="1" minFeatureSize="0" labelPerPart="0" displayAll="0" upsidedownLabels="0" scaleMin="0" fontLimitPixelSize="0" zIndex="0" obstacleFactor="1"/>
      <dd_properties>
        <Option type="Map">
          <Option type="QString" name="name" value=""/>
          <Option name="properties"/>
          <Option type="QString" name="type" value="collection"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option type="QString" name="anchorPoint" value="pole_of_inaccessibility"/>
          <Option type="int" name="blendMode" value="0"/>
          <Option type="Map" name="ddProperties">
            <Option type="QString" name="name" value=""/>
            <Option name="properties"/>
            <Option type="QString" name="type" value="collection"/>
          </Option>
          <Option type="bool" name="drawToAllParts" value="false"/>
          <Option type="QString" name="enabled" value="0"/>
          <Option type="QString" name="labelAnchorPoint" value="point_on_exterior"/>
          <Option type="QString" name="lineSymbol" value="&lt;symbol alpha=&quot;1&quot; type=&quot;line&quot; name=&quot;symbol&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer pass=&quot;0&quot; class=&quot;SimpleLine&quot; enabled=&quot;1&quot; locked=&quot;0&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;align_dash_pattern&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;capstyle&quot; value=&quot;square&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash&quot; value=&quot;5;2&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;customdash_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;dash_pattern_offset_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;draw_inside_polygon&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;joinstyle&quot; value=&quot;bevel&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_color&quot; value=&quot;60,60,60,255&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_style&quot; value=&quot;solid&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_width&quot; value=&quot;0.3&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;line_width_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;offset_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;ring_filter&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_end_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;trim_distance_start_unit&quot; value=&quot;MM&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;tweak_dash_pattern_on_corners&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;use_custom_dash&quot; value=&quot;0&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;width_map_unit_scale&quot; value=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_end_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;trim_distance_start&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_start_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_start_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;/Option>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option type=&quot;QString&quot; name=&quot;name&quot; value=&quot;&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option type=&quot;QString&quot; name=&quot;type&quot; value=&quot;collection&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>"/>
          <Option type="double" name="minLength" value="0"/>
          <Option type="QString" name="minLengthMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="minLengthUnit" value="MM"/>
          <Option type="double" name="offsetFromAnchor" value="0"/>
          <Option type="QString" name="offsetFromAnchorMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromAnchorUnit" value="MM"/>
          <Option type="double" name="offsetFromLabel" value="0"/>
          <Option type="QString" name="offsetFromLabelMapUnitScale" value="3x:0,0,0,0,0,0"/>
          <Option type="QString" name="offsetFromLabelUnit" value="MM"/>
        </Option>
      </callout>
    </settings>
  </labeling>
</qgis>
'''
    
    # Write QML file
    with open(qml_path, 'w') as f:
        f.write(qml_content)
    
    console.print(f"🎨 Created QGIS style file: {qml_path}")


def create_query_vectors_auto(
    embeddings_file: Path,
    output_dir: Path,
    method: str = "mean"
) -> None:
    """
    Automatically create query vectors for all classes found in the embeddings file.
    
    Args:
        embeddings_file: Path to the embeddings pickle file
        output_dir: Directory to save query vector files
        method: Method to aggregate embeddings ('mean', 'median', 'centroid')
    """
    console.print(f"📂 Loading embeddings from: {embeddings_file}")
    
    # Load embeddings
    try:
        df_embeddings = pd.read_pickle(embeddings_file)
        console.print(f"✅ Loaded {len(df_embeddings)} embeddings")
    except Exception as e:
        console.print(f"❌ Error loading embeddings: {e}")
        raise ValueError(f"Error loading embeddings: {e}")
    
    # Get all unique classes
    available_classes = df_embeddings['class_name'].unique()
    console.print(f"🎯 Found {len(available_classes)} unique classes:")
    for class_name in sorted(available_classes):
        class_count = len(df_embeddings[df_embeddings['class_name'] == class_name])
        console.print(f"   📝 {class_name}: {class_count} embeddings")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print(f"\n🔧 Creating query vectors using method: {method}")
    
    # Process each class
    query_vectors_info = []
    for class_name in sorted(available_classes):
        # Filter by class name
        class_embeddings = df_embeddings[df_embeddings['class_name'] == class_name]
        
        # Extract embeddings
        embeddings = np.stack(class_embeddings['image_embedding'].values)
        
        # Create query vector using specified method
        if method == "mean":
            query_vector = np.mean(embeddings, axis=0)
        elif method == "median":
            query_vector = np.median(embeddings, axis=0)
        elif method == "centroid":
            # Centroid: normalize first, then mean
            normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            query_vector = np.mean(normalized_embeddings, axis=0)
            query_vector = query_vector / np.linalg.norm(query_vector)  # Re-normalize
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Create safe filename from class name
        safe_class_name = class_name.replace(';', '_').replace('/', '_').replace(' ', '_')
        output_file = output_dir / f"query_{safe_class_name}.npy"
        
        # Save query vector
        np.save(output_file, query_vector)
        
        query_vectors_info.append({
            'class_name': class_name,
            'file_path': str(output_file),
            'num_embeddings': len(class_embeddings),
            'method': method
        })
        
        console.print(f"   ✅ {class_name} → {output_file}")
    
    # Save summary info
    summary_file = output_dir / "query_vectors_summary.csv"
    summary_df = pd.DataFrame(query_vectors_info)
    summary_df.to_csv(summary_file, index=False, quoting=1)  # quoting=1 means QUOTE_ALL
    
    console.print(f"\n📊 Summary:")
    console.print(f"   🎯 Created {len(query_vectors_info)} query vectors")
    console.print(f"   📁 Saved to: {output_dir}")
    console.print(f"   📋 Summary: {summary_file}")


def create_query_vector(
    embeddings_file: Path,
    class_name: str,
    output_file: Path,
    method: str = "mean"
) -> None:
    """
    Create a query vector from embeddings of a specific class.
    
    Args:
        embeddings_file: Path to the embeddings pickle file
        class_name: Name of the class to create query vector for
        output_file: Path to save the query vector
        method: Method to aggregate embeddings ('mean', 'median', 'centroid')
    """
    console.print(f"📂 Loading embeddings from: {embeddings_file}")
    
    # Load embeddings
    try:
        df_embeddings = pd.read_pickle(embeddings_file)
        console.print(f"✅ Loaded {len(df_embeddings)} embeddings")
    except Exception as e:
        console.print(f"❌ Error loading embeddings: {e}")
        raise ValueError(f"Error loading embeddings: {e}")
    
    # Filter by class name
    class_embeddings = df_embeddings[df_embeddings['class_name'] == class_name]
    
    if len(class_embeddings) == 0:
        available_classes = df_embeddings['class_name'].unique()
        console.print(f"❌ No embeddings found for class '{class_name}'")
        console.print(f"Available classes: {list(available_classes)}")
        raise ValueError(f"No embeddings found for class '{class_name}'")
    
    console.print(f"🎯 Found {len(class_embeddings)} embeddings for class '{class_name}'")
    
    # Extract embeddings
    embeddings = np.stack(class_embeddings['image_embedding'].values)
    
    # Create query vector using specified method
    if method == "mean":
        query_vector = np.mean(embeddings, axis=0)
    elif method == "median":
        query_vector = np.median(embeddings, axis=0)
    elif method == "centroid":
        # Centroid: normalize first, then mean
        normalized_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        query_vector = np.mean(normalized_embeddings, axis=0)
        query_vector = query_vector / np.linalg.norm(query_vector)  # Re-normalize
    else:
        console.print(f"❌ Unknown method '{method}'. Use 'mean', 'median', or 'centroid'")
        raise ValueError(f"Unknown method '{method}'")
    
    # Save query vector
    np.save(output_file, query_vector)
    console.print(f"✅ Created query vector using {method} of {len(class_embeddings)} embeddings")
    console.print(f"💾 Saved to: {output_file}")
    console.print(f"📐 Vector shape: {query_vector.shape}")


def extract_geotiff_tiles(
    geotiff_path: Path,
    tile_size: int = 256,
    overlap: int = 0
) -> List[Tuple[np.ndarray, Dict[str, Any]]]:
    """Extract tiles from a GeoTIFF file with metadata."""
    tiles = []
    
    with rasterio.open(geotiff_path) as src:
        # Get image dimensions
        height, width = src.height, src.width
        
        console.print(f"📐 GeoTIFF dimensions: {width}x{height}")
        console.print(f"🔢 Bands: {src.count}")
        console.print(f"🗺️ CRS: {src.crs}")
        
        # Calculate number of tiles
        tiles_x = (width + tile_size - 1) // tile_size
        tiles_y = (height + tile_size - 1) // tile_size
        total_tiles = tiles_x * tiles_y
        
        console.print(f"📋 Will extract {total_tiles} tiles ({tiles_x}x{tiles_y})")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Extracting tiles...", total=total_tiles)
            
            row = 0
            for y in range(0, height, tile_size - overlap):
                col = 0
                for x in range(0, width, tile_size - overlap):
                    # Calculate actual tile dimensions
                    tile_width = min(tile_size, width - x)
                    tile_height = min(tile_size, height - y)
                    
                    # Skip very small tiles or tiles that are not full size
                    if tile_width < tile_size or tile_height < tile_size:
                        col += 1
                        progress.advance(task)
                        continue
                    
                    # Create window for this tile
                    window = Window(x, y, tile_width, tile_height)
                    
                    # Read the tile data
                    tile_data = src.read(window=window)
                    
                    mask = src.read_masks(1, window=window)

                    # Skip tile if any masked (any values are 0)
                    if np.any(mask == 0):
                        col += 1
                        progress.advance(task)
                        continue
                    
                    # Convert to RGB (take first 3 bands and transpose to (H, W, C))
                    rgb_tile = tile_data[:3].transpose(1, 2, 0)

                    
                    # Normalize to 0-255 if needed
                    if rgb_tile.dtype != np.uint8:
                        # Assume data is in 0-1 range or needs scaling
                        if rgb_tile.max() <= 1.0:
                            rgb_tile = (rgb_tile * 255).astype(np.uint8)
                        else:
                            # Scale to 0-255 range
                            rgb_tile = ((rgb_tile - rgb_tile.min()) / 
                                      (rgb_tile.max() - rgb_tile.min()) * 255).astype(np.uint8)
                    
                    # Final check: ensure we have valid RGB values
                    if rgb_tile.shape[2] != 3 or rgb_tile.shape[0] != tile_size or rgb_tile.shape[1] != tile_size:
                        #console.print(f"⚠️ Skipping tile at ({x}, {y}): incorrect dimensions {rgb_tile.shape}")
                        col += 1
                        progress.advance(task)
                        continue
                    
                    # Get geographic coordinates for this tile
                    tile_transform = src.window_transform(window)
                    
                    # Metadata for this tile
                    metadata = {
                        "tile_x": x,
                        "tile_y": y,
                        "tile_width": tile_width,
                        "tile_height": tile_height,
                        "row": row,
                        "col": col,
                        "window": window,
                        "transform": tile_transform,
                        "crs": src.crs,
                        "source_file": str(geotiff_path)
                    }
                    
                    tiles.append((rgb_tile, metadata))
                    col += 1
                    progress.advance(task)
                row += 1
    
    return tiles


def process_tiles_in_batches(
    tiles: List[Tuple[np.ndarray, Dict[str, Any]]],
    model: torch.nn.Module,
    preprocess,
    device: str,
    batch_size: int = 32
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """Process tiles in batches to get CLIP embeddings."""
    tile_embeddings = []
    tile_metadata = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        total_batches = (len(tiles) + batch_size - 1) // batch_size
        task = progress.add_task("Processing tile batches...", total=total_batches)
        
        for i in range(0, len(tiles), batch_size):
            batch_tiles = tiles[i:i + batch_size]
            
            # Preprocess batch
            batch_tensors = []
            for tile_data, metadata in batch_tiles:
                try:
                    # Convert numpy array to PIL Image
                    pil_image = Image.fromarray(tile_data)
                    tensor = preprocess(pil_image)
                    batch_tensors.append(tensor)
                    tile_metadata.append(metadata)
                except Exception as e:
                    console.print(f"⚠️ Error preprocessing tile: {e}")
                    # Use dummy tensor for failed tiles
                    batch_tensors.append(torch.zeros(3, 224, 224))
                    tile_metadata.append(metadata)
            
            # Stack and process batch
            if batch_tensors:
                batch_tensor = torch.stack(batch_tensors).to(device)
                
                with torch.no_grad():
                    batch_features = model.encode_image(batch_tensor)
                    batch_features /= batch_features.norm(dim=-1, keepdim=True)
                    tile_embeddings.append(batch_features.cpu().numpy())
            
            progress.advance(task)
    
    # Combine all embeddings
    tile_embeddings = np.vstack(tile_embeddings) if tile_embeddings else np.array([])
    
    return tile_embeddings, tile_metadata


def create_shapefile_from_results(
    results: List[Dict[str, Any]], 
    tile_metadata: List[Dict[str, Any]], 
    output_shapefile: Path,
    crs: str = None,
    use_grid: bool = False,
    color_map: Optional[Dict[str, str]] = None
) -> None:
    """Create a shapefile from tile results for QGIS visualization with automatic styling.
    
    Args:
        results: List of classification results
        tile_metadata: List of tile metadata
        output_shapefile: Path for output shapefile
        crs: Coordinate reference system
        use_grid: If True, create a regular grid instead of individual tile polygons (much faster)
    """
    try:
        import geopandas as gpd
        from shapely.geometry import Polygon
        import random
    except ImportError:
        console.print("⚠️ geopandas and shapely not available. Install with: pip install geopandas shapely")
        return
    


    if use_grid:
        console.print("🗺️ Creating fast grid-based shapefile for QGIS...")
        _create_grid_shapefile(results, tile_metadata, output_shapefile, crs, color_map)
    else:
        console.print("🗺️ Creating detailed shapefile for QGIS with color styling...")
        _create_detailed_shapefile(results, tile_metadata, output_shapefile, crs, color_map)


def _create_grid_shapefile(
    results: List[Dict[str, Any]], 
    tile_metadata: List[Dict[str, Any]], 
    output_shapefile: Path,
    crs: str = None,
    color_map: Optional[Dict[str, str]] = None
) -> None:
    """Create a fast grid-based shapefile using regular grid cells.
    
    This approach is particularly optimized for UTM-projected data where:
    - Square pixels ensure perfect grid alignment
    - Linear coordinate transformation provides predictable results
    - No projection distortion within UTM zone
    """
    import geopandas as gpd
    from shapely.geometry import Polygon
    
    # Get unique classes and sort alphabetically for consistent color assignment
    unique_classes = sorted(list(set(result['best_class'] for result in results)))
    console.print(f"🎨 Found {len(unique_classes)} unique classes (alphabetically sorted): {unique_classes}")
    
    # Generate colors
    if color_map:
        # Use color_map from CSV, fallback to generated if not found
        def hex_to_rgb(hexstr):
            hexstr = hexstr.lstrip('#')
            return tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))
        class_to_color = {}
        for c in unique_classes:
            hexval = color_map.get(c.lower().replace(';;',';').replace(' ','-').split(';')[0], None)
            if hexval:
                class_to_color[c] = hex_to_rgb(hexval)
            else:
                # fallback to generated color
                class_to_color[c] = (128,128,128)
    else:
        class_to_color = _generate_class_colors(unique_classes)
    
    # Determine grid bounds from tile metadata
    if not tile_metadata:
        console.print("❌ No tile metadata available for grid creation")
        return
        

    # Use the actual tile width/height from metadata for grid cell size
    # (Assume all tiles are the same size; if not, use the minimum)
    grid_cell_width = min(meta['tile_width'] for meta in tile_metadata)
    grid_cell_height = min(meta['tile_height'] for meta in tile_metadata)

    # Find all unique tile positions
    tile_positions = [(meta['tile_x'], meta['tile_y']) for meta in tile_metadata]
    x_positions = sorted(set(pos[0] for pos in tile_positions))
    y_positions = sorted(set(pos[1] for pos in tile_positions))

    # Find overall bounds
    min_x = min(x_positions)
    max_x = max(x_positions) + grid_cell_width
    min_y = min(y_positions)
    max_y = max(y_positions) + grid_cell_height

    console.print(f"📐 Grid bounds: x({min_x}-{max_x}), y({min_y}-{max_y})")
    console.print(f"📦 Grid cell size: {grid_cell_width}x{grid_cell_height} pixels (from metadata)")
    console.print(f"🎯 Grid dimensions: {len(x_positions)} cols x {len(y_positions)} rows")
    
    # Create a lookup dictionary for quick result access
    result_lookup = {}
    for result in results:
        tile_id = result['tile_id']
        if tile_id < len(tile_metadata):
            meta = tile_metadata[tile_id]
            # Use tile position as key
            key = (meta['tile_x'], meta['tile_y'])
            result_lookup[key] = result
    
    # Get all unique tile positions to create a proper continuous grid
    tile_positions = set()
    for meta in tile_metadata:
        tile_positions.add((meta['tile_x'], meta['tile_y']))
    
    # Sort positions to ensure consistent grid creation
    sorted_x_positions = sorted(set(pos[0] for pos in tile_positions))
    sorted_y_positions = sorted(set(pos[1] for pos in tile_positions))
    
    console.print(f"📐 Grid coverage: {len(sorted_x_positions)} cols x {len(sorted_y_positions)} rows")
    
    # Create grid polygons and attributes
    geometries = []
    attributes = []
    
    # Generate continuous grid cells based on actual tile positions
    for y_pos in sorted_y_positions:
        for x_pos in sorted_x_positions:
            # Check if we have a result for this grid cell
            cell_key = (x_pos, y_pos)
            if cell_key in result_lookup:
                result = result_lookup[cell_key]
                
                # Get the correct transform for this specific tile
                tile_id = result['tile_id']
                tile_meta = tile_metadata[tile_id]
                tile_transform = tile_meta["transform"]
                window = tile_meta["window"]
                local_x = x_pos - window.col_off
                local_y = y_pos - window.row_off

                x1, y1 = tile_transform * (local_x, local_y)
                x2, y2 = tile_transform * (local_x + grid_cell_width, local_y)
                x3, y3 = tile_transform * (local_x + grid_cell_width, local_y + grid_cell_height)
                x4, y4 = tile_transform * (local_x, local_y + grid_cell_height)
                
                # Create polygon geometry
                polygon = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
                geometries.append(polygon)
                
                # Get color for this class (first match in color_map if available)
                class_name = result['best_class']
                rgb_color = class_to_color.get(class_name.replace(';;',';').split(';')[0], (128,128,128))
                
                # Collect attributes including color information
                attributes.append({
                    'tile_id': result['tile_id'],
                    'best_class': result['best_class'],
                    'similarity': round(result['query_similarity'], 4),
                    'tile_x': x_pos,
                    'tile_y': y_pos,
                    'tile_width': grid_cell_width,
                    'tile_height': grid_cell_height,
                    'source_file': tile_metadata[result['tile_id']]['source_file'],
                    'red': rgb_color[0],
                    'green': rgb_color[1],
                    'blue': rgb_color[2],
                    'color_hex': f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
                })
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
    
    # Set CRS
    if crs:
        gdf.crs = crs
    elif tile_metadata and 'crs' in tile_metadata[0]:
        gdf.crs = tile_metadata[0]['crs']
    
    # Save shapefile
    gdf.to_file(output_shapefile, driver='ESRI Shapefile')
    
    # Create QGIS style file (QML) for automatic styling
    create_qgis_style_file(output_shapefile, unique_classes, class_to_color)
    
    console.print(f"✅ Saved grid-based shapefile to {output_shapefile}")
    console.print(f"📊 Shapefile contains {len(geometries)} grid cells")
    console.print(f"🎯 CRS: {gdf.crs}")
    console.print(f"🎨 Created with {len(unique_classes)} color-coded classes")
    console.print(f"⚡ Grid-based processing: {len(geometries)} cells vs {len(results)} individual tiles")
    
    # Print class summary
    _print_class_summary(results, class_to_color)


def _create_detailed_shapefile(
    results: List[Dict[str, Any]], 
    tile_metadata: List[Dict[str, Any]], 
    output_shapefile: Path,
    crs: str = None,
    color_map: Optional[Dict[str, str]] = None
) -> None:
    """Create detailed shapefile with individual tile polygons (original method)."""
    import geopandas as gpd
    from shapely.geometry import Polygon
    
    # Create geometries and attributes for all tiles
    geometries = []
    attributes = []
    
    # Get unique classes and sort alphabetically for consistent color assignment
    unique_classes = sorted(list(set(result['best_class'] for result in results)))
    console.print(f"🎨 Found {len(unique_classes)} unique classes (alphabetically sorted): {unique_classes}")
    
    # Generate colors
    if color_map:
        def hex_to_rgb(hexstr):
            hexstr = hexstr.lstrip('#')
            return tuple(int(hexstr[i:i+2], 16) for i in (0, 2, 4))
        class_to_color = {}
        for c in unique_classes:
            hexval = color_map.get(c.strip(), None)
            if hexval:
                class_to_color[c] = hex_to_rgb(hexval)
            else:
                class_to_color[c] = (128,128,128)
    else:
        class_to_color = _generate_class_colors(unique_classes)
    
    for result in results:
        tile_id = result['tile_id']
        if tile_id < len(tile_metadata):
            metadata = tile_metadata[tile_id]
            
            # Get tile bounds in pixel coordinates
            x_min = metadata['tile_x']
            y_min = metadata['tile_y']
            x_max = x_min + metadata['tile_width']
            y_max = y_min + metadata['tile_height']
            
            # Convert pixel coordinates to geographic coordinates using the transform
            transform = metadata['transform']
            
            # Get corner coordinates using proper row/col order for xy() function
            # Note: rasterio xy() expects (row, col) not (y, x)
            x1, y1 = transform * (x_min, y_min)  # Top-left using direct transform
            x2, y2 = transform * (x_max, y_min)  # Top-right
            x3, y3 = transform * (x_max, y_max)  # Bottom-right
            x4, y4 = transform * (x_min, y_max)  # Bottom-left
            
            # Create polygon geometry
            polygon = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
            geometries.append(polygon)
            
            # Get color for this class (first match in color_map if available)
            class_name = result['best_class']
            rgb_color = class_to_color.get(class_name, (128,128,128))
            
            # Collect attributes including color information
            attributes.append({
                'tile_id': tile_id,
                'best_class': result['best_class'],
                'similarity': round(result['query_similarity'], 4),
                'tile_x': x_min,
                'tile_y': y_min,
                'tile_width': metadata['tile_width'],
                'tile_height': metadata['tile_height'],
                'source_file': metadata['source_file'],
                'red': rgb_color[0],
                'green': rgb_color[1],
                'blue': rgb_color[2],
                'color_hex': f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
            })
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
    
    # Set CRS
    if crs:
        gdf.crs = crs
    elif tile_metadata and 'crs' in tile_metadata[0]:
        gdf.crs = tile_metadata[0]['crs']
    
    # Save shapefile
    gdf.to_file(output_shapefile, driver='ESRI Shapefile')
    
    # Create QGIS style file (QML) for automatic styling
    create_qgis_style_file(output_shapefile, unique_classes, class_to_color)
    
    console.print(f"✅ Saved detailed shapefile to {output_shapefile}")
    console.print(f"📊 Shapefile contains {len(geometries)} tile polygons")
    console.print(f"🎯 CRS: {gdf.crs}")
    console.print(f"🎨 Created with {len(unique_classes)} color-coded classes")
    
    # Print class summary
    _print_class_summary(results, class_to_color)


def _generate_class_colors(unique_classes: List[str]) -> Dict[str, Tuple[int, int, int]]:
    """Generate color palette for classes."""
    def generate_color_palette(n_colors):
        """Generate visually distinct colors for classes."""
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            # Use HSV with fixed saturation and value for consistent colors
            import colorsys
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            # Convert to 0-255 range
            rgb = tuple(int(c * 255) for c in rgb)
            colors.append(rgb)
        return colors
    
    try:
        import colorsys
        class_colors = generate_color_palette(len(unique_classes))
    except:
        # Fallback to predefined colors if colorsys not available
        predefined_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (255, 192, 203), # Pink
            (165, 42, 42),  # Brown
        ]
        class_colors = (predefined_colors * ((len(unique_classes) // len(predefined_colors)) + 1))[:len(unique_classes)]
    
    # Map sorted classes to colors
    return dict(zip(unique_classes, class_colors))


def _print_class_summary(results: List[Dict[str, Any]], class_to_color: Dict[str, Tuple[int, int, int]]) -> None:
    """Print class distribution summary."""
    class_counts = {}
    for result in results:
        class_name = result['best_class']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    console.print("📋 Class distribution:")
    for class_name, count in sorted(class_counts.items()):
        color = class_to_color[class_name]
        console.print(f"   {class_name}: {count} tiles (RGB: {color})")


def create_geojson_from_results(
    results: List[Dict[str, Any]], 
    tile_metadata: List[Dict[str, Any]], 
    output_geojson: Path,
    crs: str = None
) -> None:
    """Create a GeoJSON file from tile results with color information for web mapping."""
    try:
        import geopandas as gpd
        from shapely.geometry import Polygon
        import colorsys
    except ImportError:
        console.print("⚠️ geopandas and shapely not available. Install with: pip install geopandas shapely")
        return
    
    console.print("🌐 Creating GeoJSON for web mapping with color styling...")
    
    # Get unique classes and sort alphabetically for consistent color assignment
    unique_classes = sorted(list(set(result['best_class'] for result in results)))
    
    def generate_color_palette(n_colors):
        """Generate visually distinct colors for classes."""
        colors = []
        for i in range(n_colors):
            hue = i / n_colors
            rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
            rgb = tuple(int(c * 255) for c in rgb)
            colors.append(rgb)
        return colors
    
    try:
        class_colors = generate_color_palette(len(unique_classes))
    except:
        # Fallback colors
        predefined_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
            (0, 255, 255), (255, 165, 0), (128, 0, 128), (255, 192, 203), (165, 42, 42)
        ]
        class_colors = (predefined_colors * ((len(unique_classes) // len(predefined_colors)) + 1))[:len(unique_classes)]
    
    # Map sorted classes to colors
    class_to_color = dict(zip(unique_classes, class_colors))
    
    # Create geometries and attributes for all tiles
    geometries = []
    attributes = []
    
    for result in results:
        tile_id = result['tile_id']
        if tile_id < len(tile_metadata):
            metadata = tile_metadata[tile_id]
            
            # Get tile bounds in pixel coordinates
            x_min = metadata['tile_x']
            y_min = metadata['tile_y']
            x_max = x_min + metadata['tile_width']
            y_max = y_min + metadata['tile_height']
            
            # Convert pixel coordinates to geographic coordinates
            transform = metadata['transform']
            
            # Get corner coordinates using proper row/col order for xy() function  
            # Note: rasterio xy() expects (row, col) not (y, x)
            x1, y1 = transform * (x_min, y_min)  # Top-left using direct transform
            x2, y2 = transform * (x_max, y_min)  # Top-right
            x3, y3 = transform * (x_max, y_max)  # Bottom-right
            x4, y4 = transform * (x_min, y_max)  # Bottom-left
            
            # Create polygon geometry
            polygon = Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
            geometries.append(polygon)
            
            # Get color for this class
            class_name = result['best_class']
            rgb_color = class_to_color[class_name]
            
            # Collect attributes including color information
            attributes.append({
                'tile_id': tile_id,
                'best_class': result['best_class'],
                'similarity': round(result['query_similarity'], 4),
                'tile_x': x_min,
                'tile_y': y_min,
                'tile_width': metadata['tile_width'],
                'tile_height': metadata['tile_height'],
                'source_file': metadata['source_file'],
                'red': rgb_color[0],
                'green': rgb_color[1],
                'blue': rgb_color[2],
                'color_hex': f"#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}"
            })
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
    
    # Set CRS
    if crs:
        gdf.crs = crs
    elif tile_metadata and 'crs' in tile_metadata[0]:
        gdf.crs = tile_metadata[0]['crs']
    
    # Convert to WGS84 for web compatibility
    if gdf.crs and gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')
    
    # Save GeoJSON
    gdf.to_file(output_geojson, driver='GeoJSON')
    
    console.print(f"✅ Saved GeoJSON to {output_geojson}")
    console.print(f"📊 GeoJSON contains {len(geometries)} tile polygons")
    console.print(f"🌐 CRS: {gdf.crs} (WGS84 for web compatibility)")
    console.print(f"🎨 Created with {len(unique_classes)} color-coded classes")

def load_color_map(color_csv: Path) -> Dict[str, str]:
    if color_csv is not None and Path(color_csv).exists():
        import csv
        color_map = {}
        with open(color_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Use stripped habitat_name for robust matching
                color_map[row['habitat_name'].strip().lower()] = row['cat_color'].strip()
        console.print(f"🎨 Loaded color map from {color_csv} with {len(color_map)} entries")
        return color_map

def run_process(
    geotiff_path: Path,
    query_vector_path: Path,
    embeddings_file: Path,
    output_file: Path = Path("similarity_results.csv"),
    tile_size: int = 512,
    overlap: int = 0,
    batch_size: int = 32,
    top_k: int = 5,
    create_shapefile: bool = False,
    create_geojson: bool = False,
    use_grid: bool = False,
    color_csv: Path = None
) -> None:
    """
    Process a GeoTIFF by breaking it into tiles and finding closest CLIP vectors using cosine similarity.
    
    Args:
        geotiff_path: Path to the GeoTIFF file
        query_vector_path: Path to query vector file or directory of query vectors
        embeddings_file: Path to the embeddings pickle file
        output_file: Path for the output CSV file
        tile_size: Size of tiles to extract
        overlap: Overlap between tiles
        batch_size: Batch size for processing
        top_k: Number of top results to return (unused for complete coverage)
        create_shapefile: Whether to create a shapefile for QGIS
        create_geojson: Whether to create a GeoJSON file
        use_grid: Whether to use fast grid-based shapefile (instead of individual polygons)
    """



    console.print(f"🌍 Processing GeoTIFF: {geotiff_path}")
    console.print(f"� Query vector: {query_vector_path}")
    console.print(f"� Color Map: {color_csv}")
    color_map = load_color_map(color_csv)
    console.print(f"📁 Embeddings: {embeddings_file}")
    # Validate inputs
    if not geotiff_path.exists():
        console.print(f"❌ GeoTIFF file not found: {geotiff_path}")
        raise ValueError(f"GeoTIFF file not found: {geotiff_path}")
    
    if not query_vector_path.exists():
        console.print(f"❌ Query vector file not found: {query_vector_path}")
        raise ValueError(f"Query vector file not found: {query_vector_path}")
    
    if not embeddings_file.exists():
        console.print(f"❌ Embeddings file not found: {embeddings_file}")
        raise ValueError(f"Embeddings file not found: {embeddings_file}")
    
    # Load query vectors - handle both single file and directory
    console.print("🔍 Loading query vector(s)...")
    query_vectors = {}
    
    if query_vector_path.is_file():
        # Single query vector file
        try:
            query_vector = np.load(query_vector_path)
            class_name = query_vector_path.stem.replace('query_', '').replace('_', ';')
            query_vectors[class_name] = query_vector
            console.print(f"✅ Loaded single query vector: {class_name} (shape: {query_vector.shape})")
        except Exception as e:
            console.print(f"❌ Error loading query vector: {e}")
            raise ValueError(f"Error loading query vector: {e}")
    
    elif query_vector_path.is_dir():
        # Directory of query vectors - load all .npy files
        npy_files = list(query_vector_path.glob("query_*.npy"))
        if not npy_files:
            console.print(f"❌ No query vector files found in {query_vector_path}")
            raise ValueError(f"No query vector files found in {query_vector_path}")
        
        console.print(f"📂 Found {len(npy_files)} query vector files")
        for npy_file in sorted(npy_files):
            try:
                query_vector = np.load(npy_file)
                # Convert filename back to class name (query_vehicle_car_sedan.npy -> vehicle;car;sedan)
                class_name = npy_file.stem.replace('query_', '').replace('_', ';')
                query_vectors[class_name] = query_vector
                console.print(f"   ✅ {class_name} (shape: {query_vector.shape})")
            except Exception as e:
                console.print(f"   ⚠️ Error loading {npy_file}: {e}")
        
        if not query_vectors:
            console.print(f"❌ No valid query vectors loaded")
            raise ValueError(f"No valid query vectors loaded")
    
    else:
        console.print(f"❌ Query vector path must be a file or directory: {query_vector_path}")
        raise ValueError(f"Query vector path must be a file or directory: {query_vector_path}")
    
    # Load reference embeddings and metadata from pickle (original format)
    console.print("📂 Loading reference embeddings from pickle...")
    try:
        df_embeddings = pd.read_pickle(embeddings_file)
        reference_embeddings = np.stack(df_embeddings['image_embedding'].values)
        reference_labels = df_embeddings['class_name'].tolist()
        console.print(f"✅ Loaded {len(reference_embeddings)} reference embeddings")
    except Exception as e:
        console.print(f"❌ Error loading embeddings: {e}")
        raise ValueError(f"Error loading embeddings: {e}")
    
    # Setup CLIP model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    console.print(f"📱 Using device: {device}")
    
    model_name = "ViT-B/32"  # Default CLIP model
    console.print(f"🤖 Loading CLIP model: {model_name}")
    model, preprocess = clip.load(model_name, device=device)
    
    # Extract tiles from GeoTIFF
    tiles = extract_geotiff_tiles(geotiff_path, tile_size, overlap)
    
    if not tiles:
        console.print("❌ No tiles extracted!")
        raise ValueError("No tiles extracted!")
    
    console.print(f"📦 Extracted {len(tiles)} tiles")
    
    # Process tiles in batches to get CLIP embeddings
    console.print("🔄 Computing CLIP embeddings for tiles...")
    tile_embeddings, tile_metadata = process_tiles_in_batches(
        tiles, model, preprocess, device, batch_size
    )
    
    console.print(f"✅ Computed embeddings for {len(tile_embeddings)} tiles")
    
    # Find best matching class for each tile across all query vectors
    console.print("🔍 Finding best matching class for each tile...")
    
    # Convert to PyTorch tensors for efficient GPU computation
    query_class_names = list(query_vectors.keys())
    
    # Stack query vectors into a prototype matrix and move to device
    proto_matrix = torch.stack([
        torch.from_numpy(query_vectors[class_name]).to(device) 
        for class_name in query_class_names
    ])
    
    # Normalize prototype matrix
    proto_matrix = proto_matrix / proto_matrix.norm(dim=-1, keepdim=True)
    proto_matrix = proto_matrix.to(dtype=torch.float32)
    
    console.print(f"🎯 Comparing {len(tile_embeddings)} tiles against {len(query_class_names)} query vectors")
    
    # Convert tile embeddings to PyTorch tensor and move to device
    tile_feats = torch.from_numpy(tile_embeddings).to(device)
    
    with torch.no_grad():
        # Normalize tile features
        tile_feats = tile_feats / tile_feats.norm(dim=-1, keepdim=True)
        tile_feats = tile_feats.to(dtype=torch.float32)
        
        # Compute similarities: (N_tiles, N_classes)
        sims = tile_feats @ proto_matrix.T
        
        # Find best matching class for each tile
        best_indices = sims.argmax(dim=1)
        best_similarities = sims.max(dim=1).values
    
    # Convert back to CPU for further processing
    best_indices = best_indices.cpu().numpy()
    best_similarities = best_similarities.cpu().numpy()
    
    # Process ALL tiles instead of just top-k
    console.print("🔍 Preparing results for ALL tiles...")
    results = []
    
    for tile_idx in range(len(tile_embeddings)):
        best_query_idx = best_indices[tile_idx]
        best_class_name = query_class_names[best_query_idx]
        tile_similarity = best_similarities[tile_idx]
        tile_meta = tile_metadata[tile_idx]
        
        # Create a simplified result entry for each tile
        result_entry = {
            "tile_id": tile_idx,
            "source_file": tile_meta["source_file"],
            "tile_x": tile_meta["tile_x"],
            "tile_y": tile_meta["tile_y"],
            "tile_width": tile_meta["tile_width"],
            "tile_height": tile_meta["tile_height"],
            "row": tile_meta["row"],
            "col": tile_meta["col"],
            "best_class": best_class_name,
            "query_similarity": float(tile_similarity),
        }
        results.append(result_entry)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    console.print(f"✅ Saved results to {output_file}")
    console.print(f"📊 Processed ALL {len(tile_embeddings)} tiles")
    console.print(f"🎯 Total classification results: {len(results)}")
    console.print(f"🔍 Used {len(query_class_names)} query vectors for classification")
    
    # Create spatial outputs for QGIS (using all tiles)
    if create_shapefile:
        shapefile_path = output_file.with_suffix('.shp')
        create_shapefile_from_results(results, tile_metadata, shapefile_path, use_grid=use_grid,color_map=color_map)

    if create_geojson:
        geojson_path = output_file.with_suffix('.geojson')
        create_geojson_from_results(results, tile_metadata, geojson_path)
