#!/usr/bin/env python3
"""
Example usage script for AWS Rekognition Custom Labels fashion model

This script demonstrates how to use the trained fashion recognition model
for inference on new images.
"""

import boto3
import json
import argparse
from config import AWS_REGION, REKOGNITION_CONFIG


def detect_fashion_items(image_path, model_arn, min_confidence=0.5):
    """
    Detect fashion items in an image using the trained Custom Labels model.
    
    Args:
        image_path: Path to the image file (local or S3)
        model_arn: ARN of the trained Custom Labels model
        min_confidence: Minimum confidence threshold for detections
    
    Returns:
        List of detected fashion items with bounding boxes and labels
    """
    
    # Initialize Rekognition client
    rekognition = boto3.client('rekognition', region_name=AWS_REGION)
    
    try:
        # Prepare image input
        if image_path.startswith('s3://'):
            # S3 image
            bucket, key = image_path.replace('s3://', '').split('/', 1)
            image_input = {
                'S3Object': {
                    'Bucket': bucket,
                    'Name': key
                }
            }
        else:
            # Local image
            with open(image_path, 'rb') as image_file:
                image_input = {'Bytes': image_file.read()}
        
        # Call Custom Labels detection
        response = rekognition.detect_custom_labels(
            ProjectVersionArn=model_arn,
            Image=image_input,
            MinConfidence=min_confidence
        )
        
        return response['CustomLabels']
        
    except Exception as e:
        print(f"Error detecting fashion items: {e}")
        return []


def start_model(model_arn, min_inference_units=1):
    """Start the Custom Labels model for inference."""
    
    rekognition = boto3.client('rekognition', region_name=AWS_REGION)
    
    try:
        response = rekognition.start_project_version(
            ProjectVersionArn=model_arn,
            MinInferenceUnits=min_inference_units
        )
        
        print(f"Starting model: {model_arn}")
        print(f"Status: {response['Status']}")
        
        return response['Status']
        
    except Exception as e:
        print(f"Error starting model: {e}")
        return None


def stop_model(model_arn):
    """Stop the Custom Labels model to save costs."""
    
    rekognition = boto3.client('rekognition', region_name=AWS_REGION)
    
    try:
        response = rekognition.stop_project_version(
            ProjectVersionArn=model_arn
        )
        
        print(f"Stopping model: {model_arn}")
        print(f"Status: {response['Status']}")
        
        return response['Status']
        
    except Exception as e:
        print(f"Error stopping model: {e}")
        return None


def get_model_status(model_arn):
    """Get the current status of the Custom Labels model."""
    
    rekognition = boto3.client('rekognition', region_name=AWS_REGION)
    
    try:
        response = rekognition.describe_project_versions(
            ProjectArn=model_arn.split('/version/')[0]
        )
        
        for version in response['ProjectVersionDescriptions']:
            if version['ProjectVersionArn'] == model_arn:
                return version['Status']
        
        return "NOT_FOUND"
        
    except Exception as e:
        print(f"Error getting model status: {e}")
        return "ERROR"


def print_detection_results(detections, image_path):
    """Print formatted detection results."""
    
    print(f"\n{'='*60}")
    print(f"FASHION DETECTION RESULTS")
    print(f"{'='*60}")
    print(f"Image: {image_path}")
    print(f"Detections found: {len(detections)}")
    print(f"{'='*60}")
    
    if not detections:
        print("No fashion items detected.")
        return
    
    for i, detection in enumerate(detections, 1):
        name = detection['Name']
        confidence = detection['Confidence']
        
        print(f"\n{i}. {name}")
        print(f"   Confidence: {confidence:.2f}%")
        
        if 'Geometry' in detection:
            bbox = detection['Geometry']['BoundingBox']
            print(f"   Bounding Box:")
            print(f"     Left: {bbox['Left']:.3f}")
            print(f"     Top: {bbox['Top']:.3f}")
            print(f"     Width: {bbox['Width']:.3f}")
            print(f"     Height: {bbox['Height']:.3f}")


def main():
    parser = argparse.ArgumentParser(description='Use AWS Rekognition Custom Labels for fashion detection')
    parser.add_argument('--model_arn', type=str, required=True,
                        help='ARN of the trained Custom Labels model')
    parser.add_argument('--image', type=str,
                        help='Path to image file (local or S3 URI)')
    parser.add_argument('--action', type=str, choices=['start', 'stop', 'status', 'detect'],
                        default='detect', help='Action to perform')
    parser.add_argument('--min_confidence', type=float, default=0.5,
                        help='Minimum confidence threshold')
    parser.add_argument('--min_inference_units', type=int, default=1,
                        help='Minimum inference units for model')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_model(args.model_arn, args.min_inference_units)
        
    elif args.action == 'stop':
        stop_model(args.model_arn)
        
    elif args.action == 'status':
        status = get_model_status(args.model_arn)
        print(f"Model Status: {status}")
        
    elif args.action == 'detect':
        if not args.image:
            print("Error: --image parameter required for detection")
            return
        
        # Check model status first
        status = get_model_status(args.model_arn)
        if status != 'RUNNING':
            print(f"Warning: Model status is '{status}'. Model must be RUNNING for inference.")
            print("Use --action start to start the model first.")
            return
        
        # Perform detection
        detections = detect_fashion_items(args.image, args.model_arn, args.min_confidence)
        print_detection_results(detections, args.image)


if __name__ == "__main__":
    main()