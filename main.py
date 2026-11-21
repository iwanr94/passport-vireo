"""The Republic of Vireo - an invented passport spread.

Writes /output/entry.png (1024x1024 PNG). Pillow only, no network,
no randomness: the same bytes on every run.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# --- palette -------------------------------------------------------------
BG      = (198, 192, 180)   # desk colour behind the spread
PAPER   = (243, 237, 224)   # one paper colour for both pages
INK     = (30, 32, 38)
MUTED   = (104, 100, 90)
RULE    = (150, 144, 130)
FAINT   = (196, 189, 174)

# page geometry (two pages, equal size, symmetric margins, one gutter)
PAGE_W, PAGE_H = 448, 740
LEFT_X, RIGHT_X = 48, 528
PAGE_Y = (H - PAGE_H) // 2          # 142
INNER = 34                          # text margin inside each page

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONTS = {}


def font(size, kind="sans"):
    """kind: sans | bold | serif | serifb | mono | monob"""
    names = {
        "sans":   "DejaVuSans.ttf",
        "bold":   "DejaVuSans-Bold.ttf",
        "serif":  "DejaVuSerif.ttf",
        "serifb": "DejaVuSerif-Bold.ttf",
        "mono":   "DejaVuSansMono.ttf",
        "monob":  "DejaVuSansMono-Bold.ttf",
    }
    key = (size, kind)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(os.path.join(FONT_DIR, names[kind]), size)
    return _FONTS[key]


def track_width(d, text, font, tracking):
    w = 0
    for ch in text:
        w += d.textlength(ch, font=font) + tracking
    return w - tracking if text else 0


def tracked(d, xy, text, font, fill, tracking=0.0, align="left"):
    """Draw letter-spaced text; align left/center/right against x=xy[0]."""
    x, y = xy
    total = track_width(d, text, font, tracking)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + tracking
    return total


def hair(d, x0, y, x1, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def page(d, x, y, w, h):
    """A paper page with a soft edge."""
    d.rectangle([x + 2, y + 3, x + w + 2, y + h + 3], fill=(176, 170, 158))
    d.rectangle([x, y, x + w, y + h], fill=PAPER)
    d.rectangle([x, y, x + w, y + h], outline=FAINT, width=1)


# --- data page -----------------------------------------------------------

FIELDS_ROWS = [
    ("SURNAME", "ELLISON", "GIVEN NAMES", "MARA"),
    ("NATIONALITY", "VIREAN", "SEX", "F"),
    ("DATE OF BIRTH", "14 JUN 1996", "PLACE OF BIRTH", "PORT VIREO"),
    ("DATE OF ISSUE", "12 MAR 2024", "DATE OF EXPIRY", "12 MAR 2034"),
]


def draw_portrait(d, x, y, w, h):
    """Flat-shaded head and shoulders, no photographic detail."""
    d.rectangle([x, y, x + w, y + h], fill=(231, 224, 210))
    cx = x + w / 2
    # shoulders / jacket
    d.rounded_rectangle([x, y + h * 0.70, x + w, y + h - 1],
                        radius=26, fill=(46, 52, 66))
    # collar
    d.polygon([(cx - 16, y + h * 0.72), (cx + 16, y + h * 0.72),
               (cx, y + h * 0.90)], fill=(226, 221, 208))
    # neck
    d.rectangle([cx - 11, y + h * 0.56, cx + 11, y + h * 0.76], fill=(196, 152, 124))
    # head
    d.ellipse([cx - 30, y + h * 0.16, cx + 30, y + h * 0.62], fill=(214, 170, 140))
    # hair: crown + sides, framing the face
    d.ellipse([cx - 33, y + h * 0.12, cx + 33, y + h * 0.44], fill=(38, 33, 31))
    d.rectangle([cx - 33, y + h * 0.28, cx + 33, y + h * 0.34], fill=(38, 33, 31))
    d.ellipse([cx - 24, y + h * 0.22, cx + 24, y + h * 0.50], fill=(214, 170, 140))
    d.polygon([(cx - 33, y + h * 0.16), (cx - 24, y + h * 0.16),
               (cx - 24, y + h * 0.46), (cx - 33, y + h * 0.40)], fill=(38, 33, 31))
    d.polygon([(cx + 24, y + h * 0.16), (cx + 33, y + h * 0.16),
               (cx + 33, y + h * 0.40), (cx + 24, y + h * 0.46)], fill=(38, 33, 31))
    # eyes, brow shadow, mouth
    d.ellipse([cx - 15, y + h * 0.345, cx - 9, y + h * 0.375], fill=(40, 36, 34))
    d.ellipse([cx + 9, y + h * 0.345, cx + 15, y + h * 0.375], fill=(40, 36, 34))
    d.line([(cx - 5, y + h * 0.475), (cx + 6, y + h * 0.475)],
           fill=(160, 106, 96), width=2)
    d.rectangle([x, y, x + w, y + h], outline=(206, 199, 184), width=1)


def check_digit(seed):
    """ICAO 9303 check digit."""
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(seed):
        if ch.isdigit():
            v = int(ch)
        elif "A" <= ch <= "Z":
            v = ord(ch) - 55
        else:
            v = 0
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<VRELLISON<<MARA"
    line1 = line1.ljust(44, "<")[:44]
    body = "VR20248841" + check_digit("VR20248841") + "VIR"
    body += "960614" + check_digit("960614") + "F"
    body += "340312" + check_digit("340312") + "7"
    line2 = body.ljust(44, "<")[:44]
    return line1, line2


def data_page(d):
    x0, x1 = LEFT_X + INNER, LEFT_X + PAGE_W - INNER
    cx = (x0 + x1) / 2

    tracked(d, (cx, PAGE_Y + 34), "REPUBLIC OF VIREO", font(19, "serifb"),
            INK, tracking=3.0, align="center")
    tracked(d, (cx, PAGE_Y + 66), "PASSPORT", font(10, "sans"),
            MUTED, tracking=5.2, align="center")
    hair(d, x0, PAGE_Y + 92, x1, INK)
    hair(d, x0, PAGE_Y + 96, x1, RULE)

    px, py, pw, ph = x0, PAGE_Y + 112, 128, 164
    draw_portrait(d, px, py, pw, ph)

    col1, col2 = x0 + 144, x0 + 268
    for i, (l1, v1, l2, v2) in enumerate(FIELDS_ROWS):
        y = py + i * 42
        for lx, lab, val in ((col1, l1, v1), (col2, l2, v2)):
            tracked(d, (lx, y), lab, font(6, "sans"), MUTED, tracking=0.9)
            d.text((lx, y + 11), val, font=font(12, "bold"), fill=INK)

    y = py + ph + 26
    hair(d, x0, y, x1, RULE)
    d.text((x0, y + 10), "PASSPORT NO.", font=font(6, "sans"), fill=MUTED)
    d.text((col2, y + 10), "AUTHORITY", font=font(6, "sans"), fill=MUTED)
    tracked(d, (x0, y + 21), "VR-2024-8841", font(15, "monob"), INK, tracking=0.6)
    d.text((col2, y + 21), "PORT VIREO", font=font(12, "bold"), fill=INK)

    # machine-readable zone
    top = PAGE_Y + PAGE_H - 96
    hair(d, x0, top - 14, x1, INK)
    d.rectangle([x0 - 8, top - 2, x1 + 8, PAGE_Y + PAGE_H - INNER + 4],
                fill=(236, 230, 216))
    mf = font(13, "mono")
    l1, l2 = mrz_lines()
    d.text((x0 - 2, top + 4), l1, font=mf, fill=INK)
    d.text((x0 - 2, top + 26), l2, font=mf, fill=INK)


# --- stamp page ----------------------------------------------------------

def ink_layer(w, h):
    layer = Image.new("RGBA", (int(w) + 20, int(h) + 20), (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def paste_rotated(img, layer, cx, cy, angle):
    rot = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    img.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def border_stamp(img, cx, cy, w, h, angle, color, lines):
    """Rounded double-ruled stamp. lines = [(text, size, kind, tracking, yoff)]"""
    layer, sd = ink_layer(w, h)
    box = [10, 10, 10 + w, 10 + h]
    sd.rounded_rectangle(box, radius=11, outline=color + (235,), width=3)
    sd.rounded_rectangle([16, 16, 4 + w, 4 + h], radius=7,
                         outline=color + (150,), width=1)
    for text, size, kind, tracking, yoff in lines:
        tracked(sd, (10 + w / 2, yoff), text, font(size, kind),
                color + (225,), tracking=tracking, align="center")
    paste_rotated(img, layer, cx, cy, angle)


def entry_stamp(img, cx, cy, w, h, angle, color, country, action, date):
    border_stamp(img, cx, cy, w, h, angle, color, [
        (country, 15, "bold", 2.2, 18),
        (action + "  " + date, 12, "bold", 0.8, 50),
    ])


def stamp_page(d, img):
    x0, x1 = RIGHT_X + INNER, RIGHT_X + PAGE_W - INNER
    cx = (x0 + x1) / 2

    tracked(d, (cx, PAGE_Y + 46), "VISAS AND ENDORSEMENTS", font(13, "serifb"),
            INK, tracking=2.4, align="center")
    hair(d, x0, PAGE_Y + 92, x1, INK)
    hair(d, x0, PAGE_Y + 96, x1, RULE)

    entry_stamp(img, 706, 286, 226, 82, -7.0, (146, 51, 44),
                "AURELIA", "ENTRY", "03 MAY 2025")
    entry_stamp(img, 800, 412, 206, 76, 4.5, (46, 70, 118),
                "NORDMARK", "EXIT", "21 SEP 2025")
    entry_stamp(img, 700, 534, 226, 82, -2.5, (44, 96, 70),
                "AURELIA", "ENTRY", "11 FEB 2026")

    border_stamp(img, 748, 664, 318, 88, -1.5, (150, 48, 44), [
        ("VISA CONDITION 9", 8, "bold", 1.8, 20),
        ("BEARER MUST PRESENT", 14, "bold", 0.6, 40),
        ("A SONG ON ARRIVAL", 14, "bold", 0.6, 60),
    ])

    border_stamp(img, 812, 786, 184, 50, 3.5, (52, 68, 104), [
        ("HARBOR TAX PAID", 11, "bold", 0.6, 15),
        ("2026 · PORT VIREO", 8, "bold", 0.6, 31),
    ])


# --- build ---------------------------------------------------------------

def main():
    img = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(img)

    page(d, LEFT_X, PAGE_Y, PAGE_W, PAGE_H)
    page(d, RIGHT_X, PAGE_Y, PAGE_W, PAGE_H)

    data_page(d)
    stamp_page(d, img)

    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.convert("RGB").save(path, "PNG", optimize=True)
    print(f"{path}: {img.size[0]}x{img.size[1]}, {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    main()




