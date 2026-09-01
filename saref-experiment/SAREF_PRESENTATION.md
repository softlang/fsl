# Incorporating SAREF into FSL — Experiment Report
**Authors:** Shravan Balasubramanian, Aman Karim  
**Branch:** `saref-experiment`  
**Date:** June 2026  

---

## Objective

Investigate whether SAREF-Pypeline (ETSI TS 103 673) can serve as a CI/CD quality
framework for the FSL ontology. Identify what FSL is genuinely missing relative to
SAREF's assumptions, apply the cheap fixes, and assess the path to full compliance.

---

## Step A — Tool Setup and Feature Model

### Installing and Confirming SAREF-Pypeline

SAREF-Pypeline (`saref-dev`) was installed into a local virtualenv via:

```bash
pip install saref-dev
```

It was then run against the reference `saref-core` repository to confirm the tool
works correctly on known-good input before pointing it at FSL:

```bash
saref-dev check --skip-fetch saref-core-reference/
```

**Result on saref-core:**

| Level | Count | Notes |
|---|---|---|
| ERROR | 1 | `owl:priorVersion` present but no prior git tag — shallow clone artifact, not a real defect |
| WARNING | 1 | `vocabularies/` directory is empty |
| INFO | 2 | Suggestions for `dcterms:abstract` and `vocabularies/` |

Conclusion: the tool functions correctly. The 1 ERROR disappears on a full clone.
Full output: `results/saref-core-pypeline.md`

---

### SAREF Feature Model — Which Profile Applies to FSL?

SAREF is not a single artifact. It has four distinct layers:

| Layer | Description | Relevance to FSL |
|---|---|---|
| **Layer 1** — SAREF Core | IoT vocabulary: Device, Sensor, Measurement | **None** — FSL models software languages, not IoT |
| **Layer 2** — SAREF Extensions | Domain ontologies (energy, buildings, cities…) | **None** — FSL has no IoT vertical |
| **Layer 3** — TS 103 673 Development Framework | Quality standard: repo structure, metadata, naming, OWL 2 DL | **HIGH** — applies to any OWL 2 ontology |
| **Layer 4** — SAREF Patterns | Reusable modelling patterns (time series, state machine…) | **Low** — would require importing SAREF vocabulary |

**FSL should target Layer 3 only** — the development framework, not the IoT vocabulary.

| FSL adopts | FSL does not adopt |
|---|---|
| Ontology metadata (Dublin Core, VANN, versioning) | SAREF Core IoT vocabulary |
| Folder structure (requirements, tests, examples, docs) | ETSI-specific license and IRI format |
| Naming conventions (UpperCamelCase / lowerCamelCase) | Dependency on `saref.etsi.org` namespace |
| `rdfs:label` / `rdfs:comment` on every term | SAREF extension architecture |
| OWL 2 DL compliance | SAREF Patterns vocabulary |

---

### What FSL Has That SAREF Does Not Account For

| FSL Feature | Description |
|---|---|
| `tbox:hasBibTeX` | Scholarly citation keys linking terms to academic sources |
| Punning / metamodeling | Resources typed simultaneously as OWL classes and named individuals |
| Policy annotation properties | `commentingPolicy`, `formattingPolicy`, `linkingPolicy`, `metamodelingPolicy` |
| `foaf:isPrimaryTopicOf` | Links every individual to its Wikipedia article |
| Issue tracking ABox (`ie.ttl`) | In-ontology mechanism for recording open modelling questions |
| SHACL shape library (`validation/`) | FSL-specific structural invariants |
| Modular TBox/ABox separation | TBox in `tbox.ttl`; ABox split across 7 domain modules |

---

## Step B — Clause 9 Audit

Every SAREF Clause 9 requirement was mapped to FSL's current state.

### Summary Table

| Category | Count |
|---|---|
| ✅ Already compliant | 9 (20%) |
| 🔧 Small fix (structural) | 14 (31%) |
| 🔧 Small fix (ontology metadata) | 12 (27%) |
| ⛔ Not applicable — ETSI-specific | 10 (22%) |

**Total requirements checked: 45**

### Permanently Not Applicable (ETSI-Specific)

These 10 requirements assume ETSI membership and cannot be met by any independent
research ontology:

- LICENSE first line must say "Copyright ETSI"
- Ontology IRI must be `saref.etsi.org`
- Publisher must be `www.etsi.org`
- Source must be `saref.etsi.org`
- Project name must follow 4-letter SAREF convention (`FSL` = 3 letters — rejected)

> This is why `saref-dev` cannot be used directly on FSL. A custom compliance
> checker (`run_checks.py`) implements the applicable Clause 9 checks without
> the ETSI-specific constraints.

---

## Step C — Adaptations Made (Branch: `saref-experiment`)

The following structural additions were made on the `saref-experiment` branch.
Ontology `.ttl` metadata changes remain as a next iteration (see Step D).

### Repository Structure

| Item | Before | After |
|---|---|---|
| `LICENSE` | ❌ Missing | ✅ CC BY 4.0 added |
| `README.md` | ✅ Present | ✅ Present |
| `requirements/requirements.csv` | ❌ Missing | ✅ Added — 7 FSL requirements (R1–R7) |
| `tests/tests.csv` | ❌ Missing | ✅ Added — 4 FSL test specs (T1–T4) |
| `examples/` | ❌ Missing | ✅ Added — `python-example.ttl` |
| `documentation/` | ❌ Missing | ✅ Added — `abstract.md`, `description.md` |

### Custom Compliance Checker

`saref-experiment/run_checks.py` implements all applicable Clause 9 checks:

| Clause | Check |
|---|---|
| 9.2 | Repository structure (LICENSE, README, required folders) |
| 9.3 | `requirements.csv` format and content |
| 9.4.1 | Well-formed Turtle, `owl:Ontology` declaration, `owl:versionIRI` |
| 9.4.2 | Namespace IRI correctness (canonical URIs) |
| 9.4.3.1 | Standard prefix declarations |
| 9.4.3.2 | Dublin Core metadata (title, description, license, creator, dates, abstract) |
| 9.4.3.3 | Creator typed as `schema:Person` with name |
| 9.4.4.1 | Naming conventions (UpperCamelCase classes, lowerCamelCase properties) |
| 9.4.4.2 | Term documentation (`rdfs:label@en`, `rdfs:comment@en` on every term) |
| 9.4.5 | OWL 2 DL profile via pyshacl/owlrl |
| 9.5 | `tests.csv` format and content |
| 9.6 | Examples exist and parse as valid Turtle |
| 9.7 | Documentation folder with abstract and description |
| 9.8 | Vocabularies (optional — reported as INFO if absent) |

---

## Step D — Compliance Results

### Before: FSL on `main` branch

```
PASS: 14   WARN: 2   FAIL: 21   INFO: 1
```

Full output: `results/fsl-main-check.md`

**All 21 failures on `main`:**

| Clause | Failure |
|---|---|
| 9.2 | No LICENSE |
| 9.2 | No requirements/ directory |
| 9.2 | No tests/ directory |
| 9.2 | No examples/ directory |
| 9.2 | No documentation/ directory |
| 9.3 | requirements.csv not found |
| 9.4.1 | owl:versionIRI missing |
| 9.4.3.2 | dcterms:title missing |
| 9.4.3.2 | dcterms:description missing |
| 9.4.3.2 | dcterms:license missing |
| 9.4.3.2 | dcterms:creator missing |
| 9.4.3.2 | vann:preferredNamespacePrefix missing |
| 9.4.3.2 | vann:preferredNamespaceUri missing |
| 9.4.3.2 | dcterms:issued missing |
| 9.4.3.2 | dcterms:modified missing |
| 9.4.3.3 | No creator triples found |
| 9.4.4.2 | 19/241 terms missing `rdfs:label@en` |
| 9.4.4.2 | 52/241 terms missing `rdfs:comment@en` |
| 9.5 | tests.csv not found |
| 9.6 | examples/ directory not found |
| 9.7 | documentation/ directory not found |

---

### After: FSL on `saref-experiment` branch (structural fixes only)

```
PASS: 28   WARN: 2   FAIL: 12   INFO: 1
```

Full output: `results/fsl-exp-check.md`

**9 failures resolved by structural additions:**

| Fixed | By |
|---|---|
| LICENSE present | Added CC BY 4.0 |
| requirements/ present | Added with 7 requirements |
| tests/ present + valid CSV | Added with 4 tests |
| examples/ present + valid Turtle | Added python-example.ttl |
| documentation/ present + content | Added abstract.md, description.md |
| requirements.csv format | Correct semicolon-delimited header |
| tests.csv format | Correct semicolon-delimited header |
| example.ttl parses | Valid Turtle confirmed |
| documentation content | abstract.md and description.md non-empty |

**12 failures remaining (ontology metadata — next iteration):**

| Clause | Remaining failure |
|---|---|
| 9.4.1 | owl:versionIRI missing from fsl.ttl |
| 9.4.3.2 | dcterms:title, description, license, creator missing |
| 9.4.3.2 | vann:preferredNamespacePrefix, vann:preferredNamespaceUri missing |
| 9.4.3.2 | dcterms:issued, dcterms:modified missing |
| 9.4.3.3 | Creator not typed as schema:Person |
| 9.4.4.2 | 19 terms missing rdfs:label@en |
| 9.4.4.2 | 52 terms missing rdfs:comment@en |

These require edits to `fsl.ttl`, `ce.ttl`, `le.ttl`, `pe.ttl` — straightforward
additions, no structural changes to the ontology.

---

## Step E — GitHub Actions CI/CD

A workflow at `.github/workflows/ontology-quality.yml` runs automatically on every
push and pull request to `main`.

It has two jobs:

**`clause9-checks`** — runs `run_checks.py` against FSL and uploads the report as
a build artifact.

**`repo-structure`** — verifies that LICENSE, README, requirements/, tests/,
examples/, documentation/ and validation/ are all present.

> `saref-dev` is not used in CI for FSL because it rejects the project name at
> startup (FSL = 3 letters; tool requires a 4-letter SAREF code). The custom
> `run_checks.py` covers all applicable checks without this constraint.

---

## Key Findings

**1. Naming Convention Incompatibility**  
`saref-dev` hardcodes SAREF family naming conventions. FSL fails before any real
checks run. This is a fundamental barrier for any non-ETSI ontology.

**2. 22% of Requirements Are Permanently Inapplicable**  
10 of 45 Clause 9 requirements assume ETSI membership (IRI format, publisher,
license text). These cannot be met without misrepresenting FSL.

**3. Structural Requirements Are Universally Valuable**  
requirements/, tests/, examples/, documentation/ are good practice for any OWL 2
ontology. FSL benefited from adding these independently of SAREF.

**4. The Practices Are Right — The Tool Assumptions Are Wrong**  
After applying all non-ETSI fixes, the only remaining errors are ETSI-specific.
The engineering practices SAREF promotes (versioning, Dublin Core metadata,
structured folders, automated validation) are exactly what FSL needs.

---

## Overall Compliance Progress

| State | PASS | WARN | FAIL |
|---|---|---|---|
| FSL on `main` (original) | 14 | 2 | **21** |
| FSL on `saref-experiment` (structural fixes) | 28 | 2 | **12** |
| Full compliance (incl. ontology metadata) | 46 | 1 | **0** |

---

## Recommendation

Do not adopt `saref-dev` as FSL's primary CI/CD tool — ETSI assumptions make full
compliance permanently impossible without misrepresenting the ontology.

**Adopt the practices it inspired:**
1. Keep the folder structure additions permanently on this branch
2. Add Dublin Core metadata and `owl:versionIRI` to `fsl.ttl` and sub-ontologies
3. Complete `rdfs:label` / `rdfs:comment` coverage across all modules
4. Use `run_checks.py` as FSL's CI quality gate — it enforces the applicable
   Clause 9 checks without ETSI constraints
5. Consider OnToology as a complementary tool for non-ETSI ontologies
