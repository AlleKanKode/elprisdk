# Codebase Compliance Refactoring Plan

## Goal Description
Refactor the current `elpris` project to comply with workspace rules (`.agents/rules/basic-rules.md` and `.agents/rules/structure.md`). This involves restructuring the file organization, splitting the monolithic `elpris.py` into a proper package structure (Models-View-Control), and ensuring the root directory contains only `main.py` as a Python entry point.

## User Review Required
> [!WARNING]
> The workspace rules state "Project code must be placed under **blackstat** package folder".
> Currently, the package is named `elpris`. To avoid massive renaming and confusing the current setup (`pyproject.toml`, directory names), I will keep the package as `elpris` for now properly structured.
> **If you strictly require the folder to be named `blackstat`, please let me know.** Otherwise, I will proceed with `elpris` as the package name.

## Proposed Changes

### Directory Structure
- Create `docs/` folder (for documentation).
- Create `data/` folder (for data storage).
- Create `elpris/view/` folder (for UI/Plotting logic).

### Code Migration
#### [MODIFY] [elpris.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris.py) -> [DELETE]
- This file will be dismantled and its contents moved to the `elpris` package.

#### [NEW] [elpris/models/taxes.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris/models/taxes.py)
- Will contain the `TaxAndFees` class.

#### [NEW] [elpris/control/spot_prices.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris/control/spot_prices.py)
- Will contain `hent_spotpriser` and `hent_stroem_priser` functions.
- Will replace the broken `elpris/control/requests.py`.

#### [NEW] [elpris/control/calculations.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris/control/calculations.py)
- Will contain `apply_taxes` and `round_down_to_hour`.

#### [NEW] [elpris/view/cli.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris/view/cli.py)
- Will contain `vis_aktuel_pris_og_graf` and `parse_arguments`.

#### [NEW] [main.py](file:///home/henrik/source/akk/live/ts39/elpris/main.py)
- Will be the new entry point.
- Imports `parse_arguments` and `vis_aktuel_pris_og_graf` from `elpris.view.cli`.
- Runs the application logic.

#### [MODIFY] [elpris/control/requests.py](file:///home/henrik/source/akk/live/ts39/elpris/elpris/control/requests.py) -> [DELETE]
- This file is incomplete/broken and will be replaced by `spot_prices.py`.

## Verification Plan

### Automated Tests
- Create a new test `tests/test_taxes.py` to verify `TaxAndFees` logic works after moving.
- Run `pytest` to ensure no import errors and logic holds.

### Manual Verification
- Run `uv run main.py --no-show` (or just `python main.py --no-show`) to verify the CLI works and generates the graph image without errors.
- Verify `docs/` and `data/` folders exist.
