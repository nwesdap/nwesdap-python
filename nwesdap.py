"""
NWESDAP
=======
Download Northwest European Shelf Data Analysis Product (NWESDAP)
datasets and import them as pandas DataFrames.  For more general info
on NWESDAP, see https://nwesdap.net.

The only function you need is `get_nwesdap`:

  >>> from nwesdap import get_nwesdap
  >>> df = get_nwesdap()

This function does the following:

  1. Checks if the latest version of the NWESDAP dataset is already
     present at "~/.nwesdap".
  2. If not, downloads it from Zenodo and checks the MD5 checksum,
     before saving it to "~/.nwesdap".
  3. Reads in the dataset as a pandas DataFrame.

NOTE: the dataset is downloaded in parquet format, so you will also need
to install either pyarrow or fastparquet.

See the function docstring for more information on the contents of the
imported DataFrame.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pooch


__version__ = "0.1.0"

urls = {
    "v1.2026": "https://zenodo.org/records/23495661/files/NWESDAP_v19102026.parquet?download=1"
}
filenames = {
    "v1.2026": "NWESDAP_v19102026.parquet",
}
checksums = {
    "v1.2026": "md5:b4aebd82e60ff31a465f9a14a31dd54c",
}


class NwesdapError(Exception):
    """NWESDAP custom exception."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def _parse_path_nwesdap(path_nwesdap):
    if path_nwesdap is None:
        return Path(Path.home(), ".nwesdap")
    else:
        return path_nwesdap


def _parse_version(version):
    if version is None:
        return "v1.2026"
    else:
        if version not in urls:
            raise NwesdapError(f"Version '{version}' not recognised")
        return version


def _download(version=None, path_nwesdap=None):
    """Download a NWESDAP data file and save it locally, after checking that it
    has the expected checksum (MD5).

    Parameters
    ----------
    version : str or None, optional
        Which NWESDAP version to download, by default `None`, in which case the
        most recent version is downloaded.  The options are:
            "v1.2026" (the original NWESDAP).
    path_nwesdap : str or None, optional
        Where to save the downloaded file, by default `None`, in which case the
        file is saved at "~/.nwesdap".
    """
    path_nwesdap = _parse_path_nwesdap(path_nwesdap)
    if not os.path.isdir(path_nwesdap):
        os.makedirs(path_nwesdap)
    version = _parse_version(version)
    pooch.retrieve(
        urls[version],
        known_hash=checksums[version],
        fname=filenames[version],
        path=path_nwesdap,
    )


def _get_renamer_glodap(df):
    renamer_glodap = {
        "Dataset_origin": "dataset_origin",
        "Name_ID": "name_id",
        "Unit_ID": "unit_id",
        "EXPOCODE": "expocode",
        "Cruise_ID": "cruise_id",
        "Ship": "ship",
        "Station_ID": "station_id",
        "Cast_number": "cast",
        "Bottle_ID": "bottle_id",
        "Year_UTC": "year",
        "Month_UTC": "month",
        "Day_UTC": "day",
        "Time_UTC": "time_utc",
        "Datetime": "datetime",
        "Datenum": "datenum",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Depth_bottom": "bottomdepth",
        "Sampledepth_max": "maxsampdepth",
        "Distance_to_shore": "distance_to_shore",
        "CTDPRES": "pressure",
        "Depth": "depth",
        "CTDTEMP": "temperature",
        "Theta": "theta",
        "CTDSAL": "salinity",
        "Absolute_Salinity": "abssalinity",
        "DIC": "tco2",
        "DIC_QC": "tco2_qc",
        "TA": "talk",
        "TA_QC": "talk_qc",
        "pH_T_measured": "phtsmeastp",
        "pH_T_insitu": "phtsinsitutp",
        "pH_T_insitu_QC": "phtsinsitutp_qc",
        "TEMP_pH": "ph_tmp",
        "CTDOXY": "oxygen_ctd",
        "Oxygen": "oxygen_bottle",
        "Recommended_Oxygen": "oxygen",
        "AOU": "aou",
        "Nitrate": "nitrate",
        "Nitrite": "nitrite",
        "Nitrate_and_Nitrite": "nitrate_and_nitrite",
        "Ammonium": "ammonia",
        "Phosphate": "phosphate",
        "Silicate": "silicate",
    }
    for c in df.columns:
        if c.endswith("_flagPI"):
            renamer_glodap.update(
                {c: renamer_glodap[c.replace("_flagPI", "")] + "_flag_pi"}
            )
        elif c.endswith("_QCU_flag"):
            renamer_glodap.update(
                {c: renamer_glodap[c.replace("_QCU_flag", "")] + "_flag_qcu"}
            )
    return renamer_glodap


def get_nwesdap(
    version="v1.2026",
    path_nwesdap=None,
    rename_like_glodap=True,
):
    """Read in the NWESDAP dataset, first downloading it if it's not
    already stored locally at `path_nwesdap`.

    Parameters
    ----------
    version : str, optional
        Which version of NWESDAP to open, by default "v1.2026",
        which is currently the only option.
    path_nwesdap : str or pathlib.Path, optional
        The path to look for and/or save the NWESDAP data file,
        by default None, in which case "~/.nwesdap" is used,
        where "~" is the output from `pathlib.Path.home()`.
    rename_like_glodap : bool, optional
        Whether to rename the columns to be similar to the GLODAP names,
        by default True.

    Returns
    -------
    pd.DataFrame
        The NWESDAP dataset, with the following columns (assuming that
        `rename_like_glodap` is True, otherwise, the column names will
        be as described in the NWESDAP manuscript):
            dataset_origin      | Source for this subset of the data
            name_id             | Text ID for this QCU
            unit_id             | Numerical ID for this QCU
            expocode            | Expedition code
            cruise_id           | ID for this cruise
            ship                | Sampling vessel
            station_id          | ID for this sampling station
            cast                | CTD cast number
            bottle_id           | ID for this dataset row
            year                | Year (UTC)
            month               | Month (UTC)
            day                 | Day (UTC)
            time_utc            | Time (UTC)
            datetime            | Date and time (UTC)
            datenum             | Time since 1 January 1970 00:00 UTC in days
            latitude            | Latitude in decimal °N
            longitude           | Longitude in decimal °E
            bottomdepth         | Seafloor depth in m
            maxsampdepth        | Maximum sample depth at this station in m
            distance_to_shore   | Distance to coastline in km
            pressure            | Hydrostatic pressure in dbar
            depth               | Depth in m
            temperature         | Temperature in °C
            theta               | Potential temperature in °C
            salinity            | Practical salinity
            abssalinity         | Absolute salininy in g/kg
            tco2                | Dissolved inorganic carbon in μmol/kg
            talk                | Total alkalinity in μmol/kg
            phtsmeastp          | pH on the total scale at measurement conditions
            phtsinsitutp        | pH on the total scale at insitu T & P
            ph_tmp              | Temperature of phtsmeastp in °C
            oxygen_ctd          | Dissolved oxygen from a CTD sensor in μmol/kg
            oxygen_bottle       | Dissolved oxygen from bottle samples in μmol/kg
            oxygen              | Recommended dissolved oxygen in μmol/kg
            aou                 | Apparent oxygen utilisation in μmol/kg
            nitrate             | Nitrate in μmol/kg
            nitrite             | Nitrite in μmol/kg
            nitrate_and_nitrite | Nitrate + nitrite in μmol/kg
            ammonia             | Total ammonia in μmol/kg
            phosphate           | Total phosphate in μmol/kg
            silicate            | Total silicate in μmol/kg
        There are also columns with the following formats:
            *_flagPI   | Flags assigned by the original sub-dataset PIs
            *_qc       | Datapoint-level flags assigned by NWESDAP
                       |     0 = good
                       |     1 = flagged not good by original PI
                       |     2 = suspicious from NWESDAP primary QC
                       |     3 = suspicious from NWESDAP secondary QC
                       |     9 = absent
            *_flag_qcu | QCU-level flags assigned by NWESDAP
                       |     C = climate quality (GOA-ON)
                       |     W = weather quality (GOA-ON)
                       |     X = less than weather quality
                       |     Z = absent
    """
    path_nwesdap = _parse_path_nwesdap(path_nwesdap)
    version = _parse_version(version)
    if not os.path.isdir(path_nwesdap) or filenames[version] not in os.listdir(
        path_nwesdap
    ):
        _download(version=version, path_nwesdap=path_nwesdap)
    df = pd.read_parquet(
        Path(path_nwesdap, filenames[version]),
    ).replace(-999, np.nan)
    if rename_like_glodap:
        df = df.rename(columns=_get_renamer_glodap(df))
    return df
