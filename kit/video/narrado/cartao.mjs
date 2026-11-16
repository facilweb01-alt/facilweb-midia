// Cartão final animado (oferta + chamada), em duas versões: anúncio ("toque no botão") e post ("link na bio").
// Uso: node kit/video/narrado/cartao.mjs cartao.json anuncio|post 3.2 saida.mp4 [narracao.wav]
// cartao.json: {"l1","l2","l3","bolha","dica","url","cta_anuncio","cta_post","logo":"marca/logo.png" (relativo ao json),"cores":{...}}
// "" num campo remove a linha. Sem narração, sai mudo (a música do reel continua no acrossfade da junção).
import { createRequire } from "node:module";
import { mkdirSync, readFileSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const KIT = dirname(fileURLToPath(import.meta.url));
// Playwright da máquina (o mesmo do kit/design3d): não fixe versão, senão ele procura outro Chromium.
const { chromium } = createRequire(import.meta.url)("playwright");
const [cfg, modo = "anuncio", dur = "3.2", saida = `cartao-${modo}.mp4`, voz] = process.argv.slice(2);
const q = `/tmp/cartao_${modo}_${process.pid}`; rmSync(q, { recursive: true, force: true }); mkdirSync(q, { recursive: true });
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
const C = JSON.parse(readFileSync(cfg, "utf8"));
if (C.logo && !/^(file|https?|data):/.test(C.logo)) C.logo = pathToFileURL(resolve(dirname(resolve(cfg)), C.logo)).href; // logo relativa ao cartao.json
await p.goto(`file://${KIT}/cartao.html?modo=${modo}&c=${encodeURIComponent(JSON.stringify(C))}`);
await p.waitForFunction("window.pronto === true"); await p.evaluate("document.fonts.ready");
const n = Math.round(Number(dur) * 30);
for (let i = 0; i < n; i++) { await p.evaluate((t) => window.quadro(t), i / 30); await p.screenshot({ path: `${q}/f${String(i).padStart(4, "0")}.png` }); }
await b.close();
const audio = voz ? ["-i", voz] : ["-f", "lavfi", "-t", String(dur), "-i", "anullsrc=r=48000:cl=stereo"];
execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", "30", "-i", `${q}/f%04d.png`, ...audio, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", saida]);
rmSync(q, { recursive: true, force: true });
console.log("ok", saida, n, "quadros");
