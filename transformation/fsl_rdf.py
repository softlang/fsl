"""RDFLib reader/writer for the modular FSL Turtle ontology.

The public ``graph`` attribute is the union of every ``*.ttl`` file in the
ontology directory and can be queried or updated with normal RDFLib APIs.  On
write, triples are routed back to modules by their subject namespace.  Blank
node subgraphs (OWL restrictions and RDF lists) follow their owning subject.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Iterable

from rdflib import BNode, Graph, URIRef
from rdflib.namespace import OWL, RDF, RDFS
from rdflib.plugins.serializers.turtle import TurtleSerializer
from rdflib.term import Identifier


PROPERTY_TYPES = {
    RDF.Property,
    OWL.AnnotationProperty,
    OWL.DatatypeProperty,
    OWL.ObjectProperty,
    OWL.OntologyProperty,
}


class FSLTurtleSerializer(TurtleSerializer):
    """Turtle serializer with the subject sections required by FSL policy."""

    _forced_namespaces: dict[str, URIRef]

    def serialize(
        self,
        stream: BinaryIO,
        base: str | None = None,
        encoding: str | None = None,
        spacious: bool | None = None,
        *,
        forced_namespaces: dict[str, URIRef] | None = None,
        **kwargs,
    ) -> None:
        self._forced_namespaces = forced_namespaces or {}
        super().serialize(
            stream, base=base, encoding=encoding, spacious=spacious, **kwargs
        )

    def startDocument(self) -> None:  # noqa: N802 (RDFLib API)
        # RDFLib normally emits only prefixes used in a QName. FSL's module
        # convention requires the module's default namespace even for an empty
        # module such as ie.ttl.
        self.namespaces.update(self._forced_namespaces)
        super().startDocument()

    def orderSubjects(self) -> list[Identifier]:  # noqa: N802 (RDFLib API)
        def section(subject: Identifier) -> int:
            if (subject, RDF.type, OWL.Ontology) in self.store:
                return 0
            if (
                (subject, RDF.type, OWL.Class) in self.store
                or any(self.store.triples((subject, RDFS.subClassOf, None)))
            ):
                return 1
            if (
                any((subject, RDF.type, kind) in self.store for kind in PROPERTY_TYPES)
                or any(self.store.triples((subject, RDFS.subPropertyOf, None)))
            ):
                return 2
            if isinstance(subject, BNode):
                return 4
            return 3

        subjects = list(self._subjects)
        subjects.sort(key=lambda subject: (section(subject), str(subject)))
        return subjects


@dataclass(frozen=True)
class Module:
    name: str
    source: Path
    ontology_iri: URIRef
    default_namespace: URIRef | None
    declared_prefixes: tuple[tuple[str, URIRef], ...]


class FSLOntology:
    """One mutable RDF graph backed by FSL's namespace-per-file modules."""

    def __init__(self, graph: Graph, modules: dict[str, Module], origins: dict):
        self.graph = graph
        self.modules = modules
        self._origins = origins
        self._global_prefixes = self._collect_global_prefixes()

    @classmethod
    def read(cls, ontology_dir: str | Path) -> "FSLOntology":
        ontology_dir = Path(ontology_dir)
        files = sorted(ontology_dir.glob("*.ttl"))
        if not files:
            raise FileNotFoundError(f"No Turtle files found in {ontology_dir}")

        union = Graph(bind_namespaces="none")
        modules: dict[str, Module] = {}
        origins: dict[tuple, set[str]] = defaultdict(set)

        for path in files:
            module_graph = Graph(bind_namespaces="none")
            module_graph.parse(path, format="turtle")
            ontology_iris = sorted(
                module_graph.subjects(RDF.type, OWL.Ontology), key=str
            )
            if len(ontology_iris) != 1 or not isinstance(ontology_iris[0], URIRef):
                raise ValueError(
                    f"{path} must declare exactly one named owl:Ontology; "
                    f"found {len(ontology_iris)}"
                )

            prefixes = tuple(
                (prefix or "", URIRef(namespace))
                for prefix, namespace in module_graph.namespaces()
            )
            default_namespace = next(
                (namespace for prefix, namespace in prefixes if prefix == ""), None
            )
            name = path.stem
            modules[name] = Module(
                name=name,
                source=path,
                ontology_iri=ontology_iris[0],
                default_namespace=default_namespace,
                declared_prefixes=prefixes,
            )
            for triple in module_graph:
                union.add(triple)
                origins[triple].add(name)

        result = cls(union, modules, dict(origins))
        result._bind_union_prefixes()
        return result

    def replace_object(
        self, subject: Identifier, predicate: URIRef, object_: Identifier
    ) -> frozenset[Identifier]:
        """Replace every object for ``(subject, predicate)`` with ``object_``.

        This is the RDF equivalent of setting a single-valued property. It is
        an upsert: when no matching triple exists, the new triple is simply
        added. If one or several matching triples exist, all are removed first.

        The previous object values are returned for logging or change
        detection. RDFLib's ``Graph.set`` performs the actual atomic in-memory
        remove-and-add operation.
        """

        previous = frozenset(self.graph.objects(subject, predicate))
        self.graph.set((subject, predicate, object_))
        return previous

    def write(self, output_dir: str | Path) -> dict[str, Path]:
        """Serialize every module and return its output path by module name."""

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        routed = {name: Graph(bind_namespaces="none") for name in self.modules}

        for triple in self.graph:
            module_name = self._module_for_triple(triple)
            routed[module_name].add(triple)

        written: dict[str, Path] = {}
        for name, module in sorted(self.modules.items()):
            module_graph = routed[name]
            self._bind_module_prefixes(module_graph, module)
            destination = output_dir / f"{name}.ttl"
            with destination.open("wb") as stream:
                self._serialize(module_graph, stream, module)
            written[name] = destination
        return written

    def _collect_global_prefixes(self) -> dict[str, URIRef]:
        prefixes: dict[str, URIRef] = {}
        for module in self.modules.values():
            for prefix, namespace in module.declared_prefixes:
                if not prefix:
                    continue
                previous = prefixes.get(prefix)
                if previous is not None and previous != namespace:
                    raise ValueError(
                        f"Prefix {prefix!r} has conflicting namespaces: "
                        f"{previous} and {namespace}"
                    )
                prefixes[prefix] = namespace

        # Every module namespace also has a stable qualified form for use from
        # the other files, even if that prefix did not occur in a small module.
        for module in self.modules.values():
            if module.default_namespace is not None:
                prefixes.setdefault(module.name, module.default_namespace)
        return prefixes

    def _bind_union_prefixes(self) -> None:
        for prefix, namespace in sorted(self._global_prefixes.items()):
            self.graph.bind(prefix, namespace, replace=True, override=True)

    def _bind_module_prefixes(self, graph: Graph, module: Module) -> None:
        for prefix, namespace in sorted(self._global_prefixes.items()):
            if namespace != module.default_namespace:
                graph.bind(prefix, namespace, replace=True, override=True)
        if module.default_namespace is not None:
            # Bind last so the module's own terms are rendered as :LocalName.
            graph.bind("", module.default_namespace, replace=True, override=True)

    def _module_for_subject(
        self, subject: Identifier, seen: set[BNode] | None = None
    ) -> str | None:
        if isinstance(subject, URIRef):
            for name, module in self.modules.items():
                if subject == module.ontology_iri:
                    return name
                if module.default_namespace is not None and str(subject).startswith(
                    str(module.default_namespace)
                ):
                    return name
            return None

        if not isinstance(subject, BNode):
            return None

        seen = set() if seen is None else seen
        if subject in seen:
            return None
        seen.add(subject)
        owners = {
            owner
            for parent in self.graph.subjects(None, subject)
            if (owner := self._module_for_subject(parent, seen)) is not None
        }
        if len(owners) > 1:
            raise ValueError(
                f"Blank node {subject} is referenced from multiple modules: "
                f"{sorted(owners)}"
            )
        return next(iter(owners), None)

    def _module_for_triple(self, triple: tuple) -> str:
        # Retain the original physical module for unchanged triples. This is
        # important for deliberate cross-namespace axioms such as assertions
        # about pe:ProgrammingLanguage that live in le.ttl.
        original_owners = self._origins.get(triple, set())
        if len(original_owners) == 1:
            return next(iter(original_owners))
        if len(original_owners) > 1:
            raise ValueError(
                f"Triple occurred in multiple source modules and cannot be "
                f"routed uniquely: {triple!r}"
            )

        # New triples produced through RDFLib or SPARQL Update are routed by
        # subject namespace. New blank-node structures follow their owner.
        owner = self._module_for_subject(triple[0])
        if owner is not None:
            return owner
        raise ValueError(
            "Cannot choose an output module for triple with subject "
            f"{triple[0]!r}. Use a module namespace, or attach a blank-node "
            "subgraph to a namespaced resource."
        )

    @staticmethod
    def _serialize(graph: Graph, stream: BinaryIO, module: Module) -> None:
        forced = (
            {"": module.default_namespace}
            if module.default_namespace is not None
            else {}
        )
        FSLTurtleSerializer(graph).serialize(
            stream, encoding="utf-8", forced_namespaces=forced
        )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read all FSL Turtle modules into one graph and write them back."
    )
    parser.add_argument("ontology_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    ontology = FSLOntology.read(args.ontology_dir)
    paths = ontology.write(args.output_dir)
    print(f"Loaded {len(ontology.graph)} triples from {len(paths)} modules.")
    for name, path in sorted(paths.items()):
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
