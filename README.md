# AWS Rekognition Demo with DeepFashion2 Dataset

AWS Rekognition demo for clothing classification using the DeepFashion2 dataset. This project provides tools to convert DeepFashion2 annotations into AWS Rekognition Custom Labels format for training custom clothing detection models.

## Overview

This demo focuses on using the DeepFashion2 dataset, a complex clothing classification dataset, to train an AWS Rekognition model to identify clothing pieces in images. The project includes:

- Python scripts to convert DeepFashion2 annotations to COCO format
- Tools to transform COCO annotations into AWS Rekognition manifest files
- Complete workflow for training custom clothing detection models

## Project Structure

```
rekognition-demo/
├── README.md
├── requirements.txt
├── config.py
├── coco_to_manifest.py      # Convert DeepFashion2 to COCO format
├── manifest_generator.py    # Convert COCO to AWS Rekognition manifest
├── utils/
│   ├── __init__.py
│   ├── deepfashion_parser.py
│   └── s3_utils.py
├── examples/
│   └── sample_images/
└── docs/
    └── s3_schema.md
```

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- S3 bucket for storing images and manifest files
- AWS Rekognition Custom Labels access

## Installation

1. Clone or create this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## S3 Setup

1. **Create an S3 bucket** for your project
2. **Upload images** to the S3 bucket using the path structure:
   ```
   your-bucket-name/
   └── images/
       ├── image1.jpg
       ├── image2.jpg
       └── ...
   ```

### Recommended S3 Schema

```
s3://your-rekognition-bucket/
├── images/                 # All training images
│   ├── train/
│   │   ├── tops/
│   │   ├── bottoms/
│   │   ├── dresses/
│   │   └── accessories/
│   └── validation/
│       ├── tops/
│       ├── bottoms/
│       ├── dresses/
│       └── accessories/
├── annotations/           # Annotation files
│   ├── deepfashion2_coco.json
│   └── rekognition_manifest.json
└── manifests/            # Final manifest files
    ├── training.manifest
    └── validation.manifest
```

## Configuration

1. Update the S3 bucket name in `config.py`:
   ```python
   S3_BUCKET_NAME = "your-rekognition-bucket"
   ```

## Usage

### Step 1: Convert DeepFashion2 to COCO Format

```bash
python coco_to_manifest.py
```

This script will:
- Parse DeepFashion2 annotations
- Convert them to COCO format
- Save the COCO JSON file locally

### Step 2: Generate AWS Rekognition Manifest

```bash
python manifest_generator.py
```

This script will:
- Read the COCO format annotations
- Convert them to AWS Rekognition manifest format
- Upload the manifest file to your S3 bucket

### Step 3: Train AWS Rekognition Model

1. **Create a Custom Labels Project** in AWS Rekognition Console
2. **Create a Dataset** using the uploaded manifest file
3. **Start Training** the model
4. **Start the Model** once training is complete
5. **Test the Model** with new images

## Clothing Categories

The DeepFashion2 dataset includes the following clothing categories:

- **Tops**: shirts, t-shirts, blouses, sweaters
- **Bottoms**: pants, jeans, skirts, shorts
- **Dresses**: all types of dresses
- **Accessories**: bags, shoes, hats, jewelry

## File Descriptions

- **`coco_to_manifest.py`**: Converts DeepFashion2 annotations to COCO format
- **`manifest_generator.py`**: Converts COCO format to AWS Rekognition manifest
- **`config.py`**: Configuration settings for S3 bucket and other parameters
- **`utils/deepfashion_parser.py`**: Utilities for parsing DeepFashion2 dataset
- **`utils/s3_utils.py`**: Helper functions for S3 operations

## AWS Costs

Be aware of AWS costs:
- **S3 Storage**: ~$0.023 per GB/month
- **Rekognition Training**: ~$1.00 per hour of training
- **Rekognition Inference**: ~$0.40 per hour when model is running
- **Data Transfer**: Various rates for upload/download

## Troubleshooting

### Common Issues

1. **S3 Permissions**: Ensure your AWS credentials have S3 read/write permissions
2. **Image Formats**: AWS Rekognition supports JPEG and PNG formats
3. **File Size Limits**: Maximum image size is 15MB
4. **Manifest Format**: Ensure JSON manifest follows AWS Rekognition specification

### Error Messages

- `NoCredentialsError`: Configure AWS CLI or set environment variables
- `BucketNotFound`: Verify S3 bucket name and region
- `InvalidManifest`: Check JSON format and required fields

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Resources

- [AWS Rekognition Custom Labels Documentation](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/)
- [DeepFashion2 Dataset](https://github.com/switchablenorms/DeepFashion2)
- [COCO Format Specification](https://cocodataset.org/#format-data)
