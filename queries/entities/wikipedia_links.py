"""Extract Wikipedia links and their users into wikipedia_links.json.

Run like the other queries/entities scripts, with utils on PYTHONPATH.
The fixed SPARQL query returns usages; Python groups them into nested JSON.
All ontology subjects are included, regardless of their type. N/A is included
for both predicates because this report inventories links, not compliance.
"""

import json
from rdflib import BNode
from fsl_utils import fsl_graph, fsl_prefixes_dict


QUERY = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?link ?resource ?predicate
WHERE {
  VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
  ?resource ?predicate ?link .
  FILTER (isIRI(?link))
  FILTER (STRSTARTS(STR(?link), "https://en.wikipedia.org"))
}
"""

PREDICATE_NAMES = {
    "http://xmlns.com/foaf/0.1/page": "foaf:page",
    "http://xmlns.com/foaf/0.1/isPrimaryTopicOf": "foaf:isPrimaryTopicOf",
}


# Match the most specific namespace first (e.g. ce: before the broader fsl:).
RESOURCE_PREFIXES = sorted(
    fsl_prefixes_dict.items(), key=lambda item: (-len(item[1]), item[0])
)


def resource_name(resource):
    """Use the configured prefix and local name, retaining unknown IRIs."""
    if isinstance(resource, BNode):
        return resource.n3()
    iri = str(resource)
    for prefix, namespace in RESOURCE_PREFIXES:
        if iri.startswith(namespace):
            return f"{prefix}:{iri[len(namespace):]}"
    return iri


def wikipedia_links(graph):
    """Return one object per URL, with each resource and its predicates."""
    links = {}
    for row in graph.query(QUERY):
        link = str(row["link"])
        resource = row["resource"]
        resource_id = resource_name(resource)
        predicate = PREDICATE_NAMES[str(row["predicate"])]
        resources = links.setdefault(link, {})
        resources.setdefault(resource_id, set()).add(predicate)

    return [
        {
            "link": link,
            "resources": [
                {"resource": resource, "predicates": sorted(predicates)}
                for resource, predicates in sorted(resources.items())
            ],
        }
        for link, resources in sorted(links.items())
    ]


def main():
    report = wikipedia_links(fsl_graph())
    with open("wikipedia_links.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2, ensure_ascii=False)
        output.write("\n")


if __name__ == "__main__":
    main()
