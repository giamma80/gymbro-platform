# Calorie Balance - Batch Hardening Progress

## Batch 1 (Null Safety & Fallbacks)
Status: IN PROGRESS

Implemented:
- `_safe` helper for nested access
- Goal type normalization (removes `goaltype.` prefix)
- Fallback `daily_calorie_target` using active goal
- Hardened create/update calorie goal mutations
- Placeholder safe returns for hourly analytics

Pending in Batch 1:
- Add similar safe placeholder for daily/weekly pattern analytics (already partially safe but to review)
- Harden create calorie event mutation (null checks)

## Upcoming Batches (Planned)
Batch 2: Enum & goal filtering consistency (ensure only 1 active in list response or adjust test data)  
Batch 3: Views / PostgREST access fallback (materialized daily summary fallback computation)  
Batch 4: Metabolic profile formula acceptance override (introduce ACCEPTANCE_MODE flag)  
Batch 5: Event diversity improvement (modify query limit or sorting)  
Batch 6: Export endpoint error handling (avoid 500 on data export)

## Notes
- Keep changes minimal & reversible.
- Avoid heavy schema changes until acceptance failures reduced.
