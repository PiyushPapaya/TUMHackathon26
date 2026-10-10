# Google-Flow-Prompts für die Startseite (echte BMW-Modelle)

Stil-Anker, hinten an jeden Prompt: `cinematic automotive commercial, anamorphic 35 mm, shallow depth of field, moody dusk light, wet asphalt reflections, deep blacks, restrained blue accent light, photoreal, accurate real-world car proportions, no text, no readable license plate, blurred license plate`

Lehnt Flow ein Modell ab: "BMW 5 Series" ersetzen durch "premium German electric sedan with a twin-kidney grille".

## Formate
- Bilder: 16:9 (2K), nur `split.jpg` 4:3. Video: 16:9, 1080p, 8 s. 9:16 wird nicht gebraucht (mittig zuschneiden).
- Auto bei allen Motiven im mittleren Drittel halten, untere Bildhälfte ruhig (dort liegt Text).

## Schon eingebunden (`src/frontend/public/media/`)
`poster.jpg`, `split.jpg`, `scenarios/G60-US|G60-EU|G70-US|G70-EU|F70-EU.jpg`

## Noch offen
- **`scenarios/G68-CN.jpg`:** `BMW 5 Series long wheelbase (G68), three-quarter front view, futuristic Asian megacity at night, neon reflections on wet street, [Stil-Anker]`
- **V2 Scroll-Drive** (macht die Auto-Szene beim Scrollen lebendig, Pflicht für den Effekt):
  `Locked parallel tracking shot, a dark grey BMW 5 Series (G60) drives from the left edge to the right edge of the frame at constant speed along a coastal mountain road at golden hour, strong motion blur on road and background, the car stays sharp, one continuous take, no cuts, no camera shake, [Stil-Anker]`
  Flow "Frames to Video": Startbild = Auto am linken Rand, Endbild = Auto am rechten Rand. Dauer 8 s.
- Optional V1 Hero-Loop: `Low tracking shot, BMW i5 slowly emerging from a concrete tunnel at dusk, headlights on, long shadows from pillars, volumetric light, slow push-in`

## Video einbinden
`bash scripts/make_frames.sh werkstatt/<name>/media/v2.mp4`, dann neu bauen. Ziel höchstens 8 MB (sonst fps oder Breite senken). Mehr: `docs/DEPLOY.md`.
