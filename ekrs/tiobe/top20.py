import pandas as pd

# Read TIOBE top 20
url = "https://www.tiobe.com/tiobe-index/"
df = pd.read_html(url)[0]
df = df.iloc[:, [0, 1, 4]]
df.columns = ["rank", "rank_last_year", "language"]
df.to_csv("top20.csv", index=False)

# Read software languages already in the ontology
languages = pd.read_csv("../../queries/languages/instances.csv")

# Keep only TIOBE languages missing from the ontologies
missing = df[~df["language"].isin(languages["SoftwareLanguage"])]
missing.to_csv("top20_missing.csv", index=False)
