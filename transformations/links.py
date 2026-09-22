"""
The responses left behind by externals/wikipedia/links.py are processed here.
That is:
* LLM claims about links found are verified by SPARQL queries.
* Support assessments don't change a thing.
* Replace assessments lead to deletion of existing linkage.
* Replace and resolve assessments lead to insertion of proposed link.
"""


import json
from pathlib import Path
from fsl_utils import fsl_prefixes_sparql, fsl_prefixed_name
from fsl_rdf import FSLOntology


# Some params
input_folder = "../externals/wikipedia/links"
input_folder = Path(input_folder).expanduser().resolve()


# Normalize lists of links for comparison
def normalize_links(items: list[dict[str, str]]) -> frozenset[frozenset[tuple[str, str]]]:
    return frozenset(frozenset(item.items()) for item in items)


# Template for querying linkage
query_linkage_template = fsl_prefixes_sparql + """
SELECT ?predicate ?object
WHERE {{
  {resource} ?predicate ?object .
  FILTER (?predicate IN (foaf:isPrimaryTopicOf, foaf:page))
}}
"""


# Template for linkage deletion
linkage_deletion_template = fsl_prefixes_sparql + """
DELETE {{
  {resource} ?predicate ?object .
}}
WHERE {{
  {resource} ?predicate ?object .
  FILTER (?predicate IN (foaf:isPrimaryTopicOf, foaf:page))
}}
"""


# Template for linkage insertion
linkage_insertion_template = fsl_prefixes_sparql + """
INSERT DATA {{
  {resource} {predicate} <{url}> .
}}
"""


def query_linkage(resource):
    """Query linkage for the given resource and return it in a normalized, eq-ready manner."""
    query = query_linkage_template.format(resource=resource)
    result = ontology.graph.query(query)
    links_found = []
    for row in result:
        links_found.append({
            'predicate': fsl_prefixed_name(ontology.graph, row['predicate']),
            'url': str(row['object']),
        })
    return links_found


def delete_linkage(resource):
    """Delete linkage for the given resource to make space for something better."""
    delete = linkage_deletion_template.format(resource=resource)
    ontology.graph.update(delete)


def insert_linkage(resource, predicate, url):
    """Insert linkage for the given resource."""
    insert = linkage_insertion_template.format(
        resource=resource,
        predicate=predicate,
        url=url
    )
    ontology.graph.update(insert)


# Load ontology
ontology = FSLOntology.read(Path("../ontologies"))


# Collect all responses and print some summary statistics
responses = []
counts = {}
counts["support"] = 0
counts["replace"] = 0
counts["resolve"] = 0
for response_file in sorted(
    input_folder.rglob("*.response"),
    key=lambda path: path.name.casefold(),
):
    with response_file.open("r", encoding="utf-8") as file:
        response = json.load(file)
    counts[response["assessment"]] += 1
    responses.append(response)
print("Link assessment statistics: " + str(counts))


# Process all responses for their CRUD effects
for response in responses:

    # Announcing the resource at hand
    resource = response['resource']
    assessment = response['assessment']
    print("Processing `{resource}` (with `{assessment}` assessment).".format(
        resource=resource,
        assessment=assessment
    ))

    # Assert equality for links found by LLM versus Sparql query
    links_found_by_llm = response['links_found']
    links_found_by_llm = normalize_links(links_found_by_llm)
    links_found_by_spaqrl = query_linkage(resource)
    links_found_by_spaqrl = normalize_links(links_found_by_spaqrl)
    assert links_found_by_llm == links_found_by_spaqrl, \
      "LLM/Sparql discrepancy on linkage for `{resource}`.".format(resource=resource) 

    # Delete linkage for a `replace' assessment
    if assessment == "replace":
        delete_linkage(resource)

    # Insert linkage for a `replace` and `resolve` assessment
    if assessment in ["replace", "resolve"]:
        predicate = response['link_proposed']['predicate']
        url = response['link_proposed']['url']
        insert_linkage(resource, predicate, url)

# Serialize modified ontology
ontology.write(Path("build/ontologies"))
