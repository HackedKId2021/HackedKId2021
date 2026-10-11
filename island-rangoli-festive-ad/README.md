# Island Rangoli — Mega Festive Sale motion ad

20-second motion ad for the Island Rangoli festive campaign (Instagram ads).

| File | Size | Use |
|---|---|---|
| `output/IslandRangoli_FestiveSale_9x16.mp4` | 1080×1920 | Instagram Reels / Stories |
| `output/IslandRangoli_FestiveSale_16x9.mp4` | 1920×1080 | Feed / YouTube / web |

Both are H.264 at 30 fps with AAC audio normalised to −14 LUFS.

## Storyboard
| Time | Scene |
|---|---|
| 0–3s | Rangoli mandala blooms ring by ring (white outlines, powder-texture colours), then the Island Rangoli emblem, wordmark and "Evolving Traditional Art" appear |
| 3–6s | Maroon/gold banner world, hanging diyas drop in and swing, **Mega Festive Sale** and the **Live Now** ribbon |
| 6–9s | Gold medallion slams in, counter rolls up to **Get FLAT 60% OFF**, marigold petal burst, "Limited Period Offer" |
| 9–14s | "Iconic Best Sellers" carousel styled like the site's product cards: Deep Dwar, Swarn, Deep Mandapam, Nity Crochet. On each card the old price is struck out, the sale price pops in and QUICK ADD is tapped (→ "Added to cart") |
| 14–17s | Collage of lifestyle photos: "Light Up Your Space With Regal Colors", plus the five "Why Island Rangoli Stands Out" chips |
| 17–20s | End card: hero photo, logo, "Flat 60% OFF", pulsing **SHOP NOW** with taps, islandrangoli.com, "PAN India 5–7 days" delivery line |

Brand system, matched from the site: teal `#04709E`, cream `#FFF6E7`, banner maroon `#AD4B34`, gold `#E9A23B` / `#FDD993`, sale red `#E5483B`. Fonts are Quicksand (body and buttons), Italiana (thin display headings) and Playfair Display (bold banner serif).

## Rebuild
`./build.sh` needs Node with global `playwright`, Python 3 with numpy, and ffmpeg.
- `index.html` is the animation. It is deterministic: `seek(t)` draws the frame at time t. Open `index.html?f=9x16&play` or `?f=16x9&play` to preview, or `?t=6.5` to view a single frame.
- `render.mjs` captures every frame with headless Chromium and pipes it to ffmpeg.
- `music.py` generates the score and sound effects: sitar, tanpura, dhol, bells, risers and UI taps, timed to the cuts.
- `crop_assets.py` cut the product and lifestyle imagery out of the website screenshots.

Note: the images come from website screenshots (about 280px product shots, upscaled 2×). For the sharpest result, drop the original product photos into `assets/` under the same file names and re-run `./build.sh`.
