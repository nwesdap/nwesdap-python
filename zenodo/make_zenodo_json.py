# %%
import json

import pandas as pd


authors = pd.read_excel("zenodo/Authors_list_NWESDAP.xlsx")

zjson = []
for i, row in authors.iterrows():
    rdict = {
        "person_or_org": {
            "type": "personal",
            "family_name": row.Last_name.strip(),
            "given_name": row.First_name.strip(),
        },
        "affiliations": [{"name": row["Full affiliation"].strip()}],
    }
    if isinstance(row.ORCID, str):
        rdict["person_or_org"].update(
            {
                "identifiers": [
                    {
                        "scheme": "orcid",
                        "identifier": row.ORCID.strip().split("/")[-1],
                    }
                ]
            }
        )
    zjson.append(rdict)


with open("zenodo/zenodo.json", "w") as f:
    json.dump(zjson, f)
