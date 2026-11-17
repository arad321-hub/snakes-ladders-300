"""Layout generator v2.

- Golden (championship) ladder 260 -> 300, fixed.
- Exactly one snake head in the bounce zone (288-299).
- About a third of the snakes take curvy paths: big arcs, S-sweeps, or a tail that curls into a spiral.
- Action squares: Swap x3 (~70, 150-170, ~250), Block x3, Turbo x4, Hitchhike x4, placed only in
  squares that no snake/ladder body passes through (so their icon stays visible).
- Tuned with a 2-dice / bounce-back simulation: 3 players, rounds until first winner
  (target mean ~55, median ~45) and an event every ~5 turns.
"""
import math, random, sys, json
import numpy as np
from gen import COLS, ROWS, N, rc, center, cell_of, path_cells, ladder_cells, segs_cross

import os
MAX_PER_CELL = int(os.environ.get('MAX_PER_CELL', 2))
import os
GOLDEN = (int(os.environ.get('GOLDEN_FROM', 258)), int(os.environ.get('GOLDEN_TOP', 300)))
BOUNCE_SNAKE_HEAD = 296    # least game-delaying of 296-298 (simulated)
BOUNCE_ZONE = range(288, 300)
# reference lengths read from the original 100-square board, x3
REF_SNAKES = [63, 43, 38, 21, 20, 20, 20, 10, 4, 3]
REF_LADDERS = [51, 21, 20, 20, 19, 18, 16, 10, 2]
SCALE = 3
ACTION_PLAN = {'swap': [(64, 76), (150, 170), (244, 256)],
               'block': 3, 'turbo': 4, 'hitch': 4}

# ------------------------------------------------------------------ geometry
def chaikin(P, it=3):
    P = np.asarray(P, float)
    for _ in range(it):
        Q = [P[0]]
        for a, b in zip(P[:-1], P[1:]):
            Q += [0.75 * a + 0.25 * b, 0.25 * a + 0.75 * b]
        Q.append(P[-1]); P = np.array(Q)
    return P

def resample(P, step=0.07):
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    s = np.linspace(0, seg[-1], max(30, int(seg[-1] / step)))
    return np.stack([np.interp(s, seg, P[:, 0]), np.interp(s, seg, P[:, 1])], 1)

def widths(P):
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    t = seg / seg[-1]
    return taper(t)

TIP_W = 0.045
def taper(t):
    """Body narrows gently (~40% head->tail), then a convex cone over the last 28% to a small blunt tip."""
    body = 0.195 + 0.125 * (1 - t) ** 0.8
    x = np.clip((1 - t) / 0.28, 0, 1)
    return np.where(x < 1, TIP_W + (body - TIP_W) * np.sqrt(x), body)

def add_round_cap(P, ws):
    """Extend the centreline past the tail with a half-circle width profile (rounded tip)."""
    P = np.asarray(P, float); u = P[-1] - P[-2]; u /= np.linalg.norm(u); r = ws[-1] / 2
    ang = np.linspace(0, np.pi / 2, 8)[1:]
    cap_p = [P[-1] + u * r * np.sin(a) for a in ang]
    cap_w = [max(2 * r * np.cos(a), 0.002) for a in ang]
    return np.vstack([P, cap_p]), np.r_[ws, cap_w]

def snake_geom(h, t, style, rnd):
    H, T = center(h), center(t)
    d = T - H; L = np.linalg.norm(d); u = d / L; nr = np.array([-u[1], u[0]])
    side = rnd.choice([-1, 1])
    if style == 'wave':
        waves = max(1, round(L / 1.5)); amp = 0.26 + 0.06 * rnd.random()
        ts = np.linspace(0, 1, 80)
        P = [H + d * x + nr * amp * min(1, x * 5) * min(1, (1 - x) * 6 + 0.25) * math.sin(math.pi * waves * x) for x in ts]
        P = np.array(P)
    elif style == 'arc':                 # one big C-shaped sweep
        A = side * min(1.6, 0.35 + 0.28 * L) * rnd.uniform(0.85, 1.1)
        ts = np.linspace(0, 1, 60)
        P = np.array([H + d * x + nr * (A * math.sin(math.pi * x) + 0.12 * math.sin(math.pi * 6 * x) * math.sin(math.pi * x)) for x in ts])
    elif style == 'sweep':               # big S
        A = side * min(1.2, 0.3 + 0.2 * L)
        ts = np.linspace(0, 1, 60)
        P = np.array([H + d * x + nr * A * math.sin(2 * math.pi * x) * (0.6 + 0.4 * math.sin(math.pi * x)) for x in ts])
    else:                                # 'curl': body then the tail coils into a spiral around the tail square
        r0 = 0.43
        th0 = math.atan2(H[1] - T[1], H[0] - T[0])
        S0 = T + r0 * np.array([math.cos(th0), math.sin(th0)])
        dd = S0 - H; LL = np.linalg.norm(dd); uu = dd / LL; nn = np.array([-uu[1], uu[0]])
        waves = max(1, round(LL / 1.6)); amp = 0.25
        body = [H + dd * x + nn * amp * min(1, x * 5) * (1 - x) * math.sin(math.pi * waves * x) for x in np.linspace(0, 1, 50)]
        turns = rnd.uniform(1.1, 1.4); spin = side
        sp = []
        for x in np.linspace(0, 1, 70)[1:]:
            th = th0 + spin * 2 * math.pi * turns * x
            rr = r0 * (1 - x) + 0.06 * x
            sp.append(T + rr * np.array([math.cos(th), math.sin(th)]))
        P = np.array(body + sp)
    P = chaikin(P, 2)
    P = resample(P)
    return add_round_cap(P, widths(P))

def inside(P):
    return np.all((P[:, 0] > 0.08) & (P[:, 0] < COLS - 0.08) & (P[:, 1] > 0.08) & (P[:, 1] < ROWS - 0.08))

# ------------------------------------------------------------------ build
def build(seed, n_snakes, n_ladders, curvy_frac=0.36):
    rnd = random.Random(seed)
    occ, endpoint_cells, endpoints, elems = {}, set(), set(), []

    def try_add(kind, a, b, style=None, golden=False):
        if a in endpoints or b in endpoints: return False
        ea, eb = rc(a), rc(b)
        if ea in occ or eb in occ: return False
        if ea[0] == eb[0]: return False
        if kind == 'S':
            if abs(ea[1] - eb[1]) > (8 if style != 'wave' else 6): return False
            pts, ws = snake_geom(a, b, style, rnd)
            if not inside(pts): return False
            cells = path_cells(pts, ws)
            line = pts[::5].tolist() + [pts[-1].tolist()]
        else:
            if abs(ea[1] - eb[1]) > 8: return False
            cells = ladder_cells(b, a)
            line = [center(b).tolist(), center(a).tolist()]
        nx = 0
        for e2 in elems:
            l2 = e2['line']; hit = False
            for i in range(len(line) - 1):
                for j in range(len(l2) - 1):
                    if segs_cross(line[i], line[i + 1], l2[j], l2[j + 1]):
                        hit = True; break
                if hit: break
            if hit:
                if kind == 'L' and e2['kind'] == 'L': return False
                if golden or e2.get('golden'): return False
                nx += 1
                if nx > 1: return False
        for cc in cells:
            lim = 1 if cc in (ea, eb) else MAX_PER_CELL
            if occ.get(cc, 0) + 1 > lim: return False
            if cc not in (ea, eb) and cc in endpoint_cells: return False
        for cc in cells: occ[cc] = occ.get(cc, 0) + 1
        endpoints.update([a, b]); endpoint_cells.update([ea, eb])
        elems.append(dict(kind=kind, hi=a, lo=b, line=line, cells=cells, golden=golden,
                          style=style, geom=(pts.tolist(), ws.tolist()) if kind == 'S' else None))
        return True

    # 1) golden ladder
    assert try_add('L', GOLDEN[1], GOLDEN[0], golden=True)
    # 2) exactly one snake in the bounce zone
    h = BOUNCE_SNAKE_HEAD
    for _ in range(400):
        L = rnd.randint(25, 45); (r1, c1), (r2, c2) = rc(h), rc(h - L)
        dr, dc = abs(r1 - r2), abs(c1 - c2)
        if dr == 0 or dc < max(2, 0.5 * dr) or dc > 8: continue
        if try_add('S', h, h - L, style=rnd.choice(['wave', 'arc', 'curl'])): break
    want = {'S': n_snakes, 'L': n_ladders}
    cnt = {'S': 1, 'L': 1}
    n_curvy_target = round(n_snakes * curvy_frac)
    n_curvy = sum(1 for e in elems if e['kind'] == 'S' and e['style'] != 'wave')
    attempts = 0
    while (cnt['S'] < want['S'] or cnt['L'] < want['L']) and attempts < 20000:
        attempts += 1
        kind = 'S' if cnt['S'] / want['S'] <= cnt['L'] / want['L'] else 'L'
        if cnt[kind] >= want[kind]: kind = 'L' if kind == 'S' else 'S'
        ref = REF_SNAKES if kind == 'S' else REF_LADDERS
        sc = SCALE if kind == 'S' else float(os.environ.get('LADDER_SCALE', 3))
        L = min(int(os.environ.get('MAXLEN', 130)), max(12, int(round(rnd.choice(ref) * sc * rnd.uniform(0.8, 1.2)))))
        lo = rnd.randint(2, N - 1 - L)
        cands = []
        for L2 in range(max(12, int(L * 0.85)), int(L * 1.15) + 1):
            h2 = lo + L2
            if h2 >= N: break
            (r1, c1), (r2, c2) = rc(lo), rc(h2)
            dr, dc = abs(r2 - r1), abs(c2 - c1)
            if dr == 0: continue
            if dc < max(2, 0.5 * dr) or dc > 8: continue
            cands.append(h2)
        if not cands: continue
        hi = rnd.choice(cands)
        if hi >= N or lo <= 1: continue
        if hi in BOUNCE_ZONE or lo in BOUNCE_ZONE or hi >= 288: continue
        style = None
        if kind == 'S':
            if hi < 25: continue
            bias = float(os.environ.get('SNAKE_TOP_BIAS', 0))
            if rnd.random() > (1 - bias) + bias * hi / N: continue
            curvy_left = n_curvy_target - n_curvy
            snakes_left = want['S'] - cnt['S']
            p_curvy = min(1.0, curvy_left / max(1, snakes_left) * 1.3)
            style = rnd.choice(['arc', 'curl', 'sweep']) if rnd.random() < p_curvy else 'wave'
        if try_add(kind, hi, lo, style):
            cnt[kind] += 1
            if kind == 'S' and style != 'wave': n_curvy += 1
    return elems, occ

def place_actions(elems, occ, rnd):
    ends = set()
    for e in elems: ends |= {e['hi'], e['lo']}
    def ok(s, acts):
        if s in ends or s <= 2 or s >= 288: return False
        if rc(s) in occ: return False                    # no snake/ladder body in this square
        if any(abs(s - a) <= 3 for a in acts): return False
        return True
    acts = {}
    for lo, hi in ACTION_PLAN['swap']:
        c = [s for s in range(lo, hi + 1) if ok(s, acts)]
        if not c: return None
        mid = (lo + hi) / 2
        c.sort(key=lambda s: abs(s - mid)); acts[rnd.choice(c[:4])] = 'swap'
    for t in ('block', 'turbo', 'hitch'):
        n = ACTION_PLAN[t]
        for k in range(n):
            lo, hi = 6 + k * 280 // n, 6 + (k + 1) * 280 // n
            c = [s for s in range(lo, hi) if ok(s, acts)]
            if not c: return None
            acts[rnd.choice(c)] = t
    return acts

# ------------------------------------------------------------------ fast evaluation
def solo_turns(J, games, rng, triggers=None):
    """Vectorised solo games: 2 dice, bounce back past 300. Returns turns and trigger hits."""
    jt = np.arange(N + 1)
    for a, b in J.items(): jt[a] = b
    trig = np.zeros(N + 1, bool)
    if triggers is not None: trig[list(triggers)] = True
    pos = np.ones(games, int); t = np.zeros(games, int); hits = np.zeros(games, int)
    done = np.zeros(games, bool)
    while not done.all() and t.max() < 3000:
        a = ~done
        q = pos[a] + rng.integers(1, 7, a.sum()) + rng.integers(1, 7, a.sum())
        q = np.where(q > N, 2 * N - q, q)
        hits[a] += trig[q]
        pos[a] = jt[q]; t[a] += 1; done[a] = pos[a] == N
    return t, hits

def evaluate(elems, acts, players=3, games=6000, seed=0):
    rng = np.random.default_rng(seed)
    J = {e['hi']: e['lo'] for e in elems if e['kind'] == 'S'}
    J.update({e['lo']: e['hi'] for e in elems if e['kind'] == 'L'})
    trig = set(J) | set(acts or {})
    t, h = solo_turns(J, games * players, rng, trig)
    rounds = t.reshape(games, players).min(1)
    return dict(mean=float(rounds.mean()), median=float(np.median(rounds)),
                p90=float(np.percentile(rounds, 90)), event_every=float(t.sum() / h.sum()))

def crossings(elems):
    cr = 0
    for i in range(len(elems)):
        for j in range(i + 1, len(elems)):
            l1, l2 = elems[i]['line'], elems[j]['line']
            if any(segs_cross(l1[p], l1[p + 1], l2[q], l2[q + 1]) for p in range(len(l1) - 1) for q in range(len(l2) - 1)):
                cr += 1
    return cr

if __name__ == '__main__':
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    n_s = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    n_l = int(sys.argv[3]) if len(sys.argv) > 3 else 21
    best = None
    start = int(os.environ.get('SEED_START', 0))
    for seed in range(start, start + seeds):
        elems, occ = build(seed, n_s, n_l)
        acts = place_actions(elems, occ, random.Random(seed))
        if acts is None: continue
        ns = sum(e['kind'] == 'S' for e in elems); nl = len(elems) - ns
        curvy = sum(1 for e in elems if e['kind'] == 'S' and e['style'] != 'wave')
        bz = sum(1 for e in elems if e['kind'] == 'S' and e['hi'] in BOUNCE_ZONE)
        if bz != 1: continue
        ev = evaluate(elems, acts, games=3000, seed=seed)
        cr = crossings(elems)
        bands = [0] * 5
        for e in elems:
            if e['kind'] == 'S': bands[rc(e['hi'])[0] // 3] += 1
        score = ((ns - n_s) + (nl - n_l)) * 12 - cr * 4 - abs(ev['mean'] - 55) * 3 - abs(ev['median'] - 45) * 3 \
                - abs(ev['event_every'] - 5.0) * 25 - max(0, round(n_s / 3) - curvy) * 8 - sum(abs(b - ns / 5) for b in bands) * 2
        print(f"seed {seed}: S{ns} L{nl} curvy{curvy} cross{cr} mean{ev['mean']:.1f} med{ev['median']} ev/{ev['event_every']:.2f} score {score:.1f}", flush=True)
        if best is None or score > best[0]:
            best = (score, seed, elems, acts)
    score, seed, elems, acts = best
    ev = evaluate(elems, acts, games=20000, seed=99)
    print('BEST seed', seed, ev)
    out = [dict(kind=e['kind'], hi=e['hi'], lo=e['lo'], geom=e['geom'], style=e['style'], golden=e['golden']) for e in elems]
    json.dump(dict(seed=seed, version=2, elems=out, actions={str(k): v for k, v in acts.items()}), open(os.environ.get('OUT', 'layout2.json'), 'w'))
