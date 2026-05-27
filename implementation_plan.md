# CLRS to Python Transpiler

This document outlines the architecture and design of a transpiler that converts CLRS (Cormen, Leiserson, Rivest, and Stein) pseudocode into complete, executable Python code.

## User Review Required

Please review the structure. I am planning to create two files: `clrs.lark` (for the grammar) and `transpiler.py` (which includes everything else: AST nodes, Transformer, Code Generator, Indenter, and the `translate` execution script).

## Proposed Changes

### Transpiler Implementation

#### [NEW] clrs.lark
Will contain the customized Lark grammar rules required for identifying CLRS structures. It heavily uses Python-style nesting and indentation properties using `%declare _INDENT _DEDENT` and utilizes `_NL` explicitly for whitespace tokens mapping.
- Maps keywords (`for`, `to`, `while`, `do`) to handle loop bounds accurately.
- Maps assignments (`=` and left-arrow variations).
- Declares expressions and definitions logic for variable tokens.

#### [NEW] transpiler.py
Will encompass Python logic required for taking Lark outputs and manipulating them into pure Python lines. 
- **AST Nodes**: Basic Python dataclasses representing syntactic structures (e.g., `ForLoop`, `ArrayAccess`, `Assignment`).
- **CLRSIndenter**: A lexer-postprocessor subclassed from `lark.indenter.Indenter` to orchestrate Python block nesting constraints based on indent space counting.
- **ASTTransformer**: A tree-walker mapping lark outputs directly to AST Dataclasses cleanly.
- **PythonCodeGenerator**: A tree-visitor building executable code sequentially, notably translating any 1-indexed representations dynamically to 0-indexed syntax (`A[i]` -> `A[i - 1]`).
- **translate()**: The final orchestrator logic to connect the parser, the transformer, and the code-generator sequentially.

## Open Questions

- Should I include additional support for Conditional Statements (`if`, `else_if`) or just follow exactly the features mentioned in the prompt (Assignment, Array Access, and Loops)?
- Do you want support for function definitions (`def ...`) in CLRS syntax, or should we assume the input is inline procedural statements?

## Verification Plan

### Automated Tests
- Inside the `transpiler.py`, an execution block verifying the basic functionality using the test case:
  `for i = 1 to n`
  `    A[i] = i * 2`
- Verify it natively emits strings matching the expected outcome.
