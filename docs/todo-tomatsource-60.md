# Plan: Fix af afgiftsberegningen

## Baggrund

Dokumentet beskriver en plan for at løse fejl i afgiftsberegningen i `elpris` projektet. Planen er baseret på gennemgang af koden og ønsket om at få en ren beregningsfunktion uden pandas, der arbejder direkte med API-json.

Funderede bugs i `elpris/models/taxes.py`:

- `add_tarrifs` ignorerer `charge_time` og bruger statisk `self._nettarif` (0.213) i stedet for den tidsafhængige nettarif
- `get_elafgift()` returnerer `self._elafgift * 2` (1.398), men `add_tarrifs` bruger `self._elafgift` (0.699)
- `add_taxes` har stavefejl: `carge_ex_tax` -> `charge_ex_tax`

Derudover:

- `calculations.py` er fyldt med kommenteret kode og forvirring om hvordan `add_tarrifs` skal kaldes
- Testdækningen er meget lav for tidsafhængige takster

## Plan

### Step 1: Fix `TaxAndFees` class (`elpris/models/taxes.py`)

1a. `add_tarrifs` skal bruge `self.get_nettarif(charge_time)` i stedet for `self._nettarif`, så hver time får korrekt tidsafhængig nettarif (vinter/sommer, peak/høj/lav).

1b. Afklar elafgift. To muligheder:
   - **Mulighed A**: `get_elafgift()` fjerner `* 2`, returnerer `self._elafgift` = 0.699. `add_tarrifs` bruger `self.get_elafgift()`.
   - **Mulighed B**: `add_tarrifs` bruger `self.get_elafgift()` (1.398). Prisen stiger med 0.699 kr/kWh.
   - Uanset hvad: `add_tarrifs` skal bruge getter-metoderne konsekvent.

1c. Fix stavefejl: `carge_ex_tax` -> `charge_ex_tax`.

### Step 2: Ny ren beregningsfunktion (`elpris/control/calculations.py`)

Opret `beregn_totalpris` der arbejder på enkelte poster uden pandas:

```
beregn_totalpris(spot_price_dkk_per_mwh: float, hour_dk: datetime) -> dict
```

Returnerer dict med:
- `hour_dk`: datetime
- `spotpris_kwh`: float (spotpris / 1000)
- `elafgift`: float
- `systemtarif`: float (0.054)
- `nettarif`: float (tidsafhængig, beregnet via `get_nettarif`)
- `transmissionstarif`: float (0.07)
- `total_ex_moms`: float (sum af ovenstående)
- `moms`: float (25% af total_ex_moms)
- `total_med_moms`: float

Bruger `TaxAndFees` internt. Modtager spotpris i kr/MWh (som API'et returnerer) og selv konverterer til kr/kWh.

### Step 3: Opdater `elpris/control/spot_prices.py`

- Parse API-json med Pydantic-modellen `ElspotResponse` (findes i `elpris_models.py`)
- Anvend `beregn_totalpris` på hver `ElspotRecord`
- Returner liste af dicts med prisdata (ikke DataFrame)
- Fjern pandas DataFrame-bygning fra dette lag
- Bevar 2026 -> 2025 workaround

### Step 4: Opdater `elpris/view/cli.py`

- Modtag liste af dicts fra `hent_stroem_priser`
- Konverter til DataFrame kun til plotting (matplotlib kræver det)
- Bevar eksisterende plot-logik

### Step 5: Opdater tests (`tests/test_taxes.py`)

- Test `add_tarrifs` med vinter peak (okt 17:00) -> nettarif = 0.4649
- Test `add_tarrifs` med sommer lav (jul 02:00) -> nettarif = 0.0517
- Test `add_tarrifs` med sommer høj (jun 10:00) -> nettarif = 0.0774
- Test `beregn_totalpris` med kendte værdier
- Opdater `test_tax_and_fees_default_values` hvis elafgift ændres

### Step 6: Oprydning

- Fjern al kommenteret kode fra `calculations.py` (linje 39-76)
- Fjern `apply_taxes` funktionen (erstattes af `beregn_totalpris`)
- Fjern `round_down_to_hour` hvis den ikke bruges andetsteds (bruges i `cli.py:38`)

## Åbent spørgsmål

Elafgiften: Skal den være 0.699 eller 1.398 kr/kWh? Det afgør om `get_elafgift()` skal rettes (`* 2` fjernes) eller om `add_tarrifs` skal bruge getteren. Kræver en afklaring om den aktuelle danske elafgiftssats.
