import os
from dataclasses import dataclass
from typing import List, Optional, Any
from lark import Lark, Transformer

# --- AST Definitions ---
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
class BinOp(Expr):
    left: Expr
    op: str
    right: Expr
@dataclass
class ArrayAccess(Expr):
    array: str
    index: Expr
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
class ElseIfBlock:
    condition: Expr
    body: List[Statement]
@dataclass
class ElseBlock: # Fix for the 'list' attribute error
    body: List[Statement]
@dataclass
class IfStmt(Statement):
    condition: Expr
    body: List[Statement]
    elseifs: List[ElseIfBlock]
    else_body: Optional[List[Statement]]
@dataclass
class Program(Node): statements: List[Statement]

# --- Transformer ---
class ASTTransformer(Transformer):
    def start(self, args): return Program([a for a in args if isinstance(a, Statement)])
    def statement(self, args): return args[0]
    def compound_stmt(self, args): return args[0]
    def assignment_stmt(self, args): return args[0]
    def assign(self, args): return Assignment(args[0], args[-1])
    def var(self, args): return Var(str(args[0]))
    def array_access(self, args): return ArrayAccess(str(args[0]), args[1])
    def block(self, args): return [a for a in args if isinstance(a, Statement)]
    def to_dir(self, args): return "to"
    def downto_dir(self, args): return "downto"
    def true_kw(self, args): return BoolKw(True)
    def false_kw(self, args): return BoolKw(False)
    def nil_kw(self, args): return NilKw()
    def proc_call(self, args): return ProcCall(str(args[0]), [a for a in args[1:] if isinstance(a, Expr)])
    def return_kw(self, args): return ReturnStmt(args[0] if args and isinstance(args[0], Expr) else None)
    
    def for_loop(self, args):
        return ForLoop(str(args[0]), args[1], args[2], args[3], args[4])
    
    def while_loop(self, args):
        return WhileLoop(args[0], args[1])

    def if_node(self, args):
        condition, body = args[0], args[1]
        elseifs = [a for a in args[2:] if isinstance(a, ElseIfBlock)]
        else_body = next((a.body for a in args[2:] if isinstance(a, ElseBlock)), None)
        return IfStmt(condition, body, elseifs, else_body)

    def elseif_node(self, args): return ElseIfBlock(args[0], args[1])
    def else_node(self, args): return ElseBlock(args[0])

    def bin_op(self, args):
        res = args[0]
        for i in range(1, len(args), 2):
            res = BinOp(res, str(args[i]), args[i+1])
        return res
    def number(self, args): return Number(str(args[0]))

# --- Code Generator ---
class PythonCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []

    def generate(self, node):
        indent = "    " * self.indent_level
        if isinstance(node, Program):
            for s in node.statements: self.generate(s)
        elif isinstance(node, Assignment):
            self.code.append(f"{indent}{self.expr_to_str(node.target)} = {self.expr_to_str(node.value)}")
        elif isinstance(node, ReturnStmt):
            val = f" {self.expr_to_str(node.value)}" if node.value else ""
            self.code.append(f"{indent}return{val}")
        elif isinstance(node, ForLoop):
            start, end = self.expr_to_str(node.start), self.expr_to_str(node.end)
            step = ", -1" if node.direction == "downto" else ""
            end_adj = f"({end}) - 1" if node.direction == "downto" else f"({end}) + 1"
            self.code.append(f"{indent}for {node.iterator} in range({start}, {end_adj}{step}):")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
        elif isinstance(node, IfStmt):
            self.code.append(f"{indent}if {self.expr_to_str(node.condition)}:")
            self.indent_level += 1
            for s in node.body: self.generate(s)
            self.indent_level -= 1
            for ei in node.elseifs:
                self.code.append(f"{indent}elif {self.expr_to_str(ei.condition)}:")
                self.indent_level += 1
                for s in ei.body: self.generate(s)
                self.indent_level -= 1
            if node.else_body:
                self.code.append(f"{indent}else:")
                self.indent_level += 1
                for s in node.else_body: self.generate(s)
                self.indent_level -= 1

    def expr_to_str(self, e) -> str:
        if isinstance(e, Var): return e.name
        if isinstance(e, Number): return e.value
        if isinstance(e, NilKw): return "None"
        if isinstance(e, BoolKw): return str(e.value)
        if isinstance(e, BinOp):
            op = {"^": "**", "≤": "<=", "≥": ">=", "≠": "!="}.get(e.op, e.op)
            return f"({self.expr_to_str(e.left)} {op} {self.expr_to_str(e.right)})"
        if isinstance(e, ArrayAccess):
            return f"{e.array}[({self.expr_to_str(e.index)}) - 1]"
        return str(e)

def translate(code: str) -> str:
    grammar_path = os.path.join(os.path.dirname(__file__), "clrs.lark")
    with open(grammar_path, "r", encoding="utf-8") as f:
        parser = Lark(f.read(), parser='lalr') # No Indenter used here
    ast = ASTTransformer().transform(parser.parse(code + "\n"))
    gen = PythonCodeGenerator()
    gen.generate(ast)
    return "\n".join(gen.code)