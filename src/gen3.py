"""Layout generator v3: plan rules + geometry chosen together.

Rules (agreed with the user)
- Snake heads per row (row 15 -> 2): 3,2,1,2,3,1,1,2,1,2,1,1,1,1 ; 296->254 fixed.
  Row 15 heads at 287 and 282 (+-1 allowed).
- Golden ladder 258 -> 300. One super ladder (100-125). Three long ladders (60-90).
- Three "second chance" ladders starting 4 / 6 / 8 squares above a snake tail.
- Drops / rises ratio ~1.2, 3-player game 35-40 rounds (2 dice, bounce).
- Every element slanted: horizontal/vertical ratio between 0.4 and 1.8 (no vertical, no flat ones).
- Max 3 elements per square; trigger squares (snake heads, ladder bottoms) never covered by another body;
  each element crosses at most one other; ladders never cross ladders.
- About a third of the snakes curvy (arc / S-sweep / tail spiral). Conical tails.
- Action squares near 18,44,70(swap),95,110,135,162(swap),176,198,213,228,252(swap),256(block),270 in free squares.
"""
import os, sys, json, random
import numpy as np
from gen import rc, center, path_cells, ladder_cells, segs_cross
from gen2 import snake_geom, inside, solo_turns

N = 300
MAX_PER_CELL = 3
ROW_HEADS = {15: 3, 14: 2, 13: 1, 12: 2, 11: 3, 10: 1, 9: 1, 8: 2, 7: 1, 6: 2, 5: 1, 4: 1, 3: 1, 2: 1}
ACTIONS = [(18, 'turbo'), (44, 'drain'), (70, 'swap'), (95, 'block'), (110, 'turbo'), (135, 'drain'),
           (162, 'swap'), (176, 'turbo'), (198, 'block'), (213, 'turbo'), (228, 'drain'), (252, 'swap'),
           (256, 'block'), (270, 'drain')]

def slant_ok(a, b, lo=0.4, hi=1.8):
    (r1, c1), (r2, c2) = rc(a), rc(b); dr, dc = abs(r1 - r2), abs(c1 - c2)
    return dr > 0 and dc >= 1 and lo <= dc / dr <= hi

def lines_cross(l1, l2):
    for i in range(len(l1) - 1):
        for j in range(len(l2) - 1):
            if segs_cross(l1[i], l1[i + 1], l2[j], l2[j + 1]): return True
    return False

class Board:
    def __init__(self, rnd):
        self.rnd = rnd; self.occ = {}; self.elems = []; self.ends = set(); self.trig = set()
    def free_end(self, x): return x not in self.ends and rc(x) not in self.occ
    def try_add(self, kind, hi, lo, style=None, golden=False, max_cross=1):
        if hi in self.ends or lo in self.ends: return False
        ch, cl = rc(hi), rc(lo)
        if ch in self.occ or cl in self.occ: return False
        trig_new = ch if kind == 'S' else cl
        if kind == 'S':
            pts, ws = snake_geom(hi, lo, style, self.rnd)
            if not inside(pts): return False
            cells = path_cells(pts, ws); line = pts[::5].tolist() + [pts[-1].tolist()]
        else:
            cells = ladder_cells(lo, hi); line = [center(lo).tolist(), center(hi).tolist()]
        for cc in cells:
            if cc in (ch, cl): continue
            if cc in self.trig: return False                     # never cover a trigger square
            if self.occ.get(cc, 0) + 1 > MAX_PER_CELL: return False
        # our own end squares must not already be covered by a body
        nx = 0
        for e in self.elems:
            if lines_cross(line, e['line']):
                if kind == 'L' and e['kind'] == 'L': return False
                if golden or e['golden']: return False
                nx += 1
                if nx > max_cross: return False
        for cc in cells: self.occ[cc] = self.occ.get(cc, 0) + 1
        self.ends |= {hi, lo}; self.trig.add(trig_new)
        self.elems.append(dict(kind=kind, hi=hi, lo=lo, style=style, golden=golden, line=line,
                               geom=(pts.tolist(), ws.tolist()) if kind == 'S' else None))
        return True

def place_ladder(B, a_range, r_range, tries=500, pref_side=None):
    rnd = B.rnd
    for _ in range(tries):
        a = rnd.randint(*a_range); r = rnd.randint(*r_range); b = a + r
        if b >= 288 or a < 2: continue
        if not slant_ok(a, b): continue
        if any(0 < e['hi'] - b <= 2 for e in B.elems if e['kind'] == 'S'): continue
        if B.try_add('L', b, a): return (a, b)
    return None

def build(seed, n_curvy=7):
    rnd = random.Random(seed); B = Board(rnd)
    if not B.try_add('L', 300, 258, golden=True): return None
    sup = place_ladder(B, (30, 120), (100, 125), tries=2000)
    if not sup: return None
    for ar in ((10, 90), (90, 170), (150, 215)):
        if not place_ladder(B, ar, (60, 90), tries=1500): return None
    # snakes by the row pattern, long drops first in the upper rows
    if not any(B.try_add('S', 296, 254, style=st) for st in ('arc', 'wave', 'wave', 'sweep', 'wave')): return None
    heads = []
    for row, n in sorted(ROW_HEADS.items(), reverse=True):
        lo, hi = (row - 1) * 20 + 1, row * 20
        if row == 15:
            heads += [('fixed', 287), ('fixed', 282)]
        else:
            heads += [('row', row)] * n
    drop_pool = [rnd.randint(14, 24) for _ in range(3)] + [rnd.randint(25, 45) for _ in range(9)] + \
                [rnd.randint(46, 70) for _ in range(6)] + [rnd.randint(71, 105) for _ in range(3)]
    rnd.shuffle(drop_pool)
    curvy_left = n_curvy
    for kind, v in heads:
        ok = False
        for attempt in range(600):
            if kind == 'fixed':
                h = v + rnd.choice([0, 0, 0, 1, -1])
                if h >= 288: continue                     # end zone keeps a single snake (296)
            else:
                h = rnd.randint((v - 1) * 20 + 2, v * 20 - 1)
            if h <= 22: continue
            # spread heads in a row: not next to another head of the same row
            if any(abs(h - e['hi']) <= 3 for e in B.elems if e['kind'] == 'S'): continue
            idx = rnd.randrange(len(drop_pool)) if drop_pool else None
            d0 = drop_pool[idx] if drop_pool else rnd.randint(20, 50)
            d = max(10, min(h - 2, int(d0 * rnd.uniform(0.85, 1.15))))
            t = h - d
            if not slant_ok(t, h): continue
            style = 'wave'
            if curvy_left > 0 and 20 <= d <= 90 and rnd.random() < 0.6:
                style = rnd.choice(['arc', 'sweep', 'curl'])
            if B.try_add('S', h, t, style=style):
                if drop_pool: drop_pool.pop(idx)
                if style != 'wave': curvy_left -= 1
                ok = True; break
        if not ok: return None
    # second-chance ladders: +4, +6, +8 above a snake tail (different worlds)
    tails = [e['lo'] for e in B.elems if e['kind'] == 'S' and 20 < e['lo'] < 240]
    rnd.shuffle(tails); worlds = set(); gaps = [4, 6, 8]; sc = []
    for t in tails:
        if not gaps: break
        w = (t - 1) // 60
        if w in worlds: continue
        a = t + gaps[0]
        for r in sorted(range(20, 46), key=lambda _: rnd.random()):
            b = a + r
            if b < 288 and slant_ok(a, b) and not any(0 < e['hi'] - b <= 2 for e in B.elems if e['kind'] == 'S') \
                    and B.try_add('L', b, a):
                sc.append((gaps[0], t, a, b)); gaps.pop(0); worlds.add(w); break
    if gaps: return None
    # regular ladders: fill rows 1..13 without a ladder start, up to 18 ladders
    def n_lad(): return sum(1 for e in B.elems if e['kind'] == 'L')
    for row in range(1, 14):
        if n_lad() >= 18: break
        if any(rc(e['lo'])[0] + 1 == row for e in B.elems if e['kind'] == 'L'): continue
        place_ladder(B, ((row - 1) * 20 + 2, row * 20), (15, 42), tries=400)
    while n_lad() < 18:
        if not place_ladder(B, (2, 240), (15, 42), tries=400): break
    # action squares in free squares near the planned spots
    acts = {}
    for sq, kind in ACTIONS:
        order = sorted(range(-6, 7), key=abs)
        if sq == 256: order = [0, 1, -1, -2, -3]          # keep the block right before the golden ladder
        for d in order:
            s = sq + d
            if s in B.ends or s in acts or s <= 2 or s >= 288 or rc(s) in B.occ: continue
            if any(abs(s - a) <= 1 for a in acts): continue
            acts[s] = kind; break
        else:
            return None
    return B, acts, sc

def evaluate(B, games=4000, seed=0):
    J = {e['hi']: e['lo'] for e in B.elems if e['kind'] == 'S'}
    J.update({e['lo']: e['hi'] for e in B.elems if e['kind'] == 'L'})
    rng = np.random.default_rng(seed); t, _ = solo_turns(J, games * 3, rng)
    r = t.reshape(games, 3).min(1)
    drops = sum(e['hi'] - e['lo'] for e in B.elems if e['kind'] == 'S')
    rises = sum(e['hi'] - e['lo'] for e in B.elems if e['kind'] == 'L')
    return float(r.mean()), float(np.median(r)), drops, rises

if __name__ == '__main__':
    start = int(os.environ.get('SEED_START', 0)); n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    out = sys.argv[2] if len(sys.argv) > 2 else 'layout3.json'
    best = None
    for seed in range(start, start + n):
        res = build(seed)
        if res is None: continue
        B, acts, sc = res
        m, med, d, u = evaluate(B, seed=seed)
        ns = sum(e['kind'] == 'S' for e in B.elems); nl = len(B.elems) - ns
        curvy = sum(1 for e in B.elems if e['kind'] == 'S' and e['style'] != 'wave')
        cr = sum(1 for i in range(len(B.elems)) for j in range(i + 1, len(B.elems)) if lines_cross(B.elems[i]['line'], B.elems[j]['line']))
        moved = sum(min(abs(a - s) for a in acts) for s, _ in ACTIONS)
        sides = sum(1 if rc(e['hi'])[1] > rc(e['lo'])[1] else -1 for e in B.elems if e['kind'] == 'L')
        score = abs(m - 37.5) * 3 + abs(d / u - 1.2) * 30 + cr * 1.5 + (18 - nl) * 4 + abs(sides) + max(0, 6 - curvy) * 3
        print(f'seed {seed}: S{ns} L{nl} curvy{curvy} cross{cr} mean{m:.1f} med{med} ratio{d/u:.2f} sides{sides:+d} score {score:.1f}', flush=True)
        if best is None or score < best[0]: best = (score, seed, B, acts, sc)
    if best is None: print('no layout'); sys.exit(1)
    score, seed, B, acts, sc = best
    m, med, d, u = evaluate(B, games=30000, seed=9)
    print('BEST', seed, round(m, 1), med, d, u, round(d / u, 2), 'second-chance', sc)
    json.dump(dict(version=3, seed=seed, second_chance=sc,
                   elems=[dict(kind=e['kind'], hi=e['hi'], lo=e['lo'], geom=e['geom'], style=e['style'], golden=e['golden']) for e in B.elems],
                   actions={str(k): v for k, v in acts.items()}), open(out, 'w'))
