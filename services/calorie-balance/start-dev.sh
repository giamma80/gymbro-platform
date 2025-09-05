#!/bin/bash

# Start Calorie Balance Service in development mode
# Versione ottimizzata basata su start_and_test.sh

# Colori per l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Calorie Balance Service in development mode...${NC}"

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env file with your actual configuration values${NC}"
    echo -e "${YELLOW}   Especially DATABASE_URL, SUPABASE_URL, and SUPABASE keys${NC}"
fi

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

# Funzione di cleanup per gestire CTRL+C
cleanup() {
    echo -e "\n${YELLOW}🧹 Arresto del server...${NC}"
    echo -e "${GREEN}✅ Server arrestato${NC}"
}
trap cleanup INT

# Run database migrations (when implemented)
# echo -e "${BLUE}🗃️ Running database migrations...${NC}"
# poetry run alembic upgrade head

# Start the service
echo -e "${BLUE}🏃‍♂️ Starting FastAPI server on http://localhost:8001${NC}"
echo -e "${GREEN}📖 Documentazione API disponibile su: http://localhost:8001/docs${NC}"
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
