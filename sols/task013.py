def p(g):
 h,w=len(g),len(g[0]);t=[[g[j][i]for j in range(h)]for i in range(w)]if h>w else[list(r)for r in g];u,v=len(t),len(t[0])
 f=[x for r in t for x in r];b=max(set(f),key=f.count);c=set(f)-{b};o=[]
 for C in c:
  x=[(C,(i,j))for i in range(u)for j in range(v)if t[i][j]==C]
  x and o.append(x)
 a=sum(o,[]);p=[s for c,s in a];d=max(j for i,j in p)-min(j for i,j in p)+1if p else 0;s=2*(d-1)if d>0else 1
 k=[list(r)for r in t]
 for x in o:
  if x:c,l=x[0][0],min(j for i,j in[s for c,s in x])
  for j in range(l,v,s):
   for i in range(u):k[i][j]=c
 return[[k[j][i]for j in range(len(k))]for i in range(len(k[0]))]if h>w else k