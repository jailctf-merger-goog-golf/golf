import os
from ast import *

if not os.path.isdir("./arc-dsl"):
    os.system("git clone https://github.com/michaelhodel/arc-dsl ./arc-dsl/")


with open("arc-dsl/solvers.py", "r") as f:
    code = f.read()

mappings = []
with open("data.txt", "r") as f:
    for line in f.readlines():
        num, _, hashed = [x[:-5] if x.endswith(".json") else x for x in line.strip().split()]
        code = code.replace(hashed, num)


with open("arc-dsl/constants.py", 'r') as f:
    constants_code = f.read()
    constants_ast = parse(constants_code)
    constants_replace = {q.targets[0].id: q.value for q in constants_ast.body}


# ast constant replacement
class NoConstantsModule(NodeTransformer):
    def visit_Name(self, node):
        if node.id in constants_replace:  # sub in all of the variables
            return constants_replace[node.id]
        return node

    def visit_ImportFrom(self, node: ImportFrom):
        if node.module == "constants":  # remove constants module import
            return None
        return node


class ReorderFunctions(NodeTransformer):
    def visit_Module(self, node: Module):
        stmts = []
        funcdefs = []
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                funcdefs.append(stmt)
            else:
                stmts.append(stmt)
        funcdefs = list(sorted(funcdefs, key=lambda funcdef: funcdef.name.split("_")[1].rjust(3, '0')))
        node.body = stmts + funcdefs
        return node


class AutoInlineXandOUsages(NodeTransformer):
    def visit_FunctionDef(self, node_outer: FunctionDef):
        var_usages = {}
        declared_vars = {}

        class TrackUsages(NodeVisitor):
            def visit_Assign(self, node: Assign):
                assert node.targets[0].id not in declared_vars
                declared_vars[node.targets[0].id] = node.value
                self.visit(node.value)

            def visit_Name(self, node: Name):
                if not ((node.id[0] == 'x' and node.id[1:].isnumeric()) or node.id == "O"):
                    return

                if node.id not in var_usages:
                    var_usages[node.id] = 0
                var_usages[node.id] += 1

        TrackUsages().visit(node_outer)

        class ReplaceUsages(NodeTransformer):
            def visit_Assign(self, node: Assign):
                return None

            def visit_Name(self, node: Name):
                if node.id in declared_vars:
                    result = ReplaceUsages().visit(declared_vars[node.id])
                    if var_usages[node.id] == 1:  # declaration, usage (no walrus)
                        return result
                    result = NamedExpr(target=node, value=declared_vars[node.id])
                    declared_vars.pop(node.id)
                    return result
                return node

        return ReplaceUsages().visit(node_outer)


print("rewriting constants")
code = unparse(fix_missing_locations(NoConstantsModule().visit(parse(code))))

print("reordering functions")
code = unparse(fix_missing_locations(ReorderFunctions().visit(parse(code))))

print("basic inlining in solve funcs")
code = unparse(fix_missing_locations(AutoInlineXandOUsages().visit(parse(code))))


with open("arc-dsl/solvers_fixed.py", "w") as f:
    f.write(code)