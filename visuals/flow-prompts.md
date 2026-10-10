# Google-Flow-Prompts für die Startseite

Stil-Anker (an jeden Prompt hinten anhängen): `cinematic automotive commercial, anamorphic 35 mm, shallow depth of field, moody dusk light, wet asphalt reflections, deep blacks, restrained blue accent light, photoreal, no text, no logos, no readable license plate`

Das Auto immer beschreiben als **„fictional premium German electric sedan with a modern twin-kidney-inspired grille“**. Kein echter Markenname, sonst lehnt Flow ab und es gibt Markenprobleme.

## Videos (16:9, 1080p, 8 s, „Frames to Video“ mit Start- und Endbild, wo möglich)

- **V1 Hero-Loop:** Low tracking shot, a dark grey fictional premium electric sedan emerges slowly from a concrete tunnel at dusk, headlights on, long shadows from pillars, volumetric light, slow push-in.
- **V2 Scroll-Drive (wichtigstes Video):** Locked parallel tracking shot, the sedan drives left to right at constant speed along a coastal mountain road at golden hour, strong motion blur on road and background, car sharp, one continuous take, no cuts. Start-Bild: Auto am linken Rand. End-Bild: Auto am rechten Rand.
- **V3 Datenstadt:** The sedan drives through a night city, long blue light trails, abstract glowing thin data lines floating in the air, calm and precise.
- **V4 Innenraum:** Macro slow dolly across a modern car dashboard, large curved touch display, steering wheel, ambient blue light (passt zu den Top-Beschwerden: Touchscreens, Lüftung).

## Bilder (16:9, 2K)

- **I1 Hero-Poster** = erstes Frame von V1 → `src/frontend/public/media/poster.jpg`
- **I2–I4 Szenario-Bilder** (Limousine, Kompaktwagenklasse; Studio im Nebel, Berglandschaft, Auto im Dreiviertel-Winkel) → `public/media/scenarios/<SZENARIO-ID>.jpg`, z. B. `G60-US.jpg`
- **I5 Split-Bild:** Auto in herbstlicher Berglandschaft, zwei Menschen auf Longboards (Lifestyle) → `public/media/split.jpg`
- **I6 Open-Graph-Bild** (1200×630, dunkel, Auto + Freiraum links für Text) → `src/frontend/app/opengraph-image.jpg`

## Ablauf

1. Bilder und Videos in Flow erzeugen, Dateien in `werkstatt/<name>/media/` ablegen.
2. `bash scripts/make_frames.sh werkstatt/<name>/media/v2.mp4` zerlegt V2 in WebP-Frames und schreibt das Manifest (Ziel ≤ 8 MB, das Repo ist öffentlich).
3. Fehlende Dateien sind kein Fehler: die Seite zeigt dann eine Studio-Szene mit Signallinien.
