def p(g):
 h,w=len(g),len(g[0]);v,o=set(),[]
 for i in range(h):
  for j in range(w):
   if(i,j)not in v and g[i][j]==0:
    c=[(i,j)];s=set()
    while c:
     x,y=c.pop()
     if(x,y)in v or not(0<=x<h and 0<=y<w)or g[x][y]!=0:continue
     v.add((x,y));s.add((x,y));c+=[(x+a,y+b)for a,b in[(0,1),(0,-1),(1,0),(-1,0)]]
    if s and not any(x in[0,h-1]or y in[0,w-1]for x,y in s):o+=s
 r=[list(row)for row in g]
 for i,j in o:r[i][j]=4
 return list(map(list,r))