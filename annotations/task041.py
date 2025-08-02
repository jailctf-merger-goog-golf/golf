def p(g):
  for _ in range(9):
    for i in range(9):
      for j in range(9):
        if g[i+1][j]==g[i][j+1]!=0: # fills in a square if the x+1 and y+1 both have same color
          g[i][j]=g[i+1][j]
  return g