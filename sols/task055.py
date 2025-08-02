def p(g):
  cycle = [0,2,0,4,6,3,0,1,0]
  cycle_idx = 0
  base = 0
  e=enumerate
  for y,row in e(g):
    if{*row}!={8}:
      for x,val in e(row):
        if val==8:
          cycle_idx+=1
        else:
          g[y][x]=cycle[base+cycle_idx%3]
      cycle_idx+=1
    else:
      base += 3
      
  return g