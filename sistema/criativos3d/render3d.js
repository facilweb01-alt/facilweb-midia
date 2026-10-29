// Renderiza cenas 3D (PNG com fundo transparente) a partir de cenas.json.
// Uso: node render3d.js cenas.json pasta_saida [frames fps]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path'); const http = require('http');

const [, , cfgFile, outDir, framesArg, fpsArg] = process.argv;
const cenas = JSON.parse(fs.readFileSync(cfgFile, 'utf8'));
const frames = parseInt(framesArg || '1'); const fps = parseInt(fpsArg || '30');
fs.mkdirSync(outDir, { recursive: true });
const root = __dirname;
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  const ext = path.extname(p);
  res.writeHead(200, { 'Content-Type': { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png' }[ext] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(parseInt(process.env.PORTA || "8765"), async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const [nome, cfg] of Object.entries(cenas)) {
    const pg = await b.newPage({ viewport: { width: cfg.w, height: cfg.h } });
    await pg.goto('http://127.0.0.1:' + (process.env.PORTA || '8765') + '/cena.html');
    await pg.waitForFunction(() => window.pronto === true);
    await pg.evaluate((c) => window.montar(c), cfg);
    const n = cfg.frames || frames;
    for (let i = 0; i < n; i++) {
      if (n > 1) await pg.evaluate((t) => window.quadro(t), i / fps);
      const ext = cfg.fundo ? 'jpg' : 'png';
      const out = n > 1 ? path.join(outDir, nome, `f${String(i).padStart(4, '0')}.${ext}`) : path.join(outDir, `${nome}.${ext}`);
      fs.mkdirSync(path.dirname(out), { recursive: true });
      if (cfg.fundo) await pg.screenshot({ path: out, type: 'jpeg', quality: 92 });
      else await pg.locator('canvas').screenshot({ path: out, omitBackground: true });
    }
    await pg.close();
    console.log('ok', nome, n);
  }
  await b.close(); srv.close();
});
