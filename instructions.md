# Istruzioni Generali NutriFit Platform

Questa piattaforma è composta da microservizi Python, ciascuno con una propria documentazione di dettaglio.

## Documentazione dei Microservizi

Per ogni microservizio, consulta la documentazione specifica nella relativa cartella:

- **Calorie Balance Service**: [docs/databases/calorie-balance-db.md](docs/databases/calorie-balance-db.md)
- Altri microservizi avranno una documentazione dedicata nella stessa struttura.

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
