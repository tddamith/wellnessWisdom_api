from openai import OpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from app.db.database import mysql
from dotenv import load_dotenv
import os
import json
import logging

# Load environment variables
load_dotenv()

# Initialize FastAPI router
router = APIRouter()

# OpenAI Configuration
api_key=os.environ['OPENAI_API_KEY']
client = OpenAI()  # Load API key from environment

# Request Schema
class GenerateArticleRequest(BaseModel):
    category_id: str
    category_name: str
    sub_category_id: str
    sub_category_name: str

# Response Schema
class GeneratedArticleResponse(BaseModel):
    title: str
    content: str
    tags: list[str]

class ArticleResponse(BaseModel):
    title: str
    content: str
    category_id: str
    sub_category_id: str
    image_url: str
    author: str
    tags: list[str]


@router.post("/articles/ai-create")
async def create_ai_generated_article(request: GenerateArticleRequest):
    """
    Generate an article using AI content and save it into the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Step 1: Generate Article Content with ChatGPT
                logging.info("Generating content with ChatGPT...")
                prompt = (
                    f"Write a detailed and engaging article for the subcategory '{request.sub_category_name}'"
                    f"in the category '{request.category_name}'. Use professional, informative, and engaging language."
                    f"Structure the article into the following format:"
                    f"1.Provide a title optimized for SEO along with relevant keywords."
                    f"2. **Content Sections**:\n"
                    f"   - **Introduction**: Start with a brief, captivating overview of the topic."
                    f"   - **Body**: Include well-researched, informative, and structured content with headings and subheadings."
                    f"   - **Conclusion**: Provide a strong closing summary with key takeaways.\n"
                    f"3. **Popular Content**: Research and include the best and most popular content ideas related to '{request.category_name}'"
                    f"4. use HTML tag for more easy way to readability. "
                    f"Use the following identifiers for accuracy:"
                    f"- Category ID: '{request.category_id}'"
                    f"- Subcategory ID: '{request.sub_category_id}'"
                    f"Ensure the final result is SEO-optimized, well-structured, and visually appealing to engage the audience."
                )

                # Generate content
                response = client.beta.chat.completions.parse(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": "You are a professional article writer."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format=ArticleResponse,
                )
                raw_content = response.choices[0].message.parsed

                return{
                    "data": raw_content,
                }

            except Exception as e:
                logging.error(f"Failed to create article: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to create AI-generated article: {str(e)}")
