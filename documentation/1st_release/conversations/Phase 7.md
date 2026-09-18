1. **P:** Start from a list of fundamental programming-language concepts and question whether the categories are named and scoped well enough.  
   **R:** Reworked the initial list into a more principled taxonomy, replacing the awkward “computation model” label with **computational paradigms & evaluation models** and separating overlapping areas such as **abstraction** versus **modularity**.

2. **P:** Refine categories that looked arbitrary or underdeveloped, especially abstraction mechanisms, polymorphism, metaprogramming, and concurrency.  
   **R:** Moved polymorphism into the type-related part of the taxonomy, carved out **higher-order entities** and **metaprogramming** as separate categories, and expanded concurrency to cover actor-based models, STM, asynchronous/event-driven styles, and related distinctions.

3. **P:** Push the taxonomy toward cleaner concept boundaries by questioning procedural versus function abstraction, backtracking, metaprogramming terminology, modularity wording, and the split between concurrency and parallelism.  
   **R:** Distinguished **procedural abstraction** from **function abstraction**, moved **backtracking** into **control flow**, simplified **metaprogramming** terminology, reduced **modularity** to a cleaner core, and split **concurrency** from **parallelism** as separate top-level categories.

4. **P:** Remove items that do not belong to the same abstraction level as the rest of the list.  
   **R:** Dropped **semantics** as a category because it is meta-level rather than a language concept directly realized through constructs.

5. **P:** Further factor bundled categories such as binding/scope/lifetime and state/effects/mutability.  
   **R:** Split them into distinct categories: **binding**, **scope**, **lifetime**, **state**, **mutability**, and **effects**, yielding a cleaner, more orthogonal taxonomy.

6. **P:** Reconsider the coupling of data and type systems, and ground the treatment of data in standard PL literature.  
   **R:** Split **data** from **types**, expanded the data side to include product-like, sum-like, recursive, reference-based, and object-like structures, and retained **types** as the category covering type disciplines, type checking, inference, polymorphism, and subtyping.

7. **P:** Decide whether the header should say “types” or “types & type systems.”  
   **R:** Settled on the shorter **types**, with the understanding that the category implicitly includes type systems and their governing rules.

8. **P:** Ask how composite notions such as objects should fit into the emerging taxonomy.  
   **R:** Treated **objects** not as a primitive category but as a composite concept spanning **data**, **abstraction**, **modularity**, and also depending on **state**, **mutability**, and **effects**.

9. **P:** Extend that treatment to other composite notions such as closures, actors, iterators, futures, algebraic data types, and monads.  
   **R:** Mapped these as intersections of the primitive categories, turning the taxonomy into a framework where composite concepts are explained through their dependencies on more basic concepts.

10. **P:** Combine the primitive taxonomy and the composite-concept view into one overall structure.  
    **R:** Introduced the idea of a **concept matrix**, with primitive concepts as dimensions and composite concepts as rows occupying positions in that space.

11. **P:** Reassess whether monads should appear as a row at all, given the risk of overfitting the taxonomy to one advanced topic.  
    **R:** Generalized monads into the broader category **structured computation abstractions**, so the ontology would capture the general pattern of composing computations without privileging one specific functional-programming device.

12. **P:** Decide how actual programming languages should be profiled against the concept taxonomy, and whether language-specific realizations require refined concepts.  
    **R:** Kept the concepts **general and language-independent**, and shifted language-specific variation to the **relationships** between languages and concepts rather than fragmenting the taxonomy itself.

13. **P:** Review how those language-to-concept relations should be qualified, especially regarding global properties like typing and evaluation strategy.  
    **R:** Established a clean separation: independent conceptual axes stay as concept nodes, language-wide properties become ordinary language-to-concept support statements, and only genuinely concept-specific realization details belong on qualified support edges.

14. **P:** Design an OWL/RDF representation for the concept taxonomy and language profiling.  
    **R:** Introduced **Concept**, **PrimitiveConcept**, **CompositeConcept**, **Language**, and **SupportAssertion**, with languages such as **Haskell**, **Java**, **Python**, **Cobol**, **Pascal**, **Prolog**, and **F#** profiled through support relations to concept individuals.

15. **P:** Decide between plain RDF-star, reified support assertions, and multiple support predicates.  
    **R:** Chose **native** versus **standard** support as the only support distinctions, used **SupportAssertion** as the primary reified structure, briefly mirrored it through RDF-star, and then dropped RDF-star again in favor of explicit reification for cleaner stack compatibility.

16. **P:** Restore nuances that had been flattened in the ontology and normalize older qualifier vocabularies such as forms, mechanisms, and construct families.  
    **R:** Reintroduced fine-grained concept categories such as **paradigms**, **abstraction forms**, **control mechanisms**, **type features**, **metaprogramming features**, and related subclasses, and normalized earlier “form/mechanism” vocabularies so they became part of the same unified concept universe.

17. **P:** Finalize the normalized concept hierarchy for structured computation abstractions and reflect on borderline language profiles.  
    **R:** Checked in a dedicated subclass for **structured computation concepts** and concluded that the ontology schema was now expressive enough, while the next real challenge would be tightening the curation methodology for judgment-heavy support assertions.
