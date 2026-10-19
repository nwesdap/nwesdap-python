# %%
import pandas as pd

import nwesdap


def test_get_nwesdap():
    df = nwesdap.get_nwesdap(rename_like_glodap=True)
    assert isinstance(df, pd.DataFrame)
    df = nwesdap.get_nwesdap(rename_like_glodap=False)
    assert isinstance(df, pd.DataFrame)


# test_get_nwesdap()
