# 🚨 Minimal Server Backup

**Data backup:** 16 agosto 2025  
**Motivo:** Rimozione dei file per evitare confusione nel deployment di Render.com

## File inclusi:
- `minimal-server.js` - Server Express minimale per debug
- `Dockerfile.minimal` - Dockerfile per il server minimale

## Utilizzo:
Questi file erano utilizzati per il debug del deployment quando il server Apollo principale non funzionava.
Il server minimale fornisce solo endpoint di salute (`/health`, `/ping`) senza GraphQL.

**Identificatore del servizio:** `graphql-gateway-minimal` v0.2.0

## Ripristino:
Per ripristinare il server minimale (se necessario per debug):
```bash
cp backup/minimal-server/* ./
# Modificare render.yaml per usare Dockerfile.minimal
```

⚠️ **Nota:** Il server minimale NON supporta le query GraphQL o Apollo Federation.
