from fastapi import APIRouter, HTTPException, Query
from uuid import uuid4
from typing import List
from app.db.database import mysql
from app.api.v1.schemas import ArticleCreate, ArticleResponse
from typing import List  # Ensure this import is present
from typing import Optional
import json
import logging
from pydantic import BaseModel


router = APIRouter()

class UpdateImageURLRequest(BaseModel):
    image_url: str

@router.post("/articles/", response_model=dict)
async def create_article(article: ArticleCreate):
    """
    Create a new article in the database.
    """
    article_id = str(uuid4())  # Generate a unique ID
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Insert the new article
                print(article)
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


@router.get("/articles/by-category/{category_id}", response_model=List[dict])
async def get_articles_by_category(category_id: str):
    """
    Retrieve news articles by category ID, including category and subcategory names.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Query with JOINs to fetch category and subcategory names
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

                # Debug: Log the raw result
                print("SQL Result:", result)

                if not result:
                    raise HTTPException(status_code=404, detail="No articles found for the given category ID")

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve articles: {str(e)}")

    # Return the result with category and subcategory names
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
            "category_name": row[12],  # Ensure this field is returned
            "subcategory_name": row[13],  # Ensure this field is returned
        }
        for row in result
        ]


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article_by_id(article_id: str):
    """
    Retrieve a single article by its ID.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                logging.info(f"Fetching article with ID: {article_id}")  # Log the article ID
                await cursor.execute("""
                    SELECT
                        articles.*,
                        categories.name AS category_name,
                        subcategories.name AS subcategory_name
                    FROM news_articles AS articles
                    LEFT JOIN categories ON articles.category_id = categories.id
                    LEFT JOIN subcategories ON articles.sub_category_id = subcategories.id
                    WHERE articles.id = %s
                """, (article_id,))
                result = await cursor.fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="Article not found")

            except Exception as e:
                logging.error(f"Error fetching article: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to retrieve the article: {str(e)}")

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
        "tags": eval(result[11]) if result[11] else None,
        "category_name": result[12],
        "subcategory_name": result[13],
    }

@router.get("/articles/search/", response_model=List[str])
async def get_article_suggestions():
    """
    Endpoint for article name suggestions.
    """
    # Return a list of strings as the response
    return ["Example Article 1", "Example Article 2", "Example Article 3"]



@router.get("/articles/search/suggestions/{query}", response_model=List[dict])
async def get_article_suggestions(query: str):
    """
    Retrieve article name suggestions based on a search query.
    """
    logging.info(f"Received query: {query}")

    # Handle empty or whitespace-only queries
    query = query.strip()
    if not query:
        logging.warning("Query parameter is empty or whitespace-only")
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty or whitespace-only")

    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Construct search term for SQL LIKE query
                search_term = f"%{query.lower()}%"
                logging.info(f"Constructed search term: {search_term}")

                # Execute the query to find matching article titles
                await cursor.execute("""
                   SELECT DISTINCT
                                           articles.title,
                                           articles.id,
                                           articles.image_url,
                                           MAX(categories.name) AS category_name,
                                           MAX(subcategories.name) AS sub_category_name
                                       FROM news_articles AS articles
                                       LEFT JOIN categories ON articles.category_id = categories.id
                                       LEFT JOIN subcategories ON articles.sub_category_id = subcategories.id
                                       WHERE LOWER(articles.title) LIKE %s
                                       GROUP BY articles.id
                                       ORDER BY CHAR_LENGTH(articles.title) ASC
                                       LIMIT 10;
                """, (search_term,))
                result = await cursor.fetchall()

                # Log the raw SQL result
                logging.info(f"SQL result: {result}")

                # Return an empty list if no results found
                if not result:
                    logging.info("No matching articles found")
                    return []

            except Exception as e:
                logging.error(f"Failed to retrieve suggestions: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to retrieve suggestions")

    # Extract details from the result
    suggestions = [
        {
            "id": row[1],
            "title": row[0],
            "image_url": row[2],
            "category_name": row[3],
            "sub_category_name": row[4],
        }
        for row in result
    ]
    logging.info(f"Suggestions returned: {suggestions}")
    return suggestions



@router.get("/articles/title/{title}", response_model=dict)
async def get_article_by_title(title: str):
    """
    Retrieve a single news article by its title.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # SQL query to find the article by title (case-insensitive)
                await cursor.execute("""
                    SELECT DISTINCT
                        articles.id,
                        articles.title,
                        articles.content,
                        articles.image_url,
                        articles.create_date,
                        articles.update_date,
                        articles.tags,
                        categories.name AS category_name,
                        subcategories.name AS sub_category_name
                    FROM news_articles AS articles
                    LEFT JOIN categories ON articles.category_id = categories.id
                    LEFT JOIN subcategories ON articles.sub_category_id = subcategories.id
                    WHERE LOWER(articles.title) = LOWER(%s)
                    LIMIT 1;
                """, (title,))
                result = await cursor.fetchone()

                # If no article is found, raise a 404 error
                if not result:
                    raise HTTPException(status_code=404, detail="Article not found")

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to retrieve article: {str(e)}")

    # Construct and return the response
    return {
        "id": result[0],
        "title": result[1],
        "content": result[2],
        "image_url": result[3],
        "create_date": result[4],
        "update_date": result[5],
        "tags": eval(result[6]) if result[6] else [],
        "category_name": result[7],
        "sub_category_name": result[8],
    }



@router.put("/articles/{article_id}/image", response_model=dict)
async def update_article_image_url(article_id: str, request: UpdateImageURLRequest):
    """
    Update the image_url of a news article by its ID.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Check if the article exists
                await cursor.execute("""
                    SELECT id
                    FROM news_articles
                    WHERE id = %s
                """, (article_id,))
                result = await cursor.fetchone()

                if not result:
                    raise HTTPException(status_code=404, detail="Article not found")

                # Update the image_url for the specified article
                await cursor.execute("""
                    UPDATE news_articles
                    SET image_url = %s, update_date = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (request.image_url, article_id))
                await conn.commit()

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update image URL: {str(e)}")

    return {"message": f"Image URL updated successfully for article ID {article_id}"}


@router.get("/articles/page", response_model=List[dict])
async def get_all_articles(
    skip: int = Query(0, ge=0),  # Default to skip 0, must be >= 0
    limit: int = Query(10, ge=1, le=100)  # Default to 10, must be between 1 and 100
):
    """
    Retrieve all news articles, ordered by the latest update, with pagination support.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Query to fetch articles, ordered by the latest update, with pagination (LIMIT & OFFSET)
                query = """
                    SELECT
                        articles.*,
                        subcategories.name AS subcategory_name
                    FROM news_articles AS articles
                    LEFT JOIN subcategories ON articles.sub_category_id = subcategories.id
                    ORDER BY articles.update_date DESC
                    LIMIT %s OFFSET %s
                """
                print("Executing SQL Query:", query)
                await cursor.execute(query, (limit, skip))
                result = await cursor.fetchall()

                # Check if the result is empty
                if not result:
                    raise HTTPException(status_code=404, detail="No articles found")

                # Count the total number of articles in the database (for pagination)
                await cursor.execute("""
                    SELECT COUNT(*) FROM news_articles
                """)
                total_articles = await cursor.fetchone()

                # If no total articles count, throw an error
                if total_articles is None:
                    raise HTTPException(status_code=500, detail="Failed to fetch total article count")

                # Debug: Log the total article count
                print("Total Articles:", total_articles)

            except Exception as e:
                # Catch any exception and log it for debugging
                print(f"Error while fetching articles: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to retrieve articles: {str(e)}")

    # Return the total article count and paginated articles
    return {
        "total_articles": total_articles[0],  # Total number of articles in the database
        "articles": [
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
                "subcategory_name": row[12],  # Subcategory name
            }
            for row in result
        ]
    }
