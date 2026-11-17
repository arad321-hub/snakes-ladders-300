import json, math, random, sys
import numpy as np
from gen import COLS, ROWS, N, CELL, MX, MY, PW, PH, rc, center

import os
lay = json.load(open(os.environ.get('LAYOUT', 'layout.json')))
elems = lay['elems']

def X(p): return MX + p[0] * CELL
def Y(p): return MY + p[1] * CELL
def P(p): return f"{X(p):.2f},{Y(p):.2f}"

# band colors (bottom -> top), 3 rows per band: (light, dark)
BANDS = [("#eef7e4", "#9fd27a"),   # green
         ("#e4f6f3", "#7fcfc2"),   # teal
         ("#e6f0fb", "#8fb8e8"),   # blue
         ("#f0e9fa", "#b9a0e3"),   # violet
         ("#fdf1df", "#f3bf72")]   # gold (finish)

SNAKE_COLS = [("#7cc242", "#3d8b2c", "#24561a"), ("#f59b2a", "#c7501e", "#7a3011"),
              ("#a46bd6", "#6b3fa0", "#3f2266"), ("#3fa7e0", "#1d5f9e", "#123a63"),
              ("#e8473d", "#f6c33a", "#7d1f19"), ("#f2d03b", "#d9822b", "#7a4d12"),
              ("#ef7fb0", "#b03a73", "#6b2045"), ("#2dbfae", "#127a72", "#0b4a45")]

out = []
A = out.append
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}">')
A('<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="0.9"/></filter>'
  '<radialGradient id="cup" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#fff3b0"/><stop offset="1" stop-color="#d99a14"/></radialGradient></defs>')
# page + frame
A(f'<rect width="{PW}" height="{PH}" fill="#20394a"/>')
A(f'<rect x="{MX-6}" y="{MY-6}" width="{COLS*CELL+12}" height="{ROWS*CELL+12}" rx="6" fill="#f4e3c3" stroke="#0f2230" stroke-width="1.2"/>')

THEME = sys.argv[1] if len(sys.argv) > 1 else 'worlds'
# cells
if THEME in ('worlds', 'photo'):
    if THEME == 'photo':
        from photo import background
    else:
        from worlds import background
    bdefs, bsvg = background(MX, MY, CELL, COLS, ROWS)
    A(f'<defs>{bdefs}</defs>'); A(bsvg)
    # checkerboard as a light translucent veil over the art + thin grid lines
    for n in range(1, N + 1):
        r, c = rc(n)
        x = MX + c * CELL; y = MY + (ROWS - 1 - r) * CELL
        space = r // 3 == 4
        if THEME == 'photo':
            op = (0.07 if space else (0.10 if r < 6 else 0.16)) if (r + c) % 2 == 0 else 0.0
        else:
            op = (0.10 if space else 0.30) if (r + c) % 2 == 0 else (0.0 if space else 0.08)
        if op:
            A(f'<rect x="{x:.2f}" y="{y:.2f}" width="{CELL}" height="{CELL}" fill="#ffffff" fill-opacity="{op}"/>')
    for i in range(1, COLS):
        A(f'<line x1="{MX+i*CELL}" y1="{MY}" x2="{MX+i*CELL}" y2="{MY+ROWS*CELL}" stroke="#ffffff" stroke-opacity="0.45" stroke-width="0.35"/>')
    for j in range(1, ROWS):
        A(f'<line x1="{MX}" y1="{MY+j*CELL}" x2="{MX+COLS*CELL}" y2="{MY+j*CELL}" stroke="#ffffff" stroke-opacity="0.45" stroke-width="0.35"/>')
else:
  for n in range(1, N + 1):
    r, c = rc(n)
    x = MX + c * CELL; y = MY + (ROWS - 1 - r) * CELL
    light, dark = BANDS[min(r // 3, 4)]
    fill = dark if (r + c) % 2 == 0 else light
    A(f'<rect x="{x:.2f}" y="{y:.2f}" width="{CELL}" height="{CELL}" fill="{fill}"/>')
A(f'<rect x="{MX}" y="{MY}" width="{COLS*CELL}" height="{ROWS*CELL}" fill="none" stroke="#0f2230" stroke-width="0.8"/>')

# direction arrows at row ends (small chevrons in the margin-side of end cells)
def row_arrow(r):
    # arrow showing where the path turns, drawn at the outer edge of the last cell of row r
    y = MY + (ROWS - 1 - r) * CELL
    if r % 2 == 0:   # row goes left->right, turns up on the right side
        x = MX + COLS * CELL + 1.5
        return f'<path d="M{x:.1f},{y+CELL*0.75:.1f} q3,-{CELL*0.25:.1f} 0,-{CELL*0.5:.1f}" fill="none" stroke="#f4e3c3" stroke-width="0"/>'
    return ''

# ---------- ladders ----------
def ladder(b, t):
    B, T = center(b), center(t)
    d = T - B; L = np.linalg.norm(d); u = d / L; nr = np.array([-u[1], u[0]])
    w = 0.21
    B2 = B - u * 0.18; T2 = T + u * 0.18
    s = []
    off = np.array([0.06, 0.08])
    for k in (-1, 1):  # shadow rails
        a, c_ = B2 + nr * w * k + off, T2 + nr * w * k + off
        s.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(c_):.2f}" y2="{Y(c_):.2f}" stroke="#000" stroke-opacity="0.28" stroke-width="2.6" stroke-linecap="round" filter="url(#sh)"/>')
    nr_ = int(L / 0.32)
    rungs = []
    for i in range(1, nr_ + 1):
        tt = i / (nr_ + 1)
        p = B + d * tt
        a, c_ = p + nr * w, p - nr * w
        rungs.append((a, c_))
    for a, c_ in rungs:
        s.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(c_):.2f}" y2="{Y(c_):.2f}" stroke="#6b4220" stroke-width="2.2" stroke-linecap="round"/>')
        s.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(c_):.2f}" y2="{Y(c_):.2f}" stroke="#e7b36d" stroke-width="1.2" stroke-linecap="round"/>')
    for k in (-1, 1):
        a, c_ = B2 + nr * w * k, T2 + nr * w * k
        s.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(c_):.2f}" y2="{Y(c_):.2f}" stroke="#5a3519" stroke-width="2.8" stroke-linecap="round"/>')
        s.append(f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(c_):.2f}" y2="{Y(c_):.2f}" stroke="#c98a45" stroke-width="1.6" stroke-linecap="round"/>')
    return ''.join(s)

# ---------- snakes ----------
def snake(e, idx):
    pts = np.array(e['geom'][0]); ws = np.array(e['geom'][1])
    body, stripe, line = SNAKE_COLS[idx % len(SNAKE_COLS)]
    n = len(pts)
    tg = np.gradient(pts, axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None]
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    left = pts + nr * ws[:, None] / 2; right = pts - nr * ws[:, None] / 2
    s = []
    poly = ' '.join(P(p) for p in np.vstack([left, right[::-1]]))
    sh = ' '.join(f"{X(p)+1.6:.2f},{Y(p)+2.0:.2f}" for p in np.vstack([left, right[::-1]]))
    s.append(f'<polygon points="{sh}" fill="#000" fill-opacity="0.25" filter="url(#sh)"/>')
    s.append(f'<polygon points="{poly}" fill="{body}" stroke="{line}" stroke-width="0.7" stroke-linejoin="round"/>')
    # stripes by arc length
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    step = 0.42; k = 1
    while True:
        a0 = k * step; a1 = a0 + step * 0.45
        if a1 > seg[-1] - 0.25: break
        i0 = np.searchsorted(seg, a0); i1 = np.searchsorted(seg, a1)
        if i1 > i0:
            q = np.vstack([left[i0:i1 + 1], right[i0:i1 + 1][::-1]])
            s.append(f'<polygon points="{" ".join(P(p) for p in q)}" fill="{stripe}" opacity="0.9"/>')
        k += 1
    # highlight
    hl = pts + nr * ws[:, None] * 0.18
    s.append(f'<polyline points="{" ".join(P(p) for p in hl[3:-6])}" fill="none" stroke="#fff" stroke-opacity="0.35" stroke-width="1.1" stroke-linecap="round"/>')
    s.append(f'<polygon points="{poly}" fill="none" stroke="{line}" stroke-width="0.7" stroke-linejoin="round"/>')
    # head
    H = pts[0]; fwd = -tg[0]
    ang = math.degrees(math.atan2(fwd[1], fwd[0]))
    hx, hy = X(H + fwd * 0.08), Y(H + fwd * 0.08)
    g = [f'<g transform="translate({hx:.2f},{hy:.2f}) rotate({ang:.1f})">']
    g.append(f'<path d="M7.6,0 l3.2,-0.2 l1.3,-1.1 M10.8,-0.2 l1.4,0.9" stroke="#d6232a" stroke-width="0.7" fill="none" stroke-linecap="round"/>')
    g.append(f'<ellipse cx="1.8" cy="0" rx="6.4" ry="5.0" fill="{body}" stroke="{line}" stroke-width="0.8"/>')
    g.append(f'<ellipse cx="3.2" cy="0" rx="3.6" ry="2.6" fill="#fff" fill-opacity="0.18"/>')
    for sy in (-2.4, 2.4):
        g.append(f'<circle cx="3.0" cy="{sy}" r="1.75" fill="#fff" stroke="{line}" stroke-width="0.4"/>')
        g.append(f'<circle cx="3.6" cy="{sy}" r="0.9" fill="#111"/>')
        g.append(f'<circle cx="3.9" cy="{sy-0.35}" r="0.3" fill="#fff"/>')
    g.append(f'<circle cx="7.4" cy="-1.0" r="0.35" fill="{line}"/><circle cx="7.4" cy="1.0" r="0.35" fill="{line}"/>')
    g.append('</g>')
    s.append(''.join(g))
    return ''.join(s)

ladders = [e for e in elems if e['kind'] == 'L']
snakes = [e for e in elems if e['kind'] == 'S']
STYLE = sys.argv[2] if len(sys.argv) > 2 else 'real'
order = sorted(enumerate(snakes), key=lambda t: -(t[1]['hi'] - t[1]['lo']))  # long snakes first
r1, c1 = rc(1); sx0 = MX + c1 * CELL; sy0 = MY + (ROWS - 1 - r1) * CELL
rN, cN = rc(N); tx0 = MX + cN * CELL; ty0 = MY + (ROWS - 1 - rN) * CELL
if STYLE == 'real':
    import elements as el
    BX = lambda p: MX + p[0]   # elements work in mm relative to the board origin
    BY = lambda p: MY + p[1]
    A(f'<defs>{el.DEFS}{el.DEFS2}</defs>')
    for k, e in enumerate(ladders):
        if not e.get('golden'):
            A(el.ladder(center(e['lo']), center(e['hi']), BX, BY, CELL, k))
    for i, e in order:
        A(el.snake(e, i, BX, BY, CELL, i))
    for e in ladders:
        if e.get('golden'):
            A(el.golden_ladder(center(e['lo']), center(e['hi']), BX, BY, CELL, to_finish=(e['hi'] == N)))
    for sq, kind in lay.get('actions', {}).items():
        ra, ca = rc(int(sq))
        A(el.action_icon(kind, MX + ca * CELL, MY + (ROWS - 1 - ra) * CELL, CELL))
    A(el.start_sign(sx0, sy0, CELL))
    A(el.trophy(tx0, ty0, CELL))
else:
    for e in ladders: A(ladder(e['lo'], e['hi']))
    for i, e in order:
        A(snake(e, i))
    A(f'<text x="{sx0+CELL/2:.2f}" y="{sy0+CELL*0.78:.2f}" font-family="DejaVu Sans" font-weight="bold" font-size="5" fill="#24561a" text-anchor="middle">START</text>')
    cx, cy = tx0 + CELL * 0.62, ty0 + CELL * 0.56
    A(f'<g transform="translate({cx:.2f},{cy:.2f})">'
      '<path d="M-6,-8 h12 v3 a6,7 0 0 1 -12,0z" fill="url(#cup)" stroke="#8a5a00" stroke-width="0.6"/>'
      '<path d="M-6,-6 q-4,0 -3.5,3 q0.5,2.5 4,3 M6,-6 q4,0 3.5,3 q-0.5,2.5 -4,3" fill="none" stroke="#8a5a00" stroke-width="0.9"/>'
      '<rect x="-1.2" y="4" width="2.4" height="3" fill="#d99a14" stroke="#8a5a00" stroke-width="0.5"/>'
      '<rect x="-4.5" y="7" width="9" height="2.6" rx="0.6" fill="#7a4d12"/></g>')

# numbers on top of everything, with white halo
for n in range(1, N + 1):
    r, c = rc(n)
    x = MX + c * CELL; y = MY + (ROWS - 1 - r) * CELL
    if THEME == 'photo':
        # number badge: readable on any background (snow, sand or space)
        bw = 2.4 + 4.35 * len(str(n))
        A(f'<rect x="{x+0.9:.2f}" y="{y+0.9:.2f}" width="{bw:.2f}" height="8.2" rx="2.2" fill="#ffffff" fill-opacity="0.82" stroke="#13212c" stroke-opacity="0.35" stroke-width="0.3"/>')
        A(f'<text x="{x+0.9+bw/2:.2f}" y="{y+7.35:.2f}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="6.6" fill="#13212c">{n}</text>')
    else:
        A(f'<text x="{x+1.6:.2f}" y="{y+7.4:.2f}" font-family="DejaVu Sans" font-weight="bold" font-size="7" '
          f'fill="#13212c" stroke="#ffffff" stroke-width="1.8" stroke-linejoin="round" paint-order="stroke">{n}</text>')

A('</svg>')
open('board.svg', 'w').write('\n'.join(out))
print('ok', len(snakes), 'snakes', len(ladders), 'ladders')
