def p(g):x,y=min(([*r,8].index(8),g.index(r))for r in g);z=[r[x-1:x+2]for r in g[y-1:y+2]];z[1][1]=0;z[1][1]=max(map(max,z));return z
