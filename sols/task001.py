def p(g):return [[g[r%3][c%3]*bool(g[r//3][c//3]) for c in range(9)]for r in range(9)]
