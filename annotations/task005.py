p=lambda g:[[x*r.pop(0)*2for x in r[4:]]for r in g]
p=lambda g:[[2*(x&r.pop(0))for x in r[4:]]for r in g]
p=lambda g:[[2*(x&y)for x,y in zip(r,r[4:])]for r in g]