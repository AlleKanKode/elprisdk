# AGENTS.md

## Setup
- Brug `uv` til dependencies og kommandoer. Undga `pip`; repo-reglen i `.agents/rules/basic-rules.md` siger at dependencies skal handteres med `uv`.
- Projektet kraver Python `3.13` (`.python-version`, `pyproject.toml`).

## Run And Verify
- Start appen med `uv run main.py`.
- Headless verifikation: `uv run main.py --no-show`.
- Kør tests med `uv run pytest`.
- Der er ingen verificeret lint-, typecheck- eller CI-konfiguration i repoet. Opfind ikke ekstra obligatoriske checks.

## Structure
- Produktionskode hører under `elpris/`.
- Tests hører under `tests/`.
- Root-level Python entrypoint skal være `main.py`; repo-reglerne forventer, at det er den eneste Python-fil i roden til opstart.
- Den faktiske lagdeling er:
  - `elpris/view/cli.py`: CLI-argumenter og plotting
  - `elpris/control/spot_prices.py`: hentning fra Energidataservice
  - `elpris/control/calculations.py`: afrunding og afgiftsberegning
  - `elpris/models/`: Pydantic-, enum- og afgiftsmodeller

## Repo Quirks
- Dato-logikken har en bevidst `2026 -> 2025` workaround i bade `elpris/view/cli.py` og `elpris/control/spot_prices.py`, fordi miljoets systemtid ligger foran tilgængelige Energidataservice-data. Bevar eller erstat den bevidst, hvis du rører dato-handteringen.
- Bevar danske domanenavne og brugerrettede tekster, medmindre opgaven eksplicit er at oversatte dem.
- `temp/` indeholder scratch/prototype-kode og er ikke en del af den pakkede applikation (`pyproject.toml` udelukker `temp*`).
- `elpris/notebooks/` og `__marimo__/` bruges til Marimo-notebooks, men er ikke hoved-entrypoint for appen.
- Der er en DuckDB dependency og en repo-regel om data i `data/`, men den nuværende hovedapp bruger live API-kald og plotting; DuckDB-flowet lever i scratch-kode under `temp/`.

## Tests
- Testdakningen er lille. `tests/test_taxes.py` er den eneste test med reelle assertions.
- `tests/test_models_energinet.py` er i praksis tom, så et grønt test-run er ikke stærk evidens for korrekthed.
