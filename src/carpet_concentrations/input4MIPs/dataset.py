"""
:class:`Input4MIPsDataset` and associated metadata
"""
from __future__ import annotations

import datetime as dt
import os.path
import uuid
from functools import partial
from typing import TYPE_CHECKING, Any

import cftime
import xarray as xr
from attrs import asdict, define, field
from attrs.validators import in_, matches_re

from carpet_concentrations.input4MIPs.metadata_options import (
    ACTIVITY_ID_OPTIONS,
    CONVENTION_OPTIONS,
    CREATION_DATE_REGEX,
    DATASET_CATEGORY_OPTIONS,
    INCLUDES_EMAIL_REGEX,
    UUID_REGEX,
)
from carpet_concentrations.time import get_start_of_next_month, split_time_to_year_month

if TYPE_CHECKING:
    from pathlib import Path


# If you're thinking about sub-classing this to update it for e.g. CMIP7,
# please consider instead refactoring to use the builder pattern. That will
# make the business logic and creation choices easier to follow for future
# developers (and the business logic really belongs to the class creation,
# once the rules about what can go in the class are decided, everything else
# follows pretty simply).
@define
class Input4MIPsMetadata:
    """
    Input4MIPs metadata

    These are all required fields.

    Notes
    -----
    `variable_id` is not included here because it should be derived from the
    data (which is combined with the metadata elsewhere).
    """

    activity_id: str = field(validator=in_(ACTIVITY_ID_OPTIONS))
    """Activity ID of the dataset"""

    contact: str = field(validator=matches_re(INCLUDES_EMAIL_REGEX))
    """Contact for the dataset"""

    Conventions: str = field(validator=in_(CONVENTION_OPTIONS))
    """CF conventions adhered to by the dataset"""

    dataset_category: str = field(validator=in_(DATASET_CATEGORY_OPTIONS))
    """Datset category"""

    frequency: str
    """Time frequency of the dataset"""

    further_info_url: str
    """URL with further information"""

    grid_label: str
    """Grid label of the dataset"""

    institution: str
    """Institution that produced the dataset"""

    institution_id: str
    """Unique ID of the institution that produced the dataset"""

    mip_era: str
    """MIP era of the dataset"""

    nominal_resolution: str
    """Nominal resolution of the dataset"""

    realm: str
    """Realm of the dataset"""

    source_version: str
    """Version of the dataset"""

    source_id: str
    """Source id of the dataset"""

    source: str
    """Source of the dataset (human-readable)"""

    target_mip: str
    """Target MIP of the dataset"""

    title: str
    """Title of the dataset (human-readable)"""

    def to_dataset_attributes(self) -> dict[str, str]:
        """
        Convert to a format that can be used as dataset attributes
        """
        out = {k: v for k, v in asdict(self).items()}

        return out


# As above, if you're thinking about sub-classing this to update it for e.g.
# CMIP7, please consider instead refactoring to use the builder pattern for
# the same reasons as above.
@define
class Input4MIPsMetadataOptional:
    """
    Input4MIPs optional metadata

    These are all optional fields.

    Notes
    -----
    This is currently written such that no fields outside of these can be
    provided. We don't fully understand the input4MIPs rules, so this could
    easily be the wrong choice. Refactoring should be relatively
    straightforward if needed. It would make sense that these fields are
    locked to avoid clashes with compulsory metadata...?
    """

    comment: str | None = None
    """Comment on the dataset"""

    # No idea if this can be validated or not nor what dataspecs are being
    # referred to
    data_specs_version: str | None = None
    """Data specs version used when creating the dataset"""

    external_variables: str | None = None  # No idea of comma separated or what
    """
    Variables relevant to the dataset that aren't included in the dataset itself

    For example, cell area variables like 'areacella'
    """

    grid: str | None = None  # No idea if this is meant to follow a controlled vocab
    """Human-readable version of the grid on which the dataset applies"""

    history: str | None = None
    """File modification history"""

    product: str | None = None  # No idea if this is meant to follow a controlled vocab
    """Product the data represents"""

    references: str | None = None
    """References related to the dataset"""

    region: str | None = None  # No idea if this is meant to follow a controlled vocab
    """Region to which the dataset applies"""

    release_year: str | None = None  # TODO: add validation that it is a year
    """Release year of the dataset"""

    source_description: str | None = (
        None  # No idea if this is meant to follow a controlled vocab
    )
    """Description of the dataset's source"""

    source_type: str | None = (
        None  # No idea if this is meant to follow a controlled vocab
    )
    """Description of the type of the dataset's source"""

    table_id: str | None = None  # No idea if this is meant to follow a controlled vocab
    """No idea, maybe the CMOR table used to write the dataset"""

    table_info: str | None = (
        None  # No idea if this is meant to follow a controlled vocab
    )
    """No idea, maybe info about the CMOR table used to write the dataset"""

    license: str | None = None
    """License information"""

    def to_dataset_attributes(self) -> dict[str, str]:
        """
        Convert to a format that can be used as dataset attributes
        """
        out = {k: v for k, v in asdict(self).items() if v is not None}

        return out


# As above, if you're thinking about sub-classing this to update it for e.g.
# CMIP7, please consider instead refactoring to use the builder pattern for
# the same reasons as above.
@define
class Input4MIPsDataset:
    """
    Input4MIPs dataset

    Holds input4MIPs data and also helps write them to disk in a way that
    conforms to input4MIPs standards
    """

    ds: xr.Dataset
    """
    Dataset
    """
    # Checks to add (and test):
    # - variable_id in attributes matches data (hence only one variable)
    # - variable dimensions matches expected dimensions
    # - all dimensions variables have bounds
    # - source_version and source_id are consistent
    # - assert metadata consistent with Input4MIPsMetadata
    # - grid label matches data
    # - nominal_resolution matches data
    # - realm matches data
    # - source id matches version and institution
    # - variable_id matches data
    # - check dataset_category against data
    # - check frequency against data
    # - data pint quantified so we can use cf-xarray to then go to UDUNITS
    # - all compulsory metadata fields are in ds.attrs (can use fields(
    #   Metadata))
    # - no forbidden metadata fields are in ds.attrs (would require defining
    #   forbidden fields first)

    directory_template: str = os.path.join(
        "{activity_id}",
        "{mip_era}",
        "{target_mip}",
        "{institution_id}",
        "{source_id}",
        "{realm}",
        "{frequency}",
        "{variable_id}",
        "{grid_label}",
        "v{version}",
    )
    """
    Template used to determine the directory in which to save the data
    """

    filename_template: str = "_".join(
        [
            "{variable_id}",
            "{activity_id}",
            "{dataset_category}",
            "{target_mip}",
            "{source_id}",
            "{grid_label}",
            "{start_date}",
            "{end_date}.nc",
        ]
    )
    """
    Template used to determine the filename when saving the data
    """

    @classmethod
    def from_metadata_autoadd_bounds_to_dimensions(  # noqa: PLR0913
        cls,
        ds: xr.Dataset,
        dimensions: tuple[str, ...],
        metadata: Input4MIPsMetadata,
        metadata_optional: Input4MIPsMetadataOptional | None = None,
        time_dimension: str = "time",
        monthly_time_bounds: bool = True,
        copy: bool = True,
        **kwargs: Any,
    ) -> Input4MIPsDataset:
        """
        Create instance from metadata and an unbounded dataset

        For the given dimensions, bounds are checked and added if needed. The
        metadata is then used to fill out ``ds``'s metadata before
        initialising.

        Parameters
        ----------
        ds
            Dataset

        dimensions
            Dimensions of the dataset, these are checked for appropriate
            bounds.

        metadata
            Metadata (required)

        metadata_optional
            Optional metadata

        time_dimension
            The name of the time dimension. This is provided to give full
            control of the application of ``monthly_time_bounds`` to the user.

        monthly_time_bounds
            Should added time bounds cover each month? This is needed for data
            on a monthly timestep because the middle of each timestep is not
            the start and end of the month in the case when subsequent months
            don't have the same number of days.

        copy
            Should a copy of the dataset be made? If no, the data is modified
            in place which can cause unexpected changes if references are not
            appropriately managed.

        **kwargs
            Other initialisation arguments for the instance. They are passed
            directly to the constructor.

        Returns
        -------
            Prepared instance

        Raises
        ------
        AssertionError
            ``ds.attrs`` is already set or there is more than one variable in ``ds``
        """
        if copy:
            ds = ds.copy(deep=True)
        else:
            raise NotImplementedError(copy)

        if ds.attrs:
            raise AssertionError("All metadata should be autogenerated")  # noqa: TRY003

        if len(ds.data_vars) == 1:
            variable_id = list(ds.data_vars.keys())[0]
        else:
            raise AssertionError("Can only write one variable per file")  # noqa: TRY003

        # add extra metadata following CF conventions, not really sure what
        # this does but it's free so we include it on the assumption that they
        # know more than we do (may be a bad assumption of course...)
        ds = ds.cf.guess_coord_axis().cf.add_canonical_attributes()

        # add bounds to dimensions
        for dim in dimensions:
            if dim == time_dimension:
                ds = add_time_bounds(ds, monthly_time_bounds)
            else:
                ds = ds.cf.add_bounds(dim)

        # transpose to match dimensions
        ds = ds.transpose(*dimensions, ...)

        # Get info from metadata
        attributes = {"variable_id": variable_id, **metadata.to_dataset_attributes()}
        if metadata_optional is not None:
            attributes.update(metadata_optional.to_dataset_attributes())

        ds.attrs = attributes

        return cls(ds, **kwargs)

    def write(
        self,
        root_data_dir: Path,
        unlimited_dims: tuple[str, ...] = ("time",),
        encoding_kwargs: dict[str, Any] | None = None,
    ) -> Path:
        """
        Write to disk

        Parameters
        ----------
        root_data_dir
            Root directory in which to write the file

        unlimited_dims
            Dimensions which should be unlimited

        encoding_kwargs
            Kwargs to use when encoding to disk. These are passed to
            :meth:`xr.Dataset.to_netcdf`

        Returns
        -------
            Where the file was written
        """
        if encoding_kwargs is None:
            encoding_kwargs = {"zlib": True, "complevel": 5}

        # Can shallow copy here as we don't need to worry about mangling the
        # data as the ref is not retured
        ds_disk = self.ds.copy(deep=False).pint.dequantify(format="cf")

        # Unique for every written file, so we don't provide a way for the
        # user to overwrite this at present
        ds_disk.attrs["tracking_id"] = generate_tracking_id()
        ds_disk.attrs["creation_date"] = generate_creation_timestamp()

        verify_disk_ready(ds_disk)

        out_path = self.get_filepath(
            ds_disk,
            root_data_dir,
        )

        out_path.parent.mkdir(parents=True, exist_ok=True)

        ds_disk.to_netcdf(
            out_path,
            unlimited_dims=unlimited_dims,
            encoding={ds_disk.attrs["variable_id"]: encoding_kwargs},
        )

        return out_path

    def get_filepath(
        self,
        ds_disk: xr.Dataset,
        root_data_dir: Path,
    ) -> Path:
        """
        Get filepath

        Parameters
        ----------
        ds_disk
            Disk ready dataset

        root_data_dir
            Root directory in which to generate the filepath

        Returns
        -------
            Filepath
        """
        format_date_h = partial(format_date, ds_frequency=ds_disk.attrs["frequency"])
        avail_metadata = {
            **ds_disk.attrs,
            "version": get_version(ds_disk.attrs["creation_date"]),
            "start_date": format_date_h(ds_disk.time.values.min()),
            "end_date": format_date_h(ds_disk.time.values.max()),
        }
        # This will likely require refactoring to become injectable
        avail_metadata_file_compat = {
            k: v.replace("_", "-") for k, v in avail_metadata.items()
        }

        out_dir = self.directory_template.format(**avail_metadata_file_compat)
        out_fname = self.filename_template.format(**avail_metadata_file_compat)

        return root_data_dir / out_dir / out_fname


def format_date(
    date: cftime.datetime | dt.datetime,
    ds_frequency: str,
) -> str:
    """
    Format date for filepath

    Parameters
    ----------
    date
        Date to format

    ds_frequency
        Frequency of the underlying dataset

    Returns
    -------
        Formatted date
    """
    if ds_frequency.endswith("mon"):
        datestring = date.strftime("%Y%m")
    else:
        raise NotImplementedError(ds_frequency)

    return datestring


def get_version(creation_date: str) -> str:
    """
    Get version string for filepath

    Parameters
    ----------
    creation_date
        Creation date

    Returns
    -------
        Version string
    """
    return dt.datetime.strptime(creation_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d")


def add_time_bounds(
    ds: xr.Dataset,
    monthly_time_bounds: bool = False,
    output_dim: str = "bounds",
) -> xr.Dataset:
    """
    Add time bounds to a dataset

    This should be pushed upstream to cf-xarray at some point probably

    Parameters
    ----------
    ds
        Dataset to which to add time bounds

    monthly_time_bounds
        Are we looking at monthly data i.e. should the time bounds run from
        the start of one month to the next (which isn't regular spacing but is
        most often what is desired/required)

    Returns
    -------
        Dataset with time bounds

    Notes
    -----
    There is no copy here, ``ds`` is modified in place (call
    :meth:`xarray.Dataset.copy` before passing if you don't
    want this).
    """
    # based on cf-xarray's implementation, to be pushed back upstream at some
    # point
    # https://github.com/xarray-contrib/cf-xarray/pull/441
    # https://github.com/pydata/xarray/issues/7860
    variable = "time"
    bname = f"{variable}_bounds"

    if bname in ds.variables:
        raise ValueError(  # noqa: TRY003
            f"Bounds variable name {bname!r} will conflict!"
        )

    if monthly_time_bounds:
        ds_ym = split_time_to_year_month(ds, time_axis=variable)

        # This may need to be refactored to allow the cftime_converter to be
        # injected, same idea as `convert_to_time`
        bounds = xr.DataArray(
            [
                [cftime.datetime(y, m, 1), get_start_of_next_month(y, m)]
                for y, m in zip(ds_ym.year, ds_ym.month)
            ],
            dims=(variable, "bounds"),
            coords={variable: ds[variable], "bounds": [0, 1]},
        ).transpose(..., "bounds")
    else:
        # This will require some thinking because `ds.cf.add_bounds(dim)`
        # doesn't work with cftime.datetime objects. Probably needs an issue upstream
        # and then a monkey patch or custom function here as a workaround.
        raise NotImplementedError(monthly_time_bounds)

    ds.coords[bname] = bounds
    ds[variable].attrs["bounds"] = bname

    return ds


def verify_disk_ready(ds: xr.Dataset) -> None:
    """
    Verify that a dataset is disk ready

    Parameters
    ----------
    ds
        Dataset to check

    Notes
    -----
    Very rough, doesn't really do anything right now
    """
    # call verify as a final check before writing
    # Note that we could change write to so it wraps around
    # [CMOR](https://cmor.llnl.gov/)
    # I'm not sure a) how often CMOR is used or b) how helpful it is
    # compared to just writing the same functionality here. We will have
    # to have a play and also ask CMOR devs what their roadmap looks like
    # I assume. I seem to have thought it looked promising here
    # https://github.com/PCMDI/cmor3_documentation/pull/57/files
    # This might also be worth looking at because it claims to implement CF
    # conventions: https://ncas-cms.github.io/cf-python/
    if not CREATION_DATE_REGEX.fullmatch(ds.attrs["creation_date"]):
        raise AssertionError(  # noqa: TRY003
            f"creation_date must match {CREATION_DATE_REGEX!r}"
        )

    if not UUID_REGEX.fullmatch(ds.attrs["tracking_id"]):
        raise AssertionError(f"tracking_id must match {UUID_REGEX}")  # noqa: TRY003

    if not ds["time"].encoding:
        raise AssertionError(  # noqa: TRY003
            "Not specifying a time encoding will cause all sorts of headaches"
        )


def generate_tracking_id() -> str:
    """
    Generate tracking ID

    Returns
    -------
        Tracking ID
    """
    return "hdl:21.14100/" + str(uuid.uuid4())


def generate_creation_timestamp() -> str:
    """
    Generate creation timestamp, formatted as needed for input4MIPs files

    Returns
    -------
        Creation timestamp
    """
    ts = dt.datetime.utcnow().replace(
        microsecond=0  # remove microseconds from creation_timestamp
    )

    return f"{ts.isoformat()}Z"  # Z indicates timezone is UTC
