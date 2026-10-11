# ReSpec cockpit

The web interface a product manager works in. Next.js (App Router), Tailwind, TypeScript.
It does no math itself: every number and label comes ready from the backend, so the screen,
the CSV export and the decision memo always agree.

![Cockpit](../../docs/images/cockpit.png)

## Run

The backend has to be running first (see the [main README](../../README.md#try-it)).

```bash
npm ci
npm run dev          # development, http://localhost:3000
npm run build && npm run start     # production
npm run lint
```

The API address defaults to `http://localhost:8000`. To change it, set `NEXT_PUBLIC_API_URL`
in `.env.local` **before** building. It ends up in the browser, so never put a key there.

## Pages

| Route | What it is |
|---|---|
| `/` | Start page: scroll story with live numbers, scenario cards |
| `/models` | Pick a vehicle and market |
| `/cockpit` | Ranked requirements, ask in your own words, weight sliders, export |
| `/requirements/[id]` | Score breakdown, findings, quotes, assumptions, decision panel |
| `/audit` | Audit trail with chain check |
| `/insights` | Evidence vs. assumption, opportunities, trends, what we do not know |
| `/portfolio` | Compare markets and models |
| `/benchmarks` | Quality numbers per scenario, BMW vs. competitors |
| `/evidence` | Search every piece of evidence |
| `/guide` | Short in-app guide |

The selected scenario lives in the URL (`?scenario=G60-US`), so every view can be linked directly.

## Where things are

| Folder | Content |
|---|---|
| `app/` | One folder per route |
| `src/components/cockpit/` | Ranked list, lens panel, weight sliders, `useCockpit` state hook |
| `src/components/home/` | Start page sections (GSAP and Lenis are loaded only here) |
| `src/components/shell/` | Header, footer, assistant |
| `src/components/ui/` | Small shared building blocks (button, typography, card) |
| `src/lib/api.ts` | Every backend call in one place |
| `public/media/` | Photos for the start page and scenario cards |

Unit tests: `node --experimental-strip-types --test src/**/*.test.mjs`.
