"""Rebuild one layout from gen2 by seed and settings, and save it (layout2.json by default)."""
import os, sys, json, random
import gen2
seed = int(sys.argv[1]); n_s = int(sys.argv[2]); n_l = int(sys.argv[3]); out = sys.argv[4] if len(sys.argv) > 4 else 'layout2.json'
elems, occ = gen2.build(seed, n_s, n_l)
acts = gen2.place_actions(elems, occ, random.Random(seed))
ev = gen2.evaluate(elems, acts, games=20000, seed=99)
print(seed, {k: round(v, 2) for k, v in ev.items()}, 'S', sum(e['kind'] == 'S' for e in elems), 'L', sum(e['kind'] == 'L' for e in elems))
json.dump(dict(seed=seed, version=2, settings={k: os.environ.get(k) for k in ('GOLDEN_TOP', 'MAXLEN', 'LADDER_SCALE', 'SNAKE_TOP_BIAS')},
               elems=[dict(kind=e['kind'], hi=e['hi'], lo=e['lo'], geom=e['geom'], style=e['style'], golden=e['golden']) for e in elems],
               actions={str(k): v for k, v in acts.items()}), open(out, 'w'))
