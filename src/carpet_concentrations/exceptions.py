"""
Exceptions
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable

    import xarray as xr
    from pint.facets.plain.unit import PlainUnit


class CoordinateError(ValueError):
    """
    Raised when co-ordinates are not as expected

    Named "CoordinateError" to avoid confusion with
    :class:`pint.errors.DimensionalityError`
    """

    def __init__(
        self,
        exp_dims: tuple[Hashable, ...],
        found_dims: tuple[Hashable, ...],
        array: xr.DataArray,
        extras_ok: bool,
    ) -> None:
        """
        Initialise the error

        Parameters
        ----------
        exp_dims
            Expected dimensions

        found_dims
            Actual dimensions

        array
            The array we're looking at

        extras_ok
            Could ``exp_dims`` be a subset of ``found_dims``, or did they
            have to be equal?
        """
        if extras_ok:
            error_msg = (
                f"Expected dimensions: `{exp_dims}`. These are not a subset "
                f"of the found dimensions: `{found_dims}`."
            )
        else:
            error_msg = (
                f"Expected dimensions: `{exp_dims}`. These are not equal "
                f"to the found dimensions: `{found_dims}`."
            )

        super().__init__(error_msg, array)


class NotPintQuantifiedError(ValueError):
    """
    Raised when xarray object hasn't been quantified with pint
    """

    def __init__(
        self,
        da: xr.DataArray,
    ) -> None:
        """
        Initialise the error

        Parameters
        ----------
        da
            Unquantified :obj:`xr.DataArray`
        """
        error_msg = (
            f"{da.name} must have been quantified with pint using e.g. "
            "``.pint.quantify()``"
        )

        super().__init__(error_msg, da)


class DatasetIncompatibleUnitsError(ValueError):
    """
    Raised when an :obj:`xr.Dataset` object's contains units that incompatible

    Here incompatible means they are not of the same dimensionality i.e.
    cannot be converted into one another. Obviously this requirement is only
    applied in some cases
    """

    def __init__(
        self,
        base_unit: PlainUnit,
        incompatible_unit: PlainUnit,
        ds: xr.Dataset,
    ) -> None:
        """
        Initialise the error

        Parameters
        ----------
        base_unit
            Base unit that was used in checking

        incompatible_unit
            Unit found to be incompatible during checking

        ds
            The dataset we're looking at
        """
        error_msg = f"{base_unit} is not compatible with {incompatible_unit}."

        super().__init__(error_msg, ds)
