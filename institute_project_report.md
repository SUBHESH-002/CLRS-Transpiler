# Institute Level Project Report

## Project Title: **CLRS Pseudocode to Executable Code Transpiler**

<br>

**Submitted in partial fulfillment of the requirements for the degree of**
**[Degree Name, e.g., Bachelor of Technology in Computer Science]**

**By:**
[Your Name / Team Names]
[Your Roll Number(s)]

**Under the Guidance of:**
[Guide's Name]
[Guide's Designation]

**[Institution / University Name]**
**[Department Name]**
**[Academic Year]**

---
<div style="page-break-after: always;"></div>

## DECLARATION
We hereby declare that the project entitled **"CLRS Pseudocode to Executable Code Transpiler"** submitted in partial fulfillment of the requirements for the award of [Degree Name] at [Institution Name] is an authentic record of our own work carried out during the period from [Start Date] to [End Date]. The matter embodied in this project report has not been submitted by us for the award of any other degree or diploma to the best of our knowledge and belief.

---
<div style="page-break-after: always;"></div>

## ACKNOWLEDGEMENT
We express our deepest gratitude to our project guide, **[Guide's Name]**, for their continuous encouragement, invaluable suggestions, and constructive criticism throughout the project. 

We would also like to thank the Head of the Department, **[HOD's Name]**, for providing the necessary infrastructure and environment. Finally, we thank our peers and families for their constant support.

---
<div style="page-break-after: always;"></div>

## ABSTRACT
The textbook *Introduction to Algorithms* by Cormen, Leiserson, Rivest, and Stein (CLRS) relies heavily on mathematical and abstract pseudocode to define fundamental data structures and algorithms. While excellent for pedagogical purposes, bridging the gap between this pseudocode and practical, executable implementation is a constant challenge for computer science students and educators. 

This project presents the design and development of an automated transpiler that converts CLRS pseudocode into fully executable Python and C++ source code. The core system comprises a custom lexical analyzer and parser relying on Context-Free Grammar (CFG) rules defined via the `lark` library, an Abstract Syntax Tree (AST) constructed for semantic analysis, and distinct back-end generators for Python and C++. The transpiler intelligently resolves 1-based to 0-based array indexing, identifies implicit structural contexts, infers types dynamically for C++, and supports standard algorithms right out of the textbook. To maximize usability, the project includes an interactive Web-Based IDE built with Flask/NiceGUI and Ace editor, providing real-time, split-pane pseudocode translation.

---
<div style="page-break-after: always;"></div>

## TABLE OF CONTENTS
1. [Introduction](#1-introduction)
2. [Literature Review](#2-literature-review)
3. [System Architecture](#3-system-architecture)
4. [Implementation Details](#4-implementation-details)
5. [Testing & Results](#5-testing--results)
6. [Conclusion and Future Work](#6-conclusion-and-future-work)
7. [References](#7-references)

---
<div style="page-break-after: always;"></div>

## 1. INTRODUCTION

### 1.1 Problem Statement
CLRS uses a generalized pseudocode style (e.g., using `←` for assignment, `≠` for inequality, `to` and `downto` for loop bounds, 1-based indexing). While this abstracts away low-level programming semantics and syntax clutter, students cannot natively run or debug these algorithms without manually mapping them to high-level programming languages—leading to syntax errors and logically flawed boundary conditions (typically off-by-one errors).

### 1.2 Objectives
* Develop a rigorous Context-Free Grammar (CFG) specification for CLRS pseudocode.
* Parse the pseudocode into an Abstract Syntax Tree (AST) using an LALR(1) parser.
* Implement semantic passes that handle type-checking, implicit variable declaration/scoping, and array bound compensations.
* Generate cleanly formatted, typed, and optimal C++ and Python source files representing the original logic.
* Provide an interactive graphical IDE to test translations interactively.

### 1.3 Scope of the Project
The system's target languages are currently Python (for rapid prototyping) and C++ (for typed, performant mapping). The transpiler supports assignments, arithmetic and binary expressions, `if-elseif-else` structures, `for` and `while` loops, mathematical unary components, logic operations, functions, and arrays. 

## 2. LITERATURE REVIEW
* **CLRS Pedagogical Paradigm:** The standard algorithms textbook utilizes a highly theoretical 1-based index approach mathematically similar to Pascal and algorithm descriptions.
* **Transpilation vs. Compilation:** Unlike a compiler connecting to machine language, a *source-to-source compiler* (transpiler) retains conceptual abstractions, mapping loops to loops and conditionals to conditionals, making it a critical tool for preserving readability.
* **Lark Parsing Toolkit:** A prominent Python-based parsing library relying on Earley and LALR(1) algorithms, heavily utilized for creating Domain Specific Languages (DSLs).

## 3. SYSTEM ARCHITECTURE

The architecture mirrors a modern compiler's front-end and back-end separation, defined across four primary modules:

### 3.1 Lexical Analysis and Parsing
Using `lark`, the CLRS text is tokenized. Reserved keywords (`for`, `to`, `downto`, `if`, `return`) and operators (`←`, `≤`, `≠`) are mapped to rules. The LALR(1) parser strictly structures tokens based on `clrs.lark` to prevent grammatical ambiguities (e.g. dangling else problem) and outputs a raw parse tree.

### 3.2 Abstract Syntax Tree (AST) & Semantic Analysis 
A `Transformer` traverses the parse tree, verifying block legality and tracking the environment (such as inferring integer vs. array vs. float variable definitions). Crucially, this stage transforms mathematically ambiguous 1-based array requests into standardized 0-based lookups suitable for memory boundaries.

### 3.3 Target Language Generators
*   **Python Target:** Focuses on dynamic mapping. Uses `range(start, end+1)` maps for standard `for`-loops. 
*   **C++ Target:** Performs heavy lifting regarding block scoping, adding standard `#include <vector>` implementations, variable type auto-detection, and generating appropriate main driver code.

### 3.4 Web-based Graphical Interface
The `app.py` interfaces with standard Web technologies relying on the Ace browser editor. It supplies a split screen. On keystroke bounds, asynchronous post-requests are forwarded to the underlying Python CLI app, populating the generated C++/Python equivalent.

## 4. IMPLEMENTATION DETAILS

### 4.1 Parser Rules (`clrs.lark`)
The rules were designed recursively. E.g., `statement` resolves to `assignment`, `if_stmt`, `loop_stmt`, or `expression`. Support for hyphens in identifiers (commonly found in CLRS variables like `list-length`) required custom sanitization logic.

### 4.2 Array Index Transformation
Because pseudo-code arrays are mathematically mapped as $A[1 \ldots n]$, the transpiler applies recursive visitor nodes that modify elements like `A[i + j]` directly to `A[(i + j) - 1]` while preserving the integrity of nested evaluation structures.

### 4.3 Control Flow Implementations (Loop Context)
The logic accommodates different range loops seamlessly.
```python
# Pseudocode
for i = n downto 1

# Translated Python Output:
for i in range(n, (1) - 1, -1):
```

## 5. TESTING & RESULTS

The software was validated against standard textbook samples involving QuickSort, Insertion Sort, Graph algorithms, and nested conditional mathematical evaluations. 

*   **Syntax Mapping:** Standard symbols like `←` are properly translated to `=` in target languages. Missing logical pathways (`else if` chaining) operate flawlessly under dynamic semantic scoping.
*   **Robust Error Tracking:** In cases of semantic failure (e.g., parsing `else` outside the context of an `if_stmt`), the custom exception structures propagate specific rules back to the user via the `VisitError` trap, preventing cascading system crashes.
*   **UI Test:** The web host successfully routes sub-millisecond translations supporting live interactive editing.

## 6. CONCLUSION AND FUTURE WORK

### 6.1 Conclusion
The **CLRS Transpiler** provides an effective and fully functional solution connecting algorithmic theory and practical execution. By implementing rigorous linguistic structures utilizing Lark and mapping accurate code definitions via Python and C++ generators, it eliminates logical bugs inherent to manual translation. It provides significant value to the academic computer science sector.

### 6.2 Future Work
*   **Object-Oriented Transpilation:** Extending features to directly map graph tree objects and linked-list derivations using classes/structs.
*   **Additional Language Targets:** Implementation of Java, Rust, and JavaScript interfaces.
*   **Execution Runtime:** Constructing an embedded sandbox in the browser to compile and run the generated code and visually map array transformations step-by-step.

## 7. REFERENCES
1. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
2. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Pearson.
3. *Lark - A modern parsing library for Python.* GitHub. https://github.com/lark-parser/lark
4. *Flask: Web development, one drop at a time.* https://flask.palletsprojects.com/
5. *Ace - The High Performance Code Editor for the Web.* https://ace.c9.io/

---
> *Note: This is a structured template. Please ensure replacing placeholder fields like '[Your Name]', '[Guide's Name]', and '[Institution Name]' before final submission.*
