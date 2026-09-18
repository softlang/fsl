1. **P:** Start a software-engineering vocabulary by collecting a broad list of software-engineering activities.  
   **R:** Produced a structured activity inventory covering planning, requirements, design, implementation, verification/validation, release/deployment, operations/maintenance, evolution, quality/governance, and supporting activities.

2. **P:** Decide how such activities should be presented in OWL so that broad groups and specific activities can both be used as labels.  
   **R:** Recommended modeling **activity types as classes** in a taxonomy, with coarse groupings and finer-grained subactivities linked by subclassing.

3. **P:** Reject a pure class-only target for relations such as “formalism X serves activity Y” because the relation needs a constrained object-property range.  
   **R:** Switched to an OWL 2 **punning/metamodeling** design in which each activity term is both a class in the taxonomy and an individual of **ActivityEntity**, enabling normal object properties to point to activity vocabulary items.

4. **P:** Ask for complete OWL/Turtle code covering the agreed activity hierarchy and punning pattern.  
   **R:** Produced a fairly complete **Software Engineering Activity Vocabulary (SEAV)** with grouped activity classes, finer activity types, and parallel typing as **ActivityEntity** individuals.

5. **P:** Simplify the SEAV module by removing broader/narrower helper relations and presentation clutter.  
   **R:** Dropped the proposed individual-level broader relation, compacted the Turtle style, and kept only the punning-based hierarchy plus activity declarations.

6. **P:** Remove foreign FSL content and example formalism assertions from the SE vocabulary module itself.  
   **R:** Removed **fsl:Formalism**, **fsl:servesActivity**, and the example formalism instances from the SEAV module so it remained a pure activity vocabulary.

7. **P:** Enrich the vocabulary with external-resource links.  
   **R:** Added **FOAF/Wikipedia links** where possible and then refined the policy so strong matches use **foaf:isPrimaryTopicOf** while broader or approximate matches use **foaf:page**.

8. **P:** Constrain the metamodeling layer so every activity vocabulary item has some external page/topic link.  
   **R:** Added an OWL restriction on **ActivityEntity** requiring either a **foaf:isPrimaryTopicOf** or **foaf:page** link, while noting that SHACL would be needed for real closed-world validation.

9. **P:** Generate the fully revised Turtle module with the mixed FOAF-linking strategy and the ActivityEntity restriction integrated.  
   **R:** Produced the full revised SEAV module in compact Turtle using the mixed **foaf:isPrimaryTopicOf / foaf:page** policy and the ActivityEntity restriction.

10. **P:** Move beyond activities and ask for a second axis capturing “types” or other classification dimensions of software engineering.  
    **R:** Proposed an initial list of software-engineering **contexts/modes** grouped by system scope, application domain, quality/constraint focus, lifecycle/process style, methodological paradigm, artifact focus, organizational context, and deployment model.

11. **P:** Object that several important distinctions, such as frontend/backend, monolith/microservices, TDD, and MDE, do not fit well under the simple activity-versus-type split.  
    **R:** Broadened the design into multiple orthogonal **engineering aspects/dimensions**, including **system layer**, **architectural style**, **engineering methodology**, **engineering practice**, **engineering paradigm**, **application domain**, **quality profile**, **deployment model**, and **organizational context**.

12. **P:** Clarify how TDD and MDE should be placed among those dimensions.  
    **R:** Classified **TDD** as an **engineering practice** and **MDE** as an **engineering paradigm**, separating them from broader methodological and contextual categories.

13. **P:** Integrate SEAV into the modular FSL ontology with minimal disturbance.  
    **R:** Moved the SEAV resources into module **ce**, put them into the **ce** namespace, treated them as conceptual entities, and created a revised FSL ZIP in which SEAV no longer lived as a standalone ontology.

14. **P:** Integrate SEAV more deeply into FSL.  
    **R:** Made **ce:EngineeringActivity** a subclass of **tbox:ConceptualEntity**, propagated the conceptual-entity punning regime through the SEAV hierarchy, merged **ce:CodeGenerationActivity** back into **ce:CodeGeneration**, and normalized labels to upper-case initials.

15. **P:** Consolidate external-resource linking across the whole ontology, not just SEAV.  
    **R:** Replaced **owl:sameAs** by **foaf:isPrimaryTopicOf**, replaced **rdfs:seeAlso** by **foaf:page**, pulled the FOAF-link restriction up from the SEAV layer to **tbox:Entity**, and removed competing local restrictions.

16. **P:** Simplify the SE integration further by removing the extra metamodeling class for activities.  
    **R:** Removed **ce:ActivityEntity** and reused **tbox:ConceptualEntity** directly for the punning/metamodeling role that activity vocabulary items needed.

17. **P:** Ask how software-engineering activities could be connected properly to the rest of FSL.  
    **R:** Reviewed the existing cross-module property inventory and concluded that some generic properties, especially **tbox:uses**, could already bridge activities to foundational entities, language entities, artifacts, tools, and other conceptual entities, while deeper integration would probably require a small additional activity-centered relation layer rather than forcing everything through the existing FE-centric patterns.
