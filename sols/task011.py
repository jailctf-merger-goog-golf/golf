def p(g):
 h,w=len(g),len(g[0]);f=[v for r in g for v in r];b=max(set(f),key=f.count);o,v=[],set()
 for i in range(h):
  for j in range(w):
   if(i,j)not in v and g[i][j]!=b:
    q,s=[(i,j)],[]
    while q:
     x,y=q.pop()
     if(x,y)in v or not(0<=x<h and 0<=y<w)or g[x][y]==b:continue
     v.add((x,y));s+=[(g[x][y],(x,y))];q+=[(x+d,y+e)for d in[-1,0,1]for e in[-1,0,1]if d|e]
    s and o.append(s)
 m=min(o,key=lambda O:len(set(c for c,p in O)));p=[pos for c,pos in m];a,z=min(i for i,j in p),min(j for i,j in p)
 n=[(c,(i-a,j-z))for c,(i,j)in m];u=[(c,(i*4+x,j*4+y))for c,(i,j)in n for x in range(4)for y in range(4)]
 k=[list(r)for r in g]
 for c,(i,j)in u:
  if 0<=i<h and 0<=j<w:k[i][j]=c
 for i in range(h):
  for j in range(w):
   if g[i][j]==5:k[i][j]=5
 return k