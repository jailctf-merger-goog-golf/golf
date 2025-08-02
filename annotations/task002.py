# sort of not really well golfed
def p(g):
 def f(i,j):
  if-1<i<n>j>=0==g[i][j]:
   g[i][j]=4
   for x,y in[(0,1),(1,0),(-1,0),(0,-1)]:f(i+x,j+y)
 n=len(g)
 for i in range(n):
  for j in range(n):0<i<n-1>j>0 or f(i,j)
 return[[6^c+2for c in r]for r in g]