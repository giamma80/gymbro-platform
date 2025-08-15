# 🚀 GymBro Platform - Quick Start Guide

Benvenuto nella piattaforma GymBro! Questa guida ti aiuterà a configurare l'ambiente di sviluppo in pochi minuti.

## 📋 Prerequisiti

Prima di iniziare, assicurati di avere installato:

- **Docker** e **Docker Compose** ([Download](https://docs.docker.com/get-docker/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Make** (già installato su macOS/Linux)
- **Node.js 18+** (opzionale, per frontend future)

## 🚀 Setup Rapido (5 minuti)

### 1. Clone e Setup Iniziale

```bash
# Clone del repository
git clone <your-repo-url>
cd gymbro-platform

# Setup automatico dell'ambiente
make setup
```

### 2. Configurazione API Keys (GRATUITE)

Modifica il file `.env` con le tue API keys gratuite:

```bash
# Apri .env nel tuo editor preferito
code .env
```

**Servizi da registrare (tutti GRATUITI):**

| Servizio | URL | Piano Free | Tempo Setup |
|----------|-----|------------|-------------|
| **Supabase** | https://supabase.com | 500MB DB + 50k users | 2 min |
| **OpenAI** | https://platform.openai.com | $18 credito gratis | 2 min |
| **SendGrid** | https://sendgrid.com | 100 email/giorno | 3 min |
| **Firebase** | https://console.firebase.google.com | Push notifications illimitate | 3 min |
| **USDA** | https://fdc.nal.usda.gov/api-key-signup | API gratuita | 1 min |

### 3. Avvio Piattaforma

```bash
# Avvia tutti i servizi
make start
```

Aspetta 30-60 secondi per l'avvio completo.

## ✅ Verifica Setup

### 🌐 Servizi Disponibili

Una volta avviato, avrai accesso a:

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| **GraphQL Gateway** | http://localhost:8000/docs | API unificata |
| **User Management** | http://localhost:8001/docs | Gestione utenti |
| **Data Ingestion** | http://localhost:8002/docs | Raccolta dati device |
| **Calorie Service** | http://localhost:8003/docs | Calcoli metabolici |
| **Meal Service** | http://localhost:8004/docs | Gestione pasti |
| **Analytics** | http://localhost:8005/docs | Statistiche |
| **Notifications** | http://localhost:8006/docs | Sistema notifiche |
| **LLM Service** | http://localhost:8007/docs | Query linguaggio naturale |
| **n8n Workflows** | http://localhost:5678 | Automazioni (admin/admin123) |
| **Traefik Dashboard** | http://localhost:8080 | Load balancer |

### 🏥 Health Check

```bash
# Verifica che tutti i servizi siano attivi
make health

# Mostra status dettagliato
make status
```

## 🧪 Test della Piattaforma

### 1. Registrazione Utente

```bash
# Test API registrazione
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Mario",
    "last_name": "Rossi",
    "date_of_birth": "1990-01-15T00:00:00Z",
    "gender": "male",
    "height_cm": 175.0,
    "weight_kg": 70.0,
    "activity_level": "moderately_active"
  }'
```

### 2. Login e Test Token

```bash
# Login
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Salva il token dalla risposta e testalo
TOKEN="your-jwt-token"

# Test profilo autenticato
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8001/profile"
```

### 3. Test GraphQL

Vai a http://localhost:8000/docs e prova queste query:

```graphql
# Query utente
query GetUser {
  user(id: "user-id") {
    email
    firstName
    lastName
    stats {
      totalCaloriesBurned
      currentStreak
    }
  }
}

# Mutation aggiornamento profilo
mutation UpdateProfile {
  updateProfile(input: {
    weightKg: 72.5
    activityLevel: VERY_ACTIVE
  }) {
    success
    user {
      weightKg
      activityLevel
    }
  }
}
```

## 🛠️ Comandi Utili per Sviluppo

```bash
# Visualizza logs in tempo reale
make logs

# Riavvia servizi dopo modifiche
make restart

# Solo servizi core (DB + Redis)
make start-dev

# Esegui tests
make test

# Formatta codice
make format

# Debug di un servizio specifico
make debug-user

# Reset completo (⚠️ cancella tutto)
make reset-all
```

## 🗄️ Database

### Accesso Diretto

```bash
# Shell PostgreSQL
make shell-db

# Backup
make db-backup

# Reset database (⚠️ perde tutti i dati)
make db-reset
```

### Struttura Database

La piattaforma usa PostgreSQL con queste tabelle principali:

- `users` - Profili utente e autenticazione
- `user_preferences` - Preferenze e impostazioni
- `user_stats_cache` - Cache statistiche
- `user_sessions` - Sessioni attive
- `user_audit_logs` - Log di audit (GDPR)

## 📊 Monitoring

```bash
# Avvia stack monitoring (Prometheus + Grafana)
make monitor

# Statistiche utilizzo
make stats
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## 🚀 Deploy

### 🌐 Render.com (FREE - Raccomandato per MVP)

**DEPLOY AUTOMATICO con `render.yaml`:**

```bash
# 1. File render.yaml già configurato ✅ 
# 2. Vai su https://render.com
# 3. Connetti GitHub repository
# 4. Render rileva automaticamente render.yaml
# 5. Click "Deploy" - ZERO configurazione!
```

**Costi: $0/mese** (PostgreSQL + Web Service free tier)

### Staging (Automatico)

```bash
# Push su main branch triggera deploy automatico
git push origin main
```

### Production

```bash
# Deploy production (con tag)
make deploy-prod
```

## 🆘 Troubleshooting

### Problemi Comuni

**Porta già in uso:**
```bash
# Trova e termina processo
lsof -ti:8000 | xargs kill -9
# oppure cambia porte in docker-compose.yml
```

**Database non si connette:**
```bash
# Verifica status
make status

# Reset database
make db-reset
```

**Servizio non risponde:**
```bash
# Controlla logs
make logs-user

# Riavvia tutto
make restart

# Health check
make health
```

**Permessi Docker:**
```bash
# Assicurati che Docker daemon sia attivo
sudo systemctl start docker

# Oppure aggiungi utente a gruppo docker
sudo usermod -aG docker $USER
```

### Guida Completa

```bash
# Guida troubleshooting dettagliata
make troubleshoot
```

## 📚 Prossimi Passi

1. **Esplora l'API**: Usa http://localhost:8001/docs per testare tutti gli endpoint
2. **Configura n8n**: Vai su http://localhost:5678 per creare workflow
3. **Setup CI/CD**: Configura GitHub Actions con i tuoi secrets
4. **Frontend**: Integra con React/Next.js o app mobile
5. **Monitoring**: Configura alert e dashboard personalizzati

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch feature: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Apri una Pull Request

## 📞 Supporto

- **Issues**: Apri un issue su GitHub
- **Documentazione**: Consulta `/docs` per guide dettagliate
- **Logs**: Usa `make logs` per debug

---

**🎉 Congratulazioni!** La tua piattaforma GymBro è ora attiva e funzionante!

Per qualsiasi domanda, consulta la documentazione completa in `/docs` o apri un issue su GitHub.
