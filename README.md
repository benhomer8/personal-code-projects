# Fashion Image Recognition using Amazon Rekognition and the DeepFashion2 Dataset

AWS Rekognition demo for fashion clothing recognition using the DeepFashion2 dataset. This demo focuses on using the DeepFashion2 dataset to train an AWS Rekognition model to identify clothing pieces on images.

It uses two Python scripts: one to translate the DeepFashion2 annotations to COCO (Common Objects in Context) format, and another that transforms this file into a manifest file that is used by AWS Rekognition to label images.

**Note**: It's the user's responsibility to create the S3 bucket to store the images and manifest file created by the scripts, and create the model on AWS Rekognition using the manifest file created by the scripts.

## How to Use

To use the model we need an S3 bucket setup with all the images, then follow the building order using the Python scripts. After that, upload the manifest file to S3, then use it to create the AWS Rekognition Custom Label dataset, then start the model training using it.

**Important**: The images used should be in an S3 bucket.

## S3 Bucket Setup

1. **Create an S3 bucket**
2. **Upload all images to S3** using the path `images/`

For convenience, we recommend this schema for the bucket:

```
s3://your-rekognition-bucket/
├── images/                 # All training images
│   ├── 000001.jpg
│   ├── 000002.jpg
│   └── ...
├── annotations/           # Annotation files (optional)
│   ├── deepfashion2_coco.json
│   └── rekognition_manifest.json
└── manifests/            # Final manifest files
    ├── train_manifest.json
    └── test_manifest.json
```

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- S3 bucket for storing images and manifest files
- AWS Rekognition Custom Labels access
- DeepFashion2 dataset

## Installation

1. Clone this repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your AWS credentials:
   ```bash
   aws configure
   ```

## Configuration

Update the S3 bucket name in `coco_to_manifest.py`:

```python
S3_BUCKET_NAME = "your-rekognition-bucket"
```

## Build

### Step 1: Convert DeepFashion2 to COCO Format

Run to create the COCO file:

```bash
python deepfashion2_to_coco.py --data_dir /path/to/deepfashion2/validation --output deepfashion2_coco.json
```

### Step 2: Convert COCO to Manifest and Upload to S3

Run to create the manifest file and upload to S3:

```bash
python coco_to_manifest.py --coco_file deepfashion2_coco.json --s3_bucket your-rekognition-bucket --upload_images
```

## Train

1. **Create an AWS Rekognition Custom Label Model** using the uploaded manifest file
2. **Start model training**

### Training Steps:

1. Go to AWS Rekognition Custom Labels console
2. Create a new project
3. Import dataset using "Import images labeled by SageMaker Ground Truth" option
4. Provide the S3 URI of the training manifest file
5. Start training the model
6. Once training is complete, start the model for inference

## DeepFashion2 Dataset Categories

The dataset includes 13 clothing categories:

- **short_sleeved_shirt**
- **long_sleeved_shirt** 
- **short_sleeved_outwear**
- **long_sleeved_outwear**
- **vest**
- **sling** (consolidated with vest)
- **shorts**
- **trousers**
- **skirt**
- **short_sleeved_dress**
- **long_sleeved_dress**
- **vest_dress**
- **sling_dress** (consolidated with vest_dress)

## Results

The trained model can achieve up to **85% overall accuracy**, with some clothing types reaching over **90% accuracy**. Training typically takes 24-48 hours depending on dataset size.

## File Descriptions

- **`deepfashion2_to_coco.py`**: Converts DeepFashion2 annotations to COCO format
- **`coco_to_manifest.py`**: Converts COCO format to AWS Rekognition manifest and uploads to S3
- **`config.py`**: Configuration settings for S3 bucket and other parameters
- **`requirements.txt`**: Python dependencies

## AWS Costs

Be aware of AWS costs:
- **S3 Storage**: ~$0.023 per GB/month
- **Rekognition Training**: ~$1.00 per hour of training
- **Rekognition Inference**: ~$4.00 per hour when model is running
- **Data Transfer**: Various rates for upload/download

**Important**: Remember to stop your Custom Labels model when not in use to avoid inference charges.

## Troubleshooting

### Common Issues

1. **S3 Permissions**: Ensure your AWS credentials have S3 read/write permissions
2. **Image Formats**: AWS Rekognition supports JPEG and PNG formats only
3. **File Size Limits**: Maximum image size is 15MB
4. **Manifest Format**: Ensure JSON manifest follows AWS Rekognition specification

### Error Messages

- `NoCredentialsError`: Configure AWS CLI or set environment variables
- `BucketNotFound`: Verify S3 bucket name and region
- `InvalidManifest`: Check JSON format and required fields

## About This Implementation

This project is based on the TrackIt Fashion Catalog AWS Rekognition Demo, which demonstrates an end-to-end workflow for fashion image recognition using AWS services and the DeepFashion2 dataset.

## Resources

- [AWS Rekognition Custom Labels Documentation](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/)
- [DeepFashion2 Dataset](https://github.com/switchablenorms/DeepFashion2)
- [COCO Format Specification](https://cocodataset.org/#format-data)
- [TrackIt Blog Post](https://trackit.io/image-recognition-amazon-rekognition-deepfashion2/)
