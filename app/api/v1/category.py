from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4
from app.db.database import mysql
from app.api.v1.schemas import CategoryCreate, CategoryResponse, SubCategoryCreate, SubCategoryResponse

router = APIRouter()

@router.post("/categories/", response_model=CategoryResponse)
async def create_category(category: CategoryCreate):
    category_id = str(uuid4())  # Generate UUID4
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Check if category already exists
            await cursor.execute("SELECT id FROM categories WHERE name=%s", (category.name,))
            existing = await cursor.fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Category already exists")

            # Insert new category
            await cursor.execute("""
                INSERT INTO categories (id, name, no_of_articles, order_no, icon_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (category_id, category.name, category.no_of_articles, category.order_no, category.icon_name))
            await conn.commit()

            # Fetch the created category
            await cursor.execute("SELECT * FROM categories WHERE id=%s", (category_id,))
            result = await cursor.fetchone()

    return {
        "id": result[0],
        "name": result[1],
        "create_date": result[2],
        "update_date": result[3],
        "no_of_articles": result[4],
        "order_no": result[5],
        "icon_name": result[6],
    }

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryCreate):
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Check if category exists
            await cursor.execute("SELECT id FROM categories WHERE id=%s", (category_id,))
            existing = await cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Category not found")

            # Update the category
            await cursor.execute("""
                UPDATE categories
                SET name=%s, no_of_articles=%s, order_no=%s, icon_name=%s, update_date=CURRENT_TIMESTAMP
                WHERE id=%s
            """, (category.name, category.no_of_articles, category.order_no, category.icon_name, category_id))
            await conn.commit()

            # Fetch the updated category
            await cursor.execute("SELECT * FROM categories WHERE id=%s", (category_id,))
            result = await cursor.fetchone()

    return {
        "id": result[0],
        "name": result[1],
        "create_date": result[2],
        "update_date": result[3],
        "no_of_articles": result[4],
        "order_no": result[5],
        "icon_name": result[6],
}

@router.delete("/categories/id/{category_id}", response_model=dict)
async def delete_category(category_id: str):
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Check if category exists
            await cursor.execute("SELECT id FROM categories WHERE id=%s", (category_id,))
            existing = await cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Category not found")

            # Delete the category
            await cursor.execute("DELETE FROM categories WHERE id=%s", (category_id,))
            await conn.commit()

    return {"message": f"Category with id {category_id} has been deleted successfully"}

@router.get("/categories/", response_model=list[CategoryResponse])
async def get_categories():
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM categories")
            categories = await cursor.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "create_date": row[2],
            "update_date": row[3],
            "no_of_articles": row[4],
            "order_no": row[5],
            "icon_name": row[6],
        }
        for row in categories
    ]

@router.post("/categories/bulk_upload", response_model=dict)
async def bulk_upload_categories(categories: list[CategoryCreate]):
    """
    Bulk upload categories into the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Prepare bulk insert data
                data_to_insert = [
                    (
                        str(uuid4()),  # Generate a unique ID for each category
                        category.name,
                        category.no_of_articles,
                        category.order_no,
                        category.icon_name
                    )
                    for category in categories
                ]

                # Insert categories into the database
                await cursor.executemany("""
                    INSERT INTO categories (id, name, no_of_articles, order_no, icon_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, data_to_insert)
                await conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload categories: {str(e)}")

    return {"message": f"Successfully uploaded {len(categories)} categories."}

@router.delete("/categories/all", response_model=dict)
async def delete_all_categories():
    """
    Delete all categories from the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Delete all categories
                await cursor.execute("DELETE FROM categories")
                await conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete all categories: {str(e)}")

    return {"message": "All categories have been deleted successfully."}
