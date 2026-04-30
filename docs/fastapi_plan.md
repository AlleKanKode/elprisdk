# Plan For Lokal FastAPI Server

## Mål
- Tilføj en lokal HTTP-server, så projektet kan stille elprisdata til rådighed via FastAPI i stedet for kun via CLI og graf.
- Genbrug den eksisterende logik for Energidataservice-opslag og afgiftsberegning i stedet for at duplikere den.
- Behold `main.py` som appens CLI-entrypoint; serveren skal leve under `elpris/` og startes med `uv`.

## Nuværende Udgangspunkt
- Projektet har allerede en fungerende CLI i `elpris/view/cli.py` og entrypoint i `main.py`.
- Data hentes live fra Energidataservice i `elpris/control/spot_prices.py`.
- Afgifter og tidsafrunding ligger i `elpris/control/calculations.py`.
- Pydantic-modeller findes allerede i `elpris/models/`, men de beskriver primært Energinet-responsen og ikke et API-svar til lokale klienter.
- Projektet har endnu ikke FastAPI eller uvicorn som dependency.

## Fase 1: Server Fundament
- Tilføj `fastapi` og `uvicorn` til `pyproject.toml` via `uv`.
- Opret en ny serverpakke under `elpris/server/` i stedet for at lægge HTTP-kode i CLI- eller control-laget.
- Opret mindst disse filer:
  - `elpris/server/app.py`: FastAPI-app og route-registrering
  - `elpris/server/schemas.py`: request/response-modeller for den lokale API
  - `elpris/server/__init__.py`
- Start serveren med en kommando i stil med `uv run uvicorn elpris.server.app:app --reload` under udvikling.

## Fase 2: Flyt Forretningslogik Væk Fra CLI-formen
- Undgå at lade routes arbejde direkte med `print`, `matplotlib` eller rå `DataFrame`-objekter.
- Uddrag eller tilføj en servicefunktion, som returnerer prisdata i en form, der er egnet til både CLI og HTTP-svar.
- Den funktion bør tage eksplicitte parametre som:
  - region (`dk1` eller `dk2`)
  - starttidspunkt
  - sluttidspunkt
  - eventuelt om afgifter skal være med
- Bevar den eksisterende `2026 -> 2025` workaround i serverflowet, medmindre den erstattes bevidst af en bedre strategi.

## Fase 3: Design API-kontrakten
- Start simpelt med få endpoints og udvid senere.
- Anbefalede første endpoints:
  - `GET /health`: simpelt healthcheck
  - `GET /prices/current?region=dk1`: aktuel pris for en region
  - `GET /prices/day?region=dk1`: dagens priser for en region
  - `GET /prices/range?region=dk1&start=...&end=...`: priser for et tidsinterval
- Returner JSON med danske domænefelter kun hvis det giver mening; ellers hold API-felter konsekvente og dokumenterede.
- Fastlæg tidligt om tider skal returneres som:
  - ISO 8601 i dansk tid
  - ISO 8601 i UTC
- Vær konsekvent. Den nemmeste løsning er at returnere ISO-timestamps og tydeligt dokumentere tidszonen.

## Fase 4: Definer Lokale API-modeller
- Opret Pydantic-modeller, der matcher det lokale API og ikke Energinets rå respons 1:1.
- En mulig opdeling er:
  - `PricePoint`: én time med tidspunkt, spotpris og totalpris
  - `CurrentPriceResponse`: region, timestamp og aktuel pris
  - `PriceRangeResponse`: region, start, end og liste af `PricePoint`
  - `ErrorResponse`: fejlbesked og kontekst
- Undgå at eksponere hele pandas-strukturen direkte i API-svarene.

## Fase 5: Fejlhåndtering
- Erstat `print`-baseret fejlrapportering i serverlaget med HTTP-fejl.
- Konverter typiske fejl til tydelige statuskoder:
  - ugyldig region -> `422` eller `400`
  - ingen data fra upstream -> `404` eller `502`, afhængigt af årsagen
  - upstream netværksfejl -> `502`
  - intern fejl i beregning/serialisering -> `500`
- Overvej at indføre egne exceptions i control/service-laget, så FastAPI-routes kan mappe dem til stabile HTTP-svar.

## Fase 6: Teststrategi
- Behold `uv run pytest` som standardkommando.
- Tilføj API-tests med FastAPIs `TestClient`.
- Mock Energidataservice-kald i servertests, så test ikke afhænger af live netværk.
- Start med disse tests:
  - `GET /health` returnerer `200`
  - `GET /prices/current` returnerer forventet JSON-format
  - ugyldig region giver valideringsfejl
  - tomt upstream-svar bliver til en kontrolleret HTTP-fejl
  - 2026-workarounden bryder ikke route-flowet

## Fase 7: Kørsel Og Verifikation
- Bevar eksisterende verifikation:
  - `uv run pytest`
  - `uv run main.py --no-show`
- Tilføj serververifikation:
  - `uv run uvicorn elpris.server.app:app --reload`
- Manuel kontrol i browser eller med `curl`:
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:8000/docs`
  - `http://127.0.0.1:8000/prices/day?region=dk1`

## Fase 8: Mulige Udvidelser Efter Første Version
- Cache dagens API-svar kortvarigt for at undgå unødige kald mod Energidataservice.
- Tilføj endpoint for begge regioner i samme kald.
- Tilføj vedvarende lagring i `data/` hvis DuckDB skal være en reel del af serverens flow.
- Tilføj simple metrics eller struktureret logging, hvis serveren skal bruges mere end lokalt.

## Foreslået Implementeringsrækkefølge
1. Tilføj dependencies for FastAPI-serveren.
2. Opret `elpris/server/app.py` med `GET /health`.
3. Flyt eller udtræk en genbrugelig servicefunktion, som returnerer serialiserbare prisdata.
4. Implementer `GET /prices/day` for én region.
5. Implementer `GET /prices/current` oven på samme service.
6. Tilføj API-tests med mocks.
7. Tilføj `GET /prices/range` hvis behovet stadig er der.

## Vigtige Repo-Hensyn
- Følg repo-reglen om `uv`; brug ikke `pip`.
- Læg ny produktionskode under `elpris/` og tests under `tests/`.
- Bevar danske brugerrettede tekster, medmindre opgaven eksplicit er at oversætte dem.
- Undgå at bygge serveren oven på notebook- eller `temp/`-kode; det er ikke hovedflowet i repoet.
