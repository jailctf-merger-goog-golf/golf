def p(g):
 h,w=len(g),len(g[0]);f=[v for r in g for v in r];b=max(set(f),key=f.count);p=[]
 for c in set(f):
  o=[(c,(i,j))for i,r in enumerate(g)for j,v in enumerate(r)if v==c]
  o and p.append(o)
 n=[o for o in p if o[0][0]!=0];l=max(p,key=len);r=[o for o in n if o!=l];a=sum(r,[])
 s=[];k=[list(row)for row in g]
 for x in a:
  for y in a:
   if x[0]==y[0]:
    c,((i1,j1),(i2,j2))=x[0],(x[1],y[1])
    if i1==i2:L=[(c,(i1,j))for j in range(min(j1,j2),max(j1,j2)+1)]
    elif j1==j2:L=[(c,(i,j1))for i in range(min(i1,i2),max(i1,i2)+1)]
    else:L=[]
    if L and(len(set(i for c,(i,j)in L))==1or len(set(j for c,(i,j)in L))==1):s+=L
 for c,(i,j)in s:
  if 0<=i<h and 0<=j<w:k[i][j]=c
 for i in range(h):
  for j in range(w):
   if g[i][j]==b:k[i][j]=b
 return k