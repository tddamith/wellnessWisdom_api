from pydantic import BaseModel, Field
from datetime import datetime


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
    id: int = Field(..., description="Unique identifier for the subcategory")
    create_date: datetime = Field(..., description="Creation timestamp")
    update_date: datetime = Field(..., description="Last update timestamp")
