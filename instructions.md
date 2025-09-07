# Istruzioni Generali NutriFit Platform

Questa piattaforma è composta da microservizi Python, ciascuno con una propria documentazione di dettaglio.

## Documentazione dei Microservizi

Per ogni microservizio, consulta la documentazione specifica nella relativa cartella:

- **🚨 User Management Service**: [docs/databases/user-management-db.md](docs/databases/user-management-db.md) - **CORE AUTH** - Autenticazione centralizzata, JWT, OAuth
- **Calorie Balance Service**: [docs/databases/calorie-balance-db.md](docs/databases/calorie-balance-db.md) - Metabolismo energetico, BMR, obiettivi
- **Meal Tracking Service**: [docs/databases/meal-tracking-db.md](docs/databases/meal-tracking-db.md) - AI food recognition, nutrition data
- **Health Monitor Service**: [docs/databases/health-monitor-db.md](docs/databases/health-monitor-db.md) - HealthKit sync, wearables integration
- **Notifications Service**: [docs/databases/notifications-db.md](docs/databases/notifications-db.md) - Multi-channel messaging, FCM
- **AI Coach Service**: [docs/databases/ai-coach-db.md](docs/databases/ai-coach-db.md) - Conversational AI, RAG, coaching

## Come aggiungere la documentazione di un nuovo microservizio

1. Crea un file in `docs/databases/` con nome `<nome-microservizio>-db.md`.
2. Inserisci schema ER, SQL, mapping API ↔️ tabelle, policy di sicurezza e strategie di migrazione.
3. Aggiorna questo file `instructions.md` aggiungendo il riferimento al nuovo microservizio.

## Checklist per la documentazione microservizi

- [ ] Creare la documentazione di dettaglio in `docs/databases/<nome-microservizio>-db.md`
- [ ] Aggiornare il README del microservizio con link alla documentazione database
- [ ] Aggiornare `instructions.md` con il riferimento al nuovo microservizio
- [ ] Verificare la coerenza tra datamodel applicativo e schema SQL
- [ ] Aggiornare la documentazione generale se necessario (architettura, microservizi_python)
- [ ] Versionare tutte le modifiche (commit & push)
- [ ] Aggiornare l'issue tracker segnalando la chiusura della procedura

## Riferimenti
- Documentazione generale: [docs/architettura.md](docs/architettura.md)
- Guida microservizi Python: [docs/microservizi_python.md](docs/microservizi_python.md)

---
**Nota:** Ogni microservizio può avere una documentazione di dettaglio più specifica rispetto alla documentazione generale.
