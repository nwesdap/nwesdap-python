# %%
import pandas as pd

import nwesdap


def test_get_nwesdap():
    df = nwesdap.get_nwesdap(rename_like_glodap=True)
    assert isinstance(df, pd.DataFrame)
    df = nwesdap.get_nwesdap(rename_like_glodap=False)
    assert isinstance(df, pd.DataFrame)


def test_urls_filenames_checksums():
    for u in nwesdap.urls:
        assert u in nwesdap.filenames
        assert u in nwesdap.checksums
    for f in nwesdap.filenames:
        assert f in nwesdap.urls
        assert f in nwesdap.checksums
    for c in nwesdap.checksums:
        assert c in nwesdap.urls
        assert c in nwesdap.filenames


# test_get_nwesdap()
# test_urls_filenames_checksums()
