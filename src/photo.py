"""Realistic 'worlds' background from image files (assets/backgrounds/<world>.png).

Each image is cropped (never stretched) to the strip it covers on the board,
optionally muted further, and the world above fades into the one below.
Any image size works; larger (upscaled) images simply give a sharper print.
"""
import base64, io, os
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(HERE, '..', 'assets', 'backgrounds')
WORLDS = ['meadow', 'desert', 'jungle', 'arctic', 'space']

# Where to cut the strip from each image: fraction of the image height for the
# TOP of the strip. Tune these if a different part of an image looks better.
CROP_TOP = {'meadow': 0.50, 'desert': 0.30, 'jungle': 0.20, 'arctic': 0.24, 'space': 0.24}

# Extra muting on top of what the images already have (1.0 = unchanged).
SATURATION = 0.90
CONTRAST = 0.90
BRIGHTNESS = 1.03

def _strip(world, aspect):
    im = Image.open(os.path.join(BG_DIR, f'{world}.png')).convert('RGB')
    w, h = im.size
    ch = round(w / aspect)
    if ch > h:                      # image not wide enough: crop width instead
        cw = round(h * aspect); x0 = (w - cw) // 2
        im = im.crop((x0, 0, x0 + cw, h))
    else:
        top = min(max(0, round(CROP_TOP.get(world, 0.25) * h)), h - ch)
        im = im.crop((0, top, w, top + ch))
    im = ImageEnhance.Color(im).enhance(SATURATION)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=92)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode(), im.size

def background(x0, y0, cell, cols, rows, rows_per_world=3, blend=16.0):
    W = cols * cell
    H = rows_per_world * cell
    defs, body = [], []
    for b, world in enumerate(WORLDS):
        top = y0 + (rows - rows_per_world * (b + 1)) * cell
        ext = blend if b > 0 else 0
        h = H + ext
        uri, size = _strip(world, W / h)
        img = f'<image x="{x0}" y="{top}" width="{W}" height="{h}" preserveAspectRatio="none" href="{uri}"/>'
        if ext:
            defs.append(f'<linearGradient id="pfade{b}" x1="0" y1="0" x2="0" y2="1">'
                        f'<stop offset="0" stop-color="#fff"/><stop offset="{H/h:.4f}" stop-color="#fff"/>'
                        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                        f'<mask id="pm{b}" maskUnits="userSpaceOnUse" x="{x0}" y="{top}" width="{W}" height="{h}">'
                        f'<rect x="{x0}" y="{top}" width="{W}" height="{h}" fill="url(#pfade{b})"/></mask>')
            body.append(f'<g mask="url(#pm{b})">{img}</g>')
        else:
            body.append(img)
        dpi = size[0] / (W / 25.4)
        print(f'  {world}: strip {size[0]}x{size[1]} px -> {dpi:.0f} dpi at print size')
    clip = f'<clipPath id="boardclip"><rect x="{x0}" y="{y0}" width="{W}" height="{rows*cell}"/></clipPath>'
    return ''.join(defs) + clip, f'<g clip-path="url(#boardclip)">{"".join(body)}</g>'
