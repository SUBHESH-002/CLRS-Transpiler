import os
from dataclasses import dataclass
from typing import List, Optional, Any
from lark import Lark, Transformer

# --- AST Nodes ---
@dataclass
class Node: pass
@dataclass
class Expr(Node): pass
@dataclass
class Statement(Node): pass

@dataclass
class Var(Expr): name: str
@dataclass
class Number(Expr): value: str
@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr
@dataclass
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr
@dataclass
class ArrayAccess(Expr):
    array: str
    index: Expr
@dataclass
class AttrAccess(Expr):
    obj: str
    attr: str
@dataclass
class NilKw(Expr): pass
@dataclass
class BoolKw(Expr): value: bool
@dataclass
class ProcCall(Expr):
    name: str
    args: List[Expr]
@dataclass
class Assignment(Statement):
    target: Expr
    value: Expr
@dataclass
class ReturnStmt(Statement): value: Optional[Expr]
@dataclass
class Procedure(Node):
    name: str
    params: List[str]
    body: List[Statement]
@dataclass
class ForLoop(Statement):
    iterator: str
    start: Expr
    direction: str
    end: Expr
    body: List[Statement]
@dataclass
class WhileLoop(Statement):
    condition: Expr
    body: List[Statement]
@dataclass
class RepeatLoop(Statement):
    body: List[Statement]
    condition: Expr
@dataclass
class ErrorStmt(Statement):
    message: str
@dataclass
class Exchange(Statement):
    left: Expr
    right: Expr
@dataclass
class ElseIfBlock:
    condition: Expr
    body: List[Statement]
@dataclass
class ElseBlock: 
    body: List[Statement]
@dataclass
class IfStmt(Statement):
    condition: Expr
    body: List[Statement]
    elseifs: List[ElseIfBlock]
    else_body: Optional[List[Statement]]
@dataclass
class Program(Node): statements: List[Any]

# --- Transformer ---
class ASTTransformer(Transformer):
    def start(self, args): return Program([a for a in args if isinstance(a, (Statement, Procedure))])
    def statement(self, args): return args[0]
    def assignment_stmt(self, args): return args[0]
    def assign(self, args): return Assignment(args[0], args[-1])
    def var(self, args): return Var(str(args[0]).replace('-', '_'))
    def array_access(self, args): return ArrayAccess(str(args[0]).replace('-', '_'), args[1])
    def attr_access(self, args): return AttrAccess(str(args[0]).replace('-', '_'), str(args[1]).replace('-', '_'))
    def block(self, args): return [a for a in args if isinstance(a, (Statement, ProcCall))]
    def to_dir(self, args): return "to"
    def downto_dir(self, args): return "downto"
    def true_kw(self, args): return BoolKw(True)
    def false_kw(self, args): return BoolKw(False)
    def nil_kw(self, args): return NilKw()
    def proc_call(self, args): return ProcCall(str(args[0]).replace('-', '_'), [a for a in args[1:] if isinstance(a, Expr)])
    def proc_call_stmt(self, args): return args[0]
    def return_kw(self, args): return ReturnStmt(args[0] if args and isinstance(args[0], Expr) else None)
    
    def procedure(self, args):
        name = str(args[0]).replace('-', '_')
        params = [str(p).replace('-', '_') for p in args[1:-1] if isinstance(p, str)]
        body = args[-1]
        return Procedure(name, params, body)

    def for_loop(self, args): return ForLoop(str(args[0]).replace('-', '_'), args[1], args[2], args[3], args[4])
    def while_loop(self, args): return WhileLoop(args[0], args[1])
    def repeat_loop(self, args): return RepeatLoop(args[0], args[1])
    def error_kw(self, args): return ErrorStmt(str(args[0]))
    def exchange(self, args): return Exchange(args[0], args[-1])

    def if_stmt(self, args):
        condition, body = args[0], args[1]
        elseifs = [a for a in args[2:] if isinstance(a, ElseIfBlock)]
        else_body = next((a.body for a in args[2:] if isinstance(a, ElseBlock)), None)
        return IfStmt(condition, body, elseifs, else_body)

    def elseif_node(self, args): return ElseIfBlock(args[0], args[1])
    def else_node(self, args): return ElseBlock(args[0])
    def bin_op(self, args):
        res = args[0]
        for i in range(1, len(args), 2): res = BinOp(res, str(args[i]), args[i+1])
        return res
    def unary_op(self, args): return UnaryOp(str(args[0]), args[1])
    def number(self, args): return Number(str(args[0]))

# --- Semantic Analyzer ---
class SemanticError(Exception): pass

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]
        
    def current_scope(self): return self.scopes[-1]

    def define_var(self, name, var_type):
        self.current_scope()[name] = var_type

    def get_var_type(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return None

    def analyze(self, node):
        if isinstance(node, Program):
            for s in node.statements: self.analyze(s)
        elif isinstance(node, Procedure):
            self.scopes.append({})
            # Pass 1: Find implicit array parameters
            implicit_arrays = set()
            def find_implicit(n):
                if isinstance(n, ArrayAccess) and n.array[0].isupper():
                    implicit_arrays.add(n.array)
                elif isinstance(n, AttrAccess) and n.obj[0].isupper():
                    implicit_arrays.add(n.obj)
                elif isinstance(n, Var) and n.name[0].isupper():
                    implicit_arrays.add(n.name)
                if hasattr(n, '__dict__'):
                    for val in vars(n).values():
                        if isinstance(val, Node): find_implicit(val)
                        elif isinstance(val, list):
                            for v in val:
                                if isinstance(v, Node): find_implicit(v)
            for s in node.body: find_implicit(s)
            for arr in sorted(list(implicit_arrays)):
                if arr not in node.params:
                    node.params.append(arr)
            # define parameters
            for p in node.params:
                if p[0].isupper():
                    self.define_var(p, "std::vector<int>&")
                else:
                    self.define_var(p, "int")
            # Analyze body
            for s in node.body: self.analyze(s)
            self.scopes.pop()
        elif isinstance(node, Assignment):
            self.analyze(node.value)
            val_type = getattr(node.value, "inferred_type", "auto")
            if isinstance(node.target, Var):
                if self.get_var_type(node.target.name) is None:
                    self.define_var(node.target.name, val_type)
                node.target.inferred_type = self.get_var_type(node.target.name)
            elif isinstance(node.target, ArrayAccess):
                self.analyze(node.target)
        elif isinstance(node, Var):
            t = self.get_var_type(node.name)
            if t is None:
                self.define_var(node.name, "int")
                t = "int"
            node.inferred_type = t
        elif isinstance(node, Number):
            node.inferred_type = "double" if "." in node.value else "int"
        elif isinstance(node, UnaryOp):
            self.analyze(node.expr)
            node.inferred_type = getattr(node.expr, "inferred_type", "int")
        elif isinstance(node, BinOp):
            self.analyze(node.left)
            self.analyze(node.right)
            lt = getattr(node.left, "inferred_type", "int")
            rt = getattr(node.right, "inferred_type", "int")
            node.inferred_type = "double" if "double" in (lt, rt) else "int"
        elif isinstance(node, ArrayAccess):
            if self.get_var_type(node.array) is None:
                self.define_var(node.array, "std::vector<int>&")
            self.analyze(node.index)
            node.inferred_type = "int"
        elif isinstance(node, AttrAccess):
            if node.attr == "length":
                node.inferred_type = "int"
            else:
                node.inferred_type = "auto"
        elif isinstance(node, ForLoop):
            self.analyze(node.start)
            self.analyze(node.end)
            self.scopes.append({})
            self.define_var(node.iterator, "int")
            for s in node.body: self.analyze(s)
            self.scopes.pop()
        elif hasattr(node, '__dict__'):
            for val in vars(node).values():
                if isinstance(val, Node): self.analyze(val)
                elif isinstance(val, list):
                    for v in val:
                        if isinstance(v, Node): self.analyze(v)

# --- Python Generator ---
class PythonCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []
    def generate(self, node):
        indent = "    " * self.indent_level
        if isinstance(node, Program):
            for s in node.statements: self.generate(s)
        elif isinstance(node, Procedure):
            params = ", ".join(node.params)
            self.code.append(f"\ndef {node.name}({params}):")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
        elif isinstance(node, Assignment):
            self.code.append(f"{indent}{self.expr_to_str(node.target)} = {self.expr_to_str(node.value)}")
        elif isinstance(node, ReturnStmt):
            val = f" {self.expr_to_str(node.value)}" if node.value else ""
            self.code.append(f"{indent}return{val}")
        elif isinstance(node, ProcCall):
            args = ", ".join(self.expr_to_str(a) for a in node.args)
            self.code.append(f"{indent}{node.name}({args})")
        elif isinstance(node, ForLoop):
            start, end = self.expr_to_str(node.start), self.expr_to_str(node.end)
            step = ", -1" if node.direction == "downto" else ""
            end_adj = f"({end}) - 1" if node.direction == "downto" else f"({end}) + 1"
            self.code.append(f"{indent}for {node.iterator} in range({start}, {end_adj}{step}):")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
        elif isinstance(node, WhileLoop):
            self.code.append(f"{indent}while {self.expr_to_str(node.condition)}:")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
        elif isinstance(node, IfStmt):
            self.code.append(f"{indent}if {self.expr_to_str(node.condition)}:")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            for elseif_node in node.elseifs:
                self.code.append(f"{indent}elif {self.expr_to_str(elseif_node.condition)}:")
                self.indent_level += 1
                for s in elseif_node.body: self.generate(s)
                self.indent_level -= 1
            if node.else_body:
                self.code.append(f"{indent}else:")
                self.indent_level += 1
                for s in node.else_body: self.generate(s)
                self.indent_level -= 1
        elif isinstance(node, RepeatLoop):
            self.code.append(f"{indent}while True:")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.code.append(f"{indent}    if {self.expr_to_str(node.condition)}:")
            self.code.append(f"{indent}        break")
            self.indent_level -= 1
        elif isinstance(node, ErrorStmt):
            self.code.append(f"{indent}raise Exception({node.message})")
        elif isinstance(node, Exchange):
            left, right = self.expr_to_str(node.left), self.expr_to_str(node.right)
            self.code.append(f"{indent}{left}, {right} = {right}, {left}")

    def expr_to_str(self, e) -> str:
        if isinstance(e, Var): return e.name
        if isinstance(e, Number): return e.value
        if isinstance(e, UnaryOp): return f"{e.op}{self.expr_to_str(e.expr)}"
        if isinstance(e, BinOp):
            op = {"^": "**", "≤": "<=", "≥": ">=", "≠": "!="}.get(e.op, e.op)
            return f"({self.expr_to_str(e.left)} {op} {self.expr_to_str(e.right)})"
        if isinstance(e, ArrayAccess): return f"{e.array}[{self.expr_to_str(e.index)} - 1]"
        if isinstance(e, AttrAccess): return f"{e.obj}.{e.attr}"
        if isinstance(e, ProcCall):
            args = ", ".join(self.expr_to_str(a) for a in e.args)
            return f"{e.name}({args})"
        return "None" if isinstance(e, NilKw) else str(e)

# --- C++ Generator ---
class CppCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []
    def generate(self, node):
        indent = "    " * self.indent_level
        if isinstance(node, Program):
            for s in node.statements: self.generate(s)

        elif isinstance(node, Procedure):
            param_decls = []
            for p in node.params:
                # We can access a generated mapping from SemanticAnalyzer
                # or rely on basic heuristics if not available
                ptype = "auto&"
                if p[0].isupper(): 
                    ptype = "std::vector<int>&"
                else: 
                    ptype = "int"
                param_decls.append(f"{ptype} {p}")
            params = ", ".join(param_decls)
            self.code.append(f"\nvoid {node.name}({params}) {{")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            self.code.append(f"{indent}}}")

        elif isinstance(node, Assignment):
            target_str = self.expr_to_str(node.target)
            val_str = self.expr_to_str(node.value)
            # If it's a new variable in C++, we need 'auto ' or Type
            if isinstance(node.target, Var) and not getattr(node.target, 'cpp_declared', False):
                tType = getattr(node.target, 'inferred_type', 'auto')
                self.code.append(f"{indent}{tType} {target_str} = {val_str};")
                node.target.cpp_declared = True
            else:
                self.code.append(f"{indent}{target_str} = {val_str};")

        elif isinstance(node, ReturnStmt):
            val = f" {self.expr_to_str(node.value)}" if node.value else ""
            self.code.append(f"{indent}return{val};")

        elif isinstance(node, ProcCall):
            args = ", ".join(self.expr_to_str(a) for a in node.args)
            self.code.append(f"{indent}{node.name}({args});")

        elif isinstance(node, ForLoop):
            it, start, end = node.iterator, self.expr_to_str(node.start), self.expr_to_str(node.end)
            op = "<=" if node.direction == "to" else ">="
            inc = f"++{it}" if node.direction == "to" else f"--{it}"
            self.code.append(f"{indent}for (auto {it} = {start}; {it} {op} {end}; {inc}) {{")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            self.code.append(f"{indent}}}")


        elif isinstance(node, WhileLoop):
            self.code.append(f"{indent}while ({self.expr_to_str(node.condition)}) {{")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            self.code.append(f"{indent}}}")
            
        elif isinstance(node, IfStmt):
            self.code.append(f"{indent}if ({self.expr_to_str(node.condition)}) {{")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            self.code.append(f"{indent}}}")
            for elseif_node in node.elseifs:
                self.code.append(f"{indent}else if ({self.expr_to_str(elseif_node.condition)}) {{")
                self.indent_level += 1
                for s in elseif_node.body: self.generate(s)
                self.indent_level -= 1
                self.code.append(f"{indent}}}")
            if node.else_body:
                self.code.append(f"{indent}else {{")
                self.indent_level += 1
                for s in node.else_body: self.generate(s)
                self.indent_level -= 1
                self.code.append(f"{indent}}}")
        elif isinstance(node, RepeatLoop):
            self.code.append(f"{indent}do {{")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            self.code.append(f"{indent}}} while (!({self.expr_to_str(node.condition)}));")
        elif isinstance(node, ErrorStmt):
            self.code.append(f"{indent}throw std::runtime_error({node.message});")
        elif isinstance(node, Exchange):
            left, right = self.expr_to_str(node.left), self.expr_to_str(node.right)
            self.code.append(f"{indent}std::swap({left}, {right});")

    def expr_to_str(self, e) -> str:
        if isinstance(e, Var): return e.name
        if isinstance(e, Number): return e.value
        if isinstance(e, UnaryOp): return f"{e.op}{self.expr_to_str(e.expr)}"
        if isinstance(e, BinOp):
            op = {"^": "pow", "≤": "<=", "≥": ">=", "≠": "!="}.get(e.op, e.op)
            if op == "pow": return f"pow({self.expr_to_str(e.left)}, {self.expr_to_str(e.right)})"
            return f"({self.expr_to_str(e.left)} {op} {self.expr_to_str(e.right)})"
        if isinstance(e, ArrayAccess): return f"{e.array}[{self.expr_to_str(e.index)} - 1]"
        if isinstance(e, AttrAccess): 
            if e.attr == "length": return f"{e.obj}.size()"
            return f"{e.obj}.{e.attr}"
        if isinstance(e, ProcCall):
            args = ", ".join(self.expr_to_str(a) for a in e.args)
            return f"{e.name}({args})"
        return "nullptr" if isinstance(e, NilKw) else str(e)

def translate(code: str, target_lang: str) -> str:
    grammar_path = os.path.join(os.path.dirname(__file__), "clrs.lark")
    with open(grammar_path, "r", encoding="utf-8") as f:
        parser = Lark(f.read(), parser='lalr')
    
    ast = ASTTransformer().transform(parser.parse(code + "\n"))
    SemanticAnalyzer().analyze(ast)

    if target_lang == "C++":
        # reset cpp_declared
        def reset_decl(n):
            if hasattr(n, 'cpp_declared'): n.cpp_declared = False
            if hasattr(n, '__dict__'):
                for val in vars(n).values():
                    if isinstance(val, Node): reset_decl(val)
                    elif isinstance(val, list):
                        for v in val:
                            if isinstance(v, Node): reset_decl(v)
        reset_decl(ast)
        
        # pass multiple variables through assignment in C++ without redeclaration
        class CppDeclVisitor:
            def __init__(self): self.declared = set()
            def visit(self, n):
                if isinstance(n, Assignment) and isinstance(n.target, Var):
                    if n.target.name in self.declared:
                        n.target.cpp_declared = True
                    else:
                        self.declared.add(n.target.name)
                        n.target.cpp_declared = False
                if hasattr(n, '__dict__'):
                    for val in vars(n).values():
                        if isinstance(val, Node): self.visit(val)
                        elif isinstance(val, list):
                            for v in val:
                                if isinstance(v, Node): self.visit(v)
        CppDeclVisitor().visit(ast)

    gen = PythonCodeGenerator() if target_lang == "Python" else CppCodeGenerator()
    gen.generate(ast)
    return "\n".join(gen.code)