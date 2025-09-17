"""
Entity Management API Endpoints
===============================
Template for CRUD operations on main entities for calorie-balance service.

This file contains the REST API endpoints for managing the primary 
entities of this microservice. Customize the entity models and
operations based on your service's domain.

Example entities:
- Calorie balance service: Calorie events, goals, daily balances
- Meal tracking service: Meals, recipes, ingredients
- Analytics service: Reports, metrics, insights
"""

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.database import get_supabase_client

settings = get_settings()
logger = structlog.get_logger()
router = APIRouter(prefix="/{service-name-kebab}", tags=["calorie-balance Entities"])


# ============================================================================
# MODELS (Customize these based on your service domain)
# ============================================================================


class EntityBase(BaseModel):
    """Base entity model."""

    name: str = Field(..., description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")


class EntityCreate(EntityBase):
    """Entity creation model."""

    pass


class EntityUpdate(BaseModel):
    """Entity update model."""

    name: Optional[str] = Field(None, description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")


class EntityResponse(EntityBase):
    """Entity response model."""

    id: str = Field(..., description="Entity ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Update timestamp")


# ============================================================================
# API ENDPOINTS (Customize these based on your service domain)
# ============================================================================


@router.get("/", response_model=List[EntityResponse])
async def list_entities(
    limit: int = Query(10, ge=1, le=100, description="Number of entities to return"),
    offset: int = Query(0, ge=0, description="Number of entities to skip"),
    search: Optional[str] = Query(None, description="Search term"),
) -> List[EntityResponse]:
    """
    List entities with pagination and optional search.

    Customize this endpoint based on your service's main entities.
    """
    try:
        supabase = get_supabase_client()

        # Build query (customize table name and fields)
        query = supabase.table("entities").select("*")

        if search:
            query = query.ilike("name", f"%{search}%")

        # Execute query with pagination
        result = query.range(offset, offset + limit - 1).execute()

        logger.info("Entities listed", count=len(result.data))
        return result.data

    except Exception as e:
        logger.error("Failed to list entities", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list entities")


@router.post("/", response_model=EntityResponse, status_code=201)
async def create_entity(entity: EntityCreate) -> EntityResponse:
    """
    Create a new entity.

    Customize this endpoint based on your service's main entities.
    """
    try:
        supabase = get_supabase_client()

        # Insert entity (customize table name and fields)
        result = supabase.table("entities").insert(entity.model_dump()).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create entity")

        created_entity = result.data[0]
        logger.info("Entity created", entity_id=created_entity["id"])
        return created_entity

    except Exception as e:
        logger.error("Failed to create entity", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create entity")


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str = Path(..., description="Entity ID")
) -> EntityResponse:
    """
    Get a specific entity by ID.

    Customize this endpoint based on your service's main entities.
    """
    try:
        supabase = get_supabase_client()

        # Get entity (customize table name and fields)
        result = supabase.table("entities").select("*").eq("id", entity_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Entity not found")

        entity = result.data[0]
        logger.info("Entity retrieved", entity_id=entity_id)
        return entity

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get entity", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get entity")


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str = Path(..., description="Entity ID"),
    entity_update: EntityUpdate = ...,
) -> EntityResponse:
    """
    Update a specific entity.

    Customize this endpoint based on your service's main entities.
    """
    try:
        supabase = get_supabase_client()

        # Update entity (customize table name and fields)
        update_data = {
            k: v for k, v in entity_update.model_dump().items() if v is not None
        }

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        result = (
            supabase.table("entities").update(update_data).eq("id", entity_id).execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Entity not found")

        updated_entity = result.data[0]
        logger.info("Entity updated", entity_id=entity_id)
        return updated_entity

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update entity", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update entity")


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(entity_id: str = Path(..., description="Entity ID")) -> None:
    """
    Delete a specific entity.

    Customize this endpoint based on your service's main entities.
    """
    try:
        supabase = get_supabase_client()

        # Delete entity (customize table name)
        result = supabase.table("entities").delete().eq("id", entity_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Entity not found")

        logger.info("Entity deleted", entity_id=entity_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete entity", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete entity")


# ============================================================================
# CUSTOM ENDPOINTS (Add your service-specific endpoints here)
# ============================================================================


@router.get("/{entity_id}/custom-action", response_model=Dict[str, Any])
async def custom_entity_action(
    entity_id: str = Path(..., description="Entity ID"),
) -> Dict[str, Any]:
    """
    Example custom endpoint for entity-specific actions.

    Replace this with your service-specific operations:
    - User service: /users/{user_id}/profile, /users/{user_id}/settings
    - Meal service: /meals/{meal_id}/nutrition, /meals/{meal_id}/recipes
    - Analytics service: /reports/{report_id}/generate, /metrics/{metric_id}/calculate
    """
    try:
        # Implement your custom logic here
        logger.info("Custom action performed", entity_id=entity_id)

        return {
            "entity_id": entity_id,
            "action": "custom-action",
            "result": "success",
            "message": "Custom action completed successfully",
        }

    except Exception as e:
        logger.error("Custom action failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail="Custom action failed")
