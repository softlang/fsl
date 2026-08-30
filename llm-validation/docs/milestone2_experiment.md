# Milestone 2 Experiment: SHACL + LLM-style Explanation Layer

## Objective
Evaluate whether SHACL validation results can be transformed into human-readable explanations.

## Setup
- FSL ontology (tbox.ttl)
- pySHACL validation engine
- Custom SHACL shapes for:
  - documentation completeness (rdfs:comment)
  - external reference completeness (foaf links)

## Experiments

### Experiment 1: Missing rdfs:comment
- Removed rdfs:comment from :Entity (owl:Class)
- Result: SHACL violation detected successfully

### Experiment 2: Missing FOAF link
- Removed foaf:page from :Entity (owl:Class)
- Result: SHACL violation detected successfully

## Result
Both violations were successfully detected and transformed into structured explanations.

## Observation
SHACL outputs are machine-readable but not human-friendly. A transformation layer is required.

## Conclusion
A rule-based interpretation layer can bridge SHACL validation outputs and human-readable explanations.
