1. **P:** Extend the ontology with the notion of **technological spaces**, and first explain the idea before changing the OWL.  
   **R:** Reframed the ontology so that subject areas classify by discipline while technological spaces classify by ecosystem, and proposed technological spaces as a second, orthogonal organizing dimension for languages, tools, artifacts, and transformations.

2. **P:** Collect and refine the scholarly basis for technological spaces.  
   **R:** Assembled a reusable reference set with short “role” summaries, corrected reference URLs, added grammarware- and megamodeling-related papers, and established that the ontology should later carry lightweight literature-reference entities rather than raw BibTeX dumps.

3. **P:** Reconsider the proposed cross-space ingredient categories so they align better with technological-space literature.  
   **R:** Dropped the nonstandard idea of an “artifact language” class, recognized that technological spaces are mostly organized around languages plus tools and relations, and began reshaping the design around those recurring roles.

4. **P:** Decide on the core non-language categories and on how artifacts should be represented.  
   **R:** Kept **SoftwareLanguage**, accepted **SoftwareTool**, briefly accepted **SoftwareRelation**, and decided that “artifact” should not become a top-level class but instead should be modeled contextually through the roles a technological space assigns.

5. **P:** Explore a role-based description of technological spaces via many `hasXyzLanguage` properties.  
   **R:** Identified the main recurring language roles across spaces—artifact, metalanguage, schema, constraint, query, transformation, mapping, and fallback “other language”—while treating that design as provisional rather than final.

6. **P:** Clarify whether “execution language” is a valid cross-space role.  
   **R:** Rejected **execution language** as a core category and decided that execution belongs on the tool side instead, leaving the technological-space language-role inventory cleaner and more stable.

7. **P:** Reassess the role-property design because it risks duplicating the language and tool hierarchies.  
   **R:** Shifted toward a more compact design in which classification hierarchies carry most of the semantic load, while technological spaces use only a small number of direct properties.

8. **P:** Resolve the leveling problem that spaces should not point directly to arbitrary concrete languages or tools.  
   **R:** Moved toward a megamodeling-inspired pattern in which spaces are characterized by **artifact kinds** and **tool kinds**, while concrete languages and tools remain optional representatives of those categories rather than direct defining ingredients of the space.

9. **P:** Clarify the special case of Grammarware, where the relation between artifacts and languages is easy to misunderstand.  
   **R:** Distinguished object artifacts from definition artifacts and concluded that Grammarware operates on grammar artifacts that are expressed in grammar metalanguages, while the texts described by those grammars belong to other spaces.

10. **P:** Import the megamodeling “trick” explicitly into the ontology design.  
    **R:** Adopted the pattern **TechnologicalSpace → ArtifactKind → Language**, with conformance and processing relations layered on top, so that spaces are defined by artifact kinds and their defining languages rather than by a muddled direct link to either language classes or language individuals.

11. **P:** Turn that design into a first substantial OWL review segment.  
    **R:** Introduced **TechnologicalSpace**, a first hierarchy of spaces and concrete spaces such as **Grammarware**, **Modelware**, **Programware**, **XMLware**, **JSONware**, **SQLware**, **Ontoware**, **Graphware**, **APIware**, and **Tabularware**; added **ArtifactKind**, **SoftwareTool**, and key relations such as **hasSpace**, **hasArtifactKind**, **hasToolKind**, **elementOf**, **conformsTo**, **describesArtifactKind**, **processesArtifactKind**, and **supportsLanguage**; and expanded the software-language hierarchy with many space-relevant categories and examples.

12. **P:** Revise that segment to fix conceptual problems and fill coverage gaps.  
    **R:** Detached **OntologyLanguage** from **SchemaLanguage**, introduced **SemanticDataModelLanguage** so **RDF** is treated as a semantic data model rather than an ontology language, modeled **SQL** as a language family with **DDL**, **DML**, and query parts, added or reconsidered additional spaces, and corrected the misuse of **conformsTo** by introducing **elementOf** for artifact-kind membership in a language and reserving **conformsTo** for artifact-kind-to-artifact-kind conformance.

13. **P:** Integrate the new technological-space machinery back into the full ontology, not just a review fragment.  
    **R:** Produced a complete revised ontology that merged the earlier OFSL content with technological spaces, artifact kinds, tool kinds, updated relation patterns, broader metadata coverage, and comments and links for newly added entities.

14. **P:** Improve the external-linking policy so classes and concrete entities are treated differently.  
    **R:** Adopted a nuanced rule: higher-level conceptual classes use **`rdfs:seeAlso`**, while concrete named entities continue to use **`owl:sameAs`**, and regenerated the full ontology accordingly.

15. **P:** Further clean up the ontology by adding inverses where useful, making subject areas and technological spaces pairwise distinct, removing obsolete relation taxonomy, and reifying literature references with enough detail for future BibTeX extraction.  
    **R:** Added inverse properties for the confirmed object properties, declared named subject areas and technological spaces pairwise distinct via **`owl:AllDifferent`**, removed **SoftwareRelation** and its subclasses, introduced lightweight **LiteratureReference** entities and linking properties, attached core technological-space references with concise role comments, and added the compact technological-space definition to the ontology.

16. **P:** Revisit the broader structural organization of the ontology after the technological-space extension.  
   **R:** Refactored the ontology from **OFSL** to **FSL** (“Foundations of software languages”), moved from the `ofsl` namespace to `fsl`, introduced **LanguageEntity** as a new grouping branch, renamed **PrimaryEntity** to **FoundationalEntity** and **SecondaryEntity** to **MetadataEntity**, renamed **Approach** to **MethodologicalApproach**, renamed the formal-syntax branch to **SyntaxDefinitionApproach**, **DefiningConcreteSyntax**, and **DefiningAbstractSyntax**, and adjusted property declarations so the ontology remained coherent under the new grouping structure.

17. **P:** Validate the result by summarizing what changed in the refactoring step.  
    **R:** Confirmed that the ontology now separates language entities, foundational entities, and metadata entities more clearly, while preserving the earlier technological-space machinery, inverse properties, part/extension relations, literature references, and the refined `sameAs`/`seeAlso` policy.
