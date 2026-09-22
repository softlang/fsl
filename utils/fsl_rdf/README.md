# FSL's transformation library for its file-based RDF representation

`fsl_rdf.py` loads every Turtle module into one mutable RDFLib `Graph`. When
written, triples are partitioned by the subject namespace and each module gets
its own default `:` namespace again. Cross-module resources retain their
qualified prefixes (`ae:`, `ce:`, `le:`, `tbox:`, and so on). OWL restriction
and RDF-list blank nodes follow the module of the resource that owns them.

The writer preserves RDF meaning and FSL's module/default-prefix convention;
it does not preserve comments or whitespace because those are not part of the
RDF graph model. It also orders the ontology header first, followed by class
subjects, property subjects, and remaining subjects, as requested by the
formatting policy in `tbox.ttl`.

## Requirements

See Makefile: make install

## Roundtripping test

See Makefile: make roundtrip

## Tests

See Makefile: make test

## Illustration of SPARQL Update

Use the complete in-memory graph with SPARQL Update:

```python
from pathlib import Path

from fsl_rdf import FSLOntology

ontology = FSLOntology.read(Path("ontologies"))

ontology.graph.update("""
PREFIX ce:   <http://www.softlang.org/ontologies/ce#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

DELETE {
    ce:AcceptanceTesting foaf:isPrimaryTopicOf ?oldPage .
}
INSERT {
    ce:AcceptanceTesting foaf:isPrimaryTopicOf
        <https://en.wikipedia.org/wiki/Acceptance_testing> .
}
WHERE {
    OPTIONAL { ce:AcceptanceTesting foaf:isPrimaryTopicOf ?oldPage . }
}
""")

ontology.write(Path("build/ontologies"))
```
