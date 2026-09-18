1. **P:** Add an ontology vocabulary for review issues to FSL, with a new **ie** module and issue-related properties in **tbox**.  
   **R:** Extended **tbox** with **IssueEntity** plus properties such as **subject**, **predicate**, **object**, **target**, **critique**, and **suggestion**; created an initially minimal **ie** module; wired **ie** into the modular ontology; and summarized the changes.

2. **P:** Correct the first issue-vocabulary integration because **IssueEntity** should not be a conceptual entity, and **ie** should import **tbox**.  
   **R:** Reworked the integration so **IssueEntity** became only a subclass of **Entity**, ensured that **ie** imports **tbox**, and added illustrative example issues showing the intended usage patterns.

3. **P:** Reconsider whether the extra property **target** is needed at all.  
   **R:** Analyzed the design and concluded that **target** was redundant if issue kinds are inferred from the presence of **subject**, **predicate**, and **object**, though it could still help if issue targets later became more heterogeneous.

4. **P:** Ask whether module-level issues can simply use the ontology URI as **subject** instead of needing a separate **target** property.  
   **R:** Confirmed that using the ontology/module URI as **subject** is clear enough under a documented convention, but also explained that **target** can separate “what is under review” from “how an assertion is localized.”

5. **P:** Choose a cleaner division of labor in which **target** identifies the primary reviewed resource while **subject/predicate/object** identify assertion roles.  
   **R:** Updated the issue-vocabulary documentation and examples so **target** is used for resource-level and module-level issues, while **subject**, **predicate**, and **object** are reserved for specifying the role of resources within an assertion under review.

6. **P:** Clarify the intended issue forms and enrich the examples accordingly.  
   **R:** Added or updated illustrative issues that explicitly distinguish resource issues via **target**, module issues via **target**, assertion issues focusing on the **subject** role, and assertion issues focusing on the **object** role.

7. **P:** Ensure the examples in **ie** use the default module namespace consistently.  
   **R:** Switched the illustrative issue instances in **ie** to use the default namespace form throughout.

8. **P:** Keep the vocabulary stable while refining its documentation.  
   **R:** Left the core **tbox** vocabulary structurally intact, but clarified in the comments that **target** denotes the primary reviewed resource or module, while **subject/predicate/object** denote assertion roles, yielding a cleaner distinction between resource-level review and assertion-level review.
