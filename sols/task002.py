import re
p=lambda g,i=67:g*-i or[*map(list,zip(*eval(re.sub('4(?=, 0|])|0','04'[i<1],str(p(g,i-1))))[::-1]))]