from fastapi import APIRouter, HTTPException
from uuid import uuid4
from typing import List
from app.db.database import mysql
from app.api.v1.schemas import ArticleCreate, ArticleResponse
from typing import List  # Ensure this import is present
from typing import Optional
import json

router = APIRouter()

@router.post("/articles/", response_model=ArticleResponse)
async def create_article(article: ArticleCreate):
    """
    Create a new article in the database.
    """
    article_id = str(uuid4())  # Generate a unique ID
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Insert the new article
                await cursor.execute("""
                    INSERT INTO news_articles
                    (id, title, content, author, category_id, sub_category_id, image_url, is_published, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    article_id,
                    article.title,
                    article.content,
                    article.author,
                    article.category_id,
                    article.sub_category_id,
                    article.image_url,
                    article.is_published,
                    json.dumps(article.tags) if article.tags else None  # # Convert list to JSON string or pass None
                ))
                await conn.commit()

                # Fetch the created article
                await cursor.execute("SELECT * FROM news_articles WHERE id = %s", (article_id,))
                result = await cursor.fetchone()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to create article: {str(e)}")

    return {
        "id": result[0],
        "title": result[1],
        "content": result[2],
        "author": result[3],
        "create_date": result[4],
        "update_date": result[5],
        "category_id": result[6],
        "sub_category_id": result[7],
        "image_url": result[8],
        "is_published": result[9],
        "views": result[10],
        "tags": json.loads(result[11]) if result[11] else None,  # Convert JSON string back to Python list
    }

@router.post("/articles/bulk", response_model=dict)
async def bulk_insert_articles(articles: List[ArticleCreate]):
    """
    Bulk insert articles into the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Prepare bulk data
                bulk_data = [
                    (
                        str(uuid4()),  # Generate a unique ID for each article
                        article.title,
                        article.content,
                        article.author,
                        article.category_id,
                        article.sub_category_id,
                        article.image_url,
                        article.is_published,
                        json.dumps(article.tags) if article.tags else None  # Serialize tags to JSON
                    )
                    for article in articles
                ]

                # Perform bulk insert
                await cursor.executemany("""
                    INSERT INTO news_articles
                    (id, title, content, author, category_id, sub_category_id, image_url, is_published, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, bulk_data)
                await conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to insert articles: {str(e)}")

    return {"message": f"Successfully inserted {len(articles)} articles."}

@router.get("/articles/", response_model=List[ArticleResponse])
async def get_articles(is_published: Optional[bool] = None):
    """
    Fetch all articles, optionally filtering by published status.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Build the query
                query = "SELECT * FROM news_articles"
                params = []
                if is_published is not None:
                    query += " WHERE is_published = %s"
                    params.append(is_published)

                # Execute the query
                await cursor.execute(query, tuple(params))
                results = await cursor.fetchall()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")

    # Return the results as a list of dictionaries
    return [
        {
            "id": result[0],
                    "title": result[1],
                    "content": result[2],
                    "author": result[3],
                    "create_date": result[4],
                    "update_date": result[5],
                    "category_id": result[6],
                    "sub_category_id": result[7],
                    "image_url": result[8],
                    "is_published": result[9],
                    "views": result[10],
                    "tags": eval(result[11]) if result[10] else None,
        }
        for row in results
    ]


@router.get("/articles/by-category/{category_id}", response_model=List[ArticleResponse])
async def get_articles_by_category(category_id: str):
    """
    Retrieve news articles by category ID.
    """
    if not category_id:
        raise HTTPException(status_code=400, detail="Category ID is required")

    async with mysql.pool.acquire() as conn:
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection is not established")
        async with conn.cursor() as cursor:
            try:
                # Query to fetch articles by category_id
                await cursor.execute("""
                    SELECT
                        articles.*,
                        categories.name AS category_name,
                        subcategories.name AS subcategory_name
                    FROM news_articles AS articles
                    LEFT JOIN categories ON articles.category_id = categories.id
                    LEFT JOIN subcategories ON articles.sub_category_id = subcategories.id
                    WHERE articles.category_id = %s
                """, (category_id,))
                result = await cursor.fetchall()



                # If no articles found, raise an HTTP exception
                if not result:
                    raise HTTPException(status_code=404, detail="No articles found for the given category ID")

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve articles: {str(e)}")

    # Return the list of articles
    return [
        {
            "id": row[0],
             "title": row[1],
             "content": row[2],
             "author": row[3],
             "create_date": row[4],
             "update_date": row[5],
             "category_id": row[6],
             "sub_category_id": row[7],
             "image_url": row[8],
             "is_published": row[9],
             "views": row[10],
             "tags": eval(row[11]) if row[11] else None,
             "category_name": row[12],  # Category name from JOIN
             "subcategory_name": row[13],  # Subcategory name from JOIN
        }
        for row in result
    ]
