def p(g):
  if (g[0]+g[1]).count(3)==1:
    return g[-2:][::1-2*(len(g)%2)]+g[:-2]
  else:
    return [row[-2:][::1-2*(len(g[0])%2)]+row[:-2] for row in g]
