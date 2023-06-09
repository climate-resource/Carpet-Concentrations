"""
Test :mod:`carpet_concentrations.xarray_utils`
"""
import re

import pytest
import xarray as xr

from carpet_concentrations.exceptions import CoordinateError
from carpet_concentrations.xarray_utils import check_dimensions


@pytest.mark.parametrize(
    ["inp", "exp_dims", "extras_ok", "exp_error_msg"],
    (
        (
            xr.DataArray(
                [[1, 2]],
                coords={"year": [2010], "scenario": ["a", "b"]},
                attrs={"units": "dimensionless"},
            ),
            ("year",),
            False,
            re.escape(
                "Expected dimensions: `('year',)`. These are not equal to the "
                "found dimensions: `('year', 'scenario')`."
            ),
        ),
        (
            xr.DataArray(
                [[1, 2]],
                coords={"year": [2010], "scenario": ["a", "b"]},
                attrs={"units": "dimensionless"},
            ),
            ("year",),
            True,
            None,
        ),
        (
            xr.DataArray(
                [[1, 2]],
                coords={"year": [2010], "scenario": ["a", "b"]},
                attrs={"units": "dimensionless"},
            ),
            ("year", "lat"),
            True,
            re.escape(
                "Expected dimensions: `('year', 'lat')`. These are not a "
                "subset of the found dimensions: `('year', 'scenario')`."
            ),
        ),
        (
            xr.DataArray(
                [[1, 2]],
                coords={"year": [2010], "scenario": ["a", "b"]},
                attrs={"units": "dimensionless"},
            ),
            ("year", "lat"),
            False,
            re.escape(
                "Expected dimensions: `('year', 'lat')`. These are not "
                "equal to the found dimensions: `('year', 'scenario')`."
            ),
        ),
    ),
)
def test_check_dimensions(inp, exp_dims, extras_ok, exp_error_msg):
    if exp_error_msg:
        with pytest.raises(CoordinateError, match=exp_error_msg):
            check_dimensions(inp, exp_dims, extras_ok)
    else:
        assert check_dimensions(inp, exp_dims, extras_ok) is None
