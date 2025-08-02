def p(g):
 h,w,*s=len(g),len(g[0])
 f=sum(g,s)
 b=max({*f},key=f.count)
 o={(i,j)for i in range(h)for j in range(w)if g[i][j]!=b}
 c=[*{g[i][j]for i,j in o}]
 for i,j in o:
  t,q=set(),[(i,j)]
  while q:
   (x,y),*q=q
   if(h<=x<0>y>=w or g[x][y]!=g[i][j])^1:t.add((x,y));q+=[(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
  s+=[(g[i][j],t)]
 for C,T in s:
  O=c[1-c.index(C)]
  a,A,l,R=min(T)[0]-1,max(T)[0]+1,min(T,key=lambda x:x[1])[1]-1,max(T,key=lambda x:x[1])[1]+1
  for i in range(max(0,a),min(h,A+1)):
   for j in range(max(0,l),min(w,R+1)):
    if(i in[a,A]or j in[l,R])and 0<=i<h and 0<=j<w:g[i][j]=O
 u=set()
 for _,t in s:u|=t
 if u:
  a,A,l,R=min(u)[0],max(u)[0],min(u,key=lambda x:x[1])[1],max(u,key=lambda x:x[1])[1]
  for i in range(a,A+1):
   for j in range(l,R+1):
    if(i in[a,A]or j in[l,R])and(i,j)not in u and min(abs(i-x)+abs(j-y)for x,y in u)%2<1:g[i][j]=5
 return g