from pathlib import Path

from rdflib import BNode, Graph, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL, RDF

from fsl_rdf import FSLOntology


ROOT = Path(__file__).parents[1]
ONTOLOGIES = ROOT / "ontologies"


def test_round_trip_preserves_every_module_and_union(tmp_path):
    ontology = FSLOntology.read(ONTOLOGIES)
    written = ontology.write(tmp_path)

    assert set(written) == {
        "ae",
        "ce",
        "fe",
        "fsl",
        "ie",
        "le",
        "pe",
        "tbox",
        "te",
    }

    reread = FSLOntology.read(tmp_path)
    assert isomorphic(ontology.graph, reread.graph)

    for name, source in written.items():
        original = next(
            module.source for module in ontology.modules.values() if module.name == name
        )
        assert isomorphic(Graph().parse(original), Graph().parse(source))


def test_round_trip_output_can_be_round_tripped_again(tmp_path):
    """Generated Turtle must remain stable when it becomes the next input."""

    first = tmp_path / "first"
    second = tmp_path / "second"

    original = FSLOntology.read(ONTOLOGIES)
    first_written = original.write(first)
    reread = FSLOntology.read(first)
    second_written = reread.write(second)
    reread_again = FSLOntology.read(second)

    assert isomorphic(original.graph, reread.graph)
    assert isomorphic(reread.graph, reread_again.graph)
    for name in first_written:
        assert isomorphic(
            Graph().parse(first_written[name]),
            Graph().parse(second_written[name]),
        )


def test_each_module_uses_its_own_default_namespace(tmp_path):
    ontology = FSLOntology.read(ONTOLOGIES)
    written = ontology.write(tmp_path)

    for name in ("ae", "ce", "fe", "ie", "le", "pe", "tbox", "te"):
        text = written[name].read_text(encoding="utf-8")
        assert f"@prefix : <http://www.softlang.org/ontologies/{name}#> ." in text


def test_new_blank_node_subgraph_follows_its_owner(tmp_path):
    ontology = FSLOntology.read(ONTOLOGIES)
    restriction = BNode()
    owner = URIRef("http://www.softlang.org/ontologies/ce#ExampleClass")
    ontology.graph.add((owner, RDF.type, OWL.Class))
    ontology.graph.add((owner, URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf"), restriction))
    ontology.graph.add((restriction, RDF.type, OWL.Restriction))

    written = ontology.write(tmp_path)
    ce_graph = Graph().parse(written["ce"])

    assert (owner, RDF.type, OWL.Class) in ce_graph
    assert written["ce"].exists()


def test_sparql_upsert_is_written_to_subject_module(tmp_path):
    ontology = FSLOntology.read(ONTOLOGIES)
    subject = URIRef("http://www.softlang.org/ontologies/ce#NewActivity")
    predicate = URIRef("http://xmlns.com/foaf/0.1/isPrimaryTopicOf")
    page = URIRef("https://en.wikipedia.org/wiki/Software_development_process")

    ontology.graph.update(
        """
        PREFIX ce:   <http://www.softlang.org/ontologies/ce#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        DELETE { ce:NewActivity foaf:isPrimaryTopicOf ?oldPage . }
        INSERT {
            ce:NewActivity foaf:isPrimaryTopicOf
                <https://en.wikipedia.org/wiki/Software_development_process> .
        }
        WHERE { OPTIONAL { ce:NewActivity foaf:isPrimaryTopicOf ?oldPage . } }
        """
    )

    written = ontology.write(tmp_path)
    assert (subject, predicate, page) in Graph().parse(written["ce"])
    assert all(
        (subject, predicate, page) not in Graph().parse(path)
        for name, path in written.items()
        if name != "ce"
    )


def test_replace_object_inserts_when_property_is_absent():
    ontology = FSLOntology.read(ONTOLOGIES)
    subject = URIRef("http://www.softlang.org/ontologies/ce#NewActivity")
    predicate = URIRef("http://xmlns.com/foaf/0.1/isPrimaryTopicOf")
    page = URIRef("https://en.wikipedia.org/wiki/Software_activity")

    previous = ontology.replace_object(subject, predicate, page)

    assert previous == frozenset()
    assert set(ontology.graph.objects(subject, predicate)) == {page}


def test_replace_object_replaces_all_previous_values():
    ontology = FSLOntology.read(ONTOLOGIES)
    subject = URIRef("http://www.softlang.org/ontologies/ce#AcceptanceTesting")
    predicate = URIRef("http://xmlns.com/foaf/0.1/isPrimaryTopicOf")
    old_page_1 = URIRef("https://example.org/old-page-1")
    old_page_2 = URIRef("https://example.org/old-page-2")
    new_page = URIRef("https://en.wikipedia.org/wiki/Acceptance_testing")
    ontology.graph.remove((subject, predicate, None))
    ontology.graph.add((subject, predicate, old_page_1))
    ontology.graph.add((subject, predicate, old_page_2))

    previous = ontology.replace_object(subject, predicate, new_page)

    assert previous == frozenset({old_page_1, old_page_2})
    assert set(ontology.graph.objects(subject, predicate)) == {new_page}
