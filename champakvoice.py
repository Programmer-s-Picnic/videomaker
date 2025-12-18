import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx

# =============================
# CONFIG
# =============================

WIDTH, HEIGHT = 1080, 1920
FPS = 30

HOOK_FONT_SIZE = 78
BODY_FONT_SIZE = 70
WATERMARK_FONT_SIZE = 52

BODY_DRIFT_UP_PX = 120
FADE_DURATION = 0.4

INPUT_FILE = "input.txt"
VOICE_FILE = "voice.wav"
MUSIC_FILE = "music.mp3"
OUTPUT_VIDEO = "output/short_1.mp4"

WATERMARK_TEXT = "PROGRAMMER’S PICNIC • LEARNWITHCHAMPAK.LIVE"

TOP_COLOR = (255, 153, 51)
BOTTOM_COLOR = (255, 236, 209)

HOOK_TEXT_COLOR = (255, 255, 255)
BODY_TEXT_COLOR = (40, 40, 40)

HIGHLIGHT_BG = (255, 200, 0, 180)  # saffron highlight

MUSIC_VOLUME = 0.12

# =============================
# FONT LOADER
# =============================

def load_font(size):
    for name in ["arial.ttf", "calibri.ttf", "CascadiaCode.ttf"]:
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
# TEXT WRAP
# =============================

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

# =============================
# LINE HIGHLIGHT LOGIC
# =============================

def active_line_index(total_lines, duration, t):
    if total_lines == 0:
        return -1
    slot = duration / total_lines
    idx = int(t // slot)
    return min(idx, total_lines - 1)

# =============================
# FRAME RENDERER
# =============================

def frame_renderer(hook, body, duration):
    hook_font = load_font(HOOK_FONT_SIZE)
    body_font = load_font(BODY_FONT_SIZE)
    watermark_font = load_font(WATERMARK_FONT_SIZE)

    background = create_gradient()

    temp = Image.new("RGBA", (WIDTH, HEIGHT))
    temp_draw = ImageDraw.Draw(temp)

    hook_lines = wrap_text(temp_draw, hook, hook_font, WIDTH * 0.9)
    body_lines = wrap_text(temp_draw, body, body_font, WIDTH * 0.85)

    hook_height = len(hook_lines) * (HOOK_FONT_SIZE + 10) + 30
    watermark_height = 90
    watermark_y = HEIGHT - watermark_height - 60

    def make_frame(t):
        img = background.copy()
        draw = ImageDraw.Draw(img)

        # ---------- HOOK ----------
        hook_bg = Image.new("RGBA", (WIDTH, hook_height), (0, 0, 0, 170))
        img.paste(hook_bg, (0, 0), hook_bg)

        y = 15
        for line in hook_lines:
            x = (WIDTH - draw.textlength(line, hook_font)) // 2
            draw.text((x, y), line, font=hook_font, fill=HOOK_TEXT_COLOR)
            y += HOOK_FONT_SIZE + 10

        # ---------- BODY (MOVING + LINE HIGHLIGHT) ----------
        progress = t / duration
        drift = int(BODY_DRIFT_UP_PX * progress)

        active_line = active_line_index(len(body_lines), duration, t)

        base_y = HEIGHT // 2 - len(body_lines) * (BODY_FONT_SIZE + 12) // 2 + 120
        y = base_y - drift

        for i, line in enumerate(body_lines):
            line_w = draw.textlength(line, body_font)
            x = (WIDTH - line_w) // 2

            if i == active_line:
                pad = 12
                rect = (
                    x - pad,
                    y - pad,
                    x + line_w + pad,
                    y + BODY_FONT_SIZE + pad
                )
                draw.rounded_rectangle(rect, radius=16, fill=HIGHLIGHT_BG)

            draw.text((x, y), line, font=body_font, fill=BODY_TEXT_COLOR)
            y += BODY_FONT_SIZE + 12

        # ---------- WATERMARK ----------
        wm_bg = Image.new("RGBA", (WIDTH, watermark_height), (0, 0, 0, 180))
        img.paste(wm_bg, (0, watermark_y), wm_bg)

        wm_x = (WIDTH - draw.textlength(WATERMARK_TEXT, watermark_font)) // 2
        draw.text(
            (wm_x, watermark_y + 18),
            WATERMARK_TEXT,
            font=watermark_font,
            fill=(255, 255, 255)
        )

        return np.array(img.convert("RGB"))

    return make_frame

# =============================
# MAIN
# =============================

os.makedirs("output", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

hook = lines[0]
body = " ".join(lines[1:])

voice = AudioFileClip(VOICE_FILE)
music = AudioFileClip(MUSIC_FILE).volumex(MUSIC_VOLUME)
music = music.fx(afx.audio_loop, duration=voice.duration)

final_audio = CompositeAudioClip([music, voice])

clip = VideoClip(
    frame_renderer(hook, body, voice.duration),
    duration=voice.duration
)

clip = clip.set_fps(FPS)
clip = clip.fx(vfx.fadein, FADE_DURATION)
clip = clip.set_audio(final_audio)

clip.write_videofile(
    OUTPUT_VIDEO,
    codec="libx264",
    audio_codec="aac",
    fps=FPS
)

print("SHORT READY:", OUTPUT_VIDEO)
