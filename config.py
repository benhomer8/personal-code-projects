#!/usr/bin/env python3
"""
Configuration file for AWS Rekognition Fashion Demo

Update these settings according to your AWS environment.
"""

# AWS Configuration
AWS_REGION = "us-west-2"  # Update with your preferred AWS region
AWS_PROFILE = "default"   # AWS CLI profile to use

# S3 Configuration
S3_BUCKET_NAME = "your-rekognition-bucket"  # Update with your S3 bucket name

# S3 Folder Structure
S3_FOLDERS = {
    "images": "images/",           # Folder for training images
    "manifests": "manifests/",     # Folder for manifest files
    "annotations": "annotations/", # Folder for annotation files
    "models": "models/"            # Folder for trained models
}

# Dataset Configuration
DATASET_CONFIG = {
    "local_path": "./data/",       # Local path to dataset
    "validation_split": 0.2,       # Percentage for validation set (0.2 = 20%)
    "supported_formats": [".jpg", ".jpeg", ".png"]  # Supported image formats
}

# DeepFashion2 Category Configuration
DEEPFASHION2_CATEGORIES = {
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

# Consolidated categories (as per TrackIt implementation)
CONSOLIDATED_CATEGORIES = {
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

# AWS Rekognition Custom Labels Configuration
REKOGNITION_CONFIG = {
    "project_name": "fashion-catalog-demo",
    "model_name": "deepfashion2-model",
    "min_inference_units": 1,
    "max_inference_units": 5
}

# Processing Configuration
PROCESSING_CONFIG = {
    "batch_size": 100,      # Number of images to process at once
    "max_image_size": 15,   # Maximum image size in MB (AWS Rekognition limit)
    "min_confidence": 0.5,  # Minimum confidence threshold for predictions
    "max_annotations_per_image": 10  # Maximum number of annotations per image
}