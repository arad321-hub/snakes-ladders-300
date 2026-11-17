import math, random, sys, json
import numpy as np

COLS, ROWS = 20, 15
N = COLS * ROWS
CELL = 28.0            # mm
MX, MY = 20.0, 15.0    # page margins (mm) -> page 600 x 450 (4:3)
PW, PH = COLS * CELL + 2 * MX, ROWS * CELL + 2 * MY
MAX_PER_CELL = 2

def rc(n):
    r = (n - 1) // COLS
    c = (n - 1) % COLS
    if r % 2 == 1:
        c = COLS - 1 - c
    return r, c

def center(n):  # in cell units, y downward
    r, c = rc(n)
    return np.array([c + 0.5, (ROWS - 1 - r) + 0.5])

def cell_of(p):
    c = int(math.floor(p[0])); y = int(math.floor(p[1]))
    if c < 0 or c >= COLS or y < 0 or y >= ROWS:
        return None
    return (ROWS - 1 - y, c)

# ---------------- geometry ----------------
def snake_geom(h, t, seed):
    rnd = random.Random(seed)
    H, T = center(h), center(t)
    d = T - H; L = np.linalg.norm(d); u = d / L; nrm = np.array([-u[1], u[0]])
    waves = max(1, round(L / 1.5))
    amp = 0.26 + 0.06 * rnd.random()
    phase = rnd.choice([0, math.pi])
    ts = np.linspace(0, 1, max(30, int(L * 14)))
    pts, ws = [], []
    for tt in ts:
        env = min(1.0, tt * 5) * min(1.0, (1 - tt) * 6 + 0.25)
        off = amp * env * math.sin(math.pi * waves * tt + phase)
        pts.append(H + d * tt + nrm * off)
        ws.append(0.07 + 0.25 * (1 - tt) ** 0.8)
    return np.array(pts), np.array(ws)

def ladder_geom(b, t):
    B, T = center(b), center(t)
    return B, T

def path_cells(pts, ws):
    cells = set()
    for i in range(len(pts)):
        p = pts[i]
        if i < len(pts) - 1:
            tg = pts[i + 1] - p
        else:
            tg = p - pts[i - 1]
        tg = tg / (np.linalg.norm(tg) + 1e-9); nr = np.array([-tg[1], tg[0]])
        for k in (-0.5, 0, 0.5):
            cc = cell_of(p + nr * ws[i] * k)
            if cc: cells.add(cc)
    return cells

def ladder_cells(b, t):
    B, T = ladder_geom(b, t)
    d = T - B; L = np.linalg.norm(d); u = d / L; nr = np.array([-u[1], u[0]])
    cells = set()
    for tt in np.linspace(0, 1, int(L * 14) + 2):
        for k in (-0.22, 0, 0.22):
            cc = cell_of(B + d * tt + nr * k)
            if cc: cells.add(cc)
    return cells

def segs_cross(p1, p2, q1, q2):
    def o(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
    return (o(p1,p2,q1)*o(p1,p2,q2) < 0) and (o(q1,q2,p1)*o(q1,q2,p2) < 0)

# ---------------- reference lengths (read from the 100-square board) ----------------
REF_SNAKES = [16, 20, 63, 20, 43, 4, 21, 38, 10, 25]
REF_LADDERS = [20, 19, 15, 8, 52, 21, 16, 19, 10]
SCALE = 3

def build(seed, n_snakes=30, n_ladders=27):
    rnd = random.Random(seed)
    occ = {}       # cell -> count
    endpoints = set()
    elems = []
    def try_add(kind, a, b):
        # a = higher square (snake head / ladder top), b = lower square
        if a in endpoints or b in endpoints: return False
        ra, ca = rc(a); rb, cb = rc(b)
        if (ra, ca) in occ or (rb, cb) in occ: return False
        if abs(ca - cb) > 6: return False
        if ra == rb: return False
        if kind == 'S':
            pts, ws = snake_geom(a, b, rnd.random())
            cells = path_cells(pts, ws)
        else:
            cells = ladder_cells(b, a)
        ea, eb = rc(a), rc(b)
        line = pts[::4].tolist() + [pts[-1].tolist()] if kind == 'S' else [center(b).tolist(), center(a).tolist()]
        nx = 0
        for e2 in elems:
            l2 = e2['line']
            hit = False
            for i in range(len(line) - 1):
                for j in range(len(l2) - 1):
                    if segs_cross(line[i], line[i+1], l2[j], l2[j+1]):
                        hit = True; break
                if hit: break
            if hit:
                if kind == 'L' and e2['kind'] == 'L': return False
                nx += 1
                if nx > 1: return False
        for cc in cells:
            lim = 1 if cc in (ea, eb) else MAX_PER_CELL
            if occ.get(cc, 0) + 1 > lim: return False
            # never run over somebody else's endpoint
            if cc not in (ea, eb) and cc in endpoint_cells: return False
        for e in (ea, eb):
            if occ.get(e, 0) > 0: return False
        for cc in cells: occ[cc] = occ.get(cc, 0) + 1
        endpoints.update([a, b]); endpoint_cells.update([ea, eb])
        elems.append(dict(kind=kind, hi=a, lo=b, line=line, seed=None if kind == 'L' else 0, cells=cells,
                          geom=(pts.tolist(), ws.tolist()) if kind == 'S' else None))
        return True
    endpoint_cells = set()
    # interleave so both kinds get the whole board
    order = ['S'] * n_snakes + ['L'] * n_ladders
    rnd.shuffle(order)
    # make sure late-game has bite: first place a few long snakes near the top
    counts = {'S': 0, 'L': 0}
    want = {'S': n_snakes, 'L': n_ladders}
    attempts = 0
    while (counts['S'] < n_snakes or counts['L'] < n_ladders) and attempts < 15000:
        attempts += 1
        kind = 'S' if (counts['S'] / n_snakes) <= (counts['L'] / n_ladders) else 'L'
        if counts[kind] >= want[kind]:
            kind = 'L' if kind == 'S' else 'S'
        ref = REF_SNAKES if kind == 'S' else REF_LADDERS
        L = int(round(rnd.choice(ref) * SCALE * rnd.uniform(0.8, 1.2)))
        L = max(L, 12)
        # spread: bias start square towards least-populated band
        lo = rnd.randint(2, N - 1 - L)
        hi = lo + L
        if hi >= N or lo <= 1: continue
        if kind == 'S' and hi < 25: continue
        if try_add(kind, hi, lo):
            counts[kind] += 1
    return elems, occ

def expected_turns(jumps, n):
    # Markov chain, single die, overshoot = stay put
    import numpy as np
    A = np.zeros((n, n)); bvec = np.ones(n)
    # E[s] = 1 + 1/6 sum E[next]
    for s in range(n):  # squares 1..n -> index s (0..n-1), s==n-1 absorbing
        A[s, s] += 1
        if s == n - 1:
            bvec[s] = 0; continue
        for k in range(1, 7):
            t = s + k
            if t > n - 1: t = s
            else:
                t = jumps.get(t + 1, t + 1) - 1
            A[s, t] -= 1 / 6
    E = np.linalg.solve(A, bvec)
    return E[0]

if __name__ == '__main__':
    best = None
    for seed in range(int(sys.argv[1]) if len(sys.argv) > 1 else 60):
        elems, occ = build(seed)
        ns = sum(e['kind'] == 'S' for e in elems); nl = len(elems) - ns
        # crossings between straight chords (proxy)
        cr = 0
        for i in range(len(elems)):
            for j in range(i + 1, len(elems)):
                l1, l2 = elems[i]['line'], elems[j]['line']
                if any(segs_cross(l1[p], l1[p+1], l2[q], l2[q+1]) for p in range(len(l1)-1) for q in range(len(l2)-1)): cr += 1
        # distribution of snakes over rows (want every 3-row band covered)
        bands = [0] * 5
        for e in elems:
            if e['kind'] == 'S': bands[rc(e['hi'])[0] // 3] += 1
        jm = {e['hi']: e['lo'] for e in elems if e['kind'] == 'S'}
        jm.update({e['lo']: e['hi'] for e in elems if e['kind'] == 'L'})
        et = expected_turns(jm, N)
        score = (ns + nl) * 10 - cr * 6 - sum(abs(b - 5.6) for b in bands) * 4 - abs(et - 110) * 1.5
        if best is None or score > best[0]:
            best = (score, seed, elems, ns, nl, cr, bands)
    score, seed, elems, ns, nl, cr, bands = best
    print('seed', seed, 'snakes', ns, 'ladders', nl, 'chord-crossings', cr, 'bands', bands)
    jumps = {e['hi']: e['lo'] for e in elems if e['kind'] == 'S'}
    jumps.update({e['lo']: e['hi'] for e in elems if e['kind'] == 'L'})
    print('expected turns 300 board:', round(expected_turns(jumps, N), 1))
    ref = {98:82,96:76,87:24,92:72,62:19,64:60,47:26,49:11,16:6,55:53,
           80:100,71:91,52:67,36:44,33:85,20:41,22:38,12:31,4:14}
    print('expected turns ref 100 board (approx reading):', round(expected_turns(ref, 100), 1))
    print('expected turns plain 300:', round(expected_turns({}, N), 1), 'plain 100:', round(expected_turns({}, 100), 1))
    out = [dict(kind=e['kind'], hi=e['hi'], lo=e['lo'], geom=e['geom']) for e in elems]
    json.dump(dict(seed=seed, elems=out), open('layout.json', 'w'))
