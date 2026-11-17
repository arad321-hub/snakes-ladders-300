"""Semi-realistic vector elements: snakes, ladders, START sign, trophy.

Everything is plain SVG (no raster), so it stays sharp at any print size.
Coordinates: helper functions receive a mm-converter `X/Y` from render.py.
"""
import math
import numpy as np

LIGHT = np.array([-0.6, -0.8])          # light from the upper-left (svg y is down)

def _hex(c):
    c = c.lstrip('#'); return np.array([int(c[i:i+2], 16) for i in (0, 2, 4)], float)
def _rgb(a):
    a = np.clip(a, 0, 255).round().astype(int); return '#%02x%02x%02x' % tuple(a)
def mix(c1, c2, t):
    return _rgb(_hex(c1) * (1 - t) + _hex(c2) * t)
def dark(c, t): return mix(c, '#000000', t)
def light(c, t): return mix(c, '#ffffff', t)

# ------------------------------------------------------------------ snakes
# Species: base colour + pattern. Realistic skins, but friendly faces.
SPECIES = [
    dict(name='python',  base='#c79a5c', pat='blotch', pc='#5b3a1c', pc2='#a8793f'),
    dict(name='coral',   base='#d63a2c', pat='bands',  bands=['#d63a2c', '#1f1a1a', '#f1c63c', '#1f1a1a']),
    dict(name='green',   base='#4fa63a', pat='dots',   pc='#d6f5a8'),
    dict(name='diamond', base='#b39a6c', pat='diamond', pc='#4b3a25', pc2='#e8d6a8'),
    dict(name='corn',    base='#e8883b', pat='blotch', pc='#b2301d', pc2='#e0552f', edge='#2a1408'),
    dict(name='blue',    base='#3a7fd0', pat='stripe', pc='#a9d6ff'),
    dict(name='yellow',  base='#e7c13e', pat='bars',   pc='#5e3f0f'),
    dict(name='purple',  base='#8a5ac4', pat='rings',  pc='#c7a6f0'),
]

def _frame(pts):
    tg = np.gradient(pts, axis=0); tg /= np.linalg.norm(tg, axis=1)[:, None] + 1e-9
    nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
    return tg, nr

def snake(e, idx, X, Y, CELL, uid):
    sp = SPECIES[idx % len(SPECIES)]
    base = sp['base']
    pts = np.array(e['geom'][0]) * CELL           # -> mm, relative to board origin
    ws = np.array(e['geom'][1]) * CELL * 1.12      # body width in mm
    tg, nr = _frame(pts)
    lproj = (nr @ LIGHT)                            # >0 : that side faces the light
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    total = seg[-1]
    def P(p): return f'{X(p):.2f},{Y(p):.2f}'
    def tube(frac, shift=0.0):
        c = pts + nr * (ws * shift * np.sign(lproj) * np.abs(lproj))[:, None] * 0.5
        l = c + nr * (ws * frac / 2)[:, None]; r = c - nr * (ws * frac / 2)[:, None]
        return ' '.join(P(p) for p in np.vstack([l, r[::-1]]))
    def quad(i0, i1, f0=-1, f1=1):
        l = pts[i0:i1 + 1] + nr[i0:i1 + 1] * (ws[i0:i1 + 1] * f1 / 2)[:, None]
        r = pts[i0:i1 + 1] + nr[i0:i1 + 1] * (ws[i0:i1 + 1] * f0 / 2)[:, None]
        return ' '.join(P(p) for p in np.vstack([l, r[::-1]]))
    def at(s):
        i = min(np.searchsorted(seg, s), len(pts) - 1); return i

    out = []
    # soft shadow
    sh = ' '.join(f'{X(p)+1.8:.2f},{Y(p)+2.4:.2f}' for p in np.vstack([
        pts + nr * (ws / 2)[:, None], (pts - nr * (ws / 2)[:, None])[::-1]]))
    out.append(f'<polygon points="{sh}" fill="#000" fill-opacity="0.32" filter="url(#sh)"/>')
    body = tube(1.0)
    out.append(f'<clipPath id="cb{uid}"><polygon points="{body}"/></clipPath>')
    out.append(f'<polygon points="{body}" fill="{dark(base, 0.45)}"/>')
    out.append(f'<polygon points="{tube(0.84)}" fill="{base}"/>')

    g = [f'<g clip-path="url(#cb{uid})">']
    pat = sp['pat']
    if pat == 'bands':
        cols = sp['bands']; step = 3.2; s = 9.0; k = 0
        while s < total - 1:
            i0, i1 = at(s), at(s + step * (0.55 if cols[k % 4] == '#1f1a1a' else 1.0))
            if i1 > i0:
                g.append(f'<polygon points="{quad(i0, i1, -1.3, 1.3)}" fill="{cols[k % 4]}"/>')
            s += step * (0.55 if cols[k % 4] == '#1f1a1a' else 1.0); k += 1
    elif pat == 'blotch':
        s = 9.0; side = 1
        while s < total - 2:
            i = at(s); w = ws[i]
            ang = math.degrees(math.atan2(tg[i][1], tg[i][0]))
            c = pts[i] + nr[i] * w * 0.12 * side
            rx, ry = max(1.0, w * 0.55), w * 0.42
            edge = sp.get('edge', dark(sp['pc'], 0.4))
            g.append(f'<g transform="translate({X(c):.2f},{Y(c):.2f}) rotate({ang:.0f})">'
                     f'<ellipse rx="{rx+0.45:.2f}" ry="{ry+0.45:.2f}" fill="{edge}"/>'
                     f'<ellipse rx="{rx:.2f}" ry="{ry:.2f}" fill="{sp["pc"]}"/>'
                     f'<ellipse rx="{rx*0.45:.2f}" ry="{ry*0.35:.2f}" fill="{sp["pc2"]}" opacity="0.8"/></g>')
            # small side spots
            for sd in (-1, 1):
                p2 = pts[i] + nr[i] * w * 0.42 * sd + tg[i] * w * 0.55
                g.append(f'<circle cx="{X(p2):.2f}" cy="{Y(p2):.2f}" r="{w*0.11:.2f}" fill="{edge}" opacity="0.7"/>')
            s += max(2.2, w * 1.25); side = -side
    elif pat == 'diamond':
        s = 9.0
        while s < total - 2:
            i = at(s); w = ws[i]
            ang = math.degrees(math.atan2(tg[i][1], tg[i][0]))
            L = max(1.2, w * 0.62); H = w * 0.40
            g.append(f'<g transform="translate({X(pts[i]):.2f},{Y(pts[i]):.2f}) rotate({ang:.0f})">'
                     f'<path d="M{-L},0 L0,{-H} L{L},0 L0,{H}Z" fill="{sp["pc"]}" stroke="{sp["pc2"]}" stroke-width="{max(0.25, w*0.06):.2f}"/>'
                     f'<path d="M{-L*0.4},0 L0,{-H*0.4} L{L*0.4},0 L0,{H*0.4}Z" fill="{mix(base, sp["pc"], 0.35)}"/></g>')
            s += L * 2.0
    elif pat == 'dots':
        s = 8.0
        while s < total - 2:
            i = at(s); w = ws[i]
            p = pts[i] + nr[i] * w * 0.05
            g.append(f'<circle cx="{X(p):.2f}" cy="{Y(p):.2f}" r="{max(0.25, w*0.09):.2f}" fill="{sp["pc"]}" opacity="0.9"/>')
            s += max(1.4, w * 0.55)
        # lighter flank
        g.append(f'<polygon points="{tube(0.35, -0.9)}" fill="{light(base, 0.25)}" opacity="0.35"/>')
    elif pat == 'stripe':
        g.append(f'<polygon points="{quad(0, len(pts)-1, -0.12, 0.12)}" fill="{sp["pc"]}" opacity="0.85"/>')
        g.append(f'<polygon points="{quad(0, len(pts)-1, 0.55, 0.75)}" fill="{dark(base, 0.35)}" opacity="0.6"/>')
        g.append(f'<polygon points="{quad(0, len(pts)-1, -0.75, -0.55)}" fill="{dark(base, 0.35)}" opacity="0.6"/>')
    elif pat == 'net':
        s = 8.0; k = 0
        while s < total - 2:
            i = at(s); w = ws[i]
            ang = math.degrees(math.atan2(tg[i][1], tg[i][0]))
            for sd in ((-0.28, 0.28) if k % 2 else (0.0,)):
                p = pts[i] + nr[i] * w * sd
                g.append(f'<ellipse cx="{X(p):.2f}" cy="{Y(p):.2f}" rx="{w*0.24:.2f}" ry="{w*0.17:.2f}" '
                         f'transform="rotate({ang:.0f} {X(p):.2f} {Y(p):.2f})" fill="none" stroke="{sp["pc"]}" stroke-width="{max(0.3, w*0.08):.2f}" opacity="0.75"/>')
            s += max(1.4, w * 0.42); k += 1
    elif pat == 'bars':
        s = 8.0; k = 0
        while s < total - 1.5:
            i0, i1 = at(s), at(s + 0.9)
            f = 0.85 if k % 2 == 0 else 0.5
            if i1 > i0:
                g.append(f'<polygon points="{quad(i0, i1, -f, f)}" fill="{sp["pc"]}" opacity="0.85"/>')
            s += 2.6; k += 1
    elif pat == 'rings':
        s = 9.0
        while s < total - 1:
            i0, i1 = at(s), at(s + 1.1)
            if i1 > i0:
                g.append(f'<polygon points="{quad(i0, i1, -1.3, 1.3)}" fill="{sp["pc"]}" opacity="0.85"/>')
            s += 4.2

    # scale texture: small arcs pointing to the tail
    s = 4.0; row = 0
    while s < total - 0.8:
        i = at(s); w = ws[i]
        r = max(0.35, w * 0.085)
        n = 5 if w > 4.5 else 3 if w > 2.5 else 1
        lat = np.linspace(-0.62, 0.62, n) if n > 1 else [0.0]
        for f in lat:
            f = f + (0.62 / max(n - 1, 1)) * (row % 2) * 0.5 * (1 if n > 1 else 0)
            if abs(f) > 0.7: continue
            p = pts[i] + nr[i] * w * f * 0.7
            a, b = p - nr[i] * r, p + nr[i] * r
            q = p + tg[i] * r * 1.4
            g.append(f'<path d="M{P(a)} Q{P(q)} {P(b)}" fill="none" stroke="{dark(base, 0.55)}" stroke-width="0.22" opacity="0.45"/>')
        s += r * 1.6; row += 1

    # cylindrical shading: darker shade side, light side + specular
    g.append(f'<polygon points="{tube(0.55, -1.0)}" fill="#000" opacity="0.16"/>')
    g.append(f'<polygon points="{tube(0.42, 0.9)}" fill="#fff" opacity="0.20"/>')
    g.append(f'<polygon points="{tube(0.12, 1.3)}" fill="#fff" opacity="0.40"/>')
    g.append('</g>')
    out.append(''.join(g))
    out.append(f'<polygon points="{body}" fill="none" stroke="{dark(base, 0.6)}" stroke-width="0.45" stroke-linejoin="round"/>')
    out.append(_head(sp, pts, ws, tg, X, Y, uid))
    return ''.join(out)

def _head(sp, pts, ws, tg, X, Y, uid):
    base = sp['base']
    H = pts[0]; fwd = -tg[0]; perp = np.array([-fwd[1], fwd[0]])
    ang = math.degrees(math.atan2(fwd[1], fwd[0]))
    wn = ws[0]; hw = wn * 0.68; L = wn * 1.3
    lx, ly = float(LIGHT @ fwd), float(LIGHT @ perp)
    lside = 1 if ly >= 0 else -1                     # local y side facing the light
    top = '#1f1a1a' if sp['pat'] == 'bands' else base
    hx, hy = X(H), Y(H)
    s = [f'<g transform="translate({hx:.2f},{hy:.2f}) rotate({ang:.1f})">']
    outline = (f'M{-0.4*L:.2f},{-wn/2:.2f} C{0.05*L:.2f},{-wn/2:.2f} {0.2*L:.2f},{-hw:.2f} {0.5*L:.2f},{-hw:.2f} '
               f'C{0.8*L:.2f},{-hw:.2f} {L:.2f},{-hw*0.55:.2f} {L:.2f},0 '
               f'C{L:.2f},{hw*0.55:.2f} {0.8*L:.2f},{hw:.2f} {0.5*L:.2f},{hw:.2f} '
               f'C{0.2*L:.2f},{hw:.2f} {0.05*L:.2f},{wn/2:.2f} {-0.4*L:.2f},{wn/2:.2f}')
    cid = f'hc{uid}'
    # tongue
    s.append(f'<path d="M{L-0.6:.2f},0 l3.4,0 l1.4,-1.2 M{L+2.8:.2f},0 l1.5,1.1" stroke="#c41d2a" stroke-width="0.6" fill="none" stroke-linecap="round"/>')
    # shadow
    s.append(f'<path d="{outline}Z" transform="translate(1.0,1.4)" fill="#000" opacity="0.28" filter="url(#sh)"/>')
    s.append(f'<clipPath id="{cid}"><path d="{outline}Z"/></clipPath>')
    mid = f'hm{uid}'
    s.append(f'<linearGradient id="{mid}g" gradientUnits="userSpaceOnUse" x1="{-0.4*L:.2f}" y1="0" x2="{0.02*L:.2f}" y2="0">'
             f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
             f'<mask id="{mid}" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="{-L:.2f}" y="{-2*hw:.2f}" width="{3*L:.2f}" height="{4*hw:.2f}">'
             f'<rect x="{-L:.2f}" y="{-2*hw:.2f}" width="{3*L:.2f}" height="{4*hw:.2f}" fill="url(#{mid}g)"/></mask>')
    s.append(f'<g mask="url(#{mid})">')
    s.append(f'<path d="{outline}Z" fill="{base}"/>')
    s.append(f'<g clip-path="url(#{cid})">')
    if sp['pat'] == 'bands':          # coral: black snout, yellow collar
        s.append(f'<rect x="{0.1*L:.2f}" y="{-hw*1.2:.2f}" width="{L:.2f}" height="{hw*2.4:.2f}" fill="#1f1a1a"/>')
        s.append(f'<rect x="{-0.4*L:.2f}" y="{-hw*1.2:.2f}" width="{0.32*L:.2f}" height="{hw*2.4:.2f}" fill="#f1c63c"/>')
    if sp['pat'] in ('blotch', 'diamond'):
        s.append(f'<path d="M{-0.3*L:.2f},{-hw*0.42:.2f} L{0.55*L:.2f},0 L{-0.3*L:.2f},{hw*0.42:.2f} L{-0.05*L:.2f},0Z" fill="{sp["pc"]}" opacity="0.85"/>')
    if sp['pat'] == 'stripe':
        s.append(f'<rect x="{-0.4*L:.2f}" y="{-wn*0.06:.2f}" width="{0.75*L:.2f}" height="{wn*0.12:.2f}" fill="{sp["pc"]}" opacity="0.8"/>')
    # shading: shadow side, lit side, specular
    s.append(f'<ellipse cx="{0.35*L:.2f}" cy="{-lside*hw*0.95:.2f}" rx="{L*0.9:.2f}" ry="{hw*0.55:.2f}" fill="#000" opacity="0.22"/>')
    s.append(f'<ellipse cx="{0.45*L:.2f}" cy="{lside*hw*0.3:.2f}" rx="{L*0.5:.2f}" ry="{hw*0.42:.2f}" fill="#fff" opacity="0.18"/>')
    s.append(f'<ellipse cx="{0.5*L:.2f}" cy="{lside*hw*0.32:.2f}" rx="{L*0.22:.2f}" ry="{hw*0.12:.2f}" fill="#fff" opacity="0.45"/>')
    # head plates
    pc = dark(top, 0.5)
    s.append(f'<path d="M{0.15*L:.2f},{-hw*0.38:.2f} Q{0.5*L:.2f},{-hw*0.5:.2f} {0.82*L:.2f},{-hw*0.22:.2f} '
             f'M{0.15*L:.2f},{hw*0.38:.2f} Q{0.5*L:.2f},{hw*0.5:.2f} {0.82*L:.2f},{hw*0.22:.2f} '
             f'M{0.3*L:.2f},0 L{0.7*L:.2f},0" stroke="{pc}" stroke-width="0.25" fill="none" opacity="0.5"/>')
    s.append('</g></g>')
    s.append(f'<path d="{outline}" fill="none" stroke="{dark(base, 0.6)}" stroke-width="0.45" stroke-linejoin="round"/>')
    # eyes: big and friendly, sitting on the sides of the head
    er = hw * 0.34
    for sy in (-1, 1):
        ex, ey = L * 0.56, sy * hw * 0.66
        s.append(f'<ellipse cx="{ex:.2f}" cy="{ey + sy*er*0.15:.2f}" rx="{er*1.2:.2f}" ry="{er*1.05:.2f}" fill="{dark(top, 0.5)}" opacity="0.6"/>')
        s.append(f'<circle cx="{ex:.2f}" cy="{ey:.2f}" r="{er:.2f}" fill="#fffdf2" stroke="{dark(top, 0.65)}" stroke-width="0.3"/>')
        s.append(f'<circle cx="{ex + er*0.2:.2f}" cy="{ey:.2f}" r="{er*0.72:.2f}" fill="#c99a2a"/>')
        s.append(f'<circle cx="{ex + er*0.25:.2f}" cy="{ey:.2f}" r="{er*0.5:.2f}" fill="#111"/>')
        s.append(f'<circle cx="{ex + er*0.45:.2f}" cy="{ey - er*0.3:.2f}" r="{er*0.2:.2f}" fill="#fff"/>')
    for sy in (-1, 1):
        s.append(f'<ellipse cx="{L*0.9:.2f}" cy="{sy*hw*0.24:.2f}" rx="0.38" ry="0.24" fill="{dark(top, 0.75)}"/>')
    s.append('</g>')
    return ''.join(s)

# ------------------------------------------------------------------ ladders
WOOD = dict(base='#b27a3e', dark='#5a3714', light='#e6b77a', grain='#6e4519')

def ladder(B, T, X, Y, CELL, uid):
    B = np.array(B) * CELL; T = np.array(T) * CELL
    d = T - B; Lm = np.linalg.norm(d); u = d / Lm; nr = np.array([-u[1], u[0]])
    half = 0.215 * CELL
    B2, T2 = B - u * 5.0, T + u * 5.0
    lshift = -(np.array([u[0], u[1]]) @ LIGHT) * 0  # rails run along u; light offset across
    across = nr * (0.45 * np.sign(nr @ LIGHT))       # highlight towards the light
    def P(p): return f'{X(p):.2f},{Y(p):.2f}'
    def line(a, b, col, w, op=1, extra=''):
        return (f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(b):.2f}" y2="{Y(b):.2f}" stroke="{col}" '
                f'stroke-width="{w}" stroke-linecap="round" opacity="{op}" {extra}/>')
    s = []
    # shadow
    for k in (-1, 1):
        a, b = B2 + nr * half * k + np.array([1.6, 2.2]), T2 + nr * half * k + np.array([1.6, 2.2])
        s.append(line(a, b, '#000', 3.0, 0.32, 'filter="url(#sh)"'))
    nrung = max(2, int(Lm / 8.5))
    rungs = [B + d * ((i + 0.5) / nrung) for i in range(nrung)]
    for p in rungs:
        a, b = p + nr * (half + 0.9), p - nr * (half + 0.9)
        s.append(line(a + np.array([1.4, 1.9]), b + np.array([1.4, 1.9]), '#000', 2.2, 0.25, 'filter="url(#sh)"'))
    # rungs: cylinder-like (dark rim, body, highlight)
    for p in rungs:
        a, b = p + nr * (half + 0.9), p - nr * (half + 0.9)
        s.append(line(a, b, WOOD['dark'], 2.3))
        s.append(line(a, b, WOOD['base'], 1.7))
        hu = u * 0.35 * np.sign(u @ -LIGHT if (u @ -LIGHT) != 0 else 1)
        s.append(line(a + hu, b + hu, WOOD['light'], 0.55, 0.85))
    # rails
    for k in (-1, 1):
        a, b = B2 + nr * half * k, T2 + nr * half * k
        s.append(line(a, b, WOOD['dark'], 3.1))
        s.append(line(a, b, WOOD['base'], 2.45))
        s.append(line(a - across * 1.2, b - across * 1.2, WOOD['dark'], 0.7, 0.35))
        s.append(line(a + across, b + across, WOOD['light'], 0.75, 0.9))
        # wood grain
        s.append(line(a + across * 0.3, b + across * 0.3, WOOD['grain'], 0.18, 0.55,
                      f'stroke-dasharray="{6+uid%5} 2.5 {11+uid%7} 1.8" stroke-dashoffset="{uid*3}"'))
        s.append(line(a - across * 0.5, b - across * 0.5, WOOD['grain'], 0.15, 0.45,
                      f'stroke-dasharray="{9+uid%4} 3 5 2" stroke-dashoffset="{uid*7}"'))
    # nails at the joints
    for p in rungs:
        for k in (-1, 1):
            c = p + nr * half * k
            s.append(f'<circle cx="{X(c):.2f}" cy="{Y(c):.2f}" r="0.55" fill="#6d6d6d"/>'
                     f'<circle cx="{X(c)-0.15:.2f}" cy="{Y(c)-0.15:.2f}" r="0.22" fill="#d8d8d8"/>')
    return ''.join(s)

# ------------------------------------------------------------------ START sign
def start_sign(x0, y0, cell):
    """Wooden arrow sign stuck into the ground, inside square 1."""
    cx = x0 + cell * 0.5
    s = ['<g>']
    # ground mound + grass
    s.append(f'<ellipse cx="{cx:.2f}" cy="{y0+cell-2.2:.2f}" rx="7" ry="2" fill="#000" opacity="0.25" filter="url(#sh)"/>')
    s.append(f'<ellipse cx="{cx:.2f}" cy="{y0+cell-2.6:.2f}" rx="5.5" ry="1.7" fill="#6b4a2a"/>')
    s.append(f'<ellipse cx="{cx-0.8:.2f}" cy="{y0+cell-3.0:.2f}" rx="3.5" ry="0.8" fill="#8a6338"/>')
    # post
    px = cx - 1.3
    s.append(f'<rect x="{px+0.9:.2f}" y="{y0+13:.2f}" width="2.6" height="{cell-15.5:.2f}" fill="#000" opacity="0.25" filter="url(#sh)"/>')
    s.append(f'<rect x="{px:.2f}" y="{y0+12.5:.2f}" width="2.6" height="{cell-15.2:.2f}" fill="url(#woodV)" stroke="#4a2c10" stroke-width="0.3"/>')
    s.append(f'<line x1="{px+0.9:.2f}" y1="{y0+14:.2f}" x2="{px+0.9:.2f}" y2="{y0+cell-3.5:.2f}" stroke="#5a3714" stroke-width="0.15" stroke-dasharray="3 1.5 6 1"/>')
    # grass blades in front of the post
    for i, (gx, h, a) in enumerate([(-5, 3.0, -18), (-3.6, 4.0, -8), (-2.2, 2.6, 10), (1.6, 3.6, -6), (3.0, 4.2, 12), (4.6, 2.8, 22), (0.2, 2.2, 4)]):
        bx, by = cx + gx, y0 + cell - 2.3
        tx = bx + h * math.sin(math.radians(a)); ty = by - h
        s.append(f'<path d="M{bx-0.45:.2f},{by:.2f} Q{bx:.2f},{by-h*0.6:.2f} {tx:.2f},{ty:.2f} Q{bx+0.2:.2f},{by-h*0.5:.2f} {bx+0.45:.2f},{by:.2f}Z" fill="{["#4f8f2f","#6aab3c","#3f7a26"][i%3]}"/>')
    # arrow-shaped plank pointing right (direction of play), slightly tilted
    plank = 'M-10.5,-4.2 L6.2,-4.2 L10.6,0 L6.2,4.2 L-10.5,4.2 Z'
    s.append(f'<g transform="translate({cx:.2f},{y0+15.2:.2f}) rotate(-4)">')
    s.append(f'<path d="{plank}" transform="translate(1.1,1.5)" fill="#000" opacity="0.35" filter="url(#sh)"/>')
    s.append(f'<path d="{plank}" fill="url(#woodH)" stroke="#4a2c10" stroke-width="0.45" stroke-linejoin="round"/>')
    for gy, da in ((-2.6, '7 1.5 4 2'), (-0.9, '5 2 9 1'), (1.1, '10 1.5 3 2'), (2.8, '4 2 7 1.5')):
        s.append(f'<line x1="-10" y1="{gy}" x2="{8.5 - abs(gy):.1f}" y2="{gy}" stroke="#6e4519" stroke-width="0.17" stroke-dasharray="{da}" opacity="0.7"/>')
    s.append('<path d="M-10.3,-4 L6.1,-4" stroke="#f0c98e" stroke-width="0.4" opacity="0.7"/>')
    # carved letters: light lower edge + dark letter
    s.append('<text x="-1.6" y="2.05" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="5.3" fill="#f3d3a0" opacity="0.8">START</text>')
    s.append('<text x="-1.75" y="1.8" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="5.3" fill="#3d220b">START</text>')
    for nx, ny in ((-9.2, -2.9), (-9.2, 2.9), (5.0, -2.9), (5.0, 2.9)):
        s.append(f'<circle cx="{nx}" cy="{ny}" r="0.45" fill="#555"/><circle cx="{nx-0.12}" cy="{ny-0.12}" r="0.17" fill="#ddd"/>')
    s.append('</g></g>')
    return ''.join(s)

# ------------------------------------------------------------------ trophy
def trophy(x0, y0, cell):
    """Polished gold cup on a dark wooden plinth, inside square 300."""
    s = [f'<g transform="translate({x0 + cell*0.62:.2f},{y0 + 9.6:.2f}) scale(0.98)">']
    # glow
    s.append('<ellipse cx="0" cy="7" rx="11" ry="10" fill="url(#glow)"/>')
    # shadow
    s.append('<ellipse cx="1.4" cy="18.4" rx="7.5" ry="1.4" fill="#000" opacity="0.35" filter="url(#sh)"/>')
    # handles (behind the cup)
    for sx in (-1, 1):
        s.append(f'<path d="M{5.4*sx},1.4 C{9.8*sx},0.6 {10.2*sx},6.6 {3.4*sx},7.6" fill="none" stroke="#7a5205" stroke-width="1.6" stroke-linecap="round"/>')
        s.append(f'<path d="M{5.4*sx},1.4 C{9.8*sx},0.6 {10.2*sx},6.6 {3.4*sx},7.6" fill="none" stroke="url(#goldH)" stroke-width="1.05" stroke-linecap="round"/>')
    # cup body
    cup = 'M-6.2,0.4 L6.2,0.4 C6.2,5.6 4.2,8.6 0,9.4 C-4.2,8.6 -6.2,5.6 -6.2,0.4Z'
    s.append(f'<path d="{cup}" fill="url(#goldH)" stroke="#6b4704" stroke-width="0.35"/>')
    s.append('<path d="M-3.9,1.6 C-4.1,4.8 -2.8,7.0 -1.4,7.9" fill="none" stroke="#fffbe0" stroke-width="0.7" opacity="0.75" stroke-linecap="round"/>')
    # star emblem
    pts = []
    for i in range(10):
        r = 2.0 if i % 2 == 0 else 0.85; a = -math.pi / 2 + i * math.pi / 5
        pts.append(f'{r*math.cos(a):.2f},{4.0 + r*math.sin(a):.2f}')
    s.append(f'<polygon points="{" ".join(pts)}" fill="#fff4b8" stroke="#a87808" stroke-width="0.25"/>')
    # rim
    s.append('<ellipse cx="0" cy="0.4" rx="6.2" ry="1.25" fill="url(#goldIn)" stroke="#6b4704" stroke-width="0.3"/>')
    # stem + knob
    s.append('<path d="M-1.0,9.2 L1.0,9.2 L0.7,12.6 L-0.7,12.6Z" fill="url(#goldH)" stroke="#6b4704" stroke-width="0.25"/>')
    s.append('<ellipse cx="0" cy="10.6" rx="1.7" ry="0.75" fill="url(#goldH)" stroke="#6b4704" stroke-width="0.25"/>')
    s.append('<path d="M-3.6,12.5 L3.6,12.5 L4.6,14.3 L-4.6,14.3Z" fill="url(#goldH)" stroke="#6b4704" stroke-width="0.3"/>')
    # plinth
    s.append('<rect x="-5.6" y="14.2" width="11.2" height="4.0" rx="0.5" fill="url(#plinth)" stroke="#1d130b" stroke-width="0.3"/>')
    s.append('<rect x="-3.1" y="15.3" width="6.2" height="1.8" rx="0.3" fill="url(#goldH)" stroke="#6b4704" stroke-width="0.2"/>')
    # sparkles
    for sx, sy, r in ((-7.5, -1.8, 1.5), (7.8, 2.2, 1.1), (4.6, -2.6, 0.9)):
        s.append(f'<path d="M{sx},{sy-r} L{sx+0.25*r},{sy-0.25*r} L{sx+r},{sy} L{sx+0.25*r},{sy+0.25*r} L{sx},{sy+r} '
                 f'L{sx-0.25*r},{sy+0.25*r} L{sx-r},{sy} L{sx-0.25*r},{sy-0.25*r}Z" fill="#fffbe6"/>')
    s.append('</g>')
    return ''.join(s)

DEFS = '''
<linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#7a5205"/><stop offset="0.15" stop-color="#c9961c"/><stop offset="0.33" stop-color="#fff1a8"/>
 <stop offset="0.5" stop-color="#e8b934"/><stop offset="0.75" stop-color="#a8770f"/><stop offset="0.9" stop-color="#f6d76b"/>
 <stop offset="1" stop-color="#8a5e08"/></linearGradient>
<radialGradient id="goldIn" cx="50%" cy="60%" r="60%"><stop offset="0" stop-color="#6b4704"/><stop offset="1" stop-color="#e8b934"/></radialGradient>
<linearGradient id="plinth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3d26"/><stop offset="1" stop-color="#2a1b10"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#fff6c2" stop-opacity="0.8"/><stop offset="1" stop-color="#fff6c2" stop-opacity="0"/></radialGradient>
<linearGradient id="woodH" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9a361"/><stop offset="0.5" stop-color="#b27a3e"/><stop offset="1" stop-color="#8a5a2a"/></linearGradient>
<linearGradient id="woodV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7a4f24"/><stop offset="0.4" stop-color="#c58c4c"/><stop offset="1" stop-color="#6a4320"/></linearGradient>
'''

# ------------------------------------------------------------------ golden (championship) ladder
def golden_ladder(B, T, X, Y, CELL, uid=0, to_finish=False):
    B = np.array(B) * CELL; T = np.array(T) * CELL
    d = T - B; Lm = np.linalg.norm(d); u = d / Lm; nr = np.array([-u[1], u[0]])
    half = 0.24 * CELL
    B2, T2 = B - u * 5.5, (T - u * 6.5 if to_finish else T + u * 4.0)
    across = nr * (0.5 * np.sign(nr @ LIGHT))
    def line(a, b, col, w, op=1, extra=''):
        return (f'<line x1="{X(a):.2f}" y1="{Y(a):.2f}" x2="{X(b):.2f}" y2="{Y(b):.2f}" stroke="{col}" '
                f'stroke-width="{w}" stroke-linecap="round" opacity="{op}" {extra}/>')
    s = []
    # royal glow
    for k in (-1, 0, 1):
        a, b = B2 + nr * half * k, T2 + nr * half * k
        s.append(line(a, b, '#ffe9a0', 9 if k == 0 else 6, 0.35, 'filter="url(#glowblur)"'))
    for k in (-1, 1):
        a, b = B2 + nr * half * k + np.array([1.8, 2.4]), T2 + nr * half * k + np.array([1.8, 2.4])
        s.append(line(a, b, '#000', 3.6, 0.35, 'filter="url(#sh)"'))
    nrung = max(3, int(Lm / 8.0))
    rungs = [B + d * ((i + 0.5) / nrung) for i in range(nrung)]
    # rungs: red velvet wrapped in gold
    for p in rungs:
        a, b = p + nr * (half + 0.9), p - nr * (half + 0.9)
        s.append(line(a, b, '#6b4704', 2.8))
        s.append(line(a, b, '#d9a521', 2.2))
        s.append(line(a + u * 0.35, b + u * 0.35, '#fff3b0', 0.6, 0.9))
        c = p
        s.append(f'<circle cx="{X(c):.2f}" cy="{Y(c):.2f}" r="1.25" fill="#b0122a" stroke="#6b4704" stroke-width="0.35"/>'
                 f'<circle cx="{X(c)-0.35:.2f}" cy="{Y(c)-0.35:.2f}" r="0.4" fill="#ffb3c0"/>')
    # rails
    for k in (-1, 1):
        a, b = B2 + nr * half * k, T2 + nr * half * k
        s.append(line(a, b, '#5a3a02', 3.8))
        s.append(line(a, b, '#c9961c', 3.1))
        s.append(line(a - across * 1.3, b - across * 1.3, '#7a5205', 0.9, 0.6))
        s.append(line(a + across * 0.9, b + across * 0.9, '#fff1a8', 1.0, 0.95))
        s.append(line(a + across * 1.2, b + across * 1.2, '#ffffff', 0.35, 0.8))
        # end caps: gold spheres
        for e in (a, b):
            s.append(f'<circle cx="{X(e):.2f}" cy="{Y(e):.2f}" r="2.3" fill="url(#goldBall)" stroke="#5a3a02" stroke-width="0.35"/>')
    if to_finish:
        return ''.join(s)
    # small crown at the top
    c = T2 + u * 2.0 + np.array([0, -3.2])
    ang = 0
    s.append(f'<g transform="translate({X(c):.2f},{Y(c):.2f}) rotate({ang:.1f})">'
             '<path d="M-4,1.8 L-4.6,-2.6 L-2,-0.4 L0,-3.4 L2,-0.4 L4.6,-2.6 L4,1.8Z" fill="url(#goldH)" stroke="#5a3a02" stroke-width="0.35"/>'
             '<rect x="-4" y="1.2" width="8" height="1.3" fill="url(#goldH)" stroke="#5a3a02" stroke-width="0.3"/>'
             '<circle cx="0" cy="-3.4" r="0.6" fill="#b0122a"/><circle cx="-4.6" cy="-2.6" r="0.5" fill="#1f5fd1"/>'
             '<circle cx="4.6" cy="-2.6" r="0.5" fill="#1f5fd1"/><circle cx="0" cy="0.6" r="0.6" fill="#1aa35a"/></g>')
    return ''.join(s)

# ------------------------------------------------------------------ action squares
ACTION_STYLE = {
    'turbo': ('#ff8a1f', '#c2410c', 'TURBO'),
    'block': ('#e5484d', '#8f1d22', 'BLOCK'),
    'hitch': ('#21b6a8', '#0d6b63', 'HITCHHIKE'),
    'drain': ('#21b6a8', '#0d6b63', 'ENERGY DRAIN'),
    'swap':  ('#8b5cf6', '#4c2a9e', 'SWAP'),
}

def action_icon(kind, x0, y0, cell):
    c1, c2, label = ACTION_STYLE[kind]
    cx, cy, R = x0 + cell * 0.56, y0 + cell * 0.6, 9.2
    s = [f'<g transform="translate({cx:.2f},{cy:.2f})">']
    s.append(f'<radialGradient id="ag_{kind}" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="{light(c1, 0.35)}"/>'
             f'<stop offset="0.6" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>')
    s.append(f'<circle cx="1.0" cy="1.4" r="{R}" fill="#000" opacity="0.35" filter="url(#sh)"/>')
    s.append(f'<circle r="{R}" fill="url(#goldH)"/>')
    s.append(f'<circle r="{R-1.1}" fill="url(#ag_{kind})" stroke="#5a3a02" stroke-width="0.3"/>')
    s.append(f'<path d="M{-R*0.62:.2f},{-R*0.45:.2f} A{R*0.8:.2f},{R*0.8:.2f} 0 0 1 {R*0.55:.2f},{-R*0.55:.2f}" fill="none" stroke="#fff" stroke-width="1" opacity="0.35" stroke-linecap="round"/>')
    W = '#ffffff'
    if kind == 'turbo':      # lightning bolt
        s.append('<path d="M1.2,-6.6 L-3.8,0.4 L-0.4,0.4 L-1.6,5.2 L3.8,-1.8 L0.4,-1.8 Z" fill="#fff6c2" stroke="#7a2e05" stroke-width="0.45" stroke-linejoin="round" transform="translate(0,-0.9)"/>')
    elif kind == 'block':    # striped barrier on two posts
        s.append('<rect x="-5.2" y="-1.2" width="1.3" height="5.4" fill="#ddd" stroke="#333" stroke-width="0.3"/>'
                 '<rect x="3.9" y="-1.2" width="1.3" height="5.4" fill="#ddd" stroke="#333" stroke-width="0.3"/>'
                 '<rect x="-6.4" y="-4.6" width="12.8" height="3.6" rx="0.5" fill="#fff" stroke="#333" stroke-width="0.35"/>'
                 '<clipPath id="bclip"><rect x="-6.4" y="-4.6" width="12.8" height="3.6" rx="0.5"/></clipPath>'
                 '<g clip-path="url(#bclip)">' + ''.join(
                     f'<path d="M{x},-4.6 l2,0 l-3.6,3.6 l-2,0Z" fill="#d1242b"/>' for x in (-5.6, -2.2, 1.2, 4.6, 8.0)) + '</g>')
    elif kind in ('hitch', 'drain'):    # placeholder icon until the new artwork arrives
        s.append('<path d="M-3.6,-0.6 h2.0 v6 h-2.0z" fill="#fff" stroke="#0b4a45" stroke-width="0.4"/>'
                 '<path d="M-1.2,-0.6 L0.6,-3.2 C1.0,-5.6 0.9,-6.8 2.0,-6.8 C3.4,-6.8 3.3,-4.6 2.6,-2.4 L5.2,-2.4 '
                 'C6.4,-2.4 6.6,-1.0 5.8,-0.6 C6.6,-0.2 6.4,1.0 5.6,1.2 C6.3,1.6 6.0,2.8 5.2,2.9 C5.7,3.4 5.3,4.6 4.4,4.6 '
                 'L-1.2,4.6 Z" fill="#fff" stroke="#0b4a45" stroke-width="0.45" stroke-linejoin="round" transform="translate(-0.6,-0.9)"/>')
    elif kind == 'swap':     # two curved arrows
        s.append('<path d="M-4.6,-1.4 A4.8,4.8 0 0 1 3.6,-3.6" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" transform="translate(0,-0.6)"/>'
                 '<path d="M3.6,-3.6 l0.6,-2.6 l1.6,3.2 z" fill="#fff" transform="translate(0,-0.6) rotate(18 3.6 -3.6)"/>'
                 '<path d="M4.6,1.4 A4.8,4.8 0 0 1 -3.6,3.6" fill="none" stroke="#fff" stroke-width="1.4" stroke-linecap="round" transform="translate(0,-0.6)"/>'
                 '<path d="M-3.6,3.6 l-0.6,2.6 l-1.6,-3.2 z" fill="#fff" transform="translate(0,-0.6) rotate(18 -3.6 3.6)"/>')
    fs = 2.15 if len(label) > 6 else 2.6
    s.append(f'<text x="0" y="{R-2.4:.2f}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" font-size="{fs}" '
             f'fill="#fff" stroke="{c2}" stroke-width="0.5" paint-order="stroke" letter-spacing="0.1">{label}</text>')
    s.append('</g>')
    return ''.join(s)

DEFS2 = '''
<filter id="glowblur" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>
<radialGradient id="goldBall" cx="35%" cy="35%" r="65%"><stop offset="0" stop-color="#fffbe0"/><stop offset="0.5" stop-color="#e8b934"/><stop offset="1" stop-color="#7a5205"/></radialGradient>
'''

# ------------------------------------------------------------------ artwork from images (assets/icons)
import os as _os, io as _io, base64 as _b64
_ICON_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'assets', 'icons')
_cache = {}

def icon_uri(name, px=720):
    """Return (data-uri, aspect w/h) for assets/icons/<name>.png cropped to its visible area, or None."""
    if name in _cache: return _cache[name]
    p = _os.path.join(_ICON_DIR, f'{name}.png')
    if not _os.path.exists(p):
        _cache[name] = None; return None
    from PIL import Image
    im = Image.open(p).convert('RGBA')
    bbox = im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    im = im.crop(bbox)
    s = px / max(im.size); im = im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS)
    buf = _io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    uri = 'data:image/png;base64,' + _b64.b64encode(buf.getvalue()).decode()
    W, H = im.size
    _symbols[name] = f'<symbol id="ic_{name}" viewBox="0 0 {W} {H}"><image width="{W}" height="{H}" href="{uri}"/></symbol>'
    _cache[name] = (name, W / H)
    return _cache[name]

_symbols = {}
def icon_defs():
    """Each artwork is embedded once; squares reference it with <use>."""
    return '\n'.join(f'<defs>{v}</defs>' for v in _symbols.values())

def _img(name, x, y, w, h):
    return f'<use href="#ic_{name}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>'

LABELS = {'turbo': 'TURBO', 'block': 'BLOCK', 'drain': 'ENERGY DRAIN', 'hitch': 'ENERGY DRAIN', 'swap': 'SWAP'}

def action_icon_img(kind, x0, y0, cell):
    art = icon_uri('drain' if kind == 'hitch' else kind)
    if art is None:
        return action_icon(kind, x0, y0, cell)
    uri, asp = art
    c1, c2, _ = ACTION_STYLE.get(kind, ACTION_STYLE['drain'])
    D = 21.0
    cx, cy = x0 + cell * 0.57, y0 + cell * 0.6
    s = [f'<circle cx="{cx+1.0:.2f}" cy="{cy+1.5:.2f}" r="{D/2-0.3:.2f}" fill="#000" opacity="0.38" filter="url(#sh)"/>']
    s.append(_img(uri, cx - D / 2, cy - D / 2, D, D / asp))
    label = LABELS[kind]
    fs = 2.0 if len(label) > 6 else 2.35
    bw = 1.6 + len(label) * fs * 0.66
    by = cy + D / 2 - 2.6
    s.append(f'<rect x="{cx-bw/2:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{fs+1.4:.2f}" rx="{(fs+1.4)/2:.2f}" '
             f'fill="{c2}" stroke="#e8b934" stroke-width="0.45"/>')
    s.append(f'<text x="{cx:.2f}" y="{by+fs+0.35:.2f}" text-anchor="middle" font-family="DejaVu Sans" font-weight="bold" '
             f'font-size="{fs}" fill="#fff" letter-spacing="0.08">{label}</text>')
    return ''.join(s)

def start_sign_img(x0, y0, cell):
    art = icon_uri('start')
    if art is None: return start_sign(x0, y0, cell)
    uri, asp = art
    h = 23.5; w = h * asp
    if w > 26: w = 26; h = w / asp
    x = x0 + cell - w - 0.6; y = y0 + cell - h - 0.4
    return (f'<ellipse cx="{x+w*0.48:.2f}" cy="{y+h-0.6:.2f}" rx="{w*0.32:.2f}" ry="1.1" fill="#000" opacity="0.35" filter="url(#sh)"/>'
            + _img(uri, x, y, w, h))

def trophy_img(x0, y0, cell):
    art = icon_uri('trophy')
    if art is None: return trophy(x0, y0, cell)
    uri, asp = art
    h = 23.0; w = h * asp
    x = x0 + cell - w - 0.5; y = y0 + cell - h - 0.5
    return (f'<ellipse cx="{x+w/2:.2f}" cy="{y0+cell*0.5:.2f}" rx="{w*0.75:.2f}" ry="{h*0.6:.2f}" fill="url(#glow)"/>'
            f'<ellipse cx="{x+w/2+0.8:.2f}" cy="{y+h-0.5:.2f}" rx="{w*0.36:.2f}" ry="1.1" fill="#000" opacity="0.35" filter="url(#sh)"/>'
            + _img(uri, x, y, w, h))
