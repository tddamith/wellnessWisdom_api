from fastapi import APIRouter, HTTPException, UploadFile, File, Query
import boto3
from uuid import uuid4
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI router
router = APIRouter()

# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

# Initialize S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image to AWS S3.
    """
    try:
        # Generate a unique file name
        file_extension = file.filename.split(".")[-1]
        unique_file_name = f"{uuid4()}.{file_extension}"

        # Upload file to S3
        s3_client.upload_fileobj(
            file.file,
            AWS_BUCKET_NAME,
            unique_file_name,
            ExtraArgs={"ContentType": file.content_type},
        )

        # Generate the file URL
        file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_file_name}"

        return {"file_url": file_url, "file_name": unique_file_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

@router.delete("/delete-image/")
async def delete_image(file_name: str = Query(..., description="The name of the file to delete")):
    """
    Delete an image from AWS S3 bucket.
    """
    try:
        # Delete the file from S3
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=file_name)

        return {"message": f"File {file_name} deleted successfully from bucket {AWS_BUCKET_NAME}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
