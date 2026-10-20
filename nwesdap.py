# %%
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
    version=None,
    path_nwesdap=None,
    rename_like_glodap=True,
):
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
