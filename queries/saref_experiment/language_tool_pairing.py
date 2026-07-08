from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Match each Python language version with its CPython tool version by tag
# Shows language (LanguageVersion) and tool (ToolVersion) releasing in lockstep
query = """
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX pe:   <http://www.softlang.org/ontologies/pe#>
PREFIX te:   <http://www.softlang.org/ontologies/te#>
PREFIX time: <http://www.w3.org/2006/time#>

SELECT ?langTag ?langDate ?toolTag ?toolDate WHERE {
    ?langVersion tbox:versionOf pe:Python ;
                 tbox:versionTag ?langTag ;
                 tbox:releaseDate ?langInstant .
    ?langInstant time:inXSDDate ?langDate .
    ?toolVersion tbox:versionOf te:CPython ;
                 tbox:versionTag ?toolTag ;
                 tbox:releaseDate ?toolInstant .
    ?toolInstant time:inXSDDate ?toolDate .
    FILTER (?langTag = ?toolTag)
}
ORDER BY ?langTag
"""

for row in g.query(query):
    print(f"Python {row['langTag']} ({row['langDate']})\tCPython {row['toolTag']} ({row['toolDate']})")
