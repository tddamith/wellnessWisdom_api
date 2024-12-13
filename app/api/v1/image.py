from fastapi import FastAPI, HTTPException
import openai
import requests

# Initialize FastAPI app
app = FastAPI()

# Set your OpenAI API key
openai.api_key = "your_openai_api_key"

@app.post("/generate-image-url/")
async def generate_image_url(prompt: str):
    try:
        # Use OpenAI's API to create an image prompt
        response = openai.Image.create(
            prompt=request.prompt,
            n=1,  # Number of images
            size="1024x1024"  # Image size
        )

        # Extract the image URL
        image_url = response['data'][0]['url']

        return {"image_url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
