"""
Gridder based on pre-calculated latitudinal gradient and seasonality
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

import numpy as np
from attrs import define, field

from carpet_concentrations.attrs_utils import (
    make_attrs_validator_compatible_value_instance_input,
)
from carpet_concentrations.xarray_pint_utils import (
    check_pint_quantified_dataset,
    check_pint_quantified_dataset_attrs,
)
from carpet_concentrations.xarray_utils import (
    calculate_weighted_area_mean_latitude_only,
    check_all_units_compatible_attrs,
    check_dimensions,
)

if TYPE_CHECKING:
    import xarray as xr


def _attribute_has_year_month_lat_coords(
    instance: Any,
    value: xr.Dataset,
    attr_to_get: str,
) -> None:
    check_dimensions(
        value[getattr(instance, attr_to_get)], ("year", "month", "lat"), extras_ok=True
    )


_seasonality_has_year_month_lat_coords = (
    make_attrs_validator_compatible_value_instance_input(
        partial(_attribute_has_year_month_lat_coords, attr_to_get="seasonality_name")
    )
)


_latitudinal_gradient_has_year_month_lat_coords = (
    make_attrs_validator_compatible_value_instance_input(
        partial(
            _attribute_has_year_month_lat_coords,
            attr_to_get="latitudinal_gradient_name",
        )
    )
)


def _seasonality_annual_mean_zero(
    instance: Any,
    value: xr.Dataset,
) -> None:
    seasonality = value[instance.seasonality_name]
    np.testing.assert_allclose(
        seasonality.mean("month").data.magnitude,
        0,
        atol=1e-8,
        err_msg="seasonality must have an annual-mean of zero in all years",
    )


_seasonality_annual_mean_zero_attrs = (
    make_attrs_validator_compatible_value_instance_input(_seasonality_annual_mean_zero)
)


def _latitudinal_gradient_spatial_mean(
    instance: Any,
    value: xr.Dataset,
) -> None:
    np.testing.assert_allclose(
        calculate_weighted_area_mean_latitude_only(
            value, [instance.latitudinal_gradient_name]
        )[instance.latitudinal_gradient_name].data.magnitude,
        0,
        atol=1e-8,
        err_msg=(
            "latitudinal gradient must have an area-weighted spatial-mean "
            "of zero in all timesteps"
        ),
    )


_latitudinal_gradient_spatial_mean_zero_attrs = (
    make_attrs_validator_compatible_value_instance_input(
        _latitudinal_gradient_spatial_mean
    )
)


@define
class LatitudeSeasonalityGridder:
    """
    Gridder based on specified latitudinal gradient and seasonality
    """

    gridding_values: xr.Dataset = field(
        validator=[
            check_pint_quantified_dataset_attrs,
            _seasonality_has_year_month_lat_coords,
            _seasonality_annual_mean_zero_attrs,
            _latitudinal_gradient_has_year_month_lat_coords,
            _latitudinal_gradient_spatial_mean_zero_attrs,
            check_all_units_compatible_attrs,
        ]
    )
    """
    Values to use to convert global-mean concentrations to a grid

    This should have already been turned into a pint-compatiable quantity using
    ``pint.quantify`` or similar. It should also contain variables that match
    the value of ``seasonality_name`` and ``latitudinal_gradient_name``. Both
    the variables must have at least the dimensions ("year", "month", "lat").
    The seasonality variable must have an annual-mean of zero. The latitudinal
    gradient must have a spatial-mean of zero.
    """

    seasonality_name: str = "seasonality"
    """
    Name of the seasonality variable (in ``gridding_values`` but also used
    elsewhere)
    """

    latitudinal_gradient_name: str = "latitudinal_gradient"
    """
    Name of the latitudinal gradient variable (in ``gridding_values`` but also
    used elsewhere)
    """

    def calculate(self, global_means: xr.Dataset) -> xr.Dataset:
        r"""
        Calculate gridded values

        Parameters
        ----------
        global_means
            Global-mean values. These should have already been interpolated
            such that their dimensions are ``("year", "month")`` (other
            dimensions e.g. ``"scenario"`` are also ok) to obtain sensible
            results (if not, there may be jumps at the start and end of years).
            ``global_means`` should have also already been turned into a
            pint-compatiable quantity using ``pint.quantify`` or similar.

        Returns
        -------
            Gridded values on a ``("latitude", "year", "month")`` grid (plus
            any other dimensions present in ``global_means``)

        Raises
        ------
        CoordinateError
            ``global_means`` does not have at least the dimensions of
            ``("year", "month")`` (other dimensions e.g. ``"scenario"`` are
            also ok)

        NotPintQuantifiedError
            ``global_means`` has not been quantified using ``pint.quantify`` or
            similar

        Notes
        -----
        Eq. 1 of :footcite:t:`meinshausen_et_al_2017_concentrations`. We use
        slightly different notation here for clarity.

        .. math::

            C(l, m, y, ...) = \overline{C(m, y, ...)} + S(l, m, y) + L(l, m, y)

        i.e. the concentration at latitude :math:`l` in year :math:`y` and
        month :math:`m` is the sum of the global-, annual-mean concentration in
        that year (already interpolated down to a monthly timestep), the
        seasonality at that latitude in that year in that month (varies with
        year and latitude as often scaled with something else) and the
        latitudinal gradient at that latitude in that year and month (varies
        with year and month as often scaled with something else, must
        have monthly information to avoid step changes in output). Note that
        the global-, annual-mean concentrations :math:`C(y, m)` must be
        pre-interpolated onto monthly steps using a mean-preserving alogrithm
        [#11 for function which will do this] to avoid spurious steps
        in the outputs.

        The ellipses represent extra dimensions (e.g. scenario, greenhouse
        gas) that might be in :math:`C(y, m)`. Any such dimensions are
        preserved in the output.
        """
        check_pint_quantified_dataset(global_means)
        for darray in global_means.values():
            check_dimensions(darray, ("year", "month"), extras_ok=True)

        res = (
            global_means
            + self.gridding_values["seasonality"]
            + self.gridding_values["latitudinal_gradient"]
        )

        return res
