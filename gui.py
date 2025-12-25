import sys
import os
from moviepy.editor import (
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    ColorClip
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
VIDEO_W, VIDEO_H = 1080, 1920   # Vertical (9:16)
BG_COLORS = [
    (255, 236, 210),   # saffron
    (255, 248, 230)    # lighter saffron
]
FONT = "Arial-Bold"
FONT_SIZE = 90
FONT_COLOR = "black"
MARGIN = 120
FPS = 30
SCREEN_BREAK = "===SCREEN==="
# --------------------------------------------------

# --------------------------------------------------
# ARGUMENTS (from GUI or CLI)
# --------------------------------------------------
if len(sys.argv) < 6:
    print("Usage:")
    print("python champakvoice.py input.txt voice.wav music(optional) webcam(optional) output.mp4")
    sys.exit(1)

text_file = sys.argv[1]
voice_file = sys.argv[2]
music_file = sys.argv[3]   # optional (ignored for now)
webcam_file = sys.argv[4]   # optional (ignored for now)
output_file = sys.argv[5]

os.makedirs(os.path.dirname(output_file), exist_ok=True)

print("📄 Script :", text_file)
print("🎙 Voice  :", voice_file)
print("🎬 Output :", output_file)

# --------------------------------------------------
# LOAD AUDIO
# --------------------------------------------------
audio = AudioFileClip(voice_file)
duration = audio.duration

# --------------------------------------------------
# READ SCRIPT WITH COMMANDS
# --------------------------------------------------
with open(text_file, "r", encoding="utf-8") as f:
    raw_lines = [l.strip() for l in f if l.strip()]

if not raw_lines:
    raise ValueError("input.txt is empty")

scenes = []

for line in raw_lines:
    if line.upper() == SCREEN_BREAK:
        scenes.append({"type": "blank"})
    else:
        scenes.append({"type": "text", "content": line})

total_scenes = len(scenes)
scene_duration = duration / total_scenes

print(f"🧠 Total scenes: {total_scenes}")
print(f"⏱ Each scene: {scene_duration:.2f} seconds")

# --------------------------------------------------
# BUILD VIDEO SCENES
# --------------------------------------------------
clips = []
current_time = 0

for i, scene in enumerate(scenes):
    bg_color = BG_COLORS[i % len(BG_COLORS)]

    # Background (always)
    bg = ColorClip(
        size=(VIDEO_W, VIDEO_H),
        color=bg_color,
        duration=scene_duration
    ).set_start(current_time)

    clips.append(bg)

    # Text overlay (only if text scene)
    if scene["type"] == "text":
        txt = TextClip(
            scene["content"],
            fontsize=FONT_SIZE,
            font=FONT,
            color=FONT_COLOR,
            size=(VIDEO_W - MARGIN, None),
            method="caption",
            align="center"
        ).set_position("center") \
         .set_start(current_time) \
         .set_duration(scene_duration)

        clips.append(txt)

    current_time += scene_duration

# --------------------------------------------------
# FINAL COMPOSITION
# --------------------------------------------------
final = CompositeVideoClip(
    clips,
    size=(VIDEO_W, VIDEO_H)
).set_audio(audio)

# --------------------------------------------------
# EXPORT
# --------------------------------------------------
print("🎬 Rendering video...")

final.write_videofile(
    output_file,
    fps=FPS,
    codec="libx264",
    audio_codec="aac"
)

print("✅ DONE!")
