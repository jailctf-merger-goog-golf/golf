# watch out for CRLFs!!!!

t=lambda v:[*map(list,zip(*v))];p=lambda g:t([[t(g)[:4][y][x]|t(g)[:4:-1][y][x]for x in range(10)]for y in range(4)])
# first sol (117 bytes)
