# 🔧 Environment Configuration Guide

Questa guida spiega tutti i campi di configurazione per i microservizi della piattaforma GymBro.

## 📋 Campo per Campo

### ✅ **CAMPI OBBLIGATORI**

#### 🏷️ Service Configuration
```env
SERVICE_NAME=your-service-name     # Nome del microservizio
ENVIRONMENT=development            # development|staging|production
DEBUG=false                       # true solo in development
LOG_LEVEL=INFO                    # DEBUG|INFO|WARNING|ERROR
```

#### 🔗 Supabase Configuration  
```env
SUPABASE_URL=https://xxx.supabase.co           # URL del progetto Supabase
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...      # Chiave pubblica (anon)
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...   # Chiave privata (service_role)
```

#### 🔐 Security Configuration
```env
SECRET_KEY=your-super-secret-key-here          # Chiave per JWT (min 32 caratteri)
JWT_ALGORITHM=HS256                           # Algoritmo JWT
JWT_EXPIRATION_HOURS=24                       # Scadenza token in ore
```

#### 🌐 CORS & API
```env
ALLOWED_ORIGINS=http://localhost:3000,capacitor://localhost,https://localhost,http://localhost:8080
RATE_LIMIT_REQUESTS_PER_MINUTE=60             # Rate limiting per utente
```

#### 🗄️ Database
```env
DATABASE_SCHEMA=your_service_name             # Schema database (snake_case)
STRUCTURED_LOGGING=true                       # Logging strutturato
```

#### ⚡ Feature Flags
```env
ENABLE_REAL_TIME=true                         # Supabase realtime
ENABLE_AUTH=true                             # Autenticazione Supabase
ENABLE_STORAGE=false                         # Storage Supabase (di solito false)
```

#### 🚀 Performance
```env
REQUEST_TIMEOUT_SECONDS=30                    # Timeout richieste
MAX_CONNECTIONS=100                          # Max connessioni simultanee
```

### 🔗 **CAMPI OPZIONALI**

#### 🔍 Monitoring
```env
# SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id    # Error tracking
```

#### 🤖 External Services
```env
# OPENAI_API_KEY=sk-your-openai-api-key-here                 # Solo se serve AI
```

## 🎯 Quick Setup per Nuovo Microservizio

1. **Copia il template**: `cp .env.example .env`
2. **Sostituisci i placeholder**:
   - `{service-name}` → nome del tuo servizio
   - `your-project-id.supabase.co` → URL reale Supabase
   - Chiavi Supabase reali
   - SECRET_KEY sicura (genera con `openssl rand -hex 32`)

3. **Verifica i campi obbligatori**: Tutti i campi senza `#` davanti devono essere compilati

4. **Testa la configurazione**: Avvia il servizio e controlla i log

## ⚠️ Sicurezza

- **MAI committare il file `.env`** (è in .gitignore)
- **SECRET_KEY**: Deve essere unica per ogni servizio e lunga almeno 32 caratteri
- **Chiavi Supabase**: Usa sempre le chiavi del progetto corretto
- **DEBUG=false** in produzione

## 🔄 Aggiornamenti Template

Se aggiungi nuovi campi di configurazione:
1. Aggiorna `services/your-service/.env.example`
2. Aggiorna `templates/microservice-template/supabase-client-template/.env.example`
3. Aggiorna `templates/microservice-template/supabase-client-template/app/core/config.py`
4. Aggiorna questa guida

## 🧪 Testing

Per testare se la configurazione è corretta:
```bash
# 1. Controlla che il servizio si avvii
make services-start

# 2. Testa l'health check  
curl http://localhost:800X/health

# 3. Verifica i log
make services-logs
```

---

*Mantenuto aggiornato con il servizio user-management (ultima revisione: 10 settembre 2025)*
