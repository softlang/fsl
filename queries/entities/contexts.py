import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from rdflib import BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS

from fsl_utils import fsl_graph, fsl_prefixes_dict, fsl_prefixes_sparql


CONTEXTS_DIR = Path(__file__).with_name("contexts")

PROPERTY_TYPE_NAMES = {
    OWL.ObjectProperty: "object_property",
    OWL.DatatypeProperty: "datatype_property",
    OWL.AnnotationProperty: "annotation_property",
    RDF.Property: "rdf_property",
}

# These standard annotation properties are not necessarily declared in the
# local FSL graph because their defining vocabularies are not imported.
STANDARD_ANNOTATION_PROPERTIES = {
    RDFS.label,
    RDFS.comment,
    RDFS.seeAlso,
    RDFS.isDefinedBy,
    OWL.versionInfo,
    OWL.priorVersion,
    OWL.backwardCompatibleWith,
    OWL.incompatibleWith,
    OWL.deprecated,
}

STANDARD_RDF_PROPERTY_NAMESPACES = (
    str(RDF),
    str(RDFS),
    str(OWL),
)

ENTITY_CONTEXT_QUERY = fsl_prefixes_sparql + """

SELECT DISTINCT ?entity ?direction ?subject ?predicate ?object
WHERE {
  ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
  FILTER(isIRI(?entity))

  {
    ?entity ?predicate ?object .
    BIND(?entity AS ?subject)
    BIND("outgoing" AS ?direction)
  }
  UNION
  {
    ?subject ?predicate ?entity .
    BIND(?entity AS ?object)
    BIND("incoming" AS ?direction)
  }
}
"""

PROPERTY_TYPES_QUERY = fsl_prefixes_sparql + """

SELECT DISTINCT ?predicate ?propertyType
WHERE {
  ?predicate rdf:type ?propertyType .
  VALUES ?propertyType {
    owl:ObjectProperty
    owl:DatatypeProperty
    owl:AnnotationProperty
    rdf:Property
  }
}
"""


def prefixed_name(graph, resource):
    value = str(resource)

    # Match longer namespaces first so the general fsl: namespace does not
    # hide a more specific namespace such as le: or tbox:.
    for prefix, namespace in sorted(
        fsl_prefixes_dict.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    ):
        if value.startswith(namespace):
            return f"{prefix}:{value[len(namespace):]}"

    # Preserve any additional namespace binding supplied by the graph. If no
    # binding exists, the full IRI remains available both here and in "iri".
    try:
        prefix, _, local = graph.compute_qname(resource, generate=False)
        return f"{prefix}:{local}"
    except (KeyError, ValueError):
        return value


def term_to_dict(graph, term):
    if isinstance(term, URIRef):
        return {
            "term_type": "iri",
            "value": prefixed_name(graph, term),
            # "iri": str(term),
        }

    if isinstance(term, BNode):
        return {
            "term_type": "blank_node",
            "value": f"_:{term}",
        }

    if isinstance(term, Literal):
        result = {
            "term_type": "literal",
            "value": str(term),
        }
        if term.language:
            result["language"] = term.language
        if term.datatype:
            result["datatype"] = prefixed_name(graph, term.datatype)
            result["datatype_iri"] = str(term.datatype)
        return result

    raise TypeError(f"Unsupported RDF term: {term!r}")


def load_property_types(graph):
    property_types = defaultdict(set)
    for row in graph.query(PROPERTY_TYPES_QUERY):
        property_types[row["predicate"]].add(
            PROPERTY_TYPE_NAMES[row["propertyType"]]
        )
    return property_types


def classify_predicate(predicate, property_types):
    declared_types = property_types.get(predicate)
    if declared_types:
        return sorted(declared_types)
    if predicate in STANDARD_ANNOTATION_PROPERTIES:
        return ["annotation_property"]
    if str(predicate).startswith(STANDARD_RDF_PROPERTY_NAMESPACES):
        return ["rdf_property"]
    return ["unclassified_property"]


def context_path(graph, output_dir, entity):
    name = prefixed_name(graph, entity)
    if ":" not in name or name == str(entity):
        raise ValueError(f"Entity has no namespace prefix: {entity}")

    prefix, local_name = name.split(":", 1)
    if not local_name:
        raise ValueError(f"Entity has no local name: {entity}")

    # Percent encoding keeps resource names containing '/', ':', or other
    # filesystem-sensitive characters within one portable filename.
    filename = quote(local_name, safe="-._~") + ".json"
    return output_dir / prefix / filename


def statement_sort_key(statement):
    return (
        0 if statement["direction"] == "outgoing" else 1,
        json.dumps(statement["predicate"], sort_keys=True, ensure_ascii=False),
        json.dumps(statement["subject"], sort_keys=True, ensure_ascii=False),
        json.dumps(statement["object"], sort_keys=True, ensure_ascii=False),
    )


def write_contexts(output_dir=CONTEXTS_DIR):
    graph = fsl_graph()
    property_types = load_property_types(graph)
    statements_by_entity = defaultdict(list)
    entities = {}

    for row in graph.query(ENTITY_CONTEXT_QUERY):
        entity = row["entity"]
        entity_name = prefixed_name(graph, entity)
        entities[entity_name] = entity
        statements_by_entity[entity_name].append({
            "direction": str(row["direction"]),
            "subject": term_to_dict(graph, row["subject"]),
            "predicate": term_to_dict(graph, row["predicate"]),
            "predicate_types": classify_predicate(
                row["predicate"], property_types
            ),
            "object": term_to_dict(graph, row["object"]),
        })

    paths = {}
    for entity_name, entity in entities.items():
        path = context_path(graph, output_dir, entity)
        collision_key = str(path).casefold()
        if collision_key in paths:
            raise ValueError(
                f"Context filename collision between {paths[collision_key]} "
                f"and {entity_name}: {path}"
            )
        paths[collision_key] = entity_name

    for entity_name in sorted(entities):
        path = context_path(graph, output_dir, entities[entity_name])
        path.parent.mkdir(parents=True, exist_ok=True)

        document = {
            "resource": entity_name,
            "statements": sorted(
                statements_by_entity[entity_name], key=statement_sort_key
            ),
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
            f.write("\n")

    return len(entities)


if __name__ == "__main__":
    count = write_contexts()
    print(f"Wrote {count} entity contexts to {CONTEXTS_DIR}")
