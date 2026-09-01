from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Walk the version successor chain for all entities
# Equivalent to SAREF's time-series next-observation traversal
query = """
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?entityLabel ?tag ?nextTag WHERE {
    ?entity tbox:hasVersion ?version .
    ?entity rdfs:label ?entityLabel .
    ?version tbox:versionTag ?tag ;
             tbox:hasSuccessor ?next .
    ?next tbox:versionTag ?nextTag .
}
ORDER BY ?entityLabel ?tag
"""

for row in g.query(query):
    print(f"{row['entityLabel']}\t{row['tag']}\t-->\t{row['nextTag']}")
