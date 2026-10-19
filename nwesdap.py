# %%
from pathlib import Path

import numpy as np
import pandas as pd


def _get_nwesdap_path(nwesdap_dir=None):
    if nwesdap_dir is None:
        nwesdap_dir = Path(Path.home(), ".nwesdap")
    nwesdap_path = Path(nwesdap_dir, "NWESDAP_v16102026.parquet")
    return nwesdap_path


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
        if c.endswith("_flag"):
            renamer_glodap.update(
                {c: renamer_glodap[c.replace("_flag", "")] + "_f"}
            )
    return renamer_glodap


def get_nwesdap(
    nwesdap_dir=None,
    rename_like_glodap=True,
):
    df = pd.read_parquet(
        _get_nwesdap_path(nwesdap_dir=nwesdap_dir),
    ).replace(-999, np.nan)
    if rename_like_glodap:
        df = df.rename(columns=_get_renamer_glodap(df))
    return df
