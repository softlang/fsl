import pandas as pd

# Read TIOBE top 10
tiobe = pd.read_html("https://www.tiobe.com/tiobe-index/")
tiobe = tiobe[0].head(10)
tiobe = tiobe.iloc[:, [0, 1, 4]]
tiobe.columns = ["Rank", "RankLastYear", "Language"]
tiobe.to_csv("top10.csv", index=False)

# Read software languages already in the ontology
onto = pd.read_csv("../../queries/languages/instances.csv")

# Keep only TIOBE languages missing from the ontology -- initial situation
missing = tiobe[~tiobe["Language"].isin(onto["SoftwareLanguage"])]
missing.to_csv("top10_missing_initial.csv", index=False)

# Alignment renamings
tiobe["Language"] = tiobe["Language"].replace({
    "C#": "C_Sharp",
    "C++": "Cpp",
    "Visual Basic": "Visual_Basic",
})

# Keep only TIOBE languages missing from the ontology -- final situation
missing = tiobe[~tiobe["Language"].isin(onto["SoftwareLanguage"])]
missing.to_csv("top10_missing_final.csv", index=False)
