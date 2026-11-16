"""Select up to 4 gold nodes per course (7-16 words, kind operator/goal), one per lab, seed 7.
Usage: python3 select_nodes.py nodes.json > selected.json"""
import json, random, sys
d = json.load(open(sys.argv[1]))
random.seed(7)
by = {}
for x in d:
    n = len(x['content'].split())
    if 7 <= n <= 16 and x['kind'] in ('operator', 'goal'):
        by.setdefault(x['course'], []).append(x)
sel = []
for c, xs in by.items():
    labs = sorted(set(x['slug'] for x in xs)); random.shuffle(labs)
    picked = []
    for lab in labs:
        picked.append(random.choice([x for x in xs if x['slug'] == lab]))
        if len(picked) == 4: break
    sel += picked
json.dump(sel, sys.stdout, indent=1)
