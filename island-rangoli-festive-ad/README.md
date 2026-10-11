# Island Rangoli — Mega Festive Sale motion ad

15-second motion ad for the Island Rangoli festive campaign (Instagram ads).

| File | Size | Use |
|---|---|---|
| `output/IslandRangoli_FestiveSale_9x16.mp4` | 1080×1920 | Instagram Reels / Stories |
| `output/IslandRangoli_FestiveSale_16x9.mp4` | 1920×1080 | Feed / YouTube / web |

Both are H.264 at 30 fps with AAC audio normalised to −14 LUFS.

## Storyboard
The FLAT 60% OFF offer applies to **Deep Dwar only**, so the video never presents it as site-wide.

| Time | Scene |
|---|---|
| 0–2s | Rangoli mandala blooms ring by ring, then the Island Rangoli emblem and wordmark appear |
| 2–4.5s | Maroon/gold banner world, hanging diyas drop in, **Mega Festive Sale** and the **Live Now** ribbon |
| 4.5–7.5s | **Deep Dwar** product shot with the gold badge counting up to **Get FLAT 60% OFF**, and a price chip "Rs. 899 → from Rs. 349" |
| 7.5–10s | "Iconic Best Sellers" cards at their own site prices: Deep Mandapam (-52%) and Deep Shikha (-30%), each with a QUICK ADD tap |
| 10–12.5s | Lifestyle collage: "Light Up Your Space With Regal Colors" plus the five "Why Island Rangoli" chips |
| 12.5–15s | End card: hero photo, logo, "Deep Dwar · Flat 60% OFF", **SHOP NOW**, islandrangoli.com, delivery line |

Brand system, matched from the site: teal `#04709E`, cream `#FFF6E7`, banner maroon `#AD4B34`, gold `#E9A23B` / `#FDD993`, sale red `#E5483B`. Fonts are Quicksand (body and buttons), Italiana (thin display headings) and Playfair Display (bold banner serif).

## Rebuild
`./build.sh` needs Node with global `playwright`, Python 3 with numpy, and ffmpeg.
- `index.html` is the animation. It is deterministic: `seek(t)` draws the frame at time t. Open `index.html?f=9x16&play` or `?f=16x9&play` to preview, or `?t=6.5` to view a single frame.
- `render.mjs` captures every frame with headless Chromium and pipes it to ffmpeg.
- `music.py` generates the score and sound effects: sitar, tanpura, dhol, bells, risers and UI taps, timed to the cuts.
- `crop_assets.py` cut the product and lifestyle imagery out of the website screenshots.

Note: the images come from website screenshots (about 280px product shots, upscaled 2×). For the sharpest result, drop the original product photos into `assets/` under the same file names and re-run `./build.sh`.
