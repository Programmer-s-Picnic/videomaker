import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 1080, 1920

HOOK_FONT_SIZE = 78
BODY_FONT_SIZE = 70
WATERMARK_FONT_SIZE = 52   # BIG & visible

SLIDE_DURATION = 2.8
FADE_DURATION = 0.4

INPUT_FILE = "input.txt"
OUTPUT_VIDEO = "output/short_1.mp4"

WATERMARK_TEXT = "PROGRAMMER’S PICNIC • LEARNWITHCHAMPAK.LIVE"

# Saffron gradient
TOP_COLOR = (255, 153, 51)
BOTTOM_COLOR = (255, 236, 209)

HOOK_TEXT_COLOR = (255, 255, 255)
BODY_TEXT_COLOR = (40, 40, 40)

# =============================
# FONT LOADER (WINDOWS SAFE)
# =============================
def load_font(size):
    for name in ["arial.ttf", "CascadiaCode.ttf", "calibri.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

# =============================
# BACKGROUND
# =============================
def create_gradient():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        r = int(TOP_COLOR[0] + (BOTTOM_COLOR[0] - TOP_COLOR[0]) * y / HEIGHT)
        g = int(TOP_COLOR[1] + (BOTTOM_COLOR[1] - TOP_COLOR[1]) * y / HEIGHT)
        b = int(TOP_COLOR[2] + (BOTTOM_COLOR[2] - TOP_COLOR[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img.convert("RGBA")

# =============================
# TEXT WRAPPING
# =============================
def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for w in words:
        test = current + " " + w if current else w
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines

# =============================
# SLIDE CREATION
# =============================
def create_slide(hook, body):
    img = create_gradient()
    draw = ImageDraw.Draw(img)

    hook_font = load_font(HOOK_FONT_SIZE)
    body_font = load_font(BODY_FONT_SIZE)
    watermark_font = load_font(WATERMARK_FONT_SIZE)

    # ---------- HOOK ----------
    hook_lines = wrap_text(draw, hook, hook_font, WIDTH * 0.9)
    hook_height = len(hook_lines) * (HOOK_FONT_SIZE + 10) + 30

    hook_bg = Image.new("RGBA", (WIDTH, hook_height), (0, 0, 0, 170))
    img.paste(hook_bg, (0, 0), hook_bg)

    y = 15
    for line in hook_lines:
        x = (WIDTH - draw.textlength(line, hook_font)) // 2
        draw.text((x, y), line, font=hook_font, fill=HOOK_TEXT_COLOR)
        y += HOOK_FONT_SIZE + 10

    # ---------- BODY ----------
    body_lines = wrap_text(draw, body, body_font, WIDTH * 0.85)
    y = HEIGHT // 2 - len(body_lines) * (BODY_FONT_SIZE + 12) // 2 + 120

    for line in body_lines:
        x = (WIDTH - draw.textlength(line, body_font)) // 2
        draw.text((x, y), line, font=body_font, fill=BODY_TEXT_COLOR)
        y += BODY_FONT_SIZE + 12

    # ---------- WATERMARK (BIG & CLEAR) ----------
    wm_height = 90
    wm_bg = Image.new("RGBA", (WIDTH, wm_height), (0, 0, 0, 180))
    wm_y = HEIGHT - wm_height - 60
    img.paste(wm_bg, (0, wm_y), wm_bg)

    wm_width = draw.textlength(WATERMARK_TEXT, watermark_font)
    wm_x = (WIDTH - wm_width) // 2

    draw.text(
        (wm_x, wm_y + 18),
        WATERMARK_TEXT,
        font=watermark_font,
        fill=(255, 255, 255)
    )

    return img.convert("RGB")

# =============================
# MAIN
# =============================
os.makedirs("output", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

hook = lines[0]
body = " ".join(lines[1:])

img = create_slide(hook, body)
frame = np.array(img)

clip = (
    ImageClip(frame)
    .set_duration(SLIDE_DURATION)
    .fadein(FADE_DURATION)
)

clip.write_videofile(
    OUTPUT_VIDEO,
    fps=30,
    codec="libx264",
    audio=False
)

print("✅ FINAL SHORT CREATED:", OUTPUT_VIDEO)
