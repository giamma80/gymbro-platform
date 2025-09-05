# API Roadmap - Calorie Balance Service

> **Status del microservizio**: 🟡 **In Development** - Core API implementate, Analytics in fase di sviluppo  
> **Versione attuale**: v1.0.0  
> **Ultimo aggiornamento**: 5 settembre 2025

## 📊 Overview dello Stato

| Categoria | Implementate | Totali | Completamento |
|-----------|--------------|--------|---------------|
| **Health & Status** | 3 | 3 | 🟢 100% |
| **User Management** | 3 | 5 | 🟡 60% |
| **Calorie Goals** | 2 | 6 | 🟡 33% |
| **Daily Balance** | 4 | 7 | 🟡 57% |
| **Analytics & Trends** | 0 | 4 | 🔴 0% |
| **Metabolic Profiles** | 0 | 3 | 🔴 0% |
| **Advanced Features** | 0 | 3 | 🔴 0% |
| **TOTALE** | **12** | **31** | **🟡 39%** |

---

## 🔗 API Endpoints Roadmap

### 🏥 Health & Status
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/health/` | GET | ✅ **FATTO** | P0 | Basic health check |
| `/health/ready` | GET | ✅ **FATTO** | P0 | Kubernetes readiness |
| `/health/live` | GET | ✅ **FATTO** | P0 | Kubernetes liveness |

### 👤 User Management
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/` | POST | ✅ **FATTO** | P0 | Create user profile |
| `/api/v1/users/{user_id}` | GET | ✅ **FATTO** | P0 | Get user profile |
| `/api/v1/users/{user_id}` | PUT | ✅ **FATTO** | P0 | Update user profile |
| `/api/v1/users/{user_id}` | DELETE | ❌ **TODO** | P2 | Delete user profile |
| `/api/v1/users/` | GET | ❌ **TODO** | P3 | List users (admin) |

### 🎯 Calorie Goals
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/goals/users/{user_id}` | POST | ✅ **FATTO** | P0 | Create calorie goal |
| `/api/v1/goals/users/{user_id}/active` | GET | ✅ **FATTO** | P0 | Get active goal |
| `/api/v1/goals/users/{user_id}/goals/{goal_id}` | PUT | ❌ **TODO** | P1 | Update specific goal |
| `/api/v1/goals/users/{user_id}/goals/{goal_id}` | DELETE | ❌ **TODO** | P1 | Delete goal |
| `/api/v1/goals/users/{user_id}/history` | GET | ❌ **TODO** | P2 | Goals history |
| `/api/v1/goals/users/{user_id}/goals` | GET | ❌ **TODO** | P2 | List all user goals |

### ⚖️ Daily Balance
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/balance/users/{user_id}` | PUT | ✅ **FATTO** | P0 | Update daily balance |
| `/api/v1/balance/users/{user_id}/date/{date}` | GET | ✅ **FATTO** | P0 | Get balance for date |
| `/api/v1/balance/users/{user_id}/today` | GET | ✅ **FATTO** | P0 | Get today's balance |
| `/api/v1/balance/users/{user_id}/progress` | POST | ✅ **FATTO** | P0 | Get progress data |
| `/api/v1/balance/users/{user_id}/summary/weekly` | GET | ❌ **TODO** | P1 | Weekly summary |
| `/api/v1/balance/users/{user_id}/summary/monthly` | GET | ❌ **TODO** | P1 | Monthly summary |
| `/api/v1/balance/users/{user_id}/range` | GET | ❌ **TODO** | P2 | Custom date range |

### 📊 Analytics & Trends
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/trends` | GET | ❌ **TODO** | P1 | Weekly/monthly trends |
| `/api/v1/users/{user_id}/insights` | GET | ❌ **TODO** | P1 | AI-powered insights |
| `/api/v1/users/{user_id}/analytics/weight` | GET | ❌ **TODO** | P2 | Weight trend analysis |
| `/api/v1/users/{user_id}/analytics/performance` | GET | ❌ **TODO** | P2 | Goal performance metrics |

### 🧬 Metabolic Profiles
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/profile/metabolic` | GET | ❌ **TODO** | P1 | Get metabolic profile |
| `/api/v1/users/{user_id}/profile/metabolic` | PUT | ❌ **TODO** | P1 | Update metabolic profile |
| `/api/v1/users/{user_id}/profile/metabolic/calculate` | POST | ❌ **TODO** | P2 | Recalculate BMR/TDEE |

### 🏆 Advanced Features
| Endpoint | Metodo | Status | Priorità | Note |
|----------|--------|--------|----------|------|
| `/api/v1/users/{user_id}/streaks` | GET | ❌ **TODO** | P2 | Calorie goal streaks |
| `/api/v1/users/{user_id}/challenges` | GET | ❌ **TODO** | P3 | User challenges |
| `/api/v1/users/{user_id}/badges` | GET | ❌ **TODO** | P3 | Achievement badges |

---

## 🎯 Priorità di Sviluppo

### **P0 - Critical (Completato ✅)**
Funzionalità base per MVP funzionante:
- ✅ Health checks
- ✅ User CRUD base
- ✅ Goals creation/retrieval
- ✅ Daily balance tracking

### **P1 - High Priority (Prossimi Sprint)**
Funzionalità essenziali per user experience completa:
1. **Analytics & Trends** (`/trends`, `/insights`) - **Priority 1A**
2. **Metabolic Profiles** - **Priority 1B**
3. **Goals Management** (Update/Delete) - **Priority 1C**
4. **Balance Summaries** (Weekly/Monthly) - **Priority 1D**

### **P2 - Medium Priority**
Funzionalità per migliorare engagement:
- Weight analytics
- Goal performance metrics
- Custom date ranges
- User streaks/gamification

### **P3 - Low Priority**
Funzionalità avanzate per scaling:
- Admin features
- Challenges system
- Achievement badges

---

## 🚀 Prossimi Step

### **Sprint Corrente - Week 1-2**
- [ ] **Implementare Analytics API** (`/trends`, `/insights`)
- [ ] **Aggiungere Metabolic Profile Management**
- [ ] **Completare Goals CRUD** (Update/Delete)

### **Sprint Successivo - Week 3-4**
- [ ] **Weekly/Monthly Summaries**
- [ ] **Weight Trend Analysis**
- [ ] **Performance Metrics**

### **Backlog - Future Sprints**
- [ ] **Gamification Features** (Streaks, Badges)
- [ ] **Advanced Analytics** (Predictions, ML)
- [ ] **Admin Features** (User management)

---

## 🧪 Test Coverage Status

| Categoria | Unit Tests | Integration Tests | Status |
|-----------|------------|-------------------|--------|
| **Health** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Users** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Goals** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Balance** | ✅ 100% | ✅ 100% | 🟢 Complete |
| **Analytics** | ❌ 0% | ❌ 0% | 🔴 Missing |
| **Metabolic** | ❌ 0% | ❌ 0% | 🔴 Missing |

---

## 📝 Note Tecniche

### **Dipendenze per Sviluppo Futuro:**
- **Analytics**: Richiede aggregazione dati e possibile integrazione con AI Coach Service
- **Metabolic Profiles**: Necessita algoritmi di calcolo BMR/TDEE specifici per il mercato italiano
- **Advanced Features**: Dipendenti da Notifications Service per gamification

### **Considerazioni Architetturali:**
- Mantenere separazione Domain/Application/Infrastructure
- Utilizzare CQRS pattern per analytics read-heavy operations
- Implementare caching Redis per endpoints analytics
- Preparare integrazione con N8N workflows per AI insights

### **Performance Goals:**
- Response time < 200ms per tutti gli endpoint P0/P1
- Support fino a 1000 RPS per endpoint critici
- Cache hit ratio > 80% per analytics endpoints

---

**🔄 Ultimo sync con Swagger**: 5 settembre 2025  
**📊 Completamento MVP**: 39% (12/31 endpoints)  
**🎯 Target Q1 2025**: 80% (25/31 endpoints)
