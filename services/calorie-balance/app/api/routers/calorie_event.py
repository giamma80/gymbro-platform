from fastapi import APIRouter, HTTPException
from app.api.schemas import CalorieEventCreate, CalorieEventRead
from uuid import uuid4
from datetime import datetime

router = APIRouter()

# In-memory store placeholder (replace with DB integration)
calorie_events_db = []

@router.post("/", response_model=CalorieEventRead, summary="Crea un evento calorico (consumed, burned, weight, batch)")
def create_calorie_event(event: CalorieEventCreate):
    event_id = str(uuid4())
    event_data = CalorieEventRead(
        id=event_id,
        user_id=event.user_id,
        event_type=event.event_type,
        calories=event.calories,
        weight_kg=event.weight_kg,
        timestamp=event.timestamp,
        notes=event.notes
    )
    calorie_events_db.append(event_data)
    return event_data

@router.post("/consumed", response_model=CalorieEventRead, summary="Registra calorie consumate")
def create_calorie_consumed(event: CalorieEventCreate):
    if event.event_type != "consumed":
        raise HTTPException(status_code=400, detail="event_type deve essere 'consumed'")
    return create_calorie_event(event)

@router.post("/burned", response_model=CalorieEventRead, summary="Registra calorie bruciate")
def create_calorie_burned(event: CalorieEventCreate):
    if event.event_type != "burned":
        raise HTTPException(status_code=400, detail="event_type deve essere 'burned'")
    return create_calorie_event(event)

@router.post("/weight", response_model=CalorieEventRead, summary="Registra peso")
def create_weight_event(event: CalorieEventCreate):
    if event.event_type != "weight":
        raise HTTPException(status_code=400, detail="event_type deve essere 'weight'")
    return create_calorie_event(event)

@router.post("/batch", response_model=list[CalorieEventRead], summary="Registra batch di eventi calorici")
def create_batch_events(events: list[CalorieEventCreate]):
    result = []
    for event in events:
        result.append(create_calorie_event(event))
    return result
