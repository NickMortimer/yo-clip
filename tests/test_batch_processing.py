"""Tests for the batch processing functionality."""

import tempfile
import pytest
from pathlib import Path
from PIL import Image
from yoclip.yolotoclip import collect_crops_and_metadata
import numpy as np


def create_test_yolo_dataset(temp_dir: Path, num_images: int = 3, num_objects_per_image: int = 2):
    """Create a test YOLO dataset structure."""
    images_dir = temp_dir / "images"
    labels_dir = temp_dir / "labels"
    images_dir.mkdir()
    labels_dir.mkdir()
    
    # Create classes.txt
    classes = ["person", "car", "dog"]
    (temp_dir / "classes.txt").write_text("\n".join(classes))
    
    for i in range(num_images):
        # Create a test image
        img = Image.new('RGB', (640, 480), color=(i*50, 100, 150))
        img_path = images_dir / f"image_{i:03d}.jpg"
        img.save(img_path)
        
        # Create corresponding label file
        label_path = labels_dir / f"image_{i:03d}.txt"
        labels = []
        for j in range(num_objects_per_image):
            # Generate random normalized bbox coordinates
            class_id = j % len(classes)
            x_center = 0.3 + (j * 0.2)
            y_center = 0.4 + (j * 0.15)
            width = 0.1 + (j * 0.05)
            height = 0.1 + (j * 0.05)
            labels.append(f"{class_id} {x_center} {y_center} {width} {height}")
        
        label_path.write_text("\n".join(labels))
    
    return temp_dir, classes


def test_collect_crops_and_metadata():
    """Test that crops and metadata are collected correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dataset_dir, classes = create_test_yolo_dataset(temp_path)
        
        images_dir = dataset_dir / "images"
        labels_dir = dataset_dir / "labels"
        
        crops, metadata = collect_crops_and_metadata(labels_dir, images_dir, classes)
        
        # Should have 3 images * 2 objects per image = 6 crops
        assert len(crops) == 6
        assert len(metadata) == 6
        
        # Check that all crops are PIL Images
        for crop in crops:
            assert isinstance(crop, Image.Image)
        
        # Check metadata structure
        for meta in metadata:
            assert "image" in meta
            assert "object_id" in meta
            assert "class_id" in meta
            assert "class_name" in meta
            assert "bbox" in meta
            assert meta["class_name"] in classes


def test_invalid_class_id_handling():
    """Test that invalid class IDs are handled gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        images_dir = temp_path / "images"
        labels_dir = temp_path / "labels"
        images_dir.mkdir()
        labels_dir.mkdir()
        
        classes = ["person", "car"]  # Only 2 classes
        (temp_path / "classes.txt").write_text("\n".join(classes))
        
        # Create image
        img = Image.new('RGB', (640, 480), color=(100, 100, 100))
        img_path = images_dir / "test.jpg"
        img.save(img_path)
        
        # Create label with invalid class_id (2, but we only have classes 0,1)
        label_path = labels_dir / "test.txt"
        label_path.write_text("2 0.5 0.5 0.1 0.1")  # Invalid class_id
        
        crops, metadata = collect_crops_and_metadata(labels_dir, images_dir, classes)
        
        # Should skip the invalid class_id and return empty lists
        assert len(crops) == 0
        assert len(metadata) == 0


if __name__ == "__main__":
    test_collect_crops_and_metadata()
    test_invalid_class_id_handling()
    print("✅ All tests passed!")
