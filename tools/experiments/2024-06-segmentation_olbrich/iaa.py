#!python3
import sys
import anotated_segmentations_reader as asr
from collections import defaultdict

def rewrite(segm):
    pieces = segm.split("-")
    sg = "".join(["1" + "0" * (len(piece) - 1) for piece in pieces])
    return [str(x) for x in sg]

def sub(a, b):
    for t1, t2 in zip(rewrite(a), rewrite(b)):
        if t1 == "0" and t2 == "1":
            return False
    return True

ann_a, ann_b = defaultdict(list), defaultdict(list)
wla, wsa = asr.read_Czech_final(limit=25)
wlb, wsb = asr.read_anot_2023()

erra = 0
errb = 0

for w, s in zip(wla, wsa):
    if "".join(s.split("-")) != w:
        erra += 1
    else:
        ann_a[w] = s
for w, s in zip(wlb, wsb):
    if "".join(s.split("-")) != w:
        errb += 1
    ann_b[w] = s
print(erra, errb)

allkeys = set(ann_a.keys()) & set(ann_b.keys())
common = 0
asubb = 0
bsuba = 0
wr = 0
for w in allkeys:
    if ann_a[w] == ann_b[w]:
        common += 1
    elif sub(ann_a[w], ann_b[w]):
        asubb += 1
    elif sub(ann_b[w], ann_a[w]):
        bsuba += 1
    else:
       wr += 1
       #print(ann_a[w], ann_b[w])
print(common/len(allkeys))
print((common + asubb + bsuba)/ len(allkeys))
print(common, asubb, bsuba, wr)
