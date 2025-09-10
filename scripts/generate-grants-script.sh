#!/bin/bash
set -euo pipefail

# generate-grants-script.sh
# Script per generare automaticamente il file grants SQL per un microservizio
# 
# Utilizzo:
#   ./scripts/generate-grants-script.sh <service_name> [schema_name]
#
# Esempi:
#   ./scripts/generate-grants-script.sh user-management
#   ./scripts/generate-grants-script.sh calorie-balance calorie_balance
#   ./scripts/generate-grants-script.sh workout-tracking workout_tracking

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

print_usage() {
    echo "Usage: $0 <service_name> [schema_name]"
    echo ""
    echo "Arguments:"
    echo "  service_name    Nome del microservizio (es: user-management)"
    echo "  schema_name     Nome dello schema DB (default: service_name con _ al posto di -)"
    echo ""
    echo "Esempi:"
    echo "  $0 user-management"
    echo "  $0 calorie-balance calorie_balance"
    echo "  $0 workout-tracking workout_tracking"
    exit 1
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    print_usage
fi

SERVICE_NAME="$1"
SCHEMA_NAME="${2:-$(echo "$SERVICE_NAME" | tr '-' '_')}"

SERVICE_DIR="$WORKSPACE_ROOT/services/$SERVICE_NAME"
SQL_DIR="$SERVICE_DIR/sql"
TEMPLATE_FILE="$WORKSPACE_ROOT/config/supabase/grants_template.sql"

# Validazioni
if [ ! -d "$SERVICE_DIR" ]; then
    echo "❌ Errore: Directory del servizio non trovata: $SERVICE_DIR"
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Errore: Template grants non trovato: $TEMPLATE_FILE"
    exit 1
fi

# Crea la directory sql se non esiste
mkdir -p "$SQL_DIR"

# Trova il numero del prossimo script SQL
NEXT_NUMBER="001"
if [ -d "$SQL_DIR" ]; then
    EXISTING_FILES=$(find "$SQL_DIR" -name "*.sql" -type f | wc -l)
    if [ "$EXISTING_FILES" -gt 0 ]; then
        LAST_NUMBER=$(find "$SQL_DIR" -name "[0-9][0-9][0-9]_*.sql" -type f | sort | tail -1 | sed 's/.*\/\([0-9][0-9][0-9]\)_.*/\1/')
        if [ -n "$LAST_NUMBER" ]; then
            NEXT_NUMBER=$(printf "%03d" $((10#$LAST_NUMBER + 1)))
        fi
    fi
fi

OUTPUT_FILE="$SQL_DIR/${NEXT_NUMBER}_grants.sql"

# Genera il file sostituendo il placeholder
sed "s/{{SCHEMA_NAME}}/$SCHEMA_NAME/g" "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo "✅ Generato script grants per $SERVICE_NAME:"
echo "   File: $OUTPUT_FILE"
echo "   Schema: $SCHEMA_NAME"
echo ""
echo "📋 Prossimi passi (MANUALI):"
echo "1. Apri Supabase Dashboard → SQL Editor"
echo "2. Copia il contenuto del file: $OUTPUT_FILE"
echo "3. Incolla nel SQL Editor di Supabase"
echo "4. Clicca 'Run' per eseguire i DDL SQL"
echo "5. Verifica che il microservizio si avvii correttamente"
echo ""
echo "⚠️  IMPORTANTE: Non eseguire questo script come shell script!"
echo "   I comandi DDL devono essere eseguiti nel portale Supabase."
echo ""
echo "💡 Comando per copiare negli appunti (macOS):"
echo "   cat '$OUTPUT_FILE' | pbcopy"
