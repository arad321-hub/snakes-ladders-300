"""Procedural 'worlds' background: every 3 rows is a different world, blended into the next.

Bottom -> top: meadow, desert, jungle, arctic, space.
All art is vector (SVG) so it prints sharp at any size.
"""
import math, random

def _hills(rnd, x0, w, ybase, amp, n, fill, opacity=1.0):
    pts = [f"M{x0},{ybase + amp * 3}"]
    step = w / n
    y = ybase
    pts.append(f"L{x0},{y:.1f}")
    for i in range(n):
        x1 = x0 + step * (i + 0.5); y1 = ybase - amp * rnd.uniform(0.3, 1.0)
        x2 = x0 + step * (i + 1); y2 = ybase + amp * rnd.uniform(-0.3, 0.3)
        pts.append(f"Q{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}")
    pts.append(f"L{x0 + w},{ybase + amp * 3} Z")
    return f'<path d="{" ".join(pts)}" fill="{fill}" opacity="{opacity}"/>'

def meadow(rnd, x, y, w, h):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g_meadow)"/>']
    for k, (col, op) in enumerate([("#b7e08f", 1), ("#9fd47a", 1), ("#86c765", 1)]):
        s.append(_hills(rnd, x, w, y + h * (0.25 + 0.27 * k), 6, 7, col, op))
    # flowers
    for _ in range(150):
        fx, fy = rnd.uniform(x, x + w), rnd.uniform(y + 4, y + h - 2)
        col = rnd.choice(["#ffffff", "#ffe066", "#ff8fab", "#c39bff", "#ff6b6b"])
        r = rnd.uniform(0.7, 1.4)
        s.append(f'<g opacity="0.85">' + ''.join(
            f'<circle cx="{fx + r*math.cos(a):.1f}" cy="{fy + r*math.sin(a):.1f}" r="{r*0.7:.2f}" fill="{col}"/>'
            for a in [i * 2 * math.pi / 5 for i in range(5)]) +
            f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r*0.5:.2f}" fill="#f4a51c"/></g>')
    # grass tufts
    for _ in range(220):
        gx, gy = rnd.uniform(x, x + w), rnd.uniform(y + 3, y + h)
        s.append(f'<path d="M{gx:.1f},{gy:.1f} l-1,-2.6 M{gx:.1f},{gy:.1f} l0.2,-3.2 M{gx:.1f},{gy:.1f} l1.2,-2.4" '
                 f'stroke="#5fa64a" stroke-width="0.45" stroke-linecap="round" opacity="0.6"/>')
    # butterflies
    for _ in range(8):
        bx, by = rnd.uniform(x, x + w), rnd.uniform(y + 6, y + h - 6)
        col = rnd.choice(["#ff9f1c", "#5bc0eb", "#f15bb5"])
        s.append(f'<g transform="translate({bx:.1f},{by:.1f}) rotate({rnd.uniform(-30,30):.0f})" opacity="0.8">'
                 f'<ellipse cx="-1.5" cy="-1" rx="1.6" ry="1.2" fill="{col}"/><ellipse cx="1.5" cy="-1" rx="1.6" ry="1.2" fill="{col}"/>'
                 f'<ellipse cx="-1.1" cy="0.9" rx="1.1" ry="0.9" fill="{col}"/><ellipse cx="1.1" cy="0.9" rx="1.1" ry="0.9" fill="{col}"/>'
                 f'<rect x="-0.25" y="-1.8" width="0.5" height="3.6" rx="0.25" fill="#333"/></g>')
    return ''.join(s)

def desert(rnd, x, y, w, h):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g_desert)"/>']
    # sun
    s.append(f'<circle cx="{x + w*0.83}" cy="{y + 14}" r="13" fill="#fff3c4" opacity="0.55"/>'
             f'<circle cx="{x + w*0.83}" cy="{y + 14}" r="8" fill="#ffe08a" opacity="0.8"/>')
    for k, col in enumerate(["#f4d79a", "#efc77f", "#e8b866", "#e1aa55"]):
        s.append(_hills(rnd, x, w, y + h * (0.22 + 0.22 * k), 5, 5, col))
    # dune ripples
    for _ in range(70):
        rx, ry = rnd.uniform(x, x + w), rnd.uniform(y + 8, y + h - 3)
        s.append(f'<path d="M{rx:.1f},{ry:.1f} q4,-1.4 8,0" fill="none" stroke="#c98f3c" stroke-width="0.4" opacity="0.45"/>')
    # cacti
    for _ in range(16):
        cx, cy = rnd.uniform(x + 5, x + w - 5), rnd.uniform(y + 18, y + h - 4)
        sc = rnd.uniform(0.7, 1.2)
        s.append(f'<g transform="translate({cx:.1f},{cy:.1f}) scale({sc:.2f})" opacity="0.85">'
                 '<rect x="-1.6" y="-11" width="3.2" height="11" rx="1.6" fill="#5c9e4f"/>'
                 '<path d="M-1.6,-5 h-2.2 a1.2,1.2 0 0 1 -1.2,-1.2 v-3" stroke="#5c9e4f" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
                 '<path d="M1.6,-6.5 h2 a1.2,1.2 0 0 0 1.2,-1.2 v-2" stroke="#5c9e4f" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
                 '<line x1="0" y1="-10" x2="0" y2="-1" stroke="#3f7a36" stroke-width="0.35"/>'
                 '<ellipse cx="0" cy="0" rx="4" ry="0.8" fill="#b9853d" opacity="0.5"/></g>')
    # stones
    for _ in range(30):
        sx, sy = rnd.uniform(x, x + w), rnd.uniform(y + 10, y + h)
        s.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{rnd.uniform(0.8,2):.1f}" ry="{rnd.uniform(0.5,1.1):.1f}" fill="#b5844a" opacity="0.6"/>')
    return ''.join(s)

def jungle(rnd, x, y, w, h):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g_jungle)"/>']
    leafcols = ["#1f6b45", "#2f8a52", "#5cbf6a", "#17573a", "#7fd37a", "#3fa060"]
    # big leaves
    for _ in range(230):
        lx, ly = rnd.uniform(x - 5, x + w + 5), rnd.uniform(y, y + h)
        ang = rnd.uniform(0, 360); L = rnd.uniform(5, 11); W = L * rnd.uniform(0.32, 0.45)
        col = rnd.choice(leafcols)
        s.append(f'<g transform="translate({lx:.1f},{ly:.1f}) rotate({ang:.0f})" opacity="{rnd.uniform(0.55,0.9):.2f}">'
                 f'<path d="M0,0 Q{L*0.5:.1f},{-W:.1f} {L:.1f},0 Q{L*0.5:.1f},{W:.1f} 0,0Z" fill="{col}"/>'
                 f'<line x1="0" y1="0" x2="{L*0.95:.1f}" y2="0" stroke="#2f6d2f" stroke-width="0.3" opacity="0.7"/></g>')
    # monstera-like leaves
    for _ in range(14):
        mx, my = rnd.uniform(x, x + w), rnd.uniform(y + 5, y + h - 5)
        r = rnd.uniform(5, 8)
        s.append(f'<g transform="translate({mx:.1f},{my:.1f}) rotate({rnd.uniform(0,360):.0f})" opacity="0.55">'
                 f'<circle r="{r:.1f}" fill="#185c3c"/>' +
                 ''.join(f'<path d="M0,0 L{r*1.1*math.cos(a):.1f},{r*1.1*math.sin(a):.1f}" stroke="url(#g_jungle_mid)" stroke-width="{r*0.16:.2f}"/>'
                         for a in [i * 2 * math.pi / 7 for i in range(7)]) + '</g>')
    # hanging vines
    for _ in range(18):
        vx = rnd.uniform(x, x + w); vl = rnd.uniform(14, 30)
        s.append(f'<path d="M{vx:.1f},{y-2} q3,{vl/2:.1f} 0,{vl:.1f}" fill="none" stroke="#2f6d2f" stroke-width="0.7" opacity="0.55"/>')
        for t in range(3, int(vl), 4):
            s.append(f'<ellipse cx="{vx + 1.2:.1f}" cy="{y - 2 + t:.1f}" rx="1.4" ry="0.7" fill="#5fae54" opacity="0.7"/>')
    # tropical flowers
    for _ in range(18):
        fx, fy = rnd.uniform(x, x + w), rnd.uniform(y + 4, y + h - 4)
        col = rnd.choice(["#ff5d73", "#ff9f1c", "#f15bb5"])
        s.append(''.join(f'<ellipse cx="{fx + 1.4*math.cos(a):.1f}" cy="{fy + 1.4*math.sin(a):.1f}" rx="1.4" ry="0.8" '
                         f'transform="rotate({math.degrees(a):.0f} {fx + 1.4*math.cos(a):.1f} {fy + 1.4*math.sin(a):.1f})" fill="{col}" opacity="0.85"/>'
                         for a in [i * 2 * math.pi / 5 for i in range(5)]) +
                 f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="0.7" fill="#ffe066"/>')
    return ''.join(s)

def arctic(rnd, x, y, w, h):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g_arctic)"/>']
    # aurora ribbon
    s.append(f'<path d="M{x},{y+10} C{x+w*0.25},{y-2} {x+w*0.45},{y+22} {x+w*0.7},{y+8} S{x+w*0.95},{y+4} {x+w},{y+12}" '
             f'fill="none" stroke="#9ff5d0" stroke-width="7" opacity="0.35"/>')
    # mountains
    peaks = []
    px = x - 10
    while px < x + w + 10:
        pw = rnd.uniform(30, 55); ph = rnd.uniform(22, 40)
        peaks.append((px, pw, ph)); px += pw * 0.7
    for px, pw, ph in peaks:
        base = y + h * 0.62
        tx, ty = px + pw / 2, base - ph
        s.append(f'<path d="M{px:.1f},{base:.1f} L{tx:.1f},{ty:.1f} L{px+pw:.1f},{base:.1f}Z" fill="#a9c8e2"/>')
        s.append(f'<path d="M{tx:.1f},{ty:.1f} L{px+pw:.1f},{base:.1f} L{tx+2:.1f},{base:.1f}Z" fill="#8fb3d3"/>')
        cw = pw * 0.18
        s.append(f'<path d="M{tx:.1f},{ty:.1f} L{tx+cw:.1f},{ty+ph*0.35:.1f} l-2,-2 l-2,2.5 l-2,-2.5 l-2,2 L{tx-cw:.1f},{ty+ph*0.35:.1f}Z" fill="#ffffff"/>')
    # snow ground
    s.append(_hills(rnd, x, w, y + h * 0.6, 4, 6, "#f4faff"))
    s.append(_hills(rnd, x, w, y + h * 0.8, 3, 8, "#e6f2fb"))
    # pines
    for _ in range(22):
        tx, ty = rnd.uniform(x, x + w), rnd.uniform(y + h * 0.6, y + h - 2)
        sc = rnd.uniform(0.6, 1.1)
        s.append(f'<g transform="translate({tx:.1f},{ty:.1f}) scale({sc:.2f})" opacity="0.85">'
                 '<path d="M0,-12 L4,-5 L2.5,-5 L5.5,0 L-5.5,0 L-2.5,-5 L-4,-5Z" fill="#2f6f5a"/>'
                 '<path d="M0,-12 L2,-8.5 L-2,-8.5Z M-2.5,-5 L2.5,-5 L1.8,-4 L-1.8,-4Z" fill="#fff"/>'
                 '<rect x="-0.6" y="0" width="1.2" height="1.8" fill="#6b4a2b"/></g>')
    # snowflakes
    for _ in range(140):
        fx, fy = rnd.uniform(x, x + w), rnd.uniform(y - 6, y + h)
        r = rnd.uniform(0.35, 1.2)
        if r > 0.9:
            s.append(f'<g stroke="#ffffff" stroke-width="0.3" opacity="0.9">' + ''.join(
                f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx + 1.6*math.cos(a):.1f}" y2="{fy + 1.6*math.sin(a):.1f}"/>'
                for a in [i * math.pi / 3 for i in range(6)]) + '</g>')
        else:
            s.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r:.2f}" fill="#ffffff" opacity="0.85"/>')
    return ''.join(s)

def space(rnd, x, y, w, h):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#g_space)"/>']
    # nebulae
    for cx, cy, rx, ry, g in [(0.18, 0.45, 70, 30, "neb1"), (0.55, 0.3, 90, 28, "neb2"), (0.85, 0.65, 70, 32, "neb1"), (0.4, 0.8, 60, 22, "neb3")]:
        s.append(f'<ellipse cx="{x + w*cx:.1f}" cy="{y + h*cy:.1f}" rx="{rx}" ry="{ry}" fill="url(#{g})"/>')
    # spiral galaxy
    gx, gy = x + w * 0.33, y + h * 0.35
    s.append(f'<g transform="translate({gx:.1f},{gy:.1f}) rotate(-20) scale(1,0.45)">'
             f'<circle r="16" fill="url(#galaxy)"/>')
    for arm in range(2):
        pts = []
        for i in range(60):
            t = i / 59 * 3.2; rr = 1.5 + t * 4.2
            a = t * 1.9 + arm * math.pi
            pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}")
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#e8d9ff" stroke-width="1.6" opacity="0.45" stroke-linecap="round"/>')
    s.append('</g>')
    # second small galaxy
    s.append(f'<ellipse cx="{x + w*0.7:.1f}" cy="{y + h*0.75:.1f}" rx="9" ry="3" transform="rotate(25 {x + w*0.7:.1f} {y + h*0.75:.1f})" fill="url(#galaxy)" opacity="0.8"/>')
    # stars
    for _ in range(420):
        sx, sy = rnd.uniform(x, x + w), rnd.uniform(y - 4, y + h)
        r = rnd.choice([0.25, 0.3, 0.35, 0.45, 0.6])
        s.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r}" fill="#ffffff" opacity="{rnd.uniform(0.5,1):.2f}"/>')
    for _ in range(14):
        sx, sy = rnd.uniform(x, x + w), rnd.uniform(y, y + h)
        L = rnd.uniform(1.6, 2.6)
        s.append(f'<path d="M{sx:.1f},{sy-L:.1f} L{sx+0.35:.1f},{sy:.1f} L{sx:.1f},{sy+L:.1f} L{sx-0.35:.1f},{sy:.1f}Z '
                 f'M{sx-L:.1f},{sy:.1f} L{sx:.1f},{sy+0.35:.1f} L{sx+L:.1f},{sy:.1f} L{sx:.1f},{sy-0.35:.1f}Z" fill="#fff" opacity="0.9"/>')
    # ringed planet
    px, py = x + w * 0.58, y + h * 0.62
    s.append(f'<g transform="translate({px:.1f},{py:.1f}) rotate(-18)">'
             '<ellipse rx="17" ry="4.2" fill="none" stroke="#f7d49b" stroke-width="1.6" opacity="0.8"/>'
             '<circle r="9" fill="url(#planet1)"/>'
             '<path d="M-17,0 A17,4.2 0 0 0 17,0" fill="none" stroke="#f7d49b" stroke-width="1.6" opacity="0.9"/></g>')
    # small planets + moon
    s.append(f'<circle cx="{x + w*0.08:.1f}" cy="{y + h*0.25:.1f}" r="5" fill="url(#planet2)"/>')
    s.append(f'<circle cx="{x + w*0.93:.1f}" cy="{y + h*0.3:.1f}" r="3.2" fill="url(#planet3)"/>')
    # rocket
    rx, ry = x + w * 0.15, y + h * 0.78
    s.append(f'<g transform="translate({rx:.1f},{ry:.1f}) rotate(40)" opacity="0.9">'
             '<path d="M0,-7 C2.5,-4 2.5,1 1.8,4 L-1.8,4 C-2.5,1 -2.5,-4 0,-7Z" fill="#e9eef5"/>'
             '<circle cy="-2" r="1" fill="#5bc0eb"/>'
             '<path d="M-1.8,2 l-1.8,3 l1.8,-0.5Z M1.8,2 l1.8,3 l-1.8,-0.5Z" fill="#ff5d73"/>'
             '<path d="M-1.2,4 L0,8.5 L1.2,4Z" fill="#ffb347"/></g>')
    return ''.join(s)

WORLDS = [meadow, desert, jungle, arctic, space]
NAMES = ["Meadow", "Desert", "Jungle", "Arctic", "Space"]

DEFS = '''
<linearGradient id="g_meadow" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6f0b4"/><stop offset="1" stop-color="#9fd47a"/></linearGradient>
<linearGradient id="g_desert" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fde9b8"/><stop offset="1" stop-color="#eebc6c"/></linearGradient>
<linearGradient id="g_jungle" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4fa37a"/><stop offset="1" stop-color="#2e7d5b"/></linearGradient>
<linearGradient id="g_jungle_mid"><stop offset="0" stop-color="#3a8a64"/><stop offset="1" stop-color="#3a8a64"/></linearGradient>
<linearGradient id="g_arctic" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9d9f2"/><stop offset="0.6" stop-color="#e3f1fb"/><stop offset="1" stop-color="#f4faff"/></linearGradient>
<linearGradient id="g_space" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0d2a"/><stop offset="1" stop-color="#262a6b"/></linearGradient>
<radialGradient id="neb1"><stop offset="0" stop-color="#c04cfd" stop-opacity="0.45"/><stop offset="1" stop-color="#c04cfd" stop-opacity="0"/></radialGradient>
<radialGradient id="neb2"><stop offset="0" stop-color="#3fa7ff" stop-opacity="0.38"/><stop offset="1" stop-color="#3fa7ff" stop-opacity="0"/></radialGradient>
<radialGradient id="neb3"><stop offset="0" stop-color="#ff5d9e" stop-opacity="0.35"/><stop offset="1" stop-color="#ff5d9e" stop-opacity="0"/></radialGradient>
<radialGradient id="galaxy"><stop offset="0" stop-color="#fff8e1"/><stop offset="0.25" stop-color="#f3d7ff" stop-opacity="0.8"/><stop offset="1" stop-color="#8a5cff" stop-opacity="0"/></radialGradient>
<radialGradient id="planet1" cx="35%" cy="35%"><stop offset="0" stop-color="#ffe0a3"/><stop offset="1" stop-color="#d1803c"/></radialGradient>
<radialGradient id="planet2" cx="35%" cy="35%"><stop offset="0" stop-color="#a8f0ff"/><stop offset="1" stop-color="#2a6fd6"/></radialGradient>
<radialGradient id="planet3" cx="35%" cy="35%"><stop offset="0" stop-color="#ffc2d6"/><stop offset="1" stop-color="#c2386f"/></radialGradient>
'''

def background(x0, y0, cell, cols, rows, rows_per_world=3, blend=16.0, seed=7):
    """Return (defs, svg) for the worlds background covering the board area.
    Worlds are stacked bottom->top; each world above fades in over `blend` mm
    of the world below it, so the transition is soft."""
    rnd = random.Random(seed)
    W = cols * cell
    nworld = rows // rows_per_world
    H = rows_per_world * cell
    defs = [DEFS]
    out = [f'<clipPath id="boardclip"><rect x="{x0}" y="{y0}" width="{W}" height="{rows*cell}"/></clipPath>']
    body = []
    for b in range(nworld):
        top = y0 + (rows - rows_per_world * (b + 1)) * cell
        ext = blend if b > 0 else 0          # extend down into the world below
        h = H + ext
        art = WORLDS[b % len(WORLDS)](rnd, x0, top, W, h)
        if ext:
            mid = f'm{b}'
            defs.append(f'<linearGradient id="fade{b}" x1="0" y1="0" x2="0" y2="1">'
                        f'<stop offset="0" stop-color="#fff"/><stop offset="{H/h:.4f}" stop-color="#fff"/>'
                        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                        f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x0}" y="{top}" width="{W}" height="{h}">'
                        f'<rect x="{x0}" y="{top}" width="{W}" height="{h}" fill="url(#fade{b})"/></mask>')
            body.append(f'<g mask="url(#{mid})">{art}</g>')
        else:
            body.append(art)
    out.append(f'<g clip-path="url(#boardclip)">{"".join(body)}</g>')
    return ''.join(defs), ''.join(out)
