"""Base GraphQL Queries per il servizio calorie-balance.

Questo file ora contiene SOLO le query legacy sul tavolo `calorie_balance`.
Tutti i tipi e le query/mutazioni avanzate (goals, events, balances,
analytics, metabolic profile) sono definiti in `extended_types.py` e
`extended_resolvers.py`.

Rimuovendo le definizioni duplicate dei tipi qui, evitiamo gli errori
`DuplicatedTypeName` di Strawberry.
"""

import logging
from typing import Optional

import strawberry

from app.core.database import SupabaseRepository
from app.graphql.types import UcalorieUbalanceListResponse, UcalorieUbalanceType

logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    """Query root minimale: solo le operazioni sul resource calorie_balance."""

    @strawberry.field
    async def get_calorie_balance(
        self, id: strawberry.ID
    ) -> Optional[UcalorieUbalanceType]:
        repo = SupabaseRepository("calorie_balance")
        data = await repo.get_by_id(str(id))
        if not data:
            return None
        return UcalorieUbalanceType(
            id=strawberry.ID(data["id"]),
            name=data["name"],
            description=data.get("description"),
            created_at=data["created_at"],
            updated_at=data.get("updated_at"),
        )

    @strawberry.field
    async def list_calorie_balances(
        self, limit: Optional[int] = 10, offset: Optional[int] = 0
    ) -> UcalorieUbalanceListResponse:
        try:
            repo = SupabaseRepository("calorie_balance")
            data = await repo.get_all(limit=limit, offset=offset)
            items = [
                UcalorieUbalanceType(
                    id=strawberry.ID(item["id"]),
                    name=item["name"],
                    description=item.get("description"),
                    created_at=item["created_at"],
                    updated_at=item.get("updated_at"),
                )
                for item in data
            ]
            return UcalorieUbalanceListResponse(
                success=True,
                message="Successfully retrieved calorie_balances",
                data=items,
                total=len(items),
            )
        except Exception as e:
            return UcalorieUbalanceListResponse(
                success=False,
                message=f"Error retrieving calorie_balances: {str(e)}",
                data=[],
                total=0,
            )
