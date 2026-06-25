# TODO

## Status (2025-06-25)

## Gennemført
- ✅ Refactoring til MVC-struktur (`implementation_plan.md`)
- ✅ Elafgift-bug rettet (`get_elafgift()` fjernet `* 2`)
- ✅ Stavefejl rettet (`carge_ex_tax` -> `charge_ex_tax`)
- ✅ Dynamisk nettarif i `get_nettarif()` med sæson + tidsbestemte takster
- ✅ `beregn_totalpris()` - ny beregningsfunktion uden pandas (arbejder på enkelte poster)
- ✅ Pydantic `ElspotResponse` i brug i `spot_prices.py` (JSON -> model)
- ✅ `hent_stroem_priser()` returnerer `list[dict]` i stedet for DataFrame
- ✅ `cli.py` konverterer kun til DataFrame ved plotting
- ✅ `data/elspot_dk1.json` - reference-data fra Energinet API
- ✅ `scripts/hent_og_gem_json.py` - script til at hente JSON
- ✅ `calculations.py` - ryddet for kommenteret død kode
- ✅ 12 tests (op fra 3) - dækker dynamisk nettarif og beregn_totalpris

## Tilbage

### Næste: Centraliser 2026-workaround
- `2026 -> 2025` workaround ligger i `cli.py:34-36` og `spot_prices.py:21-23`
- Opret fælles utility-funktion i `elpris/control/calculations.py`
- Opdatér AGENTS.md

### Fremtidige
- FastAPI server (`docs/fastapi_plan.md`)
- DuckDB persistence i `data/`
- Integrationstest med mock af API
- Overvej om `pandas` dependency kan droppes (kun brugt til plot i cli.py)
