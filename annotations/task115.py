def p(g):
  a = sorted(list(set(g[0])),key=lambda a:g[0].index(a))
  b = sorted(list(set(a[0]for a in g)),key=lambda a:str(g).find(str(a)))
  if len(a)>1:
    return [a]
  return [[i]for i in b]