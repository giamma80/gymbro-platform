#!/usr/bin/env python
"""Export Strawberry GraphQL SDL for the calorie-balance service.

Include basic validation (naming hygiene) to catch duplicated
type/input/enum/interface/union names before commit.

Usage:
  poetry run python scripts/export_schema.py

Exit codes:
  0 = success
  2 = schema build/import failure
  3 = duplicated type/input/enum/interface/union names detected
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Ensure we can import the application package when run from service root
CURRENT_DIR = Path(__file__).resolve().parent
SERVICE_ROOT = CURRENT_DIR.parent
APP_ROOT = SERVICE_ROOT / "app"

if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))

OUTPUT_PATH = APP_ROOT / "graphql" / "schema.graphql"


def _validate_name_uniqueness(sdl: str) -> list[str]:
    pattern = re.compile(
        r"^(type|input|enum|interface|union)\s+([A-Za-z0-9_]+)",
        re.MULTILINE,
    )
    names = [m.group(2) for m in pattern.finditer(sdl)]
    duplicates: list[str] = []
    seen: dict[str, int] = {}
    for n in names:
        seen[n] = seen.get(n, 0) + 1
    for name, count in seen.items():
        if count > 1:
            duplicates.append(name)
    return sorted(duplicates)


def main() -> int:
    try:
        from app.graphql.schema import schema  # type: ignore
    except Exception as e:  # pragma: no cover - startup failure path
        print(
            f"ERROR: impossibile importare/creare lo schema Strawberry: {e}",
            file=sys.stderr,
        )
        return 2

    try:
        sdl = schema.as_str()  # Strawberry federation schema to SDL string
    except Exception as e:  # pragma: no cover
        print(f"ERROR: build schema fallita: {e}", file=sys.stderr)
        return 2

    duplicates = _validate_name_uniqueness(sdl)
    if duplicates:
        print(
            "ERROR: definizioni duplicate (type/input/enum/interface/union): "
            + ", ".join(duplicates),
            file=sys.stderr,
        )
        return 3

    OUTPUT_PATH.write_text(sdl, encoding="utf-8")
    relative = OUTPUT_PATH.relative_to(SERVICE_ROOT)
    print(
        f"✅ Schema esportato in {relative} (dimensione: {len(sdl)} chars)"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
