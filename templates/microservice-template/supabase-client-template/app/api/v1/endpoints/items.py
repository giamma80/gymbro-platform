"""
Items Endpoints - Supabase Client Template
Service: {service-name}

Example CRUD endpoints using Supabase client.
Replace 'items' with your actual domain entity.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import uuid

from app.core.database import SupabaseRepository
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()

# Pydantic models
class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    active: bool = Field(default=True)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    active: Optional[bool] = None

class ItemResponse(ItemBase):
    id: str
    created_at: str
    updated_at: Optional[str] = None

# Repository instance
items_repo = SupabaseRepository("items")

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Create a new item."""
    try:
        item_data = item.model_dump()
        item_data["id"] = str(uuid.uuid4())
        
        created_item = await items_repo.create(item_data)
        return ItemResponse(**created_item)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create item: {str(e)}")

@router.get("/", response_model=List[ItemResponse])
async def list_items(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: Optional[str] = Query(default=None),
    active: Optional[bool] = Query(default=None)
):
    """List items with optional filtering."""
    try:
        if category or active is not None:
            filters = {}
            if category:
                filters["category"] = category
            if active is not None:
                filters["active"] = active
            
            items = await items_repo.query(**filters)
        else:
            items = await items_repo.get_all(limit=limit, offset=offset)
        
        return [ItemResponse(**item) for item in items]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list items: {str(e)}")

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """Get item by ID."""
    try:
        item = await items_repo.get_by_id(item_id)
        
        if not item:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        return ItemResponse(**item)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get item: {str(e)}")

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: str, item_update: ItemUpdate):
    """Update item by ID."""
    try:
        # Check if item exists
        existing_item = await items_repo.get_by_id(item_id)
        if not existing_item:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        # Prepare update data (only non-None fields)
        update_data = {k: v for k, v in item_update.model_dump().items() if v is not None}
        
        if not update_data:
            raise ValidationError("No valid fields to update")
        
        updated_item = await items_repo.update(item_id, update_data)
        
        if not updated_item:
            raise HTTPException(status_code=500, detail="Update operation failed")
        
        return ItemResponse(**updated_item)
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update item: {str(e)}")

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """Delete item by ID."""
    try:
        # Check if item exists
        existing_item = await items_repo.get_by_id(item_id)
        if not existing_item:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        await items_repo.delete(item_id)
        
        return {"message": f"Item with ID {item_id} deleted successfully"}
        
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete item: {str(e)}")
