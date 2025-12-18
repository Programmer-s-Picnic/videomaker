# python - <<EOF
from moviepy.editor import AudioFileClip
a = AudioFileClip("voice.wav")
print("Duration:", a.duration)
# EOF
