# Crop some videos that have different dimensions to 960x720.
ffmpeg -i video_import -vf "crop=960:in_h:160:0" -c:a copy video_export

# Downasample these 960x720 videos to 576x432
ffmpeg -i video_import -vf scale="576:-1" video_export]

# Sharpen some blurry videos.
ffmpeg -i video_import -vf unsharp=13:13:5 video_export

# Create a list of videos with black frames to exclude.
ffmpeg -i video_import -vf "blackdetect=d=5:pix_th=0.10,metadata=mode=print:file=text_export" -f rawvideo -y /NUL

# Create a list of videos with frozen frames to exclude.
ffmpeg -i video_import -vf "freezedetect=n=-60dB:d=5,metadata=mode=print:file=text_export" -map 0:v:0 -f null -

# Also exclude videos that are corrupted, the magazine is covered and the mouse is absent.

