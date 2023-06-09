# Changelog

## v0.4.1 (2023-06-09)

### Fix

- **{py:clas}`carpet_concentrations.dataset.Input4MIPsMetadata`**: add validation of frequency metadata

## v0.4.0 (2023-06-07)

### Feat

- **Makefile**: add licence-check target

## v0.3.0 (2023-05-27)

### BREAKING CHANGE

- Removed {py:mod}`carpet_concentrations.unit_registry`

### Feat

- **unit_registry**: remove {py:mod}`carpet_concentrations.unit_registry`

## v0.2.1 (2023-05-27)

### Fix

- **src/carpet_concentrations/input4MIPs/dataset.py**: fix up type hint

### Refactor

- remove unused type: ignore

## v0.2.0 (2023-05-22)

### Feat

- **src/carpet_concentrations/input4MIPs**: add {py:mod}`carpet_concentrations.input4MIPs` to handle dataset writing
- **LatitudeSeasonalityGridder**: add {py:class}`carpet_concentrations.gridders.latitude_seasonality_gridder.LatitudeSeasonalityGridder`
- **src/carpet_concentrations/time.py**: add {py:mod}`carpet_concentrations.time`
