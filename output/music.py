import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
import moviepy.video.fx.all as vfx
import pyttsx3
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

INPUT_FILE = "1input.txt"
OUTPUT_VIDEO = "output/4.mp4"
VOICE_FILE = "voice.wav"
MUSIC_FILE = "ring.mp3"

WATERMARK_TEXT = "PROGRAMMER’S PICNIC • LEARNWITHCHAMPAK.LIVE"

TOP_COLOR = (255, 153, 51)
BOTTOM_COLOR = (255, 236, 209)

HOOK_TEXT_COLOR = (255, 255, 255)
BODY_TEXT_COLOR = (40, 40, 40)

MUSIC_VOLUME = 1   # 🔉 soft background

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
    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        r = int(TOP_COLOR[0] + (BOTTOM_COLOR[0] - TOP_COLOR[0]) * y / HEIGHT)
        g = int(TOP_COLOR[1] + (BOTTOM_COLOR[1] - TOP_COLOR[1]) * y / HEIGHT)
        b = int(TOP_COLOR[2] + (BOTTOM_COLOR[2] - TOP_COLOR[2]) * y / HEIGHT)
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img.convert("RGBA")

def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = cur + " " + w if cur else w
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# =============================
# FRAME RENDERER
# =============================
def renderer(hook, body, duration):
    hf = load_font(HOOK_FONT_SIZE)
    bf = load_font(BODY_FONT_SIZE)
    wf = load_font(WATERMARK_FONT_SIZE)

    bg = create_gradient()
    tmp = Image.new("RGBA", (WIDTH, HEIGHT))
    dtmp = ImageDraw.Draw(tmp)

    hook_lines = wrap(dtmp, hook, hf, WIDTH * 0.9)
    body_lines = wrap(dtmp, body, bf, WIDTH * 0.85)

    hook_h = len(hook_lines) * (HOOK_FONT_SIZE + 10) + 30
    wm_h = 90
    wm_y = HEIGHT - wm_h - 60

    def make(t):
        p = min(max(t / duration, 0), 1)
        drift = int(BODY_DRIFT_UP_PX * p)

        img = bg.copy()
        d = ImageDraw.Draw(img)

        # Hook
        hb = Image.new("RGBA", (WIDTH, hook_h), (0, 0, 0, 170))
        img.paste(hb, (0, 0), hb)
        y = 15
        for ln in hook_lines:
            x = (WIDTH - d.textlength(ln, hf)) // 2
            d.text((x, y), ln, font=hf, fill=HOOK_TEXT_COLOR)
            y += HOOK_FONT_SIZE + 10

        # Body (moving)
        y = HEIGHT // 2 - len(body_lines) * (BODY_FONT_SIZE + 12) // 2 + 120 - drift
        for ln in body_lines:
            x = (WIDTH - d.textlength(ln, bf)) // 2
            d.text((x, y), ln, font=bf, fill=BODY_TEXT_COLOR)
            y += BODY_FONT_SIZE + 12

        # Watermark
        wb = Image.new("RGBA", (WIDTH, wm_h), (0, 0, 0, 180))
        img.paste(wb, (0, wm_y), wb)
        wx = (WIDTH - d.textlength(WATERMARK_TEXT, wf)) // 2
        d.text((wx, wm_y + 18), WATERMARK_TEXT, font=wf, fill=(255, 255, 255))

        return np.array(img.convert("RGB"))

    return make

# =============================
# MAIN
# =============================
os.makedirs("output", exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

hook = lines[0]
body = " ".join(lines[1:])
spoken = hook + ". " + body

print("🔊 Generating voice...")
engine = pyttsx3.init()
engine.save_to_file(spoken, VOICE_FILE)
engine.runAndWait()

voice = AudioFileClip(VOICE_FILE)
duration = voice.duration

print("🎵 Loading background music...")
music = AudioFileClip(MUSIC_FILE).volumex(MUSIC_VOLUME)
music = music.fx(afx.audio_loop, duration=duration)

final_audio = CompositeAudioClip([music, voice])

clip = VideoClip(renderer(hook, body, duration), duration=duration)
clip = clip.set_fps(FPS).fx(vfx.fadein, FADE_DURATION)
clip = clip.set_audio(final_audio)

clip.write_videofile(
    OUTPUT_VIDEO,
    fps=FPS,
    codec="libx264",
    audio_codec="aac"
)

print("✅ SHORT WITH MUSIC CREATED:", OUTPUT_VIDEO)
