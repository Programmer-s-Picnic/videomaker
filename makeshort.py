import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, concatenate_videoclips

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 1080, 1920
BG_COLOR = (18, 18, 18)        # Dark background
TEXT_COLOR = (255, 255, 255)  # White text
FONT_SIZE = 70
SLIDE_DURATION = 2.8          # seconds
FADE_DURATION = 0.4

INPUT_FILE = "input.txt"
OUTPUT_VIDEO = "output/short_1.mp4"

# =============================
# HELPERS
# =============================
def load_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def create_slide(text, font):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Wrap text
    max_width = WIDTH * 0.85
    words = text.split()
    lines = []
    current = ""

    for w in words:
        test = current + " " + w if current else w
        w_size = draw.textlength(test, font=font)
        if w_size <= max_width:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    total_height = len(lines) * (FONT_SIZE + 10)
    y = (HEIGHT - total_height) // 2

    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = (WIDTH - line_width) // 2
        draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        y += FONT_SIZE + 10

    return img

# =============================
# MAIN
# =============================
os.makedirs("output", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    slides_text = [l.strip() for l in f.readlines() if l.strip()]

font = load_font(FONT_SIZE)
clips = []

for text in slides_text:
    img = create_slide(text, font)
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

print("✅ Short video created:", OUTPUT_VIDEO)
