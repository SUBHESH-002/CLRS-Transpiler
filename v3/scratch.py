from transpiler import translate, Lark, ASTTransformer

c = """procedure INORDER-TREE-WALK(x)
if x != nil
INORDER-TREE-WALK(x.left)
print(x.key)
INORDER-TREE-WALK(x.right)
end
end"""

grammar_path = 'clrs.lark'
with open(grammar_path, "r", encoding="utf-8") as f:
    parser = Lark(f.read(), parser='lalr')
tree = parser.parse(c + "\n")
print(tree.pretty())

ast = ASTTransformer().transform(tree)
print(ast)
