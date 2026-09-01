from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# All language versions ordered by release date
# SAREF time-series pattern: each LanguageVersion is an observation point
query = """
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX time: <http://www.w3.org/2006/time#>

SELECT ?entity ?tag ?date WHERE {
    ?entity tbox:hasVersion ?version .
    ?version tbox:versionTag ?tag ;
             tbox:releaseDate ?instant .
    ?instant time:inXSDDate ?date .
    ?entity rdfs:label ?entityLabel .
}
ORDER BY ?entity ?date
"""

for row in g.query(query):
    print(f"{row['entity']}\t{row['tag']}\t{row['date']}")
