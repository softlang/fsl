import json
from collections import defaultdict
from pathlib import Path

from fsl_utils import fsl_graph, fsl_prefixes


# RDFLib does not consistently retain the prefixes used by each parsed Turtle
# file when several files use the default prefix.  Keep the FSL prefixes
# explicit so the JSON always uses the stable, human-readable names.
NAMESPACES = {
    "ae": "http://www.softlang.org/ontologies/ae#",
    "ce": "http://www.softlang.org/ontologies/ce#",
    "fe": "http://www.softlang.org/ontologies/fe#",
    "ie": "http://www.softlang.org/ontologies/ie#",
    "le": "http://www.softlang.org/ontologies/le#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "pe": "http://www.softlang.org/ontologies/pe#",
    "tbox": "http://www.softlang.org/ontologies/tbox#",
    "te": "http://www.softlang.org/ontologies/te#",
}


def prefixed_name(resource):
    value = str(resource)
    for prefix, namespace in NAMESPACES.items():
        if value.startswith(namespace):
            return f"{prefix}:{value[len(namespace):]}"
    raise ValueError(f"No preferred namespace prefix for {value}")


# Retrieve the ontology graph.
g = fsl_graph()

# Find every resource whose asserted type is tbox:Entity or a direct/indirect
# subclass of it. Return every named class that is asserted or implied through
# rdfs:subClassOf; anonymous class expressions cannot have prefixed names.
query = fsl_prefixes + """

SELECT DISTINCT ?entity ?class
WHERE {
  ?entity rdf:type/rdfs:subClassOf* ?class .
  FILTER(isIRI(?class))
  FILTER EXISTS {
    ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
  }
}
ORDER BY ?entity ?class
"""

classes_by_entity = defaultdict(set)
for row in g.query(query):
    classes_by_entity[prefixed_name(row["entity"])].add(
        prefixed_name(row["class"])
    )

entities = [
    {
        "entity": entity,
        "classes": sorted(classes),
    }
    for entity, classes in sorted(classes_by_entity.items())
]

output_file = Path("list.json")
with output_file.open("w", encoding="utf-8") as f:
    json.dump(entities, f, ensure_ascii=False, indent=2)
    f.write("\n")
