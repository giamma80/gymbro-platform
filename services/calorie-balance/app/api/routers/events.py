"""
Events API Router - Calorie Balance Service

🔥 HIGH-FREQUENCY ENDPOINTS - Core of event-driven architecture
Priority 1 APIs from roadmap for mobile calorie tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, date as DateType
from decimal import Decimal
from uuid import UUID
import logging

# Pydantic models for request/response
from pydantic import BaseModel, Field, validator

# Domain entities and services  
from app.domain.entities import CalorieEvent, EventType, EventSource
from app.application.services import CalorieEventService

# Dependencies
from app.core.dependencies import get_calorie_event_service, get_current_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/calorie-event", tags=["calorie-events"])


# =============================================================================
# REQUEST/RESPONSE MODELS - API Schemas
# =============================================================================

class CalorieConsumedRequest(BaseModel):
    """Request model for calorie consumption events."""
    calories: Decimal = Field(..., gt=0, le=3000, description="Calories consumed")
    source: EventSource = Field(EventSource.MANUAL, description="Data source")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (UTC)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    @validator('calories')
    def validate_calories(cls, v):
        """Validate calorie range for consumption."""
        if v <= 0:
            raise ValueError('Calories must be positive')
        if v > 3000:
            raise ValueError('Single meal cannot exceed 3000 calories')
        return v


class CalorieBurnedRequest(BaseModel):
    """Request model for calorie burn events."""
    calories: Decimal = Field(..., gt=0, le=2000, description="Calories burned")
    source: EventSource = Field(EventSource.FITNESS_TRACKER, description="Data source")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (UTC)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    @validator('calories')
    def validate_calories(cls, v):
        """Validate calorie range for burns."""
        if v <= 0:
            raise ValueError('Calories must be positive')
        if v > 2000:
            raise ValueError('Single exercise session cannot exceed 2000 calories')
        return v


class WeightMeasurementRequest(BaseModel):
    """Request model for weight measurement events."""
    weight_kg: Decimal = Field(..., gt=20, lt=500, description="Weight in kilograms")
    source: EventSource = Field(EventSource.SMART_SCALE, description="Data source") 
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (UTC)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    @validator('weight_kg')
    def validate_weight(cls, v):
        """Validate weight range."""
        if v < 20:
            raise ValueError('Weight must be at least 20kg')
        if v > 500:
            raise ValueError('Weight cannot exceed 500kg')
        return v


class BatchEventRequest(BaseModel):
    """Request model for batch event recording."""
    event_type: EventType = Field(..., description="Type of events")
    events: List[Dict[str, Any]] = Field(
        ..., min_items=1, max_items=100, description="Event data list"
    )
    
    @validator('events')
    def validate_events(cls, v):
        """Validate event batch size."""
        if len(v) > 100:
            raise ValueError('Cannot batch more than 100 events at once')
        return v


class CalorieEventResponse(BaseModel):
    """Response model for calorie events."""
    id: UUID
    user_id: UUID
    event_type: EventType
    event_timestamp: datetime
    value: Decimal
    source: EventSource
    confidence_score: Decimal
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    """Response model for timeline queries."""
    events: List[CalorieEventResponse]
    total_count: int
    date_range: Dict[str, str]
    summary: Dict[str, Any]


# =============================================================================
# PRIORITY 1 ENDPOINTS - Mobile-Optimized Event Recording
# =============================================================================

@router.post("/consumed", response_model=CalorieEventResponse, status_code=status.HTTP_201_CREATED)
async def record_calorie_consumed(
    request: CalorieConsumedRequest,
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> CalorieEventResponse:
    """
    📱 MOBILE PRIORITY 1A - Record calorie consumption event
    
    High-frequency endpoint optimized for mobile apps.
    Records food/drink calorie consumption with metadata support.
    """
    try:
        event = await service.record_calorie_consumed(
            user_id=user_id,
            calories=request.calories,
            source=request.source,
            metadata=request.metadata or {},
            timestamp=request.timestamp
        )
        
        return CalorieEventResponse.from_orm(event)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to record calorie consumed for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record calorie consumption"
        )


@router.post("/burned", response_model=CalorieEventResponse, status_code=status.HTTP_201_CREATED)
async def record_calorie_burned(
    request: CalorieBurnedRequest,
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> CalorieEventResponse:
    """
    🏃‍♂️ MOBILE PRIORITY 1A - Record calorie burn event
    
    Records exercise or activity calorie burns.
    Integrates with fitness trackers and manual entry.
    """
    try:
        event = await service.record_calorie_burned_exercise(
            user_id=user_id,
            calories=request.calories,
            source=request.source,
            metadata=request.metadata or {},
            timestamp=request.timestamp
        )
        
        return CalorieEventResponse.from_orm(event)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to record calorie burned for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record calorie burn"
        )


@router.post("/weight", response_model=CalorieEventResponse, status_code=status.HTTP_201_CREATED)
async def record_weight_measurement(
    request: WeightMeasurementRequest,
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> CalorieEventResponse:
    """
    ⚖️ MOBILE PRIORITY 1A - Record weight measurement
    
    Records weight measurements from smart scales or manual entry.
    Updates user profile and triggers metabolic recalculation.
    """
    try:
        event = await service.record_weight_measurement(
            user_id=user_id,
            weight_kg=request.weight_kg,
            source=request.source,
            metadata=request.metadata or {},
            timestamp=request.timestamp
        )
        
        return CalorieEventResponse.from_orm(event)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to record weight for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record weight measurement"
        )


# =============================================================================
# BATCH OPERATIONS - Mobile Sync Optimization
# =============================================================================

@router.post("/batch", response_model=List[CalorieEventResponse], status_code=status.HTTP_201_CREATED)
async def batch_record_events(
    request: BatchEventRequest,
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> List[CalorieEventResponse]:
    """
    📦 MOBILE PRIORITY 1B - Batch record events for offline sync
    
    Optimized for mobile offline sync scenarios.
    Processes multiple events in a single transaction.
    """
    try:
        events = await service.batch_record_events(
            user_id=user_id,
            events_data=request.events
        )
        
        return [CalorieEventResponse.from_orm(event) for event in events]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to batch record events for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process batch events"
        )


# =============================================================================
# TIMELINE AND HISTORY - Event Retrieval
# =============================================================================

@router.get("/timeline", response_model=TimelineResponse)
async def get_event_timeline(
    limit: int = Query(100, ge=1, le=500, description="Number of events to return"),
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> TimelineResponse:
    """
    📅 PRIORITY 1C - Get user event timeline
    
    Returns recent events for timeline display in mobile app.
    Optimized for infinite scroll and pull-to-refresh.
    """
    try:
        events = await service.get_recent_timeline(user_id, limit)
        
        # Calculate summary statistics
        summary = {
            "total_events": len(events),
            "consumed_events": len([e for e in events if e.event_type == EventType.CONSUMED]),
            "burned_events": len([e for e in events if e.event_type == EventType.BURNED_EXERCISE]),
            "weight_events": len([e for e in events if e.event_type == EventType.WEIGHT]),
        }
        
        if events:
            date_range = {
                "earliest": events[-1].event_timestamp.isoformat(),
                "latest": events[0].event_timestamp.isoformat()
            }
        else:
            date_range = {"earliest": "", "latest": ""}
        
        return TimelineResponse(
            events=[CalorieEventResponse.from_orm(event) for event in events],
            total_count=len(events),
            date_range=date_range,
            summary=summary
        )
        
    except Exception as e:
        logger.error(f"Failed to get timeline for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event timeline"
        )


@router.get("/history", response_model=List[CalorieEventResponse])
async def get_events_by_date_range(
    start_date: DateType = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: DateType = Query(..., description="End date (YYYY-MM-DD)"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    user_id: str = Depends(get_current_user_id),
    service: CalorieEventService = Depends(get_calorie_event_service)
) -> List[CalorieEventResponse]:
    """
    📊 PRIORITY 1C - Get events by date range
    
    Returns events for specific date range with optional type filtering.
    Used for analytics, reports, and historical data visualization.
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before or equal to end date"
            )
        
        # Limit date range to prevent large queries
        date_diff = (end_date - start_date).days
        if date_diff > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )
        
        events = await service.get_events_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return [CalorieEventResponse.from_orm(event) for event in events]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get events history for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve event history"
        )


# =============================================================================
# HEALTH CHECK AND METRICS
# =============================================================================

@router.get("/health", include_in_schema=False)
async def health_check() -> Dict[str, str]:
    """Health check for event service."""
    return {"status": "healthy", "service": "calorie-events"}


@router.get("/metrics", include_in_schema=False)
async def get_service_metrics(
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Get service metrics for monitoring."""
    try:
        # This would typically query monitoring/metrics store
        return {
            "user_id": user_id,
            "service": "calorie-events",
            "endpoints_active": 6,
            "last_activity": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        return {"error": "metrics unavailable"}