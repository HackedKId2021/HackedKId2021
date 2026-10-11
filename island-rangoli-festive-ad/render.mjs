// node render.mjs <9x16|16x9> [out.mp4] [fps]   |   node render.mjs <fmt> --stills t1,t2,... (PNG previews)
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright'); // resolves via NODE_PATH (global install)
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const [fmt = '9x16', outArg, fpsArg] = process.argv.slice(2);
const [W, H] = fmt === '9x16' ? [1080, 1920] : [1920, 1080];
const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('PAGE ERROR', e); process.exit(1); });
await page.goto(pathToFileURL(path.resolve('index.html')).href + `?f=${fmt}`);
await page.evaluate(() => window.ready);
const shot = t => page.evaluate(t => window.seek(t), t).then(() => page.screenshot({ type: 'png' }));

if (outArg === '--stills') {
  for (const t of fpsArg.split(',').map(Number)) {
    await page.evaluate(t => window.seek(t), t);
    await page.screenshot({ path: `stills/${fmt}_${t.toFixed(2)}.png` });
  }
} else {
  const fps = +(fpsArg || 30), dur = await page.evaluate(() => window.DURATION), n = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outArg || `silent_${fmt}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const buf = await shot(i / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) console.log(`${fmt} frame ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
