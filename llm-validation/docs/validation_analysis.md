# Validation Coverage Analysis

## ClassDeclarationsMustHaveCommentShape

Purpose:
Ensures ontology classes contain an rdfs:comment annotation.

Target:
Resources explicitly declared as owl:Class or rdfs:Class.

Experiment:
Removed the rdfs:comment annotation from :Entity.

Result:
SHACL validation failed as expected.

Observation:
The shape does not apply to entities typed as :ConceptualEntity.
