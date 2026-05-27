# CLRS Pseudocode to Executable Code Transpiler

## Overview
This project is an automated transpiler that converts the mathematical and abstract pseudocode found in the widely used textbook *Introduction to Algorithms* by Cormen, Leiserson, Rivest, and Stein (CLRS) into fully executable Python and C++ source code.

While the pseudocode in CLRS is excellent for pedagogical purposes (using 1-based indexing, `←` for assignment, `to`/`downto` for loops), it cannot be natively executed. This tool bridges the gap by providing a source-to-source compilation step that preserves readability while generating functionally accurate code.

## Features
- **Custom Lexer & Parser**: Built with `lark` (LALR(1) Context-Free Grammar) to process standard CLRS syntax.
- **Abstract Syntax Tree (AST)**: Performs semantic analysis, type-checking, and implicit variable declaration/scoping.
- **Array Index Resolution**: Automatically resolves 1-based array logic (e.g., $A[1 \ldots n]$) into 0-based memory-safe bounds for standard programming languages.
- **Target Language Generators**:
  - **Python**: Dynamic mapping and formatting.
  - **C++**: Statically typed mapping, block scoping, vector dependencies, and auto type detection.
- **Interactive Web IDE**: A web-based graphical interface built with Flask/NiceGUI and Ace editor, offering real-time, split-pane pseudocode translation.

## System Architecture
The transpiler is divided into frontend and backend modules:
1. **Lexical Analysis and Parsing**: `clrs.lark` defines token rules, keyword management (`for`, `if`, etc.) and basic grammar mappings to prevent dangling-else ambiguities.
2. **AST & Semantic Analysis**: Iterates the parse tree to build execution contexts, manage scope, and map indices appropriately.
3. **Target Generation**: The C++ and Python formatters iterate the AST to emit optimal, properly indented output.
4. **Web Interface**: `app.py` serves the IDE, catching keystroke updates via asynchronous callbacks and rendering the transpiled results.

## Prerequisites
- Python 3.8+
- [Lark](https://github.com/lark-parser/lark) (Parsing Toolkit)
- [Flask](https://flask.palletsprojects.com/) / [NiceGUI](https://nicegui.io/) (For the Web IDE)

To install dependencies, run:
```bash
pip install -r requirements.txt
```

## Usage
Run the Web Interface:
```bash
python app.py
```
*(Or use `app_nicegui.py` / `app_tui.py` for alternative UI interfaces).*

Enter standard CLRS pseudocode into the left editor pane to see generated Python and C++ code on the right pane in real-time.

## Example
**CLRS Pseudocode Input**:
```
for i ← n downto 1
    do something
```

**Python Transpiled Output**:
```python
for i in range(n, (1) - 1, -1):
    # do something
```

## Future Work
- Object-Oriented Transpilation for Graphs and Trees.
- Additional language targets: Java, Rust, JavaScript.
- Embedded execution sandbox in the browser for runtime visual mapping.

## References
1. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
2. *Lark - A modern parsing library for Python.* GitHub.
