"""Build drawable geometry for the approved v3 plan (fixed endpoints).

Ladders are placed first (straight), then snakes longest-first. For every snake we try many
path variants (wave / arc / sweep / curl, different seeds) and keep the one with the fewest
crossings that respects: max elements per square, no body over another element's end square,
staying inside the board. If nothing fits, the tail is nudged by 1-2 squares (diagonal kept).
Action squares must sit in squares no body passes through; otherwise they move to the nearest
free square.
"""
import json, random, sys
import numpy as np
from gen import rc, center, path_cells, ladder_cells, segs_cross
from gen2 import snake_geom, inside

MAX_PER_CELL = 3
N = 300

def diag_ok(a, b):
    (r1, c1), (r2, c2) = rc(a), rc(b); dr, dc = abs(r1 - r2), abs(c1 - c2)
    return dr > 0 and max(2, 0.5 * dr) <= dc <= 8

def lines_cross(l1, l2):
    for i in range(len(l1) - 1):
        for j in range(len(l2) - 1):
            if segs_cross(l1[i], l1[i + 1], l2[j], l2[j + 1]):
                return True
    return False

def build(plan, actions, curvy_target=7, seed=0, log=print):
    rnd = random.Random(seed)
    S = {int(k): v for k, v in plan['snakes'].items()}
    L = {int(k): v for k, v in plan['ladders'].items()}
    ends = set(S) | set(S.values()) | set(L) | set(L.values())
    end_cells = {rc(x) for x in set(S) | set(L)}            # trigger squares stay clear
    land_cells = {rc(x) for x in set(S.values()) | set(L.values())}
    occ, elems = {}, []

    def fits(cells, own_ends):
        own = {rc(x) for x in own_ends}
        for cc in cells:
            if cc in own: continue
            if cc in end_cells: return False
            if occ.get(cc, 0) + 1 > MAX_PER_CELL: return False
        return True

    def commit(e, cells):
        for cc in cells: occ[cc] = occ.get(cc, 0) + 1
        e['cells'] = cells; elems.append(e)

    # ladders
    for a, b in sorted(L.items(), key=lambda t: -(t[1] - t[0])):
        cells = ladder_cells(a, b)
        if not fits(cells, (a, b)):
            log(f'  ladder {a}->{b} touches another end square (kept, check visually)')
        commit(dict(kind='L', lo=a, hi=b, golden=(a, b) == (258, 300), style=None, geom=None,
                    line=[center(a).tolist(), center(b).tolist()]), cells)

    # snakes, longest first; choose which get curvy styles
    order = sorted(S.items(), key=lambda t: -(t[0] - t[1]))
    curvy_ok = [h for h, t in order if 20 <= h - t <= 90]
    rnd.shuffle(curvy_ok)
    curvy_set = set(curvy_ok[:curvy_target + 3])
    n_curvy = 0
    for h, t in order:
        placed = False
        tails = [t] + [t + d for d in sorted(range(-12, 13), key=abs) if d and 1 < t + d < h and t + d not in ends and diag_ok(t + d, h)]
        for tt in tails:
            best = None
            want_curvy = h in curvy_set and n_curvy < curvy_target
            styles = ['arc', 'sweep', 'curl', 'wave']
            for style in styles:
                for k in range(8):
                    r2 = random.Random(hash((h, tt, style, k, seed)) & 0xffffffff)
                    pts, ws = snake_geom(h, tt, style, r2)
                    if not inside(pts): continue
                    cells = path_cells(pts, ws)
                    if not fits(cells, (h, tt)): continue
                    line = pts[::5].tolist() + [pts[-1].tolist()]
                    nx = sum(1 for e in elems if lines_cross(line, e['line']))
                    over_land = sum(1 for cc in cells if cc in land_cells and cc not in (rc(h), rc(tt)))
                    if any(e.get('golden') and lines_cross(line, e['line']) for e in elems): continue
                    cost = nx * 10 + over_land * 6 + (0 if style == 'wave' else (-4 if want_curvy else 5))
                    if best is None or cost < best[0]:
                        best = (cost, style, pts, ws, cells, line, nx)
            if best and best[6] <= 2:
                cost, style, pts, ws, cells, line, nx = best
                if tt != t:
                    log(f'  snake {h}->{t}: tail moved to {tt}')
                    ends.discard(t); ends.add(tt); land_cells.discard(rc(t)); land_cells.add(rc(tt))
                commit(dict(kind='S', hi=h, lo=tt, style=style, golden=False,
                            geom=(pts.tolist(), ws.tolist()), line=line), cells)
                if style != 'wave': n_curvy += 1
                placed = True
                break
        if not placed:
            log(f'  !! snake {h}->{t} could not be placed cleanly')
            return None
    # action squares: move to nearest free square if a body passes through
    acts = {}
    for sq, kind in sorted(actions.items()):
        placed = False
        for allow in (0, 1):
            for d in sorted(range(-6, 7), key=abs):
                s = sq + d
                if s in ends or s in acts or s <= 2 or s >= 288: continue
                if occ.get(rc(s), 0) > allow: continue
                if any(abs(s - a) <= 1 for a in acts): continue
                if d: log(f'  action {kind} {sq} -> {s}' + (' (shares square with a body)' if allow else ''))
                acts[s] = kind; placed = True; break
            if placed: break
        if not placed:
            log(f'  !! action {kind} {sq} has no free square nearby')
            return None
    return elems, acts, n_curvy

if __name__ == '__main__':
    plan = json.load(open(sys.argv[1]))
    actions = {18: 'turbo', 110: 'turbo', 176: 'turbo', 213: 'turbo', 95: 'block', 198: 'block', 256: 'block',
               44: 'drain', 135: 'drain', 228: 'drain', 270: 'drain', 70: 'swap', 162: 'swap', 252: 'swap'}
    best = None
    for seed in range(int(sys.argv[2]) if len(sys.argv) > 2 else 20):
        msgs = []
        res = build(plan, actions, seed=seed, log=msgs.append)
        if res is None:
            print('seed', seed, 'failed:', msgs[-1] if msgs else ''); continue
        elems, acts, nc = res
        cr = sum(1 for i in range(len(elems)) for j in range(i + 1, len(elems)) if lines_cross(elems[i]['line'], elems[j]['line']))
        moved = sum(1 for m in msgs if '->' in m and ('moved' in m or 'action' in m))
        sc = cr * 3 + moved * 2 - nc * 2
        print(f'seed {seed}: crossings {cr} curvy {nc} changes {moved} score {sc}', flush=True)
        if best is None or sc < best[0]: best = (sc, seed, elems, acts, msgs)
    sc, seed, elems, acts, msgs = best
    print('BEST seed', seed); print('\n'.join(msgs))
    out = [dict(kind=e['kind'], hi=e['hi'], lo=e['lo'], geom=e['geom'], style=e['style'], golden=e['golden']) for e in elems]
    json.dump(dict(version=3, seed=seed, elems=out, actions={str(k): v for k, v in acts.items()}), open(sys.argv[3] if len(sys.argv) > 3 else 'layout3.json', 'w'))
