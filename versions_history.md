# Version History and Development Logs

This document tracks the evolution of the CLRS Transpiler, highlighting the features introduced, problems faced in each phase, and the current limitations of the system.

## Version 1.2 (Initial Prototype)
- **Features**: 
  - Basic pseudocode parsing and Python source generation via `lark`. 
  - Included a basic graphical user interface using `NiceGUI` (`app_nicegui.py`).
- **Problems Faced**:
  - The grammar (`clrs.lark`) was rudimentary and struggled with complex nested conditional structures.
  - Encountered Abstract Syntax Tree (AST) node parsing errors, such as the `else_node` error (`AttributeError: 'list' object has no attribute '__is_else_block'`), due to improper semantic tagging of execution blocks.
  - Array indexing was naive and did not dynamically resolve the mathematical 1-based index (e.g., `A[1 ... n]`) to Python's 0-based memory boundary.

## Version 2
- **Features**: 
  - Shifted the user interface from NiceGUI to a Flask-based web application (`app.py`), providing a better browser-editor experience using Ace. 
  - The core transpiler script expanded significantly to accommodate more robust AST generation.
- **Problems Faced**:
  - Bridging the split-pane live-editor with the Python backend required optimizing the transpiler for asynchronous speed to avoid UI freezing.
  - The Python generator was highly dynamic and assumed types implicitly, highlighting the need for a rigorous semantic analyzer before C++ target generation could be built.

## Version 3
- **Features**: 
  - Major architectural leap with the introduction of C++ generation. 
  - The grammar file (`clrs.lark`) expanded to accommodate more syntax rules, and the transpiler logic grew significantly. 
  - True semantic array index transformation was implemented (e.g., safely converting `A[i + j]` to `A[i + j - 1]`).
- **Problems Faced**:
  - **Bracket Clutter**: The recursive AST traversal caused excessive bracket generation for nested expressions (e.g., yielding `A[(((i * j) - 1)) - 1]`), which made the generated code less readable.
  - **C++ Scoping**: Implicit block scoping for C++ required building heavy semantic tracking to auto-detect integer, double, and vector variables dynamically.

## Version 4 (Current Main Iteration)
- **Features**: 
  - Comprehensive array and type mappings (Pseudocode numbers auto-map to C++ `int`/`double`, Capitalized identifiers map to `std::vector<int>&`).
  - Added implicit array assumptions, converting undefined capitalized variables as reference parameters in function signatures.
  - Unary `-` support implemented in the parsing grammar (e.g., `return -1`).
  - Bracket nesting logic refactored to produce much cleaner code (e.g., `A[(j - 1) - 1]`).
  - Extensive standard textbook test cases successfully validated (`binary_search`, `quick_sort`, `merge_sort`, `insertion_sort`, `max_subarray`).

---

## Current Problems, Issues & Limitations
1. **Complex Data Structures (Graphs & Trees)**: The transpiler currently focuses on arrays and primitives. It lacks Object-Oriented mapping to handle Graph structures (Vertices/Edges), Pointers, or Linked Lists representations which are heavily utilized in later chapters of CLRS.
2. **Type Inference Constraints**: The static type inference for C++ is basic. It relies on capitalization conventions (e.g., `A` is an array, `i` is an integer) and defaults to `std::vector<int>`. It does not robustly resolve multidimensional arrays (e.g., Matrices) or distinguish complex float/string allocations seamlessly.
3. **Execution Runtime Environment**: Currently, the Web IDE provides the translated source code text, but it does not contain an embedded sandbox or WebAssembly (Wasm) runtime to actually execute the generated C++ or Python code to view outputs dynamically.
4. **Strict Grammar Bounds**: Pseudocode is naturally ambiguous. Complex mathematical notations or syntactical variations in loops (that deviate slightly from the hardcoded `clrs.lark` tokens) might still break the LALR(1) parser with a `VisitError`.
