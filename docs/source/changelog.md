# Changelog

Versions follow [Semantic Versioning](https://semver.org/) (`<major>.<minor>.<patch>`).

Backward incompatible (breaking) changes will only be introduced in major versions
with advance notice in the **Deprecations** section of releases.


<!--
You should *NOT* be adding new changelog entries to this file, this
file is managed by towncrier. See changelog/README.md.

You *may* edit previous changelogs to fix problems like typo corrections or such.
To add a new changelog entry, please see
https://pip.pypa.io/en/latest/development/contributing/#news-entries,
noting that we use the `changelog` directory instead of news, md instead
of rst and use slightly different categories.
-->

<!-- towncrier release notes start -->

## carpet-concentrations v0.5.0 (2023-12-12)


### Improvements

- Added support for "yr" frequency in :func:`format_date` ([#7](https://github.com/climate-resource/Carpet-Concentrations/pulls/7))

### Trivial/Internal Changes

- [#9](https://github.com/climate-resource/Carpet-Concentrations/pulls/9)


## carpet-concentrations v0.4.2 (2023-06-09)

### Fix

- **CHANGELOG.md**: fix typo in CHANGELOG

## carpet-concentrations v0.4.1 (2023-06-09)

### Fix

- **{py:class}`carpet_concentrations.dataset.Input4MIPsMetadata`**: add validation of frequency metadata

## carpet-concentrations v0.4.0 (2023-06-07)

### Feat

- **Makefile**: add licence-check target

## carpet-concentrations v0.3.0 (2023-05-27)

### BREAKING CHANGE

- Removed {py:mod}`carpet_concentrations.unit_registry`

### Feat

- **unit_registry**: remove {py:mod}`carpet_concentrations.unit_registry`

## carpet-concentrations v0.2.1 (2023-05-27)

### Fix

- **src/carpet_concentrations/input4MIPs/dataset.py**: fix up type hint

### Refactor

- remove unused type: ignore

## carpet-concentrations v0.2.0 (2023-05-22)

### Feat

- **src/carpet_concentrations/input4MIPs**: add {py:mod}`carpet_concentrations.input4MIPs` to handle dataset writing
- **LatitudeSeasonalityGridder**: add {py:class}`carpet_concentrations.gridders.latitude_seasonality_gridder.LatitudeSeasonalityGridder`
- **src/carpet_concentrations/time.py**: add {py:mod}`carpet_concentrations.time`
