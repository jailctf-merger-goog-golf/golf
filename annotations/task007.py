p=lambda g,i=2:[[max(sum(g,[])[(i:=i+1)%3::3])for c in g]for r in g]
p=lambda g:[([max(sum(g,[])[i::3])for i in range(3)]*3)[q%3:][:7]for q in range(7)]