import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 1080, 1920
FONT_SIZE = 70
SLIDE_DURATION = 2.8
FADE_DURATION = 0.4

INPUT_FILE = "input.txt"
OUTPUT_VIDEO = "output/short_1.mp4"

WATERMARK_TEXT = "Programmer’s Picnic • learnwithchampak.live"

# Saffron gradient colors (top → bottom)
TOP_COLOR = (255, 153, 51)     # saffron
BOTTOM_COLOR = (255, 236, 209) # light saffron

TEXT_COLOR = (40, 40, 40)      # dark text
WATERMARK_COLOR = (90, 60, 30)

# =============================
# HELPERS
# =============================
def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def create_gradient():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(TOP_COLOR[0] * (1 - ratio) + BOTTOM_COLOR[0] * ratio)
        g = int(TOP_COLOR[1] * (1 - ratio) + BOTTOM_COLOR[1] * ratio)
        b = int(TOP_COLOR[2] * (1 - ratio) + BOTTOM_COLOR[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    return img

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

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

def create_slide(text, font, watermark_font):
    img = create_gradient()
    draw = ImageDraw.Draw(img)

    max_width = WIDTH * 0.85
    lines = wrap_text(draw, text, font, max_width)

    total_height = len(lines) * (FONT_SIZE + 12)
    y = (HEIGHT - total_height) // 2

    for line in lines:
        w = draw.textlength(line, font=font)
        x = (WIDTH - w) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += FONT_SIZE + 12

    # Watermark
    wm_w = draw.textlength(WATERMARK_TEXT, font=watermark_font)
    wm_x = (WIDTH - wm_w) // 2
    wm_y = HEIGHT - 80

    draw.text(
        (wm_x, wm_y),
        WATERMARK_TEXT,
        font=watermark_font,
        fill=WATERMARK_COLOR
    )

    return img

# =============================
# MAIN
# =============================
os.makedirs("output", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    slides_text = [l.strip() for l in f.readlines() if l.strip()]

font = load_font(FONT_SIZE)
watermark_font = load_font(32)

clips = []

for text in slides_text:
    img = create_slide(text, font, watermark_font)
    frame = np.array(img)

    clip = (
        ImageClip(frame)
        .set_duration(SLIDE_DURATION)
        .fadein(FADE_DURATION)
    )
    clips.append(clip)

final = concatenate_videoclips(clips, method="compose")
final.write_videofile(
    OUTPUT_VIDEO,
    fps=30,
    codec="libx264",
    audio=False
)

print("✅ Saffron short created:", OUTPUT_VIDEO)
