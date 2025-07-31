#!/usr/bin/env python3
"""
COCO to AWS Rekognition Manifest converter

This script converts COCO format annotations to AWS Rekognition Custom Labels 
manifest file format and uploads to S3.

Based on the TrackIt Fashion Catalog AWS Rekognition Demo implementation.
"""

import json
import os
import boto3
import argparse
from datetime import datetime
from urllib.parse import urljoin


# Configuration - Update these values
S3_BUCKET_NAME = "your-rekognition-bucket"  # Update this with your S3 bucket name
S3_REGION = "us-west-2"  # Update with your preferred region
LOCAL_PATH = "./data/"  # Path to your local dataset


def create_manifest_from_coco(coco_file, s3_bucket, s3_prefix="images/", split_ratio=0.8):
    """
    Convert COCO annotations to AWS Rekognition manifest format.
    
    Args:
        coco_file: Path to COCO JSON file
        s3_bucket: S3 bucket name
        s3_prefix: S3 prefix for images
        split_ratio: Train/test split ratio
    
    Returns:
        tuple: (train_manifest, test_manifest)
    """
    
    # Load COCO data
    with open(coco_file, 'r') as f:
        coco_data = json.load(f)
    
    print(f"Loaded COCO data with {len(coco_data['images'])} images and {len(coco_data['annotations'])} annotations")
    
    # Create mappings
    image_id_to_info = {img['id']: img for img in coco_data['images']}
    category_id_to_name = {cat['id']: cat['name'] for cat in coco_data['categories']}
    
    # Group annotations by image
    annotations_by_image = {}
    for ann in coco_data['annotations']:
        image_id = ann['image_id']
        if image_id not in annotations_by_image:
            annotations_by_image[image_id] = []
        annotations_by_image[image_id].append(ann)
    
    # Create manifest entries
    manifest_entries = []
    
    for image_id, image_info in image_id_to_info.items():
        # S3 URI for the image
        s3_uri = f"s3://{s3_bucket}/{s3_prefix}{image_info['file_name']}"
        
        # Get annotations for this image
        image_annotations = annotations_by_image.get(image_id, [])
        
        # Create bounding box annotations
        bounding_boxes = []
        for ann in image_annotations:
            # Convert COCO bbox format [x, y, width, height] to Rekognition format
            x, y, width, height = ann['bbox']
            
            # Normalize coordinates (Rekognition expects values between 0 and 1)
            img_width = image_info['width']
            img_height = image_info['height']
            
            left = x / img_width
            top = y / img_height
            bbox_width = width / img_width
            bbox_height = height / img_height
            
            # Ensure coordinates are within bounds
            left = max(0, min(1, left))
            top = max(0, min(1, top))
            bbox_width = max(0, min(1 - left, bbox_width))
            bbox_height = max(0, min(1 - top, bbox_height))
            
            bbox_annotation = {
                "class_id": ann['category_id'] - 1,  # Rekognition uses 0-based indexing
                "top": top,
                "left": left,
                "width": bbox_width,
                "height": bbox_height
            }
            bounding_boxes.append(bbox_annotation)
        
        # Create manifest entry
        manifest_entry = {
            "source-ref": s3_uri,
            "bounding-box": {
                "image_size": [
                    {
                        "width": image_info['width'],
                        "height": image_info['height'],
                        "depth": 3
                    }
                ],
                "annotations": bounding_boxes
            },
            "bounding-box-metadata": {
                "objects": [
                    {
                        "confidence": 1
                    } for _ in bounding_boxes
                ],
                "class-map": category_id_to_name,
                "type": "groundtruth/object-detection",
                "human-annotated": "yes",
                "creation-date": datetime.now().isoformat(),
                "job-name": "deepfashion2-labeling"
            }
        }
        
        manifest_entries.append(manifest_entry)
    
    # Split into train and test
    split_index = int(len(manifest_entries) * split_ratio)
    train_manifest = manifest_entries[:split_index]
    test_manifest = manifest_entries[split_index:]
    
    print(f"Created {len(train_manifest)} training entries and {len(test_manifest)} test entries")
    
    return train_manifest, test_manifest


def save_manifest(manifest_data, filename):
    """Save manifest data to file (one JSON object per line)."""
    with open(filename, 'w') as f:
        for entry in manifest_data:
            f.write(json.dumps(entry) + '\n')
    print(f"Saved manifest to {filename}")


def upload_to_s3(local_file, s3_bucket, s3_key, region):
    """Upload file to S3."""
    try:
        s3_client = boto3.client('s3', region_name=region)
        s3_client.upload_file(local_file, s3_bucket, s3_key)
        print(f"Uploaded {local_file} to s3://{s3_bucket}/{s3_key}")
        return f"s3://{s3_bucket}/{s3_key}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None


def upload_images_to_s3(local_image_dir, s3_bucket, s3_prefix, region):
    """Upload all images from local directory to S3."""
    try:
        s3_client = boto3.client('s3', region_name=region)
        
        if not os.path.exists(local_image_dir):
            print(f"Image directory {local_image_dir} not found!")
            return False
        
        image_files = [f for f in os.listdir(local_image_dir) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        print(f"Uploading {len(image_files)} images to S3...")
        
        for i, image_file in enumerate(image_files):
            local_path = os.path.join(local_image_dir, image_file)
            s3_key = f"{s3_prefix}{image_file}"
            
            try:
                s3_client.upload_file(local_path, s3_bucket, s3_key)
                if (i + 1) % 100 == 0:
                    print(f"Uploaded {i + 1}/{len(image_files)} images...")
            except Exception as e:
                print(f"Error uploading {image_file}: {e}")
                continue
        
        print(f"Finished uploading {len(image_files)} images to s3://{s3_bucket}/{s3_prefix}")
        return True
        
    except Exception as e:
        print(f"Error uploading images to S3: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Convert COCO to AWS Rekognition manifest format')
    parser.add_argument('--coco_file', type=str, default='deepfashion2_coco.json',
                        help='Path to COCO JSON file')
    parser.add_argument('--s3_bucket', type=str, default=S3_BUCKET_NAME,
                        help='S3 bucket name')
    parser.add_argument('--s3_region', type=str, default=S3_REGION,
                        help='S3 region')
    parser.add_argument('--local_image_dir', type=str, default=os.path.join(LOCAL_PATH, 'image'),
                        help='Local directory containing images')
    parser.add_argument('--upload_images', action='store_true',
                        help='Upload images to S3')
    parser.add_argument('--split_ratio', type=float, default=0.8,
                        help='Train/test split ratio')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.coco_file):
        print(f"COCO file {args.coco_file} not found!")
        return
    
    # Update global config if provided
    global S3_BUCKET_NAME, S3_REGION
    if args.s3_bucket != "your-rekognition-bucket":
        S3_BUCKET_NAME = args.s3_bucket
    if args.s3_region != S3_REGION:
        S3_REGION = args.s3_region
    
    print(f"Using S3 bucket: {S3_BUCKET_NAME}")
    print(f"Using S3 region: {S3_REGION}")
    
    # Convert COCO to manifest format
    train_manifest, test_manifest = create_manifest_from_coco(
        args.coco_file, 
        S3_BUCKET_NAME, 
        split_ratio=args.split_ratio
    )
    
    # Save manifest files
    train_manifest_file = "train_manifest.json"
    test_manifest_file = "test_manifest.json"
    
    save_manifest(train_manifest, train_manifest_file)
    save_manifest(test_manifest, test_manifest_file)
    
    # Upload images to S3 if requested
    if args.upload_images:
        print("Uploading images to S3...")
        upload_images_to_s3(args.local_image_dir, S3_BUCKET_NAME, "images/", S3_REGION)
    
    # Upload manifest files to S3
    print("Uploading manifest files to S3...")
    train_s3_uri = upload_to_s3(train_manifest_file, S3_BUCKET_NAME, 
                               "manifests/train_manifest.json", S3_REGION)
    test_s3_uri = upload_to_s3(test_manifest_file, S3_BUCKET_NAME, 
                              "manifests/test_manifest.json", S3_REGION)
    
    if train_s3_uri and test_s3_uri:
        print("\n" + "="*60)
        print("CONVERSION COMPLETE!")
        print("="*60)
        print(f"Training manifest: {train_s3_uri}")
        print(f"Test manifest: {test_s3_uri}")
        print("\nNext steps:")
        print("1. Go to AWS Rekognition Custom Labels console")
        print("2. Create a new project")
        print("3. Import dataset using the training manifest S3 URI")
        print("4. Start training your model")
        print("="*60)
    else:
        print("Error: Failed to upload manifest files to S3")


if __name__ == "__main__":
    main()