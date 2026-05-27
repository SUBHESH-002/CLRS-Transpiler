import os
from dataclasses import dataclass
from typing import List, Optional

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
class ElseBlock:
    body: List[Statement]
@dataclass
class IfStmt(Statement):
    condition: Expr
    body: List[Statement]
    elseifs: List[ElseIfBlock]
    else_body: Optional[List[Statement]]
@dataclass
class Program(Node): statements: List[Statement]
@dataclass
class ProcCallStmt(Statement):
    call: ProcCall

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
    def proc_call_stmt(self, args): return ProcCallStmt(args[0])
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
        elif isinstance(node, ProcCallStmt):
            args_str = ", ".join(self.expr_to_str(arg) for arg in node.call.args)
            self.code.append(f"{indent}{node.call.name}({args_str})")

    def expr_to_str(self, e) -> str:
        if isinstance(e, Var): return e.name
        if isinstance(e, Number): return e.value
        if isinstance(e, NilKw): return "None"
        if isinstance(e, BoolKw): return str(e.value)
        if isinstance(e, BinOp):
            op = {"^": "**", "≤": "<=", "≥": ">=", "≠": "!=", "and": "and", "or": "or"}.get(e.op.lower() if e.op in ("and", "or", "AND", "OR") else e.op, e.op)
            return f"({self.expr_to_str(e.left)} {op} {self.expr_to_str(e.right)})"
        if isinstance(e, ArrayAccess):
            return f"{e.array}[({self.expr_to_str(e.index)}) - 1]"
        if isinstance(e, ProcCall):
            args_str = ", ".join(self.expr_to_str(arg) for arg in e.args)
            return f"{e.name}({args_str})"
        return str(e)

class CppCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []

    def generate(self, node):
        indent = "    " * self.indent_level
        if isinstance(node, Program):
            for s in node.statements: self.generate(s)
        elif isinstance(node, Assignment):
            self.code.append(f"{indent}{self.expr_to_str(node.target)} = {self.expr_to_str(node.value)};")
        elif isinstance(node, ReturnStmt):
            val = f" {self.expr_to_str(node.value)}" if node.value else ""
            self.code.append(f"{indent}return{val};")
        elif isinstance(node, ForLoop):
            it = node.iterator
            start = self.expr_to_str(node.start)
            end = self.expr_to_str(node.end)
            if node.direction == "to":
                self.code.append(f"{indent}for (auto {it} = {start}; {it} <= {end}; ++{it}) {{")
            else:
                self.code.append(f"{indent}for (auto {it} = {start}; {it} >= {end}; --{it}) {{")
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
            for ei in node.elseifs:
                self.code.append(f"{indent}else if ({self.expr_to_str(ei.condition)}) {{")
                self.indent_level += 1
                for s in ei.body: self.generate(s)
                self.indent_level -= 1
                self.code.append(f"{indent}}}")
            if node.else_body:
                self.code.append(f"{indent}else {{")
                self.indent_level += 1
                for s in node.else_body: self.generate(s)
                self.indent_level -= 1
                self.code.append(f"{indent}}}")
        elif isinstance(node, ProcCallStmt):
            args_str = ", ".join(self.expr_to_str(arg) for arg in node.call.args)
            self.code.append(f"{indent}{node.call.name}({args_str});")

    def expr_to_str(self, e) -> str:
        if isinstance(e, Var): return e.name
        if isinstance(e, Number): return e.value
        if isinstance(e, NilKw): return "nullptr"
        if isinstance(e, BoolKw): return "true" if e.value else "false"
        if isinstance(e, BinOp):
            op = {"^": "pow", "≤": "<=", "≥": ">=", "≠": "!=", "and": "&&", "or": "||"}.get(e.op.lower() if e.op in ("and", "or", "AND", "OR") else e.op, e.op)
            if op == "pow":
                return f"pow({self.expr_to_str(e.left)}, {self.expr_to_str(e.right)})"
            return f"({self.expr_to_str(e.left)} {op} {self.expr_to_str(e.right)})"
        if isinstance(e, ArrayAccess):
            # Maintains the Real-World 1-to-0 indexing shift
            return f"{e.array}[({self.expr_to_str(e.index)}) - 1]"
        if isinstance(e, ProcCall):
            args_str = ", ".join(self.expr_to_str(arg) for arg in e.args)
            return f"{e.name}({args_str})"
        return str(e)

def translate(code: str, target_lang: str) -> str:
    # 1. Load the grammar file
    grammar_path = os.path.join(os.path.dirname(__file__), "clrs.lark")
    with open(grammar_path, "r", encoding="utf-8") as f:
        parser = Lark(f.read(), parser='lalr')
    
    # 2. Parse the input and transform into an AST
    # We add a newline to ensure the parser handles the last line correctly
    ast = ASTTransformer().transform(parser.parse(code + "\n"))
    
    # 3. SELECT THE GENERATOR BASED ON THE UI INPUT
    # This is where we solve the Version 2 multi-language problem
    if target_lang == "Python":
        gen = PythonCodeGenerator()
    else:
        gen = CppCodeGenerator()
        
    # 4. Generate and return the code
    gen.generate(ast)
    return "\n".join(gen.code)