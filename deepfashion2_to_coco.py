#!/usr/bin/env python3
"""
DeepFashion2 to COCO format converter

This script converts DeepFashion2 annotations to COCO format for use with
AWS Rekognition Custom Labels training.

Based on the TrackIt Fashion Catalog AWS Rekognition Demo implementation.
"""

import os
import json
import argparse
from collections import defaultdict
from datetime import datetime


def convert_deepfashion2_to_coco(data_dir, output_file):
    """
    Convert DeepFashion2 annotations to COCO format.
    
    Args:
        data_dir: Path to DeepFashion2 dataset directory
        output_file: Path for output COCO JSON file
    """
    
    # DeepFashion2 category mapping
    category_mapping = {
        1: "short_sleeved_shirt",
        2: "long_sleeved_shirt", 
        3: "short_sleeved_outwear",
        4: "long_sleeved_outwear",
        5: "vest",
        6: "sling",
        7: "shorts",
        8: "trousers",
        9: "skirt",
        10: "short_sleeved_dress",
        11: "long_sleeved_dress",
        12: "vest_dress",
        13: "sling_dress"
    }
    
    # Consolidate similar categories as per TrackIt implementation
    consolidated_mapping = {
        1: "short_sleeved_shirt",
        2: "long_sleeved_shirt",
        3: "short_sleeved_outwear", 
        4: "long_sleeved_outwear",
        5: "vest",
        6: "vest",  # sling -> vest
        7: "shorts",
        8: "trousers",
        9: "skirt",
        10: "short_sleeved_dress",
        11: "long_sleeved_dress", 
        12: "vest_dress",
        13: "vest_dress"  # sling_dress -> vest_dress
    }
    
    # Initialize COCO structure
    coco_data = {
        "info": {
            "description": "DeepFashion2 dataset converted to COCO format",
            "version": "1.0",
            "year": datetime.now().year,
            "contributor": "TrackIt Fashion Catalog Demo",
            "date_created": datetime.now().isoformat()
        },
        "licenses": [
            {
                "id": 1,
                "name": "Unknown",
                "url": ""
            }
        ],
        "categories": [],
        "images": [],
        "annotations": []
    }
    
    # Create categories
    unique_categories = set(consolidated_mapping.values())
    for idx, cat_name in enumerate(sorted(unique_categories), 1):
        coco_data["categories"].append({
            "id": idx,
            "name": cat_name,
            "supercategory": "clothing"
        })
    
    # Create category name to ID mapping
    cat_name_to_id = {cat["name"]: cat["id"] for cat in coco_data["categories"]}
    
    # Process images and annotations
    image_dir = os.path.join(data_dir, "image")
    anno_dir = os.path.join(data_dir, "annos")
    
    if not os.path.exists(image_dir) or not os.path.exists(anno_dir):
        raise ValueError(f"Image or annotation directory not found in {data_dir}")
    
    image_id = 1
    annotation_id = 1
    
    # Get all annotation files
    anno_files = [f for f in os.listdir(anno_dir) if f.endswith('.json')]
    
    print(f"Processing {len(anno_files)} annotation files...")
    
    for anno_file in sorted(anno_files):
        image_name = anno_file.replace('.json', '.jpg')
        image_path = os.path.join(image_dir, image_name)
        
        # Skip if image doesn't exist
        if not os.path.exists(image_path):
            print(f"Warning: Image {image_name} not found, skipping...")
            continue
            
        # Load annotation
        with open(os.path.join(anno_dir, anno_file), 'r') as f:
            anno_data = json.load(f)
        
        # Get image dimensions (you might need to use PIL for this)
        # For now, using default values - you should implement proper image dimension reading
        width, height = 512, 512  # Default values - should be replaced with actual image dimensions
        
        # Add image info
        image_info = {
            "id": image_id,
            "file_name": image_name,
            "width": width,
            "height": height,
            "license": 1
        }
        coco_data["images"].append(image_info)
        
        # Process each item in the annotation
        for item_key in anno_data:
            if item_key in ['source', 'pair_id']:
                continue
                
            item_data = anno_data[item_key]
            
            # Get category info
            category_id = item_data.get('category_id')
            if category_id not in consolidated_mapping:
                continue
                
            category_name = consolidated_mapping[category_id]
            coco_category_id = cat_name_to_id[category_name]
            
            # Get bounding box
            bbox = item_data.get('bounding_box', [])
            if len(bbox) != 4:
                continue
                
            x1, y1, x2, y2 = bbox
            width_bbox = x2 - x1
            height_bbox = y2 - y1
            area = width_bbox * height_bbox
            
            # Create annotation
            annotation = {
                "id": annotation_id,
                "image_id": image_id,
                "category_id": coco_category_id,
                "bbox": [x1, y1, width_bbox, height_bbox],  # COCO format: [x, y, width, height]
                "area": area,
                "iscrowd": 0
            }
            
            # Add segmentation if available
            segmentation = item_data.get('segmentation', [])
            if segmentation:
                annotation["segmentation"] = segmentation
            else:
                # Create simple segmentation from bbox
                annotation["segmentation"] = [[x1, y1, x2, y1, x2, y2, x1, y2]]
            
            coco_data["annotations"].append(annotation)
            annotation_id += 1
        
        image_id += 1
        
        if image_id % 1000 == 0:
            print(f"Processed {image_id-1} images...")
    
    # Save COCO file
    with open(output_file, 'w') as f:
        json.dump(coco_data, f, indent=2)
    
    print(f"Conversion complete! COCO file saved to: {output_file}")
    print(f"Total images: {len(coco_data['images'])}")
    print(f"Total annotations: {len(coco_data['annotations'])}")
    print(f"Categories: {[cat['name'] for cat in coco_data['categories']]}")


def main():
    parser = argparse.ArgumentParser(description='Convert DeepFashion2 to COCO format')
    parser.add_argument('--data_dir', type=str, required=True,
                        help='Path to DeepFashion2 dataset directory')
    parser.add_argument('--output', type=str, default='deepfashion2_coco.json',
                        help='Output COCO JSON file path')
    
    args = parser.parse_args()
    
    convert_deepfashion2_to_coco(args.data_dir, args.output)


if __name__ == "__main__":
    main()