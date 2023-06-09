"""
Tools for helping with :mod:`xarray`
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import xarray as xr

from carpet_concentrations.attrs_utils import (
    make_attrs_validator_compatible_single_input,
)
from carpet_concentrations.exceptions import (
    CoordinateError,
    DatasetIncompatibleUnitsError,
)

if TYPE_CHECKING:
    from collections.abc import Hashable


def check_dimensions(
    inp: xr.DataArray, exp_dims: tuple[Hashable, ...], extras_ok: bool = False
) -> None:
    """
    Check dimensions of an :obj:`xr.DataArray`

    Parameters
    ----------
    inp
        Data to check

    exp_dims
        Dimensions we expect the data to have

    extras_ok
        Is it ok if there are other dimensions present in the data,
        beyond those specified in ``extra_dims``?

    Raises
    ------
    CoordinateError
        Dimensions aren't as expected
    """
    dims = inp.dims

    if extras_ok:
        problem = not set(exp_dims).issubset(set(dims))
    else:
        problem = set(exp_dims) != set(dims)

    if problem:
        raise CoordinateError(exp_dims, dims, inp, extras_ok)


def calculate_weighted_area_mean_latitude_only(
    inp: xr.Dataset,
    variables: list[str],
    bounds_dim_name: str = "bounds",
    lat_name: str = "lat",
    lat_bounds_name: str = "lat_bounds",
) -> xr.Dataset:
    """
    Calculate area mean based on only latitude information

    See :footcite:t:`kelly_savric_2020_computation`

    Parameters
    ----------
    inp
        :obj:`xr.Dataset` to process

    variables
        Variables of which to calculate the area-mean

    bounds_dim_name
        Name of the dimension which defines bounds

    lat_name
        Name of the latitude dimension

    lat_bounds_name
        Name of the latitude bounds variable

    Returns
    -------
        :obj:`xr.Dataset` with area-weighted mean of ``variables``
    """
    lat_bnds = inp[lat_bounds_name].pint.to("radian")

    # as they are constants, r^2 and longitude factors drop out
    # in area weights. Would have to be more careful with
    # longitudes if on a non-uniform grid.
    area_weighting = np.sin(lat_bnds).diff(dim=bounds_dim_name).squeeze()

    area_weighted_mean = (inp[variables] * area_weighting).sum(
        lat_name
    ) / area_weighting.sum(lat_name)

    # #8: allow dependency injection here
    keys_to_check = list(inp.data_vars.keys()) + list(inp.coords.keys())
    other_stuff = [v for v in keys_to_check if v not in variables]
    out = xr.merge([area_weighted_mean, inp[other_stuff]])

    return out


def check_all_units_compatible(ds: xr.Dataset) -> None:
    """
    Check all units in an :obj:`xr.Dataset` are compatible

    This only checks the data variables, not units of co-ordinates or
    dimensions.

    Here compatible means the units can be converted into one another

    Parameters
    ----------
    ds
        Dataset to check

    Raises
    ------
    DatasetIncompatibleUnitsError
        Some of the units in the dataset are incompatible
    """
    # #9: add dependency injection
    data_var_units = [
        v.data.units for v in ds.data_vars.values() if hasattr(v.data, "units")
    ]

    base_unit = data_var_units[0]
    for data_var_unit in data_var_units[1:]:
        if not data_var_unit.is_compatible_with(base_unit):
            raise DatasetIncompatibleUnitsError(base_unit, data_var_unit, ds)


check_all_units_compatible_attrs = make_attrs_validator_compatible_single_input(
    check_all_units_compatible
)
