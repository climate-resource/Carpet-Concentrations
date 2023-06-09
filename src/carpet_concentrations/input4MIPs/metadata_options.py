"""
Metdata options

This module could be refactored so that it is autogenerated from some other
source (or simply be an adapter to some other API) in future to remove the
need for manual updates.

This might be the right source: https://github.com/PCMDI/input4MIPs-cmor-tables
"""
from __future__ import annotations

import re
from collections.abc import Container

ACTIVITY_ID_OPTIONS: tuple[str, ...] = ("input4MIPs",)
"""
Valid options for "activity_id""
"""

CONVENTION_OPTIONS: tuple[str, ...] = ("CF-1.7 CMIP-6.2", "CF-1.6")
"""
Valid options for "Convention""
"""

DATASET_CATEGORY_OPTIONS: tuple[str, ...] = (
    "aerosolProperties",
    "atmosphericState",
    "emissions",
    "GHGConcentrations",
    "landState",
    "ozone",
    "radiation",
    "SSTsAndSeaIce",
    "solar",
    "surfaceAir",
    "surfaceFluxes",
)
"""
Valid options for "dataset_category""
"""

INCLUDES_EMAIL_REGEX: re.Pattern[str] = re.compile(r"^.*?(\S+@\S+\.\S+).*$")
"""
Regular expression that checks there is something like an email somewhere

This is very loose and just provides a basic check to really avoid obvious
typos. It turns out writing a perfect regexp for email addresses is hard (see
e.g. https://stackoverflow.com/questions/201323/how-can-i-validate-an-email-address-using-a-regular-expression)
"""

CREATION_DATE_REGEX: re.Pattern[str] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$"
)
"""
Regular expression that checks the creation date is formatted correctly
"""

UUID_REGEX: re.Pattern[str] = re.compile(
    r"^hdl:21.14100\/[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$"
)
"""
Regular expression that checks the creation date is formatted correctly
"""

FREQUENCY_OPTIONS: Container[str] = (
    "1hr",
    "1hrCM",
    "1hrPt",
    "3hr",
    "3hrPt",
    "6hr",
    "6hrPt",
    "day",
    "dec",
    "fx",
    "mon",
    "monC",
    "monPt",
    "subhrPt",
    "yr",
    "yrC",
    "yrPt",
)
