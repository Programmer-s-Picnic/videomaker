import tkinter as tk
from tkinter import filedialog, messagebox
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ColorClip,
    ImageClip
)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
APP_TITLE = "Programmer’s Picnic – Offline Shorts Maker"

VIDEO_W, VIDEO_H = 1080, 1920
BG_COLORS = [(255, 236, 210), (255, 248, 230)]

TEXT_FONT_SIZE = 96
CODE_FONT_SIZE = 56
WATERMARK_SIZE = 32

FPS = 30
SCREEN_BREAK = "===SCREEN==="
OUTPUT_DIR = "output"

WATERMARK_TEXT = "Programmer’s Picnic • Champak Roy"

# Common Windows fonts (change if needed)
FONT_TEXT = "arialbd.ttf"
FONT_CODE = "consola.ttf"
FONT_WATERMARK = "arial.ttf"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# PIL TEXT → IMAGE (NO IMAGEMAGICK)
# --------------------------------------------------


def render_text_image(text, font_path, font_size):
    font = ImageFont.truetype(font_path, font_size)

    dummy = Image.new("RGBA", (VIDEO_W, VIDEO_H))
    draw = ImageDraw.Draw(dummy)

    lines = text.split("\n")
    widths = []
    heights = []

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        widths.append(w)
        heights.append(h)

    img_w = max(widths) + 40
    img_h = sum(heights) + (len(lines) - 1) * 10 + 40

    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    y = 20
    for line, h in zip(lines, heights):
        draw.text((20, y), line, font=font, fill="black")
        y += h + 10

    return img

# --------------------------------------------------
# GUI APP
# --------------------------------------------------


class ShortsGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("580x580")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text=APP_TITLE,
                 font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.script_path = self.file_row("Input text (.txt)")
        self.voice_path = self.file_row("Voice (wav/mp3)")

        out_frame = tk.Frame(self)
        out_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(out_frame, text="Output name:",
                 width=18, anchor="w").pack(side="left")
        self.output_name = tk.Entry(out_frame)
        self.output_name.insert(0, "python_silent_mistake")
        self.output_name.pack(side="left", expand=True, fill="x")

        tk.Button(
            self,
            text="🎬 Create Short",
            font=("Segoe UI", 12, "bold"),
            bg="#f59e0b",
            command=self.create_video
        ).pack(pady=12)

        self.status = tk.Label(self, text="Ready", fg="green")
        self.status.pack(pady=8)

    def file_row(self, label):
        frame = tk.Frame(self)
        frame.pack(fill="x", padx=20, pady=4)
        tk.Label(frame, text=label, width=18, anchor="w").pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(frame, text="Browse",
                  command=lambda e=entry: self.browse(e)).pack(side="right")
        return entry

    def browse(self, entry):
        path = filedialog.askopenfilename()
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    # --------------------------------------------------
    def create_video(self):
        script = self.script_path.get()
        voice = self.voice_path.get()
        out_name = self.output_name.get().strip()

        if not script or not voice:
            messagebox.showerror("Missing files", "Text and Voice required")
            return

        output_path = os.path.join(OUTPUT_DIR, out_name + ".mp4")

        try:
            audio = AudioFileClip(voice)
            duration = audio.duration

            scenes = []
            in_code = False
            buffer = []

            with open(script, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.rstrip()

                    if line.startswith("```"):
                        if in_code:
                            scenes.append(("code", "\n".join(buffer)))
                            buffer = []
                            in_code = False
                        else:
                            in_code = True
                        continue

                    if in_code:
                        buffer.append(line)
                        continue

                    if not line:
                        continue

                    if line.upper() == SCREEN_BREAK:
                        scenes.append(("blank", ""))
                    else:
                        scenes.append(("text", line))

            scene_dur = duration / len(scenes)
            clips = []
            t = 0

            for i, (stype, content) in enumerate(scenes):
                bg = ColorClip(
                    size=(VIDEO_W, VIDEO_H),
                    color=BG_COLORS[i % 2],
                    duration=scene_dur
                ).set_start(t)
                clips.append(bg)

                # watermark
                wm_img = render_text_image(
                    WATERMARK_TEXT, FONT_WATERMARK, WATERMARK_SIZE
                )
                wm = ImageClip(np.array(wm_img)) \
                    .set_opacity(0.35) \
                    .set_position(("right", "bottom")) \
                    .set_start(t) \
                    .set_duration(scene_dur)
                clips.append(wm)

                if stype in ("text", "code"):
                    font = FONT_TEXT if stype == "text" else FONT_CODE
                    size = TEXT_FONT_SIZE if stype == "text" else CODE_FONT_SIZE

                    img = render_text_image(content, font, size)
                    clip = ImageClip(np.array(img)) \
                        .set_position("center") \
                        .set_start(t) \
                        .set_duration(scene_dur)
                    clips.append(clip)

                t += scene_dur

            final = CompositeVideoClip(
                clips, size=(VIDEO_W, VIDEO_H)
            ).set_audio(audio)

            final.write_videofile(
                output_path,
                fps=FPS,
                codec="libx264",
                audio_codec="aac"
            )

            messagebox.showinfo("Success", f"Video created:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    ShortsGUI().mainloop()
