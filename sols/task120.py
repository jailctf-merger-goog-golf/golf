def p(g):
  w=len(g[0])
  r=range
  return [[[g[y][x],8][1<=x<w-1 and 1<=y<len(g)-1 and (g[y+1][x+1]==g[y-1][x-1]!=0)&g[y][x]>0]for x in r(w)]for y in r(len(g))]