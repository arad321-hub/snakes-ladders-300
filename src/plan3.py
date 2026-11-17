"""Numeric plan search (v3): snake heads by the user's row pattern, balanced ladders.

Targets
- 3 players, 2 dice, bounce: mean rounds 35-40 (aim ~37.5)
- total drops / total rises ~1.2-1.3 (snakes a bit stronger, like the original)
- golden 258->300, one super ladder (100+), three long ladders (60-90),
  three "second chance" ladders starting 4 / 6 / 8 squares above a snake tail
- every element diagonal; no shared endpoints; no ladder top 1-2 squares before a snake head
"""
import random, json, sys
import numpy as np
from gen import rc, center, segs_cross
from gen2 import solo_turns

N = 300
HEADS = [296, 287, 282, 278, 266, 249, 237, 226, 218, 211, 203, 193, 167, 157, 144, 131, 114, 106, 97, 69, 53, 37]
FIXED_S = {296: 254}
GOLDEN = (258, 300)

def diag_ok(a, b):
    (r1, c1), (r2, c2) = rc(a), rc(b); dr, dc = abs(r1 - r2), abs(c1 - c2)
    return dr > 0 and max(2, 0.5 * dr) <= dc <= 8

def pick(rnd, base, lo, hi, used, ok, tries=200):
    for _ in range(tries):
        v = rnd.randint(lo, hi)
        if ok(v) and v not in used: return v
    return None

def make(rnd):
    used = set(HEADS) | {254, 258, 300}
    S = dict(FIXED_S)
    # snake drops: mostly 20-60, a few long ones, a couple of short bites
    drop_pool = [rnd.randint(14, 24) for _ in range(4)] + [rnd.randint(25, 45) for _ in range(9)] + \
                [rnd.randint(46, 70) for _ in range(5)] + [rnd.randint(71, 110) for _ in range(3)]
    rnd.shuffle(drop_pool)
    for h in HEADS:
        if h in S: continue
        d0 = drop_pool.pop()
        t = None
        for d in sorted(range(max(10, d0 - 12), d0 + 13), key=lambda d: abs(d - d0)):
            tt = h - d
            if tt >= 2 and tt not in used and diag_ok(tt, h): t = tt; break
        if t is None: return None
        S[h] = t; used.add(t)
    L = {GOLDEN[0]: GOLDEN[1]}
    heads = set(S)
    def ladder_ok(a, b):
        if not (a not in used and b not in used and b < 288 and a > 1 and diag_ok(a, b)
                and not any(0 < h - b <= 2 for h in heads)):
            return False
        return not any(segs_cross(center(a), center(b), center(x), center(y)) for x, y in L.items())
    def add_ladder(a_rng, r_rng):
        for _ in range(400):
            a = rnd.randint(*a_rng); r = rnd.randint(*r_rng); b = a + r
            if ladder_ok(a, b):
                L[a] = b; used.update([a, b]); return True
        return False
    # super ladder from the lower half
    if not add_ladder((40, 130), (100, 125)): return None
    # three long ladders, spread
    for rng_ in ((10, 90), (100, 170), (150, 210)):
        if not add_ladder(rng_, (60, 90)): return None
    # three second-chance ladders: start 4 / 6 / 8 squares above a snake tail (different worlds)
    tails = sorted(S.values())
    cands = [t for t in tails if 20 < t < 240]
    rnd.shuffle(cands)
    gaps = [4, 6, 8]; done_worlds = set()
    for t in cands:
        if not gaps: break
        w = (t - 1) // 60
        if w in done_worlds: continue
        g = gaps[0]; a = t + g
        ok = False
        for r in sorted(range(20, 46), key=lambda _: rnd.random()):
            if ladder_ok(a, a + r):
                L[a] = a + r; used.update([a, a + r]); ok = True; break
        if ok: gaps.pop(0); done_worlds.add(w)
    if gaps: return None
    # regular ladders to fill rows without a ladder start (rows 1..13), up to 18 ladders total
    rows_with = {rc(a)[0] for a in L}
    for row in range(0, 13):
        if len(L) >= 18: break
        if row in rows_with: continue
        if add_ladder((row * 20 + 1, row * 20 + 20), (15, 40)): rows_with.add(row)
    while len(L) < 18:
        if not add_ladder((2, 240), (15, 40)): return None
    return S, L

def score(S, L, games=4000, seed=0):
    rng = np.random.default_rng(seed)
    t, _ = solo_turns({**S, **L}, games * 3, rng)
    r = t.reshape(games, 3).min(1)
    drops = sum(h - t for h, t in S.items()); rises = sum(b - a for a, b in L.items())
    return r.mean(), np.median(r), drops, rises

if __name__ == '__main__':
    best = None
    for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 300):
        rnd = random.Random(seed)
        res = make(rnd)
        if res is None: continue
        S, L = res
        m, med, d, u = score(S, L, seed=seed)
        ratio = d / u
        sides = [1 if rc(b)[1] > rc(a)[1] else -1 for a, b in L.items()]
        sc = abs(m - 37.5) * 3 + abs(ratio - 1.25) * 40 + abs(sum(sides)) * 1.5
        if best is None or sc < best[0]:
            best = (sc, seed, S, L, m, med, d, u)
            print(f'seed {seed}: mean {m:.1f} med {med} drops {d} rises {u} ratio {ratio:.2f} score {sc:.2f}', flush=True)
    sc, seed, S, L, m, med, d, u = best
    m, med, d, u = score(S, L, games=30000, seed=9)
    print('BEST', seed, round(m, 1), med, d, u, round(d / u, 2))
    json.dump(dict(seed=seed, snakes={str(k): v for k, v in S.items()}, ladders={str(k): v for k, v in L.items()}), open('/tmp/runs/plan3.json', 'w'))
