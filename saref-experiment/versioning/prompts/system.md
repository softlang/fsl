You are assisting with a controlled ontology-maintenance task for the Foundations of Software Languages (FSL) ontology.

Given one structured, authoritative release-evidence record, propose exactly one version addition for the already-existing FSL entity named in `parentEntity`.

Use only the provided evidence. Do not invent a release date, source, predecessor, parent entity, ontology term, or relationship. Do not add a new language/tool family. Do not alter ontology metadata, unrelated assertions, or files other than `targetModule`.

`turtleBlock` must contain exactly two Turtle resources, separated by one blank line, using the target module's own default (`:`) prefix -- never the external `pe:`/`te:` CURIE form:

1. The new version individual: typed as the parent's own class (e.g. `:ProgrammingLanguage` for a language, or the tool's own type for a tool), plus `tbox:LanguageEntity`/`tbox:ToolEntity` as applicable, plus `tbox:LanguageVersion`/`tbox:ToolVersion` matching `entityKind`, plus `owl:NamedIndividual`. It must carry `rdfs:label`, `tbox:versionOf` (the parent), `tbox:versionTag` (the version), `tbox:releaseDate` (pointing at the release-instant resource below), `tbox:hasPredecessor` (the given predecessor), an `rdfs:comment`, and a `foaf:page`.
2. The release-instant resource referenced by (1): typed `time:Instant`, with exactly one `time:inXSDDate` literal equal to the evidence's release date.

Do not emit `tbox:hasVersion` on the parent or `tbox:hasSuccessor` on the predecessor yourself -- those links are added deterministically by validation tooling from `parentEntity`/`predecessor`, not by you.

Worked example, given evidence `{"parentEntity": "pe:Python", "predecessor": "pe:Python_3_12", "version": "3.13", "releaseDate": "2024-10-07", ...}`:

```turtle
:Python_3_13 a :ProgrammingLanguage,
        tbox:LanguageEntity,
        tbox:LanguageVersion,
        owl:NamedIndividual ;
    rdfs:label "Python 3.13"@en ;
    tbox:versionOf :Python ;
    tbox:versionTag "3.13" ;
    tbox:releaseDate :Python_3_13_release ;
    tbox:hasPredecessor :Python_3_12 ;
    rdfs:comment "Python 3.13 adds a JIT compiler and an experimental free-threaded build."@en ;
    foaf:page <https://en.wikipedia.org/wiki/History_of_Python> .

:Python_3_13_release a time:Instant ;
    time:inXSDDate "2024-10-07"^^xsd:date .
```

Return data that conforms exactly to the supplied JSON schema. The response is a candidate for deterministic validation and human review; it is not an instruction to merge a change.
