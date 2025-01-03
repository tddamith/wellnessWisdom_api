import os
import requests
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

app = FastAPI()

# Replace with your NewsAPI key or use an environment variable
API_KEY = os.getenv("NEWSAPI_KEY")

# Create a new APIRouter instance
router = APIRouter()

@router.get("/top20news")
async def get_top_20_news():
    """
    Fetch top 20 news headlines (worldwide) using NewsAPI.
    Return the news articles in JSON format.
    """
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": API_KEY,
        "language": "en",
        "pageSize": 20
        # You can add "country" or "sources" if you want a specific region or news source
        # e.g., "country": "us" for US headlines
    }

    try:
        # Sending the GET request to the NewsAPI
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an exception for 4xx/5xx status codes

        # Parse the response JSON data
        data = response.json()

        # Check if the status is 'ok'
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            return JSONResponse(content={
                "status": "success",
                "totalResults": data.get("totalResults", 0),
                "articles": articles
            }, status_code=200)
        else:
            # Handle error if the status is not 'ok'
            return JSONResponse(content={
                "status": "error",
                "message": data.get("message", "Unknown error from NewsAPI")
            }, status_code=500)

    except requests.exceptions.RequestException as e:
        # Handle any requests exceptions
        return JSONResponse(content={
            "status": "error",
            "message": str(e)
        }, status_code=500)



