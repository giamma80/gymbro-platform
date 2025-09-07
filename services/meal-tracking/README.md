# NutriFit Meal Tracking Service

## Overview

Il **Meal Tracking Service** gestisce il riconoscimento, logging e analisi nutrizionale dei pasti con **AI-powered food recognition** e integrazione OpenFoodFacts.

### Core Responsibilities
- 🍎 **Food Recognition**: AI image recognition via GPT-4V per identificazione alimenti
- 📊 **Nutritional Analysis**: Calcolo automatico valori nutrizionali da OpenFoodFacts DB
- 🍽️ **Meal Logging**: Tracking pasti con timestamp e porzioni precise
- 📱 **Mobile-First**: Foto upload e quick-add interfaces ottimizzate per smartphone
- 🔄 **Event Publishing**: Invio calorie events al Calorie Balance Service

> **📋 [API Development Roadmap](API-roadmap.md)** - Stato sviluppo API e integrazione roadmap  
> **Status**: 🚧 **IN DEVELOPMENT** | **v0.1.0** | **Foundation Phase**

## 🧠 AI-Powered Features

### Food Recognition Pipeline
```
📸 Photo Capture → 🤖 GPT-4V Analysis → 🔍 OpenFoodFacts Lookup → 📊 Nutritional Data → ⚖️ Calorie Event
```

### Recognition Capabilities
- **Visual Food Identification**: GPT-4V per riconoscimento ingredienti e porzioni
- **Italian Food Database**: Focus su cucina italiana via OpenFoodFacts
- **Portion Estimation**: AI-assisted portion size calculation
- **Custom Foods**: User-defined foods con nutritional data

## Architecture

Clean Architecture + Event-Driven Pattern:

```
app/
├── core/              # Configuration, database, shared utilities
├── domain/            # Food entities, meal models, nutrition values
├── application/       # Food recognition use cases, meal logging commands
├── infrastructure/    # OpenFoodFacts client, GPT-4V integration, file storage
└── api/              # REST endpoints for mobile, admin interfaces
```

## Domain Model

### Core Entities
- **Food**: Prodotto alimentare con valori nutrizionali
- **Meal**: Pasto con timestamp e lista di food items
- **Portion**: Quantità specifica di food con peso/volume
- **NutritionProfile**: Profilo nutrizionale dettagliato (calorie, macro, micro)
- **FoodPhoto**: Immagine per AI recognition con metadata

### Value Objects
- **NutritionValue**: Valore nutrizionale per 100g/100ml
- **PortionSize**: Dimensione porzione con unità di misura
- **RecognitionConfidence**: Score affidabilità AI (0.0-1.0)
- **FoodCategory**: Categoria alimentare per classificazione

## API Endpoints

### Health & Status
- `GET /health` - Basic health check
- `GET /health/ready` - Kubernetes readiness probe
- `GET /health/live` - Kubernetes liveness probe

### 🤖 AI Food Recognition
- `POST /api/v1/recognition/photo` - Upload photo for AI recognition 🚧
- `GET /api/v1/recognition/suggestions/{food_name}` - Get food suggestions 🚧
- `POST /api/v1/recognition/verify` - Verify AI recognition result 🚧
- `GET /api/v1/recognition/history/users/{user_id}` - Recognition history 🚧

### 🍽️ Meal Management
- `POST /api/v1/meals/users/{user_id}` - Create meal entry 🚧
- `GET /api/v1/meals/users/{user_id}/today` - Get today's meals 🚧
- `PUT /api/v1/meals/{meal_id}` - Update meal 🚧
- `DELETE /api/v1/meals/{meal_id}` - Delete meal 🚧
- `GET /api/v1/meals/users/{user_id}/history` - Meal history 🚧

### 🍎 Food Database
- `GET /api/v1/foods/search` - Search foods in database 🚧
- `GET /api/v1/foods/{food_id}` - Get food details 🚧
- `POST /api/v1/foods/custom` - Add custom food 🚧
- `GET /api/v1/foods/categories` - Get food categories 🚧
- `GET /api/v1/foods/popular` - Get popular foods 🚧

### 📊 Nutritional Analysis
- `GET /api/v1/nutrition/users/{user_id}/daily` - Daily nutrition summary 🚧
- `GET /api/v1/nutrition/users/{user_id}/weekly` - Weekly nutrition trends 🚧
- `POST /api/v1/nutrition/analyze` - Analyze custom food combination 🚧
- `GET /api/v1/nutrition/recommendations/users/{user_id}` - Nutrition recommendations 🚧

### 🔄 Integration Events
- `POST /api/v1/events/calorie-consumed` - Send calorie event to balance service 🚧
- `GET /api/v1/events/status` - Check integration status 🚧

## Database Schema

### Core Tables (Planned)
- **`foods`** - OpenFoodFacts synchronized food database
- **`meals`** - User meal entries con timestamp
- **`meal_items`** - Food items dentro ogni meal con porzioni
- **`food_photos`** - AI recognition photos con metadata
- **`nutrition_profiles`** - Detailed nutritional information per food
- **`custom_foods`** - User-defined foods non in OpenFoodFacts
- **`recognition_logs`** - AI recognition attempts per miglioramento accuracy

### Performance Views (Planned)
- **`daily_nutrition_summary`** - Aggregazioni giornaliere valori nutrizionali
- **`popular_foods`** - Most logged foods per suggestions
- **`user_food_preferences`** - Learning pattern per personalizzazione

## External Integrations

### 🤖 AI Services
- **OpenAI GPT-4V**: Food image recognition e portion estimation
- **OpenFoodFacts API**: Database nutrizionale globale con focus italiano
- **Custom ML Models**: Porzione estimation fine-tuned per cucina italiana

### 📱 Mobile Integration
- **Camera Integration**: Native photo capture con preprocessing
- **Quick Add Interface**: Barcode scanning + voice input
- **Offline Mode**: Cached food data per usage senza connessione
- **Sync Service**: Batch upload when connection restored

### 🔄 Microservices Integration
- **Calorie Balance Service**: Real-time calorie events publishing
- **AI Coach Service**: Meal data for nutritional coaching insights
- **Health Monitor Service**: Nutrition data correlation con health metrics
- **Notifications Service**: Meal reminders e nutrition alerts

## Development Roadmap

### Phase 1: Foundation (Current)
- [ ] Setup service structure con Clean Architecture
- [ ] Database schema design e migration scripts
- [ ] Basic REST API skeleton
- [ ] OpenFoodFacts integration per food lookup
- [ ] Simple manual meal logging

### Phase 2: AI Integration
- [ ] GPT-4V integration per food photo recognition
- [ ] Portion estimation algorithms
- [ ] Recognition confidence scoring
- [ ] Custom food creation workflow

### Phase 3: Mobile Optimization
- [ ] Optimized photo upload endpoints
- [ ] Batch sync APIs per offline support
- [ ] Quick-add interfaces (barcode, voice)
- [ ] Real-time nutrition summaries

### Phase 4: Intelligence Features
- [ ] Meal pattern learning
- [ ] Personalized food suggestions
- [ ] Nutrition goal integration
- [ ] Advanced analytics e reporting

## Setup & Development

### Prerequisites
- Python 3.11+
- Poetry
- PostgreSQL (via Supabase)
- OpenAI API key per GPT-4V
- OpenFoodFacts API access

### Local Development
```bash
# Install dependencies
poetry install

# Setup environment
cp .env.example .env

# Create database schema
poetry run python create_tables_direct.py

# Start development server
poetry run uvicorn app.main:app --reload --port 8002
```

### Testing
```bash
# Run all tests
poetry run pytest

# Test AI recognition (requires API keys)
poetry run pytest tests/ai/

# Test OpenFoodFacts integration
poetry run pytest tests/integration/
```

## Performance Considerations

### AI Recognition Optimization
- **Image Preprocessing**: Resize e compression prima dell'upload
- **Batch Recognition**: Multiple foods in single photo
- **Confidence Thresholds**: Fallback to manual entry for low confidence
- **Caching**: OpenFoodFacts data cached locally per performance

### Mobile Performance
- **Progressive Image Upload**: Thumbnail first, full resolution on demand
- **Predictive Caching**: Pre-load popular foods per user patterns
- **Quick Actions**: One-tap logging per frequently consumed foods
- **Background Sync**: Upload in background per user experience

---

## 🍎 Technology Stack

**Core**: FastAPI + SQLAlchemy + Supabase + Redis  
**AI**: OpenAI GPT-4V + Custom ML models  
**External APIs**: OpenFoodFacts + Barcode scanning services  
**Storage**: Supabase Storage per food photos  
**Architecture**: Clean Architecture + Event-Driven + Domain-Driven Design

---

**Status**: 🚧 **Foundation Phase** - Core structure e database design in progress  
**Next Milestone**: OpenFoodFacts integration + Basic meal logging  
**AI Integration**: Planned for Phase 2 development
