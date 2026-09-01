from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# All versions across both LanguageVersion and ToolVersion individuals
# Demonstrates the pattern covers "languages and technologies" as SAREF suggests
query = """
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX time: <http://www.w3.org/2006/time#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?entityLabel ?tag ?date WHERE {
    ?entity tbox:hasVersion ?version .
    ?version tbox:versionTag ?tag ;
             tbox:releaseDate ?instant .
    ?instant time:inXSDDate ?date .
    ?entity rdfs:label ?entityLabel .
    FILTER (?date > "2015-01-01"^^xsd:date)
}
ORDER BY ?entityLabel ?date
"""

for row in g.query(query):
    print(f"{row['entityLabel']}\t{row['tag']}\t{row['date']}")
