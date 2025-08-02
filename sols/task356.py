z=lambda v:[*map(list,zip(*v))]
def p(g):
  for y,r in enumerate(g):
    for x,t in enumerate(r):
      left=[*r,8].index(8)+1
      right=9-[*r[::-1],8].index(8)
      for n in range(left, right):
        r[n] = r[n]or 6
  g=z(g)
  for y,r in enumerate(g):
    for x,t in enumerate(r):
      left=[*r,8].index(8)+1
      right=9-[*r[::-1],8].index(8)
      for n in range(left, right):
        r[n] = 8
  return z([(t>0)*8 for t in r] for r in g)