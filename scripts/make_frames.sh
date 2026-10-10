#!/usr/bin/env bash
# Zerlegt das Scroll-Drive-Video in WebP-Frames für die Canvas-Szene der Startseite.
# Warum Frames: Ein Canvas-Bild pro Scroll-Position ruckelt nicht, <video>-Scrubbing schon.
# Aufruf: bash scripts/make_frames.sh pfad/zu/v2.mp4 [fps=24] [breite=1600]
set -euo pipefail
src="${1:?Pfad zum Video angeben}"
fps="${2:-24}"
width="${3:-1600}"
out="src/frontend/public/media/car"
mkdir -p "$out"
rm -f "$out"/f_*.webp
ffmpeg -y -i "$src" -vf "fps=${fps},scale=${width}:-2" -c:v libwebp -quality 78 "$out/f_%04d.webp"
count=$(ls "$out"/f_*.webp | wc -l)
height=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 -vf "scale=${width}:-2" "$src" 2>/dev/null || echo 0)
printf '{"count": %s, "pattern": "/media/car/f_%%04d.webp", "width": %s, "height": %s}\n' "$count" "$width" "${height:-0}" > "$out/manifest.json"
echo "$count Frames, $(du -sh "$out" | cut -f1) gesamt (Ziel: höchstens 8 MB; sonst fps oder Breite senken)"
