from fastapi import APIRouter, HTTPException
from datetime import datetime
from uuid import uuid4
from app.db.database import mysql
from app.api.v1.schemas import CategoryCreate, CategoryResponse, SubCategoryCreate, SubCategoryResponse

router = APIRouter()

@router.post("/subcategories/", response_model=SubCategoryResponse)
async def create_subcategory(subcategory: SubCategoryCreate):
    sub_category_id = str(uuid4())
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # Check if parent category exists
            await cursor.execute("SELECT id FROM categories WHERE id=%s", (subcategory.category_id,))
            category = await cursor.fetchone()
            if not category:
                raise HTTPException(status_code=404, detail="Parent category not found")

            # Insert new subcategory
            await cursor.execute("""
                INSERT INTO subcategories (id, name, category_id, no_of_articles, order_no, icon_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                sub_category_id,
                subcategory.name,
                subcategory.category_id,
                subcategory.no_of_articles,
                subcategory.order_no,
                subcategory.icon_name
            ))
            await conn.commit()

            # Fetch the created subcategory
            await cursor.execute("SELECT * FROM subcategories ORDER BY id DESC LIMIT 1")
            result = await cursor.fetchone()

            return {
                "id": result[0],                # Subcategory ID
                "name": result[1],              # Subcategory name
                "category_id": result[2],       # Parent category ID
                "no_of_articles": result[5],    # Number of articles
                "order_no": result[6],          # Display order
                "icon_name": result[7],         # Icon name
                "create_date": result[3],       # Creation timestamp
                "update_date": result[4],       # Update timestamp
            }

@router.post("/subcategories/bulk_upload", response_model=dict)
async def bulk_upload_subcategories(subcategories: list[SubCategoryCreate]):
    """
    Bulk upload subcategories into the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Validate parent categories for all subcategories
                category_ids = {subcategory.category_id for subcategory in subcategories}
                await cursor.execute(
                    "SELECT id FROM categories WHERE id IN %s",
                    (tuple(category_ids),)
                )
                existing_category_ids = {row[0] for row in await cursor.fetchall()}
                missing_categories = category_ids - existing_category_ids
                if missing_categories:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Parent categories not found for IDs: {', '.join(missing_categories)}"
                    )

                # Prepare bulk insert data
                data_to_insert = [
                    (
                        subcategory.name,
                        subcategory.category_id,
                        subcategory.no_of_articles,
                        subcategory.order_no,
                        subcategory.icon_name
                    )
                    for subcategory in subcategories
                ]

                # Insert subcategories into the database
                await cursor.executemany("""
                    INSERT INTO subcategories (name, category_id, no_of_articles, order_no, icon_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, data_to_insert)
                await conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to upload subcategories: {str(e)}")

    return {"message": f"Successfully uploaded {len(subcategories)} subcategories."}

@router.delete("/subcategories/all", response_model=dict)
async def delete_all_subcategories():
    """
    Delete all subcategories from the database.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Delete all subcategories
                await cursor.execute("DELETE FROM subcategories")
                await conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete all subcategories: {str(e)}")

    return {"message": "All subcategories have been deleted successfully."}

@router.get("/categories_with_subcategories/")
async def get_categories_with_subcategories():
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            # SQL Query to join categories and subcategories
            await cursor.execute("""
                SELECT
                    c.id AS category_id,
                    c.name AS category_name,
                    c.create_date AS category_create_date,
                    c.update_date AS category_update_date,
                    c.no_of_articles AS category_no_of_articles,
                    c.order_no AS category_order_no,
                    c.icon_name AS category_icon_name,
                    s.id AS subcategory_id,
                    s.name AS subcategory_name,
                    s.category_id AS subcategory_category_id,
                    s.create_date AS subcategory_create_date,
                    s.update_date AS subcategory_update_date,
                    s.no_of_articles AS subcategory_no_of_articles,
                    s.order_no AS subcategory_order_no,
                    s.icon_name AS subcategory_icon_name
                FROM categories c
                LEFT JOIN subcategories s ON c.id = s.category_id
            """)
            result = await cursor.fetchall()

    # Organize the data into a dictionary for categories and their subcategories
    category_dict = {}
    for row in result:
        category_id = row[0]
        if category_id not in category_dict:
            category_dict[category_id] = {
                "id": row[0],
                "name": row[1],
                "create_date": row[2],
                "update_date": row[3],
                "no_of_articles": row[4],
                "order_no": row[5],
                "icon_name": row[6],
                "subcategories": []
            }
        if row[7]:  # Check if the subcategory exists (LEFT JOIN may return NULL)
            category_dict[category_id]["subcategories"].append({
                "id": row[7],
                "name": row[8],
                "category_id": row[9],
                "create_date": row[10],
                "update_date": row[11],
                "no_of_articles": row[12],
                "order_no": row[13],
                "icon_name": row[14],
            })

    return list(category_dict.values())

@router.put("/subcategories/update_ids", response_model=dict)
async def update_all_subcategory_ids():
    """
    Update all subcategory IDs with new UUID4 values.
    """
    async with mysql.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            try:
                # Fetch all current subcategories
                await cursor.execute("SELECT id FROM subcategories")
                subcategories = await cursor.fetchall()

                # Prepare the update queries
                updates = [(str(uuid4()), subcategory[0]) for subcategory in subcategories]

                # Execute batch updates
                await cursor.executemany("""
                    UPDATE subcategories
                    SET id = %s
                    WHERE id = %s
                """, updates)
                await conn.commit()

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update subcategory IDs: {str(e)}")

    return {"message": f"Successfully updated IDs for {len(subcategories)} subcategories."}
