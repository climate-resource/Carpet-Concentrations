"""
Test :mod:`carpet_concentrations.input4mips`
"""
import re

import cftime
import pytest
import xarray as xr

from carpet_concentrations.input4MIPs.dataset import (
    Input4MIPsDataset,
    Input4MIPsMetadata,
    add_time_bounds,
    format_date,
    verify_disk_ready,
)


# The valid inputs are derived based on a check of https://docs.google.com/document/d/1pU9IiJvPJwRvIgVaSDdJ4O0Jeorv_2ekEtted34K9cA/edit#
# on 18 May 2023. This will need to be updated for CMIP7 (and I'm not sure how
# closely this was enforced in CMIP6)
@pytest.fixture(scope="function")
def valid_input_input4mips_metadata():
    return {
        "contact": "contact details (jim@address.com)",
        "dataset_category": "SSTsAndSeaIce",
        "frequency": "mon",
        "further_info_url": "https://pcmdi.llnl.gov/mips/amip",
        "grid_label": "gn",
        "Conventions": "CF-1.7 CMIP-6.2",
        "activity_id": "input4MIPs",
        "institution": (
            "Program for Climate Model Diagnosis and Intercomparison, "
            "Lawrence Livermore National Laboratory, Livermore, CA 94550, USA"
        ),
        "institution_id": "PCMDI",
        "mip_era": "CMIP6",
        "nominal_resolution": "1x1 degree",
        "realm": "ocean",
        "source_version": "1.1.6",
        "source_id": "PCMDI-AMIP-1-1-6",
        "source": (
            "PCMDI-AMIP 1.1.6: Merged SST based on UK MetOffice HadISST " "and NCEP OI2"
        ),
        "target_mip": "CMIP",
        "title": "PCMDI-AMIP 1.1.6 dataset prepared for input4MIPs",
    }


def test_valid_input_input4mips_metadata(valid_input_input4mips_metadata):
    Input4MIPsMetadata(**valid_input_input4mips_metadata)


@pytest.mark.parametrize(
    [
        "failing_field",
        "failing_value",
        "exp_error",
        "exp_msg",
    ],
    [
        ("activity_id", "junkghjasd", ValueError, "'activity_id' must be in"),
        ("contact", "Mr. Big", ValueError, "'contact' must match regex"),
        ("Conventions", "junkghjasd", ValueError, "'Conventions' must be in"),
        ("dataset_category", "junkghjasd", ValueError, "'dataset_category' must be in"),
        ("frequency", "daily", ValueError, r"'frequency' must be in \('1hr'"),
    ],
)
def test_invalid_input_input4mips_metadata(
    valid_input_input4mips_metadata,
    failing_field,
    failing_value,
    exp_error,
    exp_msg,
):
    invalid_input_input4mips_metadata = {
        **valid_input_input4mips_metadata,
        failing_field: failing_value,
    }

    with pytest.raises(exp_error, match=exp_msg):
        Input4MIPsMetadata(**invalid_input_input4mips_metadata)


# Tests to write:
# - frequency has set of choices too [TODO look these up]
# - further_info_url is a URL
# - grid_label has set of choices too [TODO look these up]
# - institution_id has set of choices too [TODO look these up]
# - mip_era has set of choices too [TODO look these up]
# - nominal_resolution has set of choices too [TODO look these up]
# - realm has set of choices too [TODO look these up]
# - source_version should be MAJOR.MINOR.PATCH (use regexp)
# - `source_id` should end in `source_version.replace(".", "-")`. inconsistent
#   source_id and source_version raises (input4MIPsMetadataError).
# - `source` probably has rules, but it's very unclear from the example
# - target_mip has set of choices too [TODO look these up]
# - variable id is generated based on the dataset, not part of metadata

# - grid has set of choices too [TODO look these up]
# - license restriction?
# - metadata restriction? (Are additional things in netCDF an issue?)
# - class method auto adds creation time
# - passing creation_date to class method raises
# - asdict works
# - standard_name should come from specific set [TODO look these up]
# - units should come from specific set from udunits [TODO look these up,
#   cf-xarray may handle this for us...]

# - Optional metadata tests
# - no point writing until we know what the rules are

# - Input4MIPs dataset
# - add data tests (all written in
#   https://gitlab.com/climate-resource/global-emissions/-/blob/main/src/carpet/src/carpet/outputs.py)
# - test class method
# - test get filepath
# - test unit handling with cf xarray (can convert to CF conventions using
#   https://cf-xarray.readthedocs.io/en/latest/units.html#formatting-units,
#   have to be careful to not explode the registry handling though but
#   registry can be passed to e.g. quantify)


def test_from_metadata_autoadd_bounds_to_dimensions_no_copy_raises():
    # Would want to refactor to make testing easier here I suspect
    # (dependency injection would help)
    with pytest.raises(NotImplementedError, match="False"):
        Input4MIPsDataset.from_metadata_autoadd_bounds_to_dimensions(
            "mock",
            "mock",
            "mock",
            copy=False,
        )


def test_from_metadata_autoadd_bounds_to_dimensions_prexexsting_attrs():
    inp = xr.Dataset(
        {
            "var": (
                ("year",),
                [1, 2, 3],
            ),
        },
        coords={"year": [2010, 2011, 2012]},
        attrs={"pre": "existing"},
    )
    with pytest.raises(AssertionError, match="All metadata should be autogenerated"):
        Input4MIPsDataset.from_metadata_autoadd_bounds_to_dimensions(
            inp,
            "mock",
            "mock",
        )


def test_from_metadata_autoadd_bounds_to_dimensions_multivar():
    inp = xr.Dataset(
        {
            "var": (
                ("year",),
                [1, 2, 3],
            ),
            "var_2": (
                ("year",),
                [4, 5, 6],
            ),
        },
        coords={"year": [2010, 2011, 2012]},
    )
    with pytest.raises(AssertionError, match="Can only write one variable per file"):
        Input4MIPsDataset.from_metadata_autoadd_bounds_to_dimensions(
            inp,
            "mock",
            "mock",
        )


@pytest.mark.parametrize(
    "date, freq, exp",
    (
        (cftime.DatetimeGregorian(2012, 1, 3), "mon", "201201"),
        (cftime.DatetimeGregorian(2012, 4, 1), "mon", "201204"),
        (cftime.DatetimeGregorian(2022, 1, 3), "yr", "2022"),
        (cftime.DatetimeGregorian(2022, 11, 13), "yr", "2022"),
        (cftime.DatetimeGregorian(1, 11, 13), "mon", "000111"),
        (cftime.DatetimeGregorian(1, 11, 13), "yr", "0001"),
    ),
)
def test_format_date(date, freq, exp):
    res = format_date(date, ds_frequency=freq)
    assert res == exp


def test_add_time_bounds_name_clash():
    inp = xr.Dataset(
        {
            "var": (
                ("time",),
                [1, 2, 3],
            ),
        },
        coords={
            "time": [2010, 2011, 2012],
            "time_bounds": (
                ("time", "bounds"),
                [[2010, 2011], [2011, 2012], [2012, 2013]],
            ),
            "bounds": [0, 1],
        },
    )
    with pytest.raises(
        ValueError, match="Bounds variable name 'time_bounds' will conflict!"
    ):
        add_time_bounds(inp)


def test_add_time_bounds_not_monthly_time_bounds():
    inp = xr.Dataset(
        {
            "var": (
                ("time",),
                [1, 2, 3],
            ),
        },
        coords={"time": [2010, 2011, 2012]},
    )
    with pytest.raises(NotImplementedError, match="False"):
        add_time_bounds(inp, monthly_time_bounds=False)


@pytest.mark.parametrize(
    "bad_attr, bad_value, exp_error, exp_msg",
    (
        (
            "creation_date",
            "20230504",
            AssertionError,
            re.escape(
                "creation_date must match "
                "re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$')"
            ),
        ),
        (
            "tracking_id",
            "23",
            AssertionError,
            re.escape(
                "tracking_id must match "
                "re.compile('^hdl:21.14100\\\\/[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$')"
            ),
        ),
    ),
)
def test_verify_disk_ready(bad_attr, bad_value, exp_error, exp_msg):
    inp = xr.Dataset(
        {
            "var": (
                ("time",),
                [1, 2, 3],
            ),
        },
        coords={"time": [2010, 2011, 2012]},
        attrs={
            "creation_date": "2023-05-17T18:00:02Z",
            "tracking_id": "hdl:21.14100/4k2n878f-1832-4jn3-o4jh-8594jrnfth12",
        },
    )
    inp["time"].encoding = {"units": "units", "calendar": "calendar"}

    inp.attrs[bad_attr] = bad_value

    with pytest.raises(exp_error, match=exp_msg):
        verify_disk_ready(inp)


def test_verify_no_time_encoding():
    inp = xr.Dataset(
        {
            "var": (
                ("time",),
                [1, 2, 3],
            ),
        },
        coords={"time": [2010, 2011, 2012]},
        attrs={
            "creation_date": "2023-05-17T18:00:02Z",
            "tracking_id": "hdl:21.14100/4k2n878f-1842-4jn3-o4jh-8594jrnfth12",
        },
    )

    with pytest.raises(
        AssertionError,
        match="Not specifying a time encoding will cause all sorts of headaches",
    ):
        verify_disk_ready(inp)
