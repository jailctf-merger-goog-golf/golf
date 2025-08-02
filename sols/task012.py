def p(g):
 h,w=len(g),len(g[0]);f=sum(g,[]);L=min(set(f),key=f.count)
 r=[[L if v==0else v for v in R]for R in g];L2=min(sum(r,[]),key=sum(r,[]).count)
 k=[list(R)for R in g]
 for i in range(h):
  for j in range(w):
   if g[i][j]==L2:
    for d,e in[(0,1),(0,-1),(1,0),(-1,0)]:
     if 0<=i+d<h and 0<=j+e<w:k[i+d][j+e]=L2
 b=max(sum(k,[]),key=sum(k,[]).count);o,v=[],set()
 for i in range(h):
  for j in range(w):
   if(i,j)not in v and k[i][j]!=b:
    q,s=[(i,j)],[]
    while q:
     x,y=q.pop()
     if(x,y)in v or not(0<=x<h and 0<=y<w)or k[x][y]==b:continue
     v.add((x,y));s+=[x,y];q+=[(x+d,y+e)for d in[-1,0,1]for e in[-1,0,1]if d|e]
    s and o.append(s)
 for O in o:
  if O:
   a,A,z,Z=min(O[::2]),max(O[::2]),min(O[1::2]),max(O[1::2])
   for i in range(a,A+1):k[i][i-a+z if i-a+z<w else Z]=k[i][A-i+z if A-i+z<w else Z]=L
 return k