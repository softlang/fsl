1. **P:** Start from the consolidated ontology and rename it at the OWL level.  
   **R:** Renamed the ontology to **Ontology on Formalisms for Software Languages (OFSL)**, changed the ontology IRI/base/prefix from `sle` to `ofsl`, and updated the ontology label and comment accordingly.

2. **P:** Introduce an explicit meta-layer for ontology entities so resources are not distinguished only by namespace or by being classes versus individuals.  
   **R:** Added **OntologyEntity** at the top, with **PrimaryEntity** and **SecondaryEntity** as its only subclasses, enabling a punning-based metamodel where ontology resources can be typed as primary or secondary entities.

3. **P:** Add a secondary-entity class for subject areas based on the provided CSV data.  
   **R:** Introduced the class **Area** and added one individual per CSV row, such as **SLE**, **CC**, **PLT**, **TCS**, **SE**, **FM**, **KR**, **CL**, and **NLP**, each with label, comment, and Wikipedia link.

4. **P:** Tighten the meta-model so that only **PrimaryEntity** and **SecondaryEntity** specialize **OntologyEntity**.  
   **R:** Adopted the rule that domain resources like **Area**, **FormalSystem**, and **SoftwareLanguage** are typed as primary or secondary entities via punning, but are no longer made subclasses of **OntologyEntity**.

5. **P:** Add a property connecting primary entities to areas, with one to three areas per primary entity, and suggest assignments across the ontology.  
   **R:** Declared **hasArea** with domain **PrimaryEntity**, range **Area**, and 1–3 qualified-cardinality constraints; then attached area assignments to all primary entities, favoring **SLE**, **CC**, **PLT**, and **TCS** while using the other areas more selectively.

6. **P:** Refactor the ontology so that “approaches” become a dedicated top-level part of the taxonomy.  
   **R:** Introduced the top-level class **Approach**, moved the old `...Approach` resources into a new approach hierarchy, dropped “approach” from their URIs and labels, and declared a new property **serves** for relating non-approach entities to approaches.

7. **P:** Reclassify denotational, operational, and axiomatic semantics within that new approach hierarchy.  
   **R:** Moved **DenotationalSemantics**, **OperationalSemantics**, and **AxiomaticSemantics** into the approach branch as individuals of **FormalSemantics** rather than treating them as parallel standalone entities merely serving it.

8. **P:** Simplify the metaprogramming branch because no further hierarchy is expected under some approach resources.  
   **R:** Kept **Metaprogramming** as a class under **Approach**, but collapsed **ProgramTransformation** and **SyntaxDirectedTranslation** into individuals of **Metaprogramming**, with existing formalisms linked to them via **serves**.

9. **P:** Add a syntax-oriented counterpart to formal semantics in the approach taxonomy.  
   **R:** Introduced **FormalSyntax** as a new subclass of **Approach**, and added **ConcreteSyntax** and **AbstractSyntax** as its instances, with labels, comments, areas, and Wikipedia links where appropriate.

10. **P:** Connect concrete-syntax-related formalisms to the new syntax branch.  
    **R:** Added **serves** relations from **ContextFreeGrammar**, **RegularGrammar**, **BackusNaurForm**, and **ExtendedBackusNaurForm** to **ConcreteSyntax**.

11. **P:** Introduce a structural/composition-like relation without duplicating taxonomy.  
    **R:** First proposed a broad **hasComponent** relation, then restricted it to genuinely non-taxonomic cases and settled on the minimal useful assertions that **AttributeGrammar** contains a **ContextFreeGrammar** basis and **ExtendedBackusNaurForm** extends **BackusNaurForm**.

12. **P:** Rename the structural relation to something more natural.  
    **R:** Replaced **hasComponent** by **includes**, keeping only the minimal structural assertions for **AttributeGrammar** and **ExtendedBackusNaurForm**.

13. **P:** Introduce a new dependency-style relation for cases of conceptual or technical reliance.  
    **R:** Added **leverages**, made **includes** a subproperty of it, and committed a first set of reliance relations, including semantics approaches leveraging **AbstractSyntax**, **SyntaxDirectedTranslation** leveraging **ContextFreeGrammar**, **ProgramTransformation** leveraging **TermRewritingSystem**, and **Metaprogramming** leveraging **FormalSyntax**.

14. **P:** Review additional semantics-related dependencies.  
    **R:** Accepted that **DenotationalSemantics** leverages **LambdaCalculus**, and later also accepted that **AxiomaticSemantics** leverages **ProgramLogic** and **OperationalSemantics** leverages **AbstractRewritingSystem**.

15. **P:** Extend the ontology with a theory branch to better capture mathematical dependencies of denotational semantics.  
    **R:** Added a new top-level class **Theory** under **FormalSystem**, introduced **DomainTheory** as its subclass, reclassified **TypeTheory** as a subclass of **Theory**, and recorded that **DenotationalSemantics** leverages **DomainTheory**.

16. **P:** Refine the operational-semantics side by introducing models of computation.  
    **R:** Added **ModelOfComputation** as a new top-level primary-entity class, made **AbstractRewritingSystem** and **TransitionSystem** its subclasses, removed their earlier placement under **FormalSystem**, and recorded that **OperationalSemantics** uses both of them.

17. **P:** Reject an ill-fitting dependency between operational semantics and process calculi, and add a better property for that case.  
    **R:** Dropped the idea that **OperationalSemantics** leverages **ProcessCalculus**, introduced **isSpecifiedBy**, and used it to state that **CommunicatingSequentialProcesses** and **CalculusOfCommunicatingSystems** are specified by **OperationalSemantics**.

18. **P:** Add methodological usefulness relations from semantics approaches to transformation and metaprogramming.  
    **R:** Added that **DenotationalSemantics** and **OperationalSemantics** both **serve** **ProgramTransformation** and **Metaprogramming**.

19. **P:** Clean up the property vocabulary to use more common names and add inverses.  
    **R:** Renamed **leverages** to **uses**, renamed **includes** to **hasPart**, made **hasPart** a subproperty of **uses**, and added inverse properties **isUsedBy**, **isServedBy**, and **specifies** for **uses**, **serves**, and **isSpecifiedBy** respectively.

20. **P:** Emit the full updated OWL/Turtle ontology after all accepted changes.  
    **R:** Produced the full OFSL ontology integrating the new ontology header, meta-layer, area system, approach taxonomy, syntax/semantics branches, theory and model-of-computation branches, revised properties, inverse properties, and all updated assertions.
