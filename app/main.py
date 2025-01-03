from fastapi  import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.db.database import connect_all, close_all
from app.api.v1.category import router as category_router
from app.api.v1.sub_category import router as sub_category_router
from app.api.v1.articles import router as articles_router
from app.api.v1.upload_image import router as upload_image_router
from app.api.v1.article_ai import router as article_ai_router
from app.api.v1.token import router as token_router
from app.api.v1.trends import router as trends_router
from app.api.v1.top_news import router as top_news_router
# from app.api.v1.proxy_download import router as proxy_download_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Write logs to a file
        logging.StreamHandler()         # Print logs to the console
    ]
)

app = FastAPI()
# Register the sync router (optional manual sync)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db():
    # Connect to MongoDB and MySQL during application startup
    await connect_all()
    #asyncio.create_task(auto_sync_impressions(3600))
    #asyncio.create_task(run_task_at_time(auto_sync_impressions, target_hour=3, target_minute=0))
@app.on_event("shutdown")
async def shutdown_db():
    # Close database connections during application shutdown
    await close_all()


# Register the sync router
# app.include_router(yt_download_link_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1",tags=["Categories"])
app.include_router(sub_category_router, prefix="/api/v1",tags=["SubCategories"])
app.include_router(articles_router, prefix="/api/v1",tags=["Articles"])
app.include_router(upload_image_router, prefix="/api/v1",tags=["UploadImage"])
app.include_router(article_ai_router, prefix="/api/v1",tags=["ArticlesAI"])
app.include_router(token_router, prefix="/api/v1",tags=["Authentication"])
app.include_router(trends_router, prefix="/api/v1",tags=["Trends"])
app.include_router(top_news_router, prefix="/api/v1",tags=["TopNews"])

@app.get("/")
async def read_root():
    return {"message": "insight API"}
