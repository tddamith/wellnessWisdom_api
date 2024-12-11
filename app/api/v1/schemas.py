from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the category")
    no_of_articles: int = Field(0, description="Number of articles in the category")
    order_no: int = Field(0, description="Order of the category for display")
    icon_name: str | None = Field(
        None, max_length=255, description="Icon name or path for the category"
    )


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryResponse(CategoryBase):
    id: str = Field(..., description="Unique identifier for the category")
    create_date: datetime = Field(..., description="Creation timestamp")
    update_date: datetime = Field(..., description="Last update timestamp")


class SubCategoryBase(BaseModel):
    name: str = Field(..., max_length=255, description="Name of the subcategory")
    category_id: str = Field(..., description="ID of the parent category")
    no_of_articles: int = Field(0, description="Number of articles in the subcategory")
    order_no: int = Field(0, description="Order of the subcategory for display")
    icon_name: str | None = Field(
        None, max_length=255, description="Icon name or path for the subcategory"
    )


class SubCategoryCreate(SubCategoryBase):
    """Schema for creating a new subcategory."""
    pass


class SubCategoryResponse(SubCategoryBase):
    id: str = Field(..., description="Unique identifier for the subcategory")  # Update to str
    name: str = Field(..., max_length=255, description="Name of the subcategory")
    category_id: str = Field(..., description="ID of the parent category")
    create_date: datetime = Field(..., description="Creation timestamp")
    update_date: datetime = Field(..., description="Last update timestamp")
    no_of_articles: int = Field(0, description="Number of articles in the subcategory")
    order_no: int = Field(0, description="Order of the subcategory for display")
    icon_name: str | None = Field(
         None, max_length=255, description="Icon name or path for the subcategory"
     )


# Article Schemas
class ArticleBase(BaseModel):
    title: str = Field(..., max_length=255, description="Title of the article")
    content: str = Field(..., description="Content of the article")
    author: Optional[str] = Field(None, max_length=255, description="Author of the article")
    category_id: Optional[str] = Field(None, description="ID of the category associated with the article")
    sub_category_id: Optional[str] = Field(None, description="ID of the subcategory associated with the article")
    image_url: Optional[str] = Field(None, max_length=255, description="URL of the article's featured image")
    is_published: bool = Field(False, description="Publication status of the article")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the article")


class ArticleCreate(ArticleBase):
    """Schema for creating a new article."""
    pass


class ArticleResponse(ArticleBase):
    id: str = Field(..., description="Unique identifier for the article")
    create_date: datetime = Field(..., description="Creation timestamp")
    update_date: datetime = Field(..., description="Last update timestamp")
    views: int = Field(0, description="Number of views for the article")
