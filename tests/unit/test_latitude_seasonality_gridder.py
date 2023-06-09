"""
Test :class:`carpet_concentrations.gridders.LatitudeSeasonalityGridder`
"""
import re

import cf_xarray  # noqa: F401 # required to add cf accessors
import numpy as np
import pint.errors
import pint_xarray
import pytest
import xarray as xr
from openscm_units import unit_registry

from carpet_concentrations.exceptions import (
    CoordinateError,
    DatasetIncompatibleUnitsError,
    NotPintQuantifiedError,
)
from carpet_concentrations.gridders import LatitudeSeasonalityGridder

pint_xarray.accessors.default_registry = pint_xarray.setup_registry(unit_registry)


@pytest.fixture
def default_years():
    return np.array([1750, 1751])


@pytest.fixture
def default_months():
    return np.arange(1, 13)


@pytest.fixture
def default_lats():
    return np.array([-60, 0, 60])


@pytest.fixture()
def valid_input(default_years, default_months, default_lats):
    latitudinal_gradient = np.array(
        [
            np.broadcast_to([-1, 0, 1], (12, 3)),
            np.broadcast_to([-1, 0, 1], (12, 3)),
        ]
    )

    seasonality = np.broadcast_to(
        np.array(
            [
                [0, 1, 2, 2, 1, 0, 0, -1, -2, -2, -1, 0],
                [0, 1, 2, 2, 1, 0, 0, -1, -2, -2, -1, 0],
            ]
        ),
        (3, 2, 12),
    ).copy()

    inp = (
        xr.Dataset(
            {
                "latitudinal_gradient": (
                    (
                        "year",
                        "month",
                        "lat",
                    ),
                    latitudinal_gradient,
                    {"units": "ppm"},
                ),
                "seasonality": (
                    ("lat", "year", "month"),
                    seasonality,
                    {"units": "ppm"},
                ),
            },
            coords={
                "year": default_years,
                "lat": default_lats,
                "month": default_months,
            },
        )
        .cf.add_bounds("lat")
        .pint.quantify({"lat_bounds": "deg"})
    )

    return inp


@pytest.fixture
def valid_global_means(default_years, default_months):
    # Global means have to be on a monthly timestep before they can be used
    global_means = np.arange(1, default_years.size * default_months.size + 1).reshape(
        (default_years.size, default_months.size)
    )

    global_means = xr.Dataset(
        {
            "Atmospheric Concentrations|CO2": (
                ("year", "month"),
                global_means,
                {"units": "ppm"},
            ),
        },
        coords={"year": default_years, "month": default_months},
    ).pint.quantify()

    return global_means


def test_valid_no_error(valid_input, valid_global_means):
    LatitudeSeasonalityGridder(valid_input).calculate(valid_global_means)


def test_valid_multi_dim_input(valid_input, valid_global_means):
    scenarios = xr.DataArray(
        [1, 2],
        coords={"scenario": ["a", "b"]},
        attrs={"units": "dimensionless"},
    ).pint.quantify()

    inp = valid_input * scenarios
    inp0 = inp.sel(scenario=["a"])
    inp1 = inp.sel(scenario=["b"])

    global_means = valid_global_means * scenarios
    global_means0 = global_means.sel(scenario=["a"])
    global_means1 = global_means.sel(scenario=["b"])

    res0 = LatitudeSeasonalityGridder(inp0).calculate(global_means0)
    res1 = LatitudeSeasonalityGridder(inp1).calculate(global_means1)
    res = LatitudeSeasonalityGridder(inp).calculate(global_means)

    xr.testing.assert_equal(
        res0.sel(scenario="a"),
        res.sel(scenario="a"),
    )

    xr.testing.assert_equal(
        res1.sel(scenario="b"),
        res.sel(scenario="b"),
    )


def test_latitude_seasonality_gridder():
    lats = [-60, 0, 60]
    latitudinal_gradient = np.broadcast_to(
        np.array(
            [
                [-1, 0, 1],
                [-1, 0, 1],
            ]
        ),
        (12, 2, 3),
    ).transpose([1, 0, 2])
    seasonality = np.broadcast_to(
        np.array(
            [
                [0, 1, 2, 2, 1, 0, 0, -1, -2, -2, -1, 0],
                [0, 1, 2, 2, 1, 0, 0, -1, -2, -2, -1, 0],
            ]
        ),
        (3, 2, 12),
    ).transpose([1, 2, 0])
    years = np.array([2020, 2030])
    months = np.arange(1, 13)
    # Global means have to be on a monthly timestep before they can be used
    global_means = np.arange(1, 25).reshape((years.size, months.size))
    name = "Atmospheric Concentrations|CO2"

    exp = latitudinal_gradient + seasonality + global_means[:, :, np.newaxis]

    inp = (
        xr.Dataset(
            {
                "latitudinal_gradient": (
                    (
                        "year",
                        "month",
                        "lat",
                    ),
                    latitudinal_gradient,
                    {"units": "ppm"},
                ),
                "seasonality": (
                    ("year", "month", "lat"),
                    seasonality,
                    {"units": "ppm"},
                ),
            },
            coords={"year": years, "lat": lats, "month": months},
        )
        .cf.add_bounds("lat")
        .pint.quantify({"lat_bounds": "deg"})
    )

    global_means = xr.Dataset(
        {
            name: (("year", "month"), global_means, {"units": "ppm"}),
        },
        coords={"year": years, "month": months},
    ).pint.quantify()

    res = LatitudeSeasonalityGridder(inp).calculate(global_means)

    exp = xr.Dataset(
        {name: (("year", "month", "lat"), exp, {"units": "ppm"})},
        coords={"year": years, "lat": lats, "month": months},
    ).pint.quantify()

    xr.testing.assert_equal(exp, res)


@pytest.mark.parametrize(
    "seasonality_name,seasonality_name_exp",
    (
        (None, "seasonality"),
        ("hi", "hi"),
    ),
)
def test_error_seasonality_missing(seasonality_name, seasonality_name_exp, valid_input):
    inp = valid_input.drop_vars("seasonality")

    init_kwargs = {"gridding_values": inp}
    if seasonality_name is not None:
        init_kwargs["seasonality_name"] = seasonality_name

    with pytest.raises(KeyError, match=seasonality_name_exp):
        LatitudeSeasonalityGridder(**init_kwargs)


@pytest.mark.parametrize(
    "latitudinal_gradient_name,latitudinal_gradient_name_exp",
    (
        (None, "latitudinal_gradient"),
        ("hi", "hi"),
    ),
)
def test_error_latitudinal_gradient_missing(
    latitudinal_gradient_name, latitudinal_gradient_name_exp, valid_input
):
    inp = valid_input.drop_vars("latitudinal_gradient")

    init_kwargs = {"gridding_values": inp}
    if latitudinal_gradient_name is not None:
        init_kwargs["latitudinal_gradient_name"] = latitudinal_gradient_name

    with pytest.raises(KeyError, match=latitudinal_gradient_name_exp):
        LatitudeSeasonalityGridder(**init_kwargs)


def test_error_seasonality_wrong_dimensions(valid_input):
    inp = valid_input.mean("month")

    error_msg = re.escape(
        "Expected dimensions: `('year', 'month', 'lat')`. "
        "These are not a subset of the found dimensions: `('lat', 'year')`"
    )
    with pytest.raises(CoordinateError, match=error_msg):
        LatitudeSeasonalityGridder(inp)


def test_error_seasonality_annual_mean_non_zero(valid_input):
    inp = valid_input.copy()
    inp["seasonality"] += unit_registry.Quantity(1, "ppm")

    error_msg = re.escape("seasonality must have an annual-mean of zero in all years")
    with pytest.raises(AssertionError, match=error_msg):
        LatitudeSeasonalityGridder(inp)


def test_error_latitudinal_gradient_wrong_dimensions(valid_input):
    inp = valid_input
    inp["latitudinal_gradient"] = inp["latitudinal_gradient"].mean("lat")

    error_msg = re.escape(
        "Expected dimensions: `('year', 'month', 'lat')`. "
        "These are not a subset of the found dimensions: `('year', 'month')`"
    )
    with pytest.raises(CoordinateError, match=error_msg):
        LatitudeSeasonalityGridder(inp)


def test_error_latitudinal_gradient_spatial_mean_non_zero(valid_input):
    inp = valid_input.copy()
    inp["latitudinal_gradient"] += unit_registry.Quantity(1, "ppm")

    error_msg = re.escape(
        "latitudinal gradient must have an area-weighted spatial-mean of "
        "zero in all timesteps"
    )
    with pytest.raises(AssertionError, match=error_msg):
        LatitudeSeasonalityGridder(inp)


@pytest.mark.parametrize(
    "seasonality_units,latitudinal_gradient_units,exp_error",
    (
        ("ppm", "ppm", False),
        ("ppm", "ppb", False),
        ("ppm", "kg", True),
    ),
)
def test_error_seasonality_latitudinal_gradient_different_units(
    seasonality_units, latitudinal_gradient_units, exp_error, valid_input
):
    inp = valid_input.pint.dequantify().pint.quantify(
        seasonality=seasonality_units,
        latitudinal_gradient=latitudinal_gradient_units,
    )

    if exp_error:
        error_msg = re.escape("kilogram is not compatible with ppm")
        with pytest.raises(DatasetIncompatibleUnitsError, match=error_msg):
            LatitudeSeasonalityGridder(inp)
    else:
        LatitudeSeasonalityGridder(inp)


def test_error_inp_not_quantified(valid_input):
    inp = valid_input.pint.dequantify()

    error_msg = re.escape(
        "latitudinal_gradient must have been quantified with "
        "pint using e.g. ``.pint.quantify()"
    )
    with pytest.raises(NotPintQuantifiedError, match=error_msg):
        LatitudeSeasonalityGridder(inp)


def test_error_global_means_not_quantified(valid_input, valid_global_means):
    error_msg = re.escape(
        f"{list(valid_global_means.keys())[0]} must have been quantified "
        "with pint using e.g. ``.pint.quantify()"
    )
    with pytest.raises(NotPintQuantifiedError, match=error_msg):
        LatitudeSeasonalityGridder(valid_input).calculate(
            valid_global_means.pint.dequantify()
        )


def test_error_global_means_not_on_year_month_coords(valid_input, valid_global_means):
    error_msg = re.escape(
        "Expected dimensions: `('year', 'month')`. These are not a subset "
        "of the found dimensions: `('year',)`"
    )
    with pytest.raises(CoordinateError, match=error_msg):
        LatitudeSeasonalityGridder(valid_input).calculate(
            valid_global_means.mean("month")
        )


def test_multiple_scenarios_handling(valid_input, valid_global_means):
    scenarios = xr.DataArray(
        [1, 0.8, 2],
        coords={"scenario": ["ssp126", "ssp245", "ssp370"]},
        attrs={"units": "dimensionless"},
    ).pint.quantify()

    global_means = valid_global_means * scenarios
    res = LatitudeSeasonalityGridder(valid_input).calculate(global_means)

    assert set(res.dims) == {"year", "lat", "scenario", "month"}
    for scenario, sds in res.groupby("scenario"):
        scen_specific_calc = LatitudeSeasonalityGridder(valid_input).calculate(
            valid_global_means * scenarios.sel(scenario=scenario).data.magnitude
        )

        xr.testing.assert_equal(sds.drop_vars("scenario"), scen_specific_calc)


def test_dims_conflict(valid_input, valid_global_means):
    # No error, but missing dims are dropped.
    # This is in line with xarray so leaving as is
    inp = (
        valid_input
        * xr.DataArray(
            [1, 1, 1],
            coords={"scenario": ["a", "b", "c"]},
            attrs={"units": "dimensionless"},
        ).pint.quantify()
    )

    global_means = (
        valid_global_means
        * xr.DataArray(
            [1, 1, 1],
            coords={"scenario": ["a", "b", "d"]},
            attrs={"units": "dimensionless"},
        ).pint.quantify()
    )

    res = LatitudeSeasonalityGridder(inp).calculate(global_means)

    assert list(res["scenario"].values) == ["a", "b"]


def test_missing_timepoints_global_mean(valid_input, valid_global_means):
    sel_months = [1, 3, 6, 12]
    global_means = valid_global_means.sel(month=sel_months)
    res = LatitudeSeasonalityGridder(valid_input).calculate(global_means)

    np.testing.assert_equal(res["month"].values, sel_months)


def test_unit_conversion(valid_input, valid_global_means):
    global_means_ppb = valid_global_means.pint.to("ppb")

    res = LatitudeSeasonalityGridder(valid_input).calculate(global_means_ppb)
    res_no_unit_conversion = LatitudeSeasonalityGridder(valid_input).calculate(
        valid_global_means
    )

    for v in res.data_vars.values():
        assert v.data.units == "ppb"

    xr.testing.assert_equal(res, res_no_unit_conversion.pint.to("ppb"))


def test_incompatible_units(valid_input, valid_global_means):
    global_means = valid_global_means.pint.dequantify()
    for k in global_means.data_vars:
        global_means[k].attrs["units"] = "kg"

    global_means = global_means.pint.quantify()

    error_msg = re.escape(
        "Cannot convert from 'kilogram' ([mass]) to 'ppm' ([concentrations])"
    )
    with pytest.raises(pint.errors.DimensionalityError, match=error_msg):
        LatitudeSeasonalityGridder(valid_input).calculate(global_means)
