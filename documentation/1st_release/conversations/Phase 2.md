1. **P:** Start from a dictionary of formalisms and ask which listed items count as a “calculus.”  
   **R:** Identified the calculus-like items, then shifted to building a broader taxonomy for all entities rather than stopping at that label.

2. **P:** Propose categories plus entity-to-category assignments for the full list.  
   **R:** Produced an initial two-part artifact: a category dictionary with Wikipedia support links and an entity classification dictionary.

3. **P:** Prune weak or redundant categories such as duplicate grammar labels, one-off specializations, and self-referential notation/parsing labels.  
   **R:** Simplified the taxonomy by keeping stronger classifiers, replacing `grammar_notation` with **Metasyntax**, dropping `parsing_formalism`, and generalizing `term_rewriting` to **Formal system**.

4. **P:** Normalize category naming.  
   **R:** Renamed categories to human-readable title case with spaces, making the taxonomy presentation consistent.

5. **P:** Promote list items that really denote families/classes rather than individuals.  
   **R:** Moved **Lambda calculus** and **Process calculus** to category level and removed their duplicate entity entries.

6. **P:** Remove overlapping concurrency/semantics categories and keep only the most defensible classifiers.  
   **R:** Dropped **Concurrency model**, merged the semantics pair into **Formal semantics approach**, and kept a leaner category set.

7. **P:** Fix unsupported or too-broad categories for specific entities.  
   **R:** Repaired **Program logic** by linking it to an existing Wikipedia category; replaced the broad knowledge-representation classifier by promoting **Description logic** itself to category level.

8. **P:** Rework the UML-related category to better fit modeling rather than finite-state machinery.  
   **R:** Replaced **State machine modeling** with **Modeling language** as the classifier for **UML state machine**.

9. **P:** Differentiate parsing expression grammar from ordinary formal grammars.  
   **R:** Added **Analytic grammar** for **Parsing expression grammar** after rejecting a weaker top-down parsing label.

10. **P:** Tighten the ontology to strict subclass / instance-of reasoning.  
    **R:** Removed **Program logic** from **Axiomatic semantics**, and later cleaned up the accidental reappearance of **Description logic** as an entity while preserving it as a category.

11. **P:** Reassess **Attribute grammar** so it is not reduced to plain formal grammar.  
    **R:** Reclassified it under **Formal system**, briefly via a mixed assignment and then by removing the **Formal grammar** label entirely.

12. **P:** Promote **Lambda cube** to category level and add explicit category hierarchy information.  
    **R:** Expanded the artifact from two to three Python fragments: categories, category-parent relations, and entity assignments; **Lambda cube** became a subclass of **Lambda calculus**.

13. **P:** Keep only the most specific categories on entity assignments and formalize what counts as a subclass of **Formal system**.  
    **R:** Trimmed inherited labels from entities and added subclass links such as **Formal grammar**, **Lambda calculus**, **Type theory**, **Description logic**, **Process calculus**, and **Program logic** under **Formal system**.

14. **P:** Revisit EBNF and grammar boundaries.  
    **R:** Replaced **Metasyntax** with **Metalanguage** for **Extended Backus–Naur form**, and refined grammar coverage by introducing **Generative grammar** so **Context-free grammar** and **Regular grammar** became generative while PEG stayed analytic.

15. **P:** Refine rewriting and usage-based classifications for attribute grammars and term rewriting systems.  
    **R:** Added **Abstract rewriting system** for **Term rewriting system**, then accepted a deliberately multi-faceted taxonomy by introducing **Metaprogramming approach**, **Program transformation approach**, and **Syntax-directed translation approach**.

16. **P:** Convert the stabilized three-fragment taxonomy into an ontology artifact.  
    **R:** Derived an OWL/Turtle serialization with classes, subclass axioms, `owl:sameAs` links to Wikipedia, and short English `rdfs:comment` descriptions.
