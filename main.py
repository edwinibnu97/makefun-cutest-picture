#!/usr/bin/env python3
"""Make the cutest picture — deterministic cute kitten generator.

Pure Python standard library only (zlib, struct, math, os). No network,
no randomness, no third-party modules. Writes one PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

The program is run twice by the grader; both runs must produce
byte-identical output. Everything here is fixed constants, so the
output is fully deterministic.

Subject: a chubby kitten face — big round eyes, pink nose, blush
cheeks, whiskers and a little bow. Drawn with simple geometry
(circles, triangles, lines) on a soft pastel background.
"""

import math
import os
import struct
import zlib

W = 512
H = 512

# ---- palette (RGB) -------------------------------------------------------
BG_TOP = (191, 232, 255)      # soft sky blue
BG_BOTTOM = (255, 239, 214)   # warm cream
HEAD = (255, 248, 240)        # warm white fur
INNER_EAR = (255, 179, 193)   # soft pink
EYE = (38, 38, 38)           # dark brown-black
HIGHLIGHT = (255, 255, 255)   # white eye sparkle
NOSE = (255, 143, 163)        # pink nose
MOUTH = (138, 109, 92)        # soft brown mouth
BLUSH = (255, 207, 212)       # soft pink blush
WHISKER = (107, 91, 82)       # grey-brown whiskers
BOW = (255, 122, 162)         # pink bow wings
BOW_CENTER = (255, 92, 138)   # deeper pink bow knot


# ---- image buffer --------------------------------------------------------
def new_image(w, h, fill):
    return [[fill] * w for _ in range(h)]


def set_px(img, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        img[y][x] = color


def fill_background(img):
    """Gentle vertical gradient, top sky blue -> bottom warm cream."""
    for y in range(H):
        t = y / (H - 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        row = [(r, g, b)] * W
        img[y] = row


def fill_circle(img, cx, cy, r, color):
    r2 = r * r
    for y in range(max(0, cy - r), min(H, cy + r + 1)):
        dy = y - cy
        for x in range(max(0, cx - r), min(W, cx + r + 1)):
            dx = x - cx
            if dx * dx + dy * dy <= r2:
                img[y][x] = color


def _sign(x1, y1, x2, y2, x3, y3):
    return (x1 - x3) * (y2 - y3) - (x2 - x3) * (y1 - y3)


def fill_triangle(img, p1, p2, p3, color):
    x_min = max(0, min(p1[0], p2[0], p3[0]))
    x_max = min(W - 1, max(p1[0], p2[0], p3[0]))
    y_min = max(0, min(p1[1], p2[1], p3[1]))
    y_max = min(H - 1, max(p1[1], p2[1], p3[1]))
    d = _sign(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
    if d == 0:
        return
    for y in range(y_min, y_max + 1):
        for x in range(x_min, x_max + 1):
            d1 = _sign(x, y, p1[0], p1[1], p2[0], p2[1])
            d2 = _sign(x, y, p2[0], p2[1], p3[0], p3[1])
            d3 = _sign(x, y, p3[0], p3[1], p1[0], p1[1])
            neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (neg and pos):
                img[y][x] = color


def draw_line(img, x0, y0, x1, y1, color):
    """Bresenham line, 1 px thick."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(img, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def draw_thick_point(img, x, y, color, size=2):
    for dy in range(size):
        for dx in range(size):
            set_px(img, x + dx, y + dy, color)


def draw_smile(img):
    """Little 'w' smile under the nose: short stem + two curves."""
    for y in range(340, 349):
        draw_thick_point(img, 255, y, MOUTH, 2)
    # left curve: parabola opening up (a touch deeper so it reads at 300px)
    for t in range(0, 15):
        x = 255 - t
        y = 349 + (t * t) // 11
        draw_thick_point(img, x, y, MOUTH, 2)
    # right curve
    for t in range(0, 15):
        x = 256 + t
        y = 349 + (t * t) // 11
        draw_thick_point(img, x, y, MOUTH, 2)


# ---- the kitten ----------------------------------------------------------
def draw_kitten(img):
    # Ears first (head circle overlaps their bases for a clean join).
    fill_triangle(img, (150, 70), (130, 180), (240, 160), HEAD)   # left ear
    fill_triangle(img, (362, 70), (272, 160), (382, 180), HEAD)   # right ear
    fill_triangle(img, (158, 95), (150, 165), (215, 150), INNER_EAR)
    fill_triangle(img, (354, 95), (297, 150), (362, 165), INNER_EAR)

    # Big round head.
    fill_circle(img, 256, 295, 150, HEAD)

    # Bow on the right ear (a touch of charm).
    fill_triangle(img, (355, 110), (325, 90), (325, 130), BOW)
    fill_triangle(img, (355, 110), (385, 90), (385, 130), BOW)
    fill_circle(img, 355, 110, 9, BOW_CENTER)

    # Blush cheeks (under the eyes, drawn before whiskers).
    fill_circle(img, 165, 335, 20, BLUSH)
    fill_circle(img, 347, 335, 20, BLUSH)

    # Big bright eyes with sparkles.
    fill_circle(img, 200, 285, 30, EYE)
    fill_circle(img, 312, 285, 30, EYE)
    fill_circle(img, 190, 275, 10, HIGHLIGHT)
    fill_circle(img, 302, 275, 10, HIGHLIGHT)
    fill_circle(img, 210, 293, 4, HIGHLIGHT)
    fill_circle(img, 322, 293, 4, HIGHLIGHT)

    # Tiny pink nose + smile.
    fill_triangle(img, (244, 325), (268, 325), (256, 340), NOSE)
    draw_smile(img)

    # Whiskers, three per side.
    draw_line(img, 140, 310, 85, 295, WHISKER)
    draw_line(img, 140, 325, 85, 325, WHISKER)
    draw_line(img, 140, 340, 85, 355, WHISKER)
    draw_line(img, 372, 310, 427, 295, WHISKER)
    draw_line(img, 372, 325, 427, 325, WHISKER)
    draw_line(img, 372, 340, 427, 355, WHISKER)


# ---- minimal PNG encoder (stdlib only) -----------------------------------
def _chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def encode_png(width, height, img):
    raw = bytearray()
    for row in img:
        raw.append(0)  # filter: None
        for (r, g, b) in row:
            raw += bytes((r, g, b))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


def main():
    img = new_image(W, H, BG_TOP)
    fill_background(img)
    draw_kitten(img)
    data = encode_png(W, H, img)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
