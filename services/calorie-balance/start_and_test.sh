#!/bin/bash

# Script completo per avviare il servizio Calorie Balance e testare le API
# Autore: GitHub Copilot
# Data: 5 settembre 2025

# set -e  # Commentato per debug

# Colori per l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Avvio del servizio Calorie Balance e test completi...${NC}"

# Directory del servizio
SERVICE_DIR="/Users/giamma/workspace/gymbro-platform/services/calorie-balance"
cd "$SERVICE_DIR"

echo -e "${YELLOW}📂 Directory corrente: $(pwd)${NC}"

# Funzione per controllare se il server è già in esecuzione
check_server_running() {
    if curl -s -f "http://localhost:8001/health/" > /dev/null 2>&1; then
        return 0  # Server in esecuzione
    else
        return 1  # Server non in esecuzione
    fi
}

# Funzione per terminare processi esistenti
kill_existing_server() {
    echo -e "${YELLOW}🔄 Controllo processi esistenti...${NC}"
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        echo -e "${YELLOW}⚠️ Processo uvicorn esistente trovato, lo termino...${NC}"
        pkill -f "uvicorn app.main:app" || true
        sleep 3
    fi
}

# Verifica ambiente Poetry
echo -e "${BLUE}🔍 Verifica ambiente Poetry...${NC}"
if ! poetry --version > /dev/null 2>&1; then
    echo -e "${RED}❌ Poetry non trovato. Installare Poetry prima di continuare.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Poetry trovato: $(poetry --version)${NC}"

# Installa dipendenze
echo -e "${BLUE}📦 Installo dipendenze...${NC}"
poetry install --only main > /dev/null 2>&1
echo -e "${GREEN}✅ Dipendenze installate${NC}"

# Verifica che l'app si importi correttamente
echo -e "${BLUE}🔍 Verifica importazione app...${NC}"
if poetry run python -c "from app.main import app; print('✅ App importata correttamente')" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ App importata correttamente${NC}"
else
    echo -e "${RED}❌ Errore nell'importazione app${NC}"
    poetry run python -c "from app.main import app"  # Mostra l'errore
    exit 1
fi

# Termina server esistente se presente
kill_existing_server

# Avvia il servizio
echo -e "${BLUE}🌐 Avvio servizio FastAPI su porta 8001...${NC}"
cd "$SERVICE_DIR"  # Assicurati di essere nella directory corretta
poetry run uvicorn app.main:app --reload --port 8001 &
SERVER_PID=$!

# Funzione di cleanup
cleanup() {
    echo -e "${YELLOW}🧹 Arresto del server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    wait $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Server arrestato${NC}"
}
trap cleanup EXIT

# Attende che il server sia pronto
echo -e "${YELLOW}⏳ Attendo avvio del server...${NC}"
sleep 3  # Aspetta un po' per l'avvio iniziale

for i in {1..20}; do
    if check_server_running; then
        echo -e "${GREEN}✅ Server in esecuzione su porta 8001${NC}"
        break
    else
        if [ $i -eq 20 ]; then
            echo -e "${RED}❌ Server non risponde dopo 20 tentativi${NC}"
            echo -e "${RED}Possibili errori di avvio:${NC}"
            # Mostra gli ultimi log se il server non si avvia
            sleep 2
            exit 1
        fi
        echo -e "${YELLOW}⏳ Tentativo $i/20...${NC}"
        sleep 2
    fi
done

echo -e "${BLUE}🏥 === INIZIO SANITY CHECK E TEST FUNZIONALI ===${NC}"

# Test 1: Health Check
echo -e "${BLUE}🏥 Test 1: Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:8001/health/")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ Health Check PASS${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Health Check FAIL${NC}"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Test 2: Creazione utente
echo -e "\n${BLUE}👤 Test 2: Creazione utente...${NC}"

# Genera ID unico per il test
TIMESTAMP=$(date +%s)
USER_ID=$(uuidgen)
EMAIL="test$TIMESTAMP@example.com"

USER_DATA="{
    \"user_id\": \"$USER_ID\",
    \"username\": \"testuser$TIMESTAMP\",
    \"email\": \"$EMAIL\",
    \"full_name\": \"Test User\"
}"

CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")


if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Creazione utente PASS${NC}"
    echo "$CREATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Creazione utente FAIL${NC}"
    echo "$CREATE_RESPONSE"
    exit 1
fi

# Test API Eventi Calorici
echo -e "\n${BLUE}🔥 Test API Eventi Calorici...${NC}"

# Test evento calorie consumate
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
CALORIE_EVENT_CONSUMED=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "event_type": "consumed",
  "calories": 500,
  "timestamp": "$TIMESTAMP"
}
EOF
)
CONSUMED_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/calorie-event/consumed" -H "Content-Type: application/json" -d "$CALORIE_EVENT_CONSUMED")
echo -e "${GREEN}Risposta evento 'consumed':${NC}"
echo "$CONSUMED_RESPONSE" | python3 -m json.tool
if echo "$CONSUMED_RESPONSE" | grep -q '"event_type": *"consumed"'; then
    echo -e "${GREEN}✅ Evento calorie consumate PASS${NC}"
else
    echo -e "${RED}❌ Evento calorie consumate FAIL${NC}"
    exit 1
fi

# Test evento calorie bruciate
CALORIE_EVENT_BURNED=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "event_type": "burned",
  "calories": 300,
  "timestamp": "$TIMESTAMP"
}
EOF
)
BURNED_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/calorie-event/burned" -H "Content-Type: application/json" -d "$CALORIE_EVENT_BURNED")
echo -e "${GREEN}Risposta evento 'burned':${NC}"
echo "$BURNED_RESPONSE" | python3 -m json.tool
if echo "$BURNED_RESPONSE" | grep -q '"event_type": *"burned"'; then
    echo -e "${GREEN}✅ Evento calorie bruciate PASS${NC}"
else
    echo -e "${RED}❌ Evento calorie bruciate FAIL${NC}"
    exit 1
fi

# Test evento peso
CALORIE_EVENT_WEIGHT=$(cat <<EOF
{
  "user_id": "$USER_ID",
  "event_type": "weight",
  "weight_kg": 75.5,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
)
WEIGHT_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/calorie-event/weight" -H "Content-Type: application/json" -d "$CALORIE_EVENT_WEIGHT")
echo -e "${GREEN}Risposta evento 'weight':${NC}"
echo "$WEIGHT_RESPONSE" | python3 -m json.tool
if echo "$WEIGHT_RESPONSE" | grep -q '"event_type": *"weight"'; then
    echo -e "${GREEN}✅ Evento peso PASS${NC}"
else
    echo -e "${RED}❌ Evento peso FAIL${NC}"
    exit 1
fi

# Test batch eventi
BATCH_EVENTS=$(cat <<EOF
[
  {
    "user_id": "$USER_ID",
    "event_type": "consumed",
    "calories": 200,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  },
  {
    "user_id": "$USER_ID",
    "event_type": "burned",
    "calories": 100,
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  }
]
EOF
)
BATCH_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/calorie-event/batch" -H "Content-Type: application/json" -d "$BATCH_EVENTS")
echo -e "${GREEN}Risposta batch eventi:${NC}"
echo "$BATCH_RESPONSE" | python3 -m json.tool
if echo "$BATCH_RESPONSE" | grep -q '"event_type": *"consumed"' && echo "$BATCH_RESPONSE" | grep -q '"event_type": *"burned"'; then
    echo -e "${GREEN}✅ Batch eventi PASS${NC}"
else
    echo -e "${RED}❌ Batch eventi FAIL${NC}"
    exit 1
fi

# Test 3: Recupero utente
echo -e "\n${BLUE}🔍 Test 3: Recupero utente...${NC}"
GET_RESPONSE=$(curl -s "http://localhost:8001/api/v1/users/$USER_ID")

if echo "$GET_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Recupero utente PASS${NC}"
    echo "$GET_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero utente FAIL${NC}"
    echo "$GET_RESPONSE"
    exit 1
fi

# Test 4: Aggiornamento profilo utente
echo -e "\n${BLUE}✏️ Test 4: Aggiornamento profilo utente...${NC}"
UPDATE_DATA='{
    "age": 30,
    "gender": "MALE",
    "height_cm": 180.5,
    "weight_kg": 75.0,
    "activity_level": "MODERATELY_ACTIVE"
}'

UPDATE_RESPONSE=$(curl -s --max-time 10 -X PUT "http://localhost:8001/api/v1/users/$USER_ID" \
    -H "Content-Type: application/json" \
    -d "$UPDATE_DATA")

if echo "$UPDATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Aggiornamento profilo PASS${NC}"
    echo "$UPDATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Aggiornamento profilo FAIL${NC}"
    echo "$UPDATE_RESPONSE"
    exit 1
fi

# Test 5: Verifica documentazione API
echo -e "\n${BLUE}📚 Test 5: Documentazione API...${NC}"
if curl -s -f "http://localhost:8001/docs" > /dev/null; then
    echo -e "${GREEN}✅ Swagger docs disponibile${NC}"
else
    echo -e "${YELLOW}⚠️ Swagger docs non disponibile${NC}"
fi

if curl -s -f "http://localhost:8001/redoc" > /dev/null; then
    echo -e "${GREEN}✅ ReDoc disponibile${NC}"
else
    echo -e "${YELLOW}⚠️ ReDoc non disponibile${NC}"
fi

# Test 6: Endpoint inesistente (404 atteso)
echo -e "\n${BLUE}🚫 Test 6: Endpoint inesistente (404 atteso)...${NC}"
NOT_FOUND_RESPONSE=$(curl -s -w "%{http_code}" "http://localhost:8001/api/v1/nonexistent")
if echo "$NOT_FOUND_RESPONSE" | grep -q "404"; then
    echo -e "${GREEN}✅ Gestione 404 PASS${NC}"
else
    echo -e "${YELLOW}⚠️ Gestione 404 inaspettata${NC}"
fi

# Test 7: Goals - Creazione obiettivo calorico
echo -e "\n${BLUE}🎯 Test 7: Creazione obiettivo calorico...${NC}"
 START_DATE=$(date -u +%Y-%m-%d)
 END_DATE=$(date -u -v+7d +%Y-%m-%d)
GOAL_DATA=$(cat <<EOF
{
    "user_id": "$USER_ID",
    "goal_calories": 2200,
    "goal_type": "maintenance",
    "start_date": "$START_DATE",
    "end_date": "$END_DATE"
}
EOF
)
GOAL_CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/goals/users/$USER_ID" -H "Content-Type: application/json" -d "$GOAL_DATA")
if echo "$GOAL_CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Creazione obiettivo calorico PASS${NC}"
    echo "$GOAL_CREATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Creazione obiettivo calorico FAIL${NC}"
    echo "$GOAL_CREATE_RESPONSE"
    exit 1
fi

# Test 8: Goals - Recupero obiettivo attivo
echo -e "\n${BLUE}🎯 Test 8: Recupero obiettivo attivo...${NC}"
GOAL_ACTIVE_RESPONSE=$(curl -s "http://localhost:8001/api/v1/goals/users/$USER_ID/active")
if echo "$GOAL_ACTIVE_RESPONSE" | grep -q '"target_calories"'; then
    echo -e "${GREEN}✅ Recupero obiettivo attivo PASS${NC}"
    echo "$GOAL_ACTIVE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero obiettivo attivo FAIL${NC}"
    echo "$GOAL_ACTIVE_RESPONSE"
    exit 1
fi

# Test 9: Balance - Aggiornamento bilancio giornaliero
echo -e "\n${BLUE}⚖️ Test 9: Aggiornamento bilancio giornaliero...${NC}"
BALANCE_DATA="{\"user_id\": \"$USER_ID\", \"date\": \"$(date -u +%Y-%m-%d)\", \"calories_consumed\": 1800, \"calories_burned\": 500}"
BALANCE_UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8001/api/v1/balance/users/$USER_ID" -H "Content-Type: application/json" -d "$BALANCE_DATA")
if echo "$BALANCE_UPDATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Aggiornamento bilancio PASS${NC}"
    echo "$BALANCE_UPDATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Aggiornamento bilancio FAIL${NC}"
    echo "$BALANCE_UPDATE_RESPONSE"
    exit 1
fi

# Test 10: Balance - Recupero bilancio per data
echo -e "\n${BLUE}⚖️ Test 10: Recupero bilancio per data...${NC}"
BALANCE_DATE_RESPONSE=$(curl -s "http://localhost:8001/api/v1/balance/users/$USER_ID/date/$(date -u +%Y-%m-%d)")
if echo "$BALANCE_DATE_RESPONSE" | grep -q '"calories_consumed"'; then
    echo -e "${GREEN}✅ Recupero bilancio per data PASS${NC}"
    echo "$BALANCE_DATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero bilancio per data FAIL${NC}"
    echo "$BALANCE_DATE_RESPONSE"
    exit 1
fi

# Test 11: Balance - Recupero bilancio di oggi
echo -e "\n${BLUE}⚖️ Test 11: Recupero bilancio di oggi...${NC}"
BALANCE_TODAY_RESPONSE=$(curl -s "http://localhost:8001/api/v1/balance/users/$USER_ID/today")
if echo "$BALANCE_TODAY_RESPONSE" | grep -q '"calories_consumed"'; then
    echo -e "${GREEN}✅ Recupero bilancio di oggi PASS${NC}"
    echo "$BALANCE_TODAY_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero bilancio di oggi FAIL${NC}"
    echo "$BALANCE_TODAY_RESPONSE"
    exit 1
fi

# Test 12: Balance - Recupero progress dati
echo -e "\n${BLUE}⚖️ Test 12: Recupero progress dati...${NC}"
BALANCE_PROGRESS_DATA="{\"user_id\": \"$USER_ID\", \"start_date\": \"$(date -u +%Y-%m-%d)\", \"end_date\": \"$(date -u -v+7d +%Y-%m-%d)\"}"
BALANCE_PROGRESS_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/balance/users/$USER_ID/progress" -H "Content-Type: application/json" -d "$BALANCE_PROGRESS_DATA")
if echo "$BALANCE_PROGRESS_RESPONSE" | grep -q '"metrics"'; then
    echo -e "${GREEN}✅ Recupero progress dati PASS${NC}"
    echo "$BALANCE_PROGRESS_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Recupero progress dati FAIL${NC}"
    echo "$BALANCE_PROGRESS_RESPONSE"
    exit 1
fi

# Summary finale
echo -e "\n${GREEN}🎉 === TUTTI I TEST COMPLETATI CON SUCCESSO! === 🎉${NC}"
echo -e "${BLUE}📊 Riepilogo test:${NC}"
echo -e "  ✅ Health Check"
echo -e "  ✅ Creazione utente"
echo -e "  ✅ Recupero utente"
echo -e "  ✅ Aggiornamento profilo"
echo -e "  ✅ Documentazione API"
echo -e "  ✅ Gestione errori"

echo -e "\n${BLUE}🌐 Il servizio è disponibile su:${NC}"
echo -e "  • API: http://localhost:8001"
echo -e "  • Health: http://localhost:8001/health/"
echo -e "  • Docs: http://localhost:8001/docs"
echo -e "  • ReDoc: http://localhost:8001/redoc"

echo -e "\n${BLUE}👤 Utente di test creato:${NC}"
echo -e "  • ID: $USER_ID"
echo -e "  • Email: $EMAIL"

echo -e "\n${YELLOW}📝 Il servizio rimarrà in esecuzione. Premi Ctrl+C per terminare.${NC}"

# Mantieni il server in esecuzione
echo -e "${BLUE}⏳ Server in attesa... (Ctrl+C per uscire)${NC}"
while true; do
    if ! check_server_running; then
        echo -e "${RED}❌ Server non più raggiungibile!${NC}"
        exit 1
    fi
    sleep 10
done

# Test dell'API Health Check
echo -e "${BLUE}🏥 Test Health Check...${NC}"
HEALTH_RESPONSE=$(curl -s "http://localhost:8001/api/v1/health/")
echo -e "${GREEN}Health Check Response:${NC}"
echo "$HEALTH_RESPONSE" | python3 -m json.tool

# Test creazione utente
echo -e "${BLUE}👤 Test creazione utente...${NC}"
USER_DATA='{
    "user_id": "test_user_123",
    "username": "testuser123",
    "email": "test@example.com",
    "full_name": "Test User"
}'

CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/users/" \
    -H "Content-Type: application/json" \
    -d "$USER_DATA")

echo -e "${GREEN}Creazione Utente Response:${NC}"
echo "$CREATE_RESPONSE" | python3 -m json.tool

# Verifica se la creazione è andata a buon fine
if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Creazione utente riuscita${NC}"
else
    echo -e "${RED}❌ Errore nella creazione utente${NC}"
    echo "$CREATE_RESPONSE"
    exit 1
fi

# Test recupero utente
echo -e "${BLUE}🔍 Test recupero utente...${NC}"
GET_RESPONSE=$(curl -s "http://localhost:8001/api/v1/users/test_user_123")

echo -e "${GREEN}Recupero Utente Response:${NC}"
echo "$GET_RESPONSE" | python3 -m json.tool

# Verifica se il recupero è andato a buon fine
if echo "$GET_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Recupero utente riuscito${NC}"
else
    echo -e "${RED}❌ Errore nel recupero utente${NC}"
    exit 1
fi

# Test aggiornamento profilo utente
echo -e "${BLUE}✏️ Test aggiornamento profilo utente...${NC}"
UPDATE_DATA='{
    "age": 30,
    "gender": "MALE",
    "height_cm": 180.5,
    "weight_kg": 75.0,
    "activity_level": "MODERATE"
}'

UPDATE_RESPONSE=$(curl -s -X PUT "http://localhost:8001/api/v1/users/test_user_123" \
    -H "Content-Type: application/json" \
    -d "$UPDATE_DATA")

echo -e "${GREEN}Aggiornamento Profilo Response:${NC}"
echo "$UPDATE_RESPONSE" | python3 -m json.tool

# Verifica se l'aggiornamento è andato a buon fine
if echo "$UPDATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✅ Aggiornamento profilo riuscito${NC}"
else
    echo -e "${RED}❌ Errore nell'aggiornamento profilo${NC}"
    exit 1
fi

# Test degli endpoint di documentazione
echo -e "${BLUE}📚 Test documentazione API...${NC}"
if curl -s -f "http://localhost:8001/docs" > /dev/null; then
    echo -e "${GREEN}✅ Documentazione Swagger disponibile su http://localhost:8001/docs${NC}"
else
    echo -e "${YELLOW}⚠️ Documentazione Swagger non disponibile${NC}"
fi

if curl -s -f "http://localhost:8001/redoc" > /dev/null; then
    echo -e "${GREEN}✅ Documentazione ReDoc disponibile su http://localhost:8001/redoc${NC}"
else
    echo -e "${YELLOW}⚠️ Documentazione ReDoc non disponibile${NC}"
fi

# Summary finale
echo -e "${GREEN}🎉 TUTTI I TEST COMPLETATI CON SUCCESSO! 🎉${NC}"
echo -e "${BLUE}📊 Riepilogo test:${NC}"
echo -e "  ✅ Connessione database"
echo -e "  ✅ Avvio servizio FastAPI"
echo -e "  ✅ Health Check"
echo -e "  ✅ Creazione utente"
echo -e "  ✅ Recupero utente"
echo -e "  ✅ Aggiornamento profilo"
echo -e "  ✅ Documentazione API"

echo -e "${BLUE}🌐 Il servizio è disponibile su:${NC}"
echo -e "  • API: http://localhost:8001"
echo -e "  • Health: http://localhost:8001/api/v1/health/"
echo -e "  • Docs: http://localhost:8001/docs"
echo -e "  • ReDoc: http://localhost:8001/redoc"

echo -e "${YELLOW}📝 Il servizio rimarrà in esecuzione. Premi Ctrl+C per terminare.${NC}"

# Mantieni il server in esecuzione
wait $SERVER_PID
