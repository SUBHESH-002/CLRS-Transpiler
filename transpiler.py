import os
from dataclasses import dataclass
from typing import List, Optional

from lark import Lark, Transformer, Token
from lark.indenter import Indenter


# --- AST Definitions ---
class Node: pass
class Expr(Node): pass
class Statement(Node): pass

@dataclass
class Var(Expr):
    name: str

@dataclass
class Number(Expr):
    value: str

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
class BoolKw(Expr):
    value: bool

@dataclass
class ProcCall(Expr):
    name: str
    args: List[Expr]

@dataclass
class ProcCallStmt(Statement):
    call: ProcCall

@dataclass
class Assignment(Statement):
    target: Expr
    value: Expr

@dataclass
class ReturnStmt(Statement):
    value: Optional[Expr]

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
class Program(Node):
    statements: List[Statement]


# --- Indenter ---
class CLRSIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


# --- Transformer ---
class ASTTransformer(Transformer):
    def start(self, args):
        statements = [a for a in args if isinstance(a, Statement)]
        return Program(statements)

    def statement(self, args): return args[0]
    def compound_stmt(self, args): return args[0]
    def assignment_stmt(self, args): return args[0]
        
    def assign(self, args):
        return Assignment(args[0], args[-1])

    def var(self, args): return Var(str(args[0]))
    def array_access(self, args): return ArrayAccess(str(args[0]), args[1])

    def do_kw(self, args): return None
    def then_kw(self, args): return None
        
    def block(self, args):
        return [a for a in args if isinstance(a, Statement)]

    def to_dir(self, args): return "to"
    def downto_dir(self, args): return "downto"

    def true_kw(self, args): return BoolKw(True)
    def false_kw(self, args): return BoolKw(False)
    def nil_kw(self, args): return NilKw()

    def proc_call(self, args):
        name = str(args[0])
        call_args = [a for a in args[1:] if isinstance(a, Expr)]
        return ProcCall(name, call_args)

    def proc_call_stmt(self, args): return ProcCallStmt(args[0])

    def return_kw(self, args):
        val = args[0] if len(args) > 0 and isinstance(args[0], Expr) else None
        return ReturnStmt(val)

    def _filter_args(self, args):
        return [a for a in args if a is not None and not (isinstance(a, Token) and a.type in ('_NL', '_INDENT', '_DEDENT'))]

    def for_loop(self, args):
        filtered = self._filter_args(args)
        iterator = str(filtered[0])
        start = filtered[1]
        direction = filtered[2]
        end = filtered[3]
        body = filtered[4]
        return ForLoop(iterator, start, direction, end, body)

    def while_loop(self, args):
        filtered = self._filter_args(args)
        return WhileLoop(filtered[0], filtered[1])

    def if_node(self, args):
        filtered = self._filter_args(args)
        condition = filtered[0]
        body = filtered[1]
        elseifs = [a for a in filtered[2:] if isinstance(a, ElseIfBlock)]
        
        else_body = None
        for a in filtered[2:]:
            if isinstance(a, ElseBlock):
                else_body = a.body
        return IfStmt(condition, body, elseifs, else_body)

    def elseif_node(self, args):
        filtered = self._filter_args(args)
        return ElseIfBlock(filtered[0], filtered[1])

    def else_node(self, args):
        filtered = self._filter_args(args)
        return ElseBlock(filtered[0])

    def bin_op(self, args):
        if len(args) == 3:
            return BinOp(args[0], str(args[1]), args[2])
        res = args[0]
        i = 1
        while i < len(args):
            res = BinOp(res, str(args[i]), args[i+1])
            i += 2
        return res

    def number(self, args): return Number(str(args[0]))


# --- Code Generator ---
class PythonCodeGenerator:
    def __init__(self):
        self.indent_level = 0
        self.code = []

    def get_indent(self):
        return "    " * self.indent_level

    def generate(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.generate(stmt)
        elif isinstance(node, Assignment):
            target = self.expr_to_str(node.target)
            value = self.expr_to_str(node.value)
            self.code.append(f"{self.get_indent()}{target} = {value}")
        elif isinstance(node, ProcCallStmt):
            self.code.append(f"{self.get_indent()}{self.expr_to_str(node.call)}")
        elif isinstance(node, ReturnStmt):
            val = f" {self.expr_to_str(node.value)}" if node.value else ""
            self.code.append(f"{self.get_indent()}return{val}")
        elif isinstance(node, ForLoop):
            start = self.expr_to_str(node.start)
            end_str = self.expr_to_str(node.end)
            if node.direction == "to":
                if isinstance(node.end, BinOp) and node.end.op == "-" and isinstance(node.end.right, Number) and node.end.right.value == "1":
                    end_simplified = self.expr_to_str(node.end.left)
                    self.code.append(f"{self.get_indent()}for {node.iterator} in range({start}, {end_simplified}):")
                else:
                    self.code.append(f"{self.get_indent()}for {node.iterator} in range({start}, {end_str} + 1):")
            else:
                if isinstance(node.end, Number) and node.end.value == "1":
                    self.code.append(f"{self.get_indent()}for {node.iterator} in range({start}, 0, -1):")
                elif isinstance(node.end, BinOp) and node.end.op == "+" and isinstance(node.end.right, Number) and node.end.right.value == "1":
                    end_simplified = self.expr_to_str(node.end.left)
                    self.code.append(f"{self.get_indent()}for {node.iterator} in range({start}, {end_simplified}, -1):")
                else:
                    self.code.append(f"{self.get_indent()}for {node.iterator} in range({start}, {end_str} - 1, -1):")
            self.indent_level += 1
            if not node.body:
                self.code.append(f"{self.get_indent()}pass")
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1
        elif isinstance(node, WhileLoop):
            condition = self.expr_to_str(node.condition)
            self.code.append(f"{self.get_indent()}while {condition}:")
            self.indent_level += 1
            if not node.body:
                self.code.append(f"{self.get_indent()}pass")
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1
        elif isinstance(node, IfStmt):
            condition = self.expr_to_str(node.condition)
            self.code.append(f"{self.get_indent()}if {condition}:")
            self.indent_level += 1
            if not node.body:
                self.code.append(f"{self.get_indent()}pass")
            for stmt in node.body:
                self.generate(stmt)
            self.indent_level -= 1

            for elif_block in node.elseifs:
                elif_cond = self.expr_to_str(elif_block.condition)
                self.code.append(f"{self.get_indent()}elif {elif_cond}:")
                self.indent_level += 1
                if not elif_block.body:
                    self.code.append(f"{self.get_indent()}pass")
                for stmt in elif_block.body:
                    self.generate(stmt)
                self.indent_level -= 1

            if node.else_body is not None:
                self.code.append(f"{self.get_indent()}else:")
                self.indent_level += 1
                if not node.else_body:
                    self.code.append(f"{self.get_indent()}pass")
                for stmt in node.else_body:
                    self.generate(stmt)
                self.indent_level -= 1

    def expr_to_str(self, expr) -> str:
        if isinstance(expr, Var):
            return expr.name
        elif isinstance(expr, Number):
            return expr.value
        elif isinstance(expr, NilKw):
            return "None"
        elif isinstance(expr, BoolKw):
            return "True" if expr.value else "False"
        elif isinstance(expr, ProcCall):
            args_str = ", ".join(self.expr_to_str(a) for a in expr.args)
            return f"{expr.name}({args_str})"
        elif isinstance(expr, BinOp):
            op = expr.op
            if op == "^": op = "**"
            elif op == "≤": op = "<="
            elif op == "≥": op = ">="
            elif op == "≠": op = "!="
            
            left_str = self.expr_to_str(expr.left)
            right_str = self.expr_to_str(expr.right)
            
            if isinstance(expr.left, BinOp):
                left_str = f"({left_str})"
            if isinstance(expr.right, BinOp):
                right_str = f"({right_str})"
                
            return f"{left_str} {op} {right_str}"
        elif isinstance(expr, ArrayAccess):
            if isinstance(expr.index, Number):
                return f"{expr.array}[{int(expr.index.value) - 1}]"
            elif isinstance(expr.index, Var):
                return f"{expr.array}[{expr.index.name} - 1]"
            else:
                return f"{expr.array}[{self.expr_to_str(expr.index)} - 1]"
        return str(expr)


def get_parser() -> Lark:
    grammar_path = os.path.join(os.path.dirname(__file__), "clrs.lark")
    with open(grammar_path, "r", encoding="utf-8") as f:
        grammar = f.read()
    return Lark(grammar, parser='lalr', postlex=CLRSIndenter())


def translate(code: str) -> str:
    parser = get_parser()
    # Add trailing newline robustly for Indenter bounds
    if not code.endswith("\n"): 
        code += "\n"
    tree = parser.parse(code)
    
    transformer = ASTTransformer()
    ast = transformer.transform(tree)
    
    generator = PythonCodeGenerator()
    generator.generate(ast)
    return "\n".join(generator.code)

