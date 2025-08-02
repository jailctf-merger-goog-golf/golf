def p(g):
    h,w=len(g),len(g[0])
    l=[c for r in g for c in r]
    k=max(set(l),key=l.count)
    S,O,v=set(),[],set()
    for y in range(h):
        for x in range(w):
            if g[y][x]!=k and(y,x)not in v:
                C=g[y][x];i=set();q=[(y,x)];v.add((y,x))
                while q:
                    cy,cx=q.pop(0);i.add((cy,cx))
                    for ny,nx in[(cy+1,cx),(cy-1,cx),(cy,cx+1),(cy,cx-1)]:
                        if 0<=ny<h and 0<=nx<w and(ny,nx)not in v and g[ny][nx]==C:v.add((ny,nx));q.append((ny,nx))
                O.append((C,i));S|=i
    R=[[*r]for r in g]
    L=list({c for c in l if c!=0})
    if len(L)==2:
        s={L[0]:L[1],L[1]:L[0]}
        for C,i in O:
            if C in s:
                n=s[C];Y,X=zip(*i);a,b,c,d=min(Y)-1,max(Y)+1,min(X)-1,max(X)+1
                for y in range(a,b+1):
                    for x in range(c,d+1):
                        if(y in[a,b]or x in[c,d])and 0<=y<h and 0<=x<w:R[y][x]=n
    if S:
        Y,X=zip(*S);a,b,c,d=min(Y),max(Y),min(X),max(X)
        P={(y,x)for y in[a,b]for x in range(c,d+1)}|{(y,x)for x in[c,d]for y in range(a,b+1)}
        for y,x in P-S:
            if min(abs(y-sy)+abs(x-sx)for sy,sx in S)%2==0:R[y][x]=5
    return R