def p(g):
  for i in range(10):
    for j in range(10):
      if g[i][j] == 5:
        return [a[j-1:j+2]for a in g[i+1:i+4]]