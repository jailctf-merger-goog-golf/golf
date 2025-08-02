def p(g):
 h,w=len(g),len(g[0]);b=max([v for r in g for v in r],key=[v for r in g for v in r].count);o,v=[],set()
 for i in range(h):
  for j in range(w):
   if(i,j)not in v and g[i][j]!=b:
    q,s=[(i,j)],[]
    while q:
     x,y=q.pop()
     if(x,y)in v or not(0<=x<h and 0<=y<w)or g[x][y]!=g[i][j]:continue
     v.add((x,y));s+=[(g[x][y],(x,y))];q+=[(x+a,y+b)for a,b in[(0,1),(0,-1),(1,0),(-1,0)]]
    o+=s and[s]
 a=sum(o,[]);c={};r=set()
 for O in o:
  C=O[0][0];m=max(j for v,(i,j)in O)
  if C not in c or m>c[C][1]:c[C]=(O,m)
 for O,_ in c.values():r.update(O)
 m=[x for x in a if x not in r];k=[list(row)for row in g]
 for v,(i,j)in m:k[i][j]=b
 for v,(i,j)in m:
  if j+1<w:k[i][j+1]=v
 return k