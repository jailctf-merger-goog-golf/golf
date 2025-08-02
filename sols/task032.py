def p(g):
    return [*map(list,zip(*[sorted(c)for c in zip(*g)]))]