"""
Tools for helping with :mod:`xarray_pint`
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pint

from carpet_concentrations.attrs_utils import (
    make_attrs_validator_compatible_single_input,
)
from carpet_concentrations.exceptions import NotPintQuantifiedError

if TYPE_CHECKING:
    import xarray as xr


def check_pint_quantified_array(inp: xr.DataArray) -> None:
    """
    Check that input can be converted using pint

    Parameters
    ----------
    inp
        Data to check

    Raises
    ------
    NotPintQuantifiedError
        ``inp`` is not pint compatible i.e. has not already been converted
        using pint via e.g. ``.pint.quantify()``
    """
    if not isinstance(inp.data, pint.registry.Quantity):
        raise NotPintQuantifiedError(inp)


def check_pint_quantified_dataset(inp: xr.Dataset) -> None:
    """
    Check that all variables in an :obj:`xr.Dataset` can be converted using pint

    Parameters
    ----------
    inp
        Data to check
    """
    for val in inp.values():
        check_pint_quantified_array(val)


check_pint_quantified_array_attrs = make_attrs_validator_compatible_single_input(
    check_pint_quantified_array
)

check_pint_quantified_dataset_attrs = make_attrs_validator_compatible_single_input(
    check_pint_quantified_dataset
)
