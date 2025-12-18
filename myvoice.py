# ============================================================
# SHORT VIDEO GENERATOR USING YOUR OWN VOICE (OFFLINE)
# Brand: Programmer's Picnic | LearnWithChampak.live
# Author style: Teaching-friendly, clean, readable
# ============================================================

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip
import moviepy.video.fx.all as vfx

# ============================================================
# CONFIGURATION (Change things here, not inside logic)
# ============================================================

# Video size for YouTube Shorts / Instagram Reels
WIDTH, HEIGHT = 1080, 1920
FPS = 30

# Font sizes
HOOK_FONT_SIZE = 78
BODY_FONT_SIZE = 70
WATERMARK_FONT_SIZE = 52

# Animation settings
BODY_DRIFT_UP_PX = 120        # body text moves upward slowly
FADE_DURATION = 0.4           # fade in/out seconds

# Files
INPUT_FILE = "champak.txt"    # text content
VOICE_FILE = "champak.wav"      # your recorded voice
OUTPUT_VIDEO = "output/myvoice.mp4"

# Watermark / Branding
WATERMARK_TEXT = "PROGRAMMER’S PICNIC • LEARNWITHCHAMPAK.LIVE"

# Background colors (saffron theme)
TOP_COLOR = (255, 153, 51)
BOTTOM_COLOR = (255, 236, 209)

# Text colors
HOOK_TEXT_COLOR = (255, 255, 255)
BODY_TEXT_COLOR = (40, 40, 40)

# ============================================================
# FONT LOADER
# Tries common fonts; falls back safely
# ============================================================

def load_font(size):
    """
    Try loading a good system font.
    If not found, fall back to default PIL font.
    """
    for name in ["arial.ttf", "calibri.ttf", "CascadiaCode.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except:
            continue
    return ImageFont.load_default()

# ============================================================
# BACKGROUND CREATION
# Creates a vertical gradient once (performance friendly)
# ============================================================

def create_gradient():
    """
    Creates a vertical saffron gradient background.
    This is generated once and reused for all frames.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(TOP_COLOR[0] + (BOTTOM_COLOR[0] - TOP_COLOR[0]) * ratio)
        g = int(TOP_COLOR[1] + (BOTTOM_COLOR[1] - TOP_COLOR[1]) * ratio)
        b = int(TOP_COLOR[2] + (BOTTOM_COLOR[2] - TOP_COLOR[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    return img.convert("RGBA")

# ============================================================
# TEXT WRAPPING
# Breaks text into lines that fit the screen width
# ============================================================

def wrap_text(draw, text, font, max_width):
    """
    Splits text into multiple lines so it fits nicely.
    """
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test_line = current + " " + word if current else word
        if draw.textlength(test_line, font=font) <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines

# ============================================================
# FRAME RENDERER
# This function generates each video frame
# ============================================================

def renderer(hook_text, body_text, duration):
    """
    Returns a function that MoviePy calls for every frame.
    """
    hook_font = load_font(HOOK_FONT_SIZE)
    body_font = load_font(BODY_FONT_SIZE)
    watermark_font = load_font(WATERMARK_FONT_SIZE)

    # Create static background once
    background = create_gradient()

    # Dummy draw object for measuring text
    temp_img = Image.new("RGBA", (WIDTH, HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)

    # Wrap text properly
    hook_lines = wrap_text(temp_draw, hook_text, hook_font, WIDTH * 0.9)
    body_lines = wrap_text(temp_draw, body_text, body_font, WIDTH * 0.85)

    hook_box_height = len(hook_lines) * (HOOK_FONT_SIZE + 10) + 30
    watermark_height = 90
    watermark_y = HEIGHT - watermark_height - 60

    def make_frame(t):
        """
        Called for every frame at time t (seconds).
        """
        progress = min(max(t / duration, 0), 1)
        drift = int(BODY_DRIFT_UP_PX * progress)

        img = background.copy()
        draw = ImageDraw.Draw(img)

        # ----------------------------
        # Hook (Top bar)
        # ----------------------------
        hook_bg = Image.new("RGBA", (WIDTH, hook_box_height), (0, 0, 0, 170))
        img.paste(hook_bg, (0, 0), hook_bg)

        y = 15
        for line in hook_lines:
            x = (WIDTH - draw.textlength(line, hook_font)) // 2
            draw.text((x, y), line, font=hook_font, fill=HOOK_TEXT_COLOR)
            y += HOOK_FONT_SIZE + 10

        # ----------------------------
        # Body Text (Animated upward)
        # ----------------------------
        y = HEIGHT // 2 - len(body_lines) * (BODY_FONT_SIZE + 12) // 2 + 120 - drift

        for line in body_lines:
            x = (WIDTH - draw.textlength(line, body_font)) // 2
            draw.text((x, y), line, font=body_font, fill=BODY_TEXT_COLOR)
            y += BODY_FONT_SIZE + 12

        # ----------------------------
        # Watermark (Bottom bar)
        # ----------------------------
        watermark_bg = Image.new("RGBA", (WIDTH, watermark_height), (0, 0, 0, 180))
        img.paste(watermark_bg, (0, watermark_y), watermark_bg)

        wx = (WIDTH - draw.textlength(WATERMARK_TEXT, watermark_font)) // 2
        draw.text(
            (wx, watermark_y + 18),
            WATERMARK_TEXT,
            font=watermark_font,
            fill=(255, 255, 255)
        )

        return np.array(img.convert("RGB"))

    return make_frame

# ============================================================
# MAIN EXECUTION
# ============================================================

# Ensure output folder exists
os.makedirs("output", exist_ok=True)

# ----------------------------
# Load text content
# ----------------------------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

hook = lines[0]                 # first line = hook
body = " ".join(lines[1:])      # rest = body

# ----------------------------
# Safety checks for voice file
# ----------------------------
if not os.path.exists(VOICE_FILE):
    raise FileNotFoundError("❌ voice.wav not found. Please record your voice.")

if os.path.getsize(VOICE_FILE) < 1000:
    raise RuntimeError("❌ voice.wav is too small or silent.")

# ----------------------------
# Load audio (YOUR VOICE)
# ----------------------------
audio = AudioFileClip(VOICE_FILE)
duration = audio.duration

# ----------------------------
# Create video clip
# ----------------------------
clip = VideoClip(
    renderer(hook, body, duration),
    duration=duration
)

clip = (
    clip
    .set_fps(FPS)
    .fx(vfx.fadein, FADE_DURATION)
    .fx(vfx.fadeout, FADE_DURATION)
    .set_audio(audio)
)

# ----------------------------
# Export final video
# ----------------------------
clip.write_videofile(
    OUTPUT_VIDEO,
    fps=FPS,
    codec="libx264",
    audio_codec="aac"
)

print("✅ VIDEO CREATED SUCCESSFULLY:", OUTPUT_VIDEO)
