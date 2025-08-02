def p(g):
 h,w=len(g),len(g[0]);f=[v for r in g for v in r];b=max(set(f),key=f.count);o,v=[],set()
 for i in range(h):
  for j in range(w):
   if(i,j)not in v and g[i][j]!=b:
    q,s=[(i,j)],[]
    while q:
     x,y=q.pop()
     if(x,y)in v or not(0<=x<h and 0<=y<w)or g[x][y]!=g[i][j]:continue
     v.add((x,y));s+=[(g[x][y],(x,y))];q+=[(x+d,y+e)for d,e in[(0,1),(0,-1),(1,0),(-1,0)]]
    s and o.append(s)
 s=sorted(o,key=lambda O:max(i for c,(i,j)in O)-min(i for c,(i,j)in O)+1);n=len(o);k=[list(r)for r in g]
 for i,O in enumerate(s):
  for c,(x,y)in O:k[x][y]=n-i
 return k