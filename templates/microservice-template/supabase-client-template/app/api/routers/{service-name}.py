"""
Main router for {service-name} service.

This module defines the REST API endpoints for the {service-name} service,
including CRUD operations and specialized business logic endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query, Path
from pydantic import UUID4
import logging

from app.api.schemas import (
    {ServiceName}Create,
    {ServiceName}Update,
    {ServiceName}Response,
    {ServiceName}ListResponse,
    ErrorResponse
)
from app.api.dependencies import (
    {ServiceName}ServiceDep,
    CurrentUserIdDep,
    CurrentUserDep
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/{service-name}",
    tags=["{service-name}"],
    responses={{
        404: {{"model": ErrorResponse, "description": "Not found"}},
        500: {{"model": ErrorResponse, "description": "Internal server error"}}
    }}
)


@router.post(
    "/",
    response_model={ServiceName}Response,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new {service-name} record",
    description="Create a new {service-name} record for the authenticated user."
)
async def create_{service_name}(
    {service_name}_data: {ServiceName}Create,
    service: {ServiceName}ServiceDep,
    current_user_id: CurrentUserIdDep
) -> {ServiceName}Response:
    """
    Create a new {service-name} record.
    
    - **{service_name}_data**: The {service-name} data to create
    - **Returns**: The created {service-name} record
    """
    try:
        result = await service.create_{service_name}(
            user_id=current_user_id,
            {service_name}_data={service_name}_data.model_dump()
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create {service-name} record"
            )
        
        return {ServiceName}Response.from_entity(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating {service-name}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/",
    response_model={ServiceName}ListResponse,
    summary="Get user's {service-name} records",
    description="Retrieve all {service-name} records for the authenticated user with optional pagination."
)
async def get_user_{service_name}_records(
    service: {ServiceName}ServiceDep,
    current_user_id: CurrentUserIdDep,
    limit: Optional[int] = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: Optional[int] = Query(default=0, ge=0, description="Number of records to skip")
) -> {ServiceName}ListResponse:
    """
    Get all {service-name} records for the authenticated user.
    
    - **limit**: Maximum number of records to return (1-1000)
    - **offset**: Number of records to skip for pagination
    - **Returns**: List of {service-name} records
    """
    try:
        records = await service.get_user_{service_name}_records(
            user_id=current_user_id,
            limit=limit,
            offset=offset
        )
        
        return {ServiceName}ListResponse(
            records=[{ServiceName}Response.from_entity(record) for record in records],
            total=len(records),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error retrieving {service-name} records: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{{record_id}}",
    response_model={ServiceName}Response,
    summary="Get specific {service-name} record",
    description="Retrieve a specific {service-name} record by ID."
)
async def get_{service_name}_record(
    record_id: UUID4 = Path(..., description="The ID of the {service-name} record"),
    service: {ServiceName}ServiceDep,
    current_user_id: CurrentUserIdDep
) -> {ServiceName}Response:
    """
    Get a specific {service-name} record by ID.
    
    - **record_id**: The ID of the {service-name} record to retrieve
    - **Returns**: The {service-name} record
    """
    try:
        record = await service.get_{service_name}_by_id(
            record_id=str(record_id),
            user_id=current_user_id
        )
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{ServiceName} record not found"
            )
        
        return {ServiceName}Response.from_entity(record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving {service-name} record {{record_id}}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put(
    "/{{record_id}}",
    response_model={ServiceName}Response,
    summary="Update {service-name} record",
    description="Update a specific {service-name} record."
)
async def update_{service_name}_record(
    record_id: UUID4 = Path(..., description="The ID of the {service-name} record"),
    {service_name}_data: {ServiceName}Update = ...,
    service: {ServiceName}ServiceDep,
    current_user_id: CurrentUserIdDep
) -> {ServiceName}Response:
    """
    Update a {service-name} record.
    
    - **record_id**: The ID of the {service-name} record to update
    - **{service_name}_data**: The updated {service-name} data
    - **Returns**: The updated {service-name} record
    """
    try:
        # First check if record exists and belongs to user
        existing_record = await service.get_{service_name}_by_id(
            record_id=str(record_id),
            user_id=current_user_id
        )
        
        if not existing_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{ServiceName} record not found"
            )
        
        # Update the record
        updated_record = await service.update_{service_name}(
            record_id=str(record_id),
            user_id=current_user_id,
            update_data={service_name}_data.model_dump(exclude_unset=True)
        )
        
        if not updated_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update {service-name} record"
            )
        
        return {ServiceName}Response.from_entity(updated_record)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating {service-name} record {{record_id}}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete(
    "/{{record_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete {service-name} record",
    description="Delete a specific {service-name} record."
)
async def delete_{service_name}_record(
    record_id: UUID4 = Path(..., description="The ID of the {service-name} record"),
    service: {ServiceName}ServiceDep,
    current_user_id: CurrentUserIdDep
):
    """
    Delete a {service-name} record.
    
    - **record_id**: The ID of the {service-name} record to delete
    """
    try:
        # First check if record exists and belongs to user
        existing_record = await service.get_{service_name}_by_id(
            record_id=str(record_id),
            user_id=current_user_id
        )
        
        if not existing_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{ServiceName} record not found"
            )
        
        # Delete the record
        success = await service.delete_{service_name}(
            record_id=str(record_id),
            user_id=current_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete {service-name} record"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting {service-name} record {{record_id}}: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Check if the {service-name} service is healthy and can connect to the database."
)
async def health_check(service: {ServiceName}ServiceDep):
    """
    Health check endpoint for the {service-name} service.
    
    Returns:
        dict: Service health status
    """
    try:
        # Perform basic health checks
        is_healthy = await service.health_check()
        
        if not is_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is unhealthy"
            )
        
        return {{
            "status": "healthy",
            "service": "{service-name}",
            "timestamp": "{{datetime.utcnow().isoformat()}}Z"
        }}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check error: {{e}}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy"
        )
