# generate S_box_16bit
import secrets
from random import shuffle
s_box_range = list(range(2**16))
S_box_final = []
S_box_rev_final = []
for i in range(16):
    round = secrets.randbelow(10)
    for j in range(round):
        shuffle(s_box_range)
    S_box_final.append(s_box_range.copy())
    S_box_rev = [1 for i in range(2**16)]
    for index,value in enumerate(s_box_range):
        S_box_rev[value] = index
    S_box_rev_final.append(S_box_rev.copy())

with open('s_box', 'w') as s_box:
    s_box.write(str(S_box_final))

with open('s_box_rev', 'w') as s_box_rev:
    s_box_rev.write(str(S_box_rev_final))

