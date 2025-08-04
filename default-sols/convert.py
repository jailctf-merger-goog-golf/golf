import os
from ast import *
from custom_unparser import CustomUnparser

os.makedirs("arc-dsl/fixed",exist_ok=True)
if not os.path.isdir("./arc-dsl"):
    os.system("git clone https://github.com/michaelhodel/arc-dsl ./arc-dsl/")


with open("arc-dsl/solvers.py", "r") as f:
    code = f.read()

mappings = []
with open("data.txt", "r") as f:
    for line in f.readlines():
        num, _, hashed = [x[:-5] if x.endswith(".json") else x for x in line.strip().split()]
        code = code.replace(hashed, str(num).rjust(3, '0'))


with open("arc-dsl/constants.py", 'r') as f:
    constants_code = f.read()
    constants_ast = parse(constants_code)
    constants_replace = {q.targets[0].id: q.value for q in constants_ast.body}


# utility
class FindNames(NodeVisitor):
    def __init__(self):
        super().__init__()
        self.found = set()

    def find(self, node):
        self.visit(node)
        return self.found

    def visit_Name(self, node: Name):
        self.found.add(node.id)


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


class SplitSolveFunctions(NodeVisitor):
    def __init__(self):
        super().__init__()
        self.mods = []

    def do(self, node: Module) -> list[tuple[int, Module]]:
        self.mods = []
        self.visit(node)
        return self.mods

    def visit_Module(self, node: Module):
        stmts = []
        funcdefs = []
        for stmt in node.body:
            if isinstance(stmt, FunctionDef):
                funcdefs.append(stmt)
            else:
                stmts.append(stmt)
        funcdefs = list(sorted(funcdefs, key=lambda funcdef: funcdef.name.split("_")[1].rjust(3, '0')))
        for i, funcdef in enumerate(funcdefs):
            funcdef.name="p"
            self.mods.append((i+1, Module(
                body=[*stmts,funcdef],
                type_ignores=[]
            )))


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


class ForceReturnListOfLists(NodeTransformer):
    def visit_Return(self, node: Return):
        return Return(value=List(
                elts=[
                    Starred(
                        value=Call(
                            func=Name(id='map', ctx=Load()),
                            args=[
                                Name(id='list', ctx=Load()),
                                node.value],
                            keywords=[]),
                        ctx=Load())],
                ctx=Load())
            )


all_utility_funcs = {}
all_utility_funcs_deps = {}
with open("arc-dsl/dsl.py", 'r') as f:
    dsl_ast = parse(f.read())
for stmt in dsl_ast.body:
    if isinstance(stmt, FunctionDef):
        stmt.returns=[]
        for arg in stmt.args.args:
            arg.annotation=None
        all_utility_funcs[stmt.name]=stmt
for uf_name in all_utility_funcs:
    all_utility_funcs_deps[uf_name]=set(all_utility_funcs)&FindNames().find(all_utility_funcs[uf_name])
    all_utility_funcs_deps[uf_name] -= {uf_name}


class PlaceUsedFunctionsAndRemoveImports(NodeTransformer):
    def visit_Module(self, node: Module):

        used_names = set()

        # resolve recursive
        def resolve(name):
            if name in dir(__builtins__):
                return
            used_names.add(name)
            for dep in all_utility_funcs_deps[name]:
                resolve(dep)

        for name in {un for un in FindNames().find(node) if not ((un[0] == 'x' and un[1:].isnumeric()) or un == "I")}:
            resolve(name)

        # remove dsl import
        node.body.pop(0)

        for used_name in sorted(used_names):
            node.body.insert(0, all_utility_funcs[used_name])

        return node


print("rewriting constants")
code_ast = fix_missing_locations(NoConstantsModule().visit(parse(code)))

print("basic inlining in solve funcs")
code_ast = fix_missing_locations(AutoInlineXandOUsages().visit(code_ast))

print("finding solve functions")
modules = {n: fix_missing_locations(mod) for n,mod in SplitSolveFunctions().do(code_ast)}

print("force putting ")
modules = {n: fix_missing_locations(ForceReturnListOfLists().visit(modules[n])) for n in modules}

print("putting in dsl functions")
modules = {n: fix_missing_locations(PlaceUsedFunctionsAndRemoveImports().visit(modules[n])) for n in modules}

print("custom unparsing")
modules = {n: CustomUnparser().visit(modules[n]) for n in modules}

for n in modules:
    with open(f"arc-dsl/fixed/task{n:03d}.py", 'w') as f:
        f.write(modules[n])
