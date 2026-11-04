// TC-AUD-D.1 (tc-22110) on Windows — the Telegram message when a live's sound is lost.
//
// The case asks for a real broadcast with an assistant muting the mic. We never broadcast (QA
// ruling: we only watch other people's lives), and Mac did not either — its r184 run fed the live
// through LHM_FLV_URL and sent all-zero audio for 40 s while the picture kept going, which is the
// engine's "silence > 20 s" rule rather than a real mic switch. Same method here, same defaults
// (no LHM_WALL_* overrides, so the 20 s boundary under test is the shipped one).
//
// What is REAL in this run: the installed UAT build, the engine, the audio tap, the wall rule, the
// Telegram delivery loop, the QA bot and the QA group. Only the sound the app analyses is fed.
//
// The app's own calls to api.telegram.org are tapped PASS-THROUGH (recorded, then forwarded), so
// the exact bytes of the message are evidence and the message still reaches the group for the
// bold/link check in Telegram Web.

import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { writeFileSync, appendFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const PROJ = 'C:\\Users\\Desktop\\Documents\\GitHub\\takra-insight\\apps\\desktop\\desktop\\';
const { _electron: electron } = createRequire(PROJ)('@playwright/test');
const FFMPEG = 'C:\\Program Files\\Takra Insight UAT\\resources\\ffmpeg\\ffmpeg.exe';

const OUT = process.env.OUT_DIR;
const FLV = process.env.FLV_PATH;
const PORT = Number(process.env.FLV_PORT || 9501);
// where the silence sits inside the FLV (build-aud-d1.ps1)
const SILENCE_AT = Number(process.env.SILENCE_AT || 90);
const SILENCE_FOR = Number(process.env.SILENCE_FOR || 45);
const WATCH_MIN = Number(process.env.WATCH_MIN || 7);
mkdirSync(OUT, { recursive: true });

const env = {};
for (const line of readFileSync(PROJ + '.env.development', 'utf8').split(/\r?\n/)) {
  const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
  if (m) env[m[1]] = m[2];
}
const TIKTOK_LIVES = (env.BACKUP_CANDIDATES || '').split(',').map((s) => s.trim()).filter(Boolean)
  .map((h) => `https://www.tiktok.com/${h}/live`);
const SHOPEE = env.SHOPEE_LIVE_URL;

const R = { startedAt: new Date().toISOString(), flv: FLV, silenceAt: SILENCE_AT, silenceFor: SILENCE_FOR, streams: [] };
const log = (...a) => {
  const l = `[${new Date().toISOString().slice(11, 19)}] ` + a.join(' ');
  console.log(l);
  try { appendFileSync(join(OUT, 'run.log'), l + '\n', 'utf8'); } catch {}
};
const save = () => writeFileSync(join(OUT, 'results.json'), JSON.stringify(R, null, 2), 'utf8');

// ───────── the simulated live, paced in REAL time (-re), so 90 s of speech really take 90 s ─────────
const server = createServer((req, res) => {
  const connectedAt = Date.now();
  R.streams.push({ connectedAt: new Date(connectedAt).toISOString(), url: req.url });
  log(`>>> stream pulled (${req.url}) — silence window starts at +${SILENCE_AT}s `
    + `(${new Date(connectedAt + SILENCE_AT * 1000).toISOString().slice(11, 19)}Z)`);
  res.writeHead(200, { 'Content-Type': 'video/x-flv', 'Cache-Control': 'no-store' });
  const ff = spawn(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-re', '-i', FLV, '-c', 'copy', '-f', 'flv', 'pipe:1']);
  ff.stdout.pipe(res);
  ff.stderr.on('data', (d) => { try { appendFileSync(join(OUT, 'mockflv.log'), String(d), 'utf8'); } catch {} });
  res.on('close', () => { try { ff.kill('SIGKILL'); } catch {} });
});
await new Promise((r) => server.listen(PORT, '127.0.0.1', r));
log(`serving the simulated live on http://127.0.0.1:${PORT}/live.flv`);

const app = await electron.launch({
  executablePath: 'C:\\Program Files\\Takra Insight UAT\\Takra Insight UAT.exe',
  timeout: 180_000,
  // BLANK_PAGE=1 adds the repo's own QA hook (lib/blank-live-page-hook.js, dev+UAT only). Without it
  // the live page's CDP capture overwrites LHM_FLV_URL with the real CDN url, so the engine measures
  // the REAL live's audio and the fed silence is never heard (measured by session 0b, 2026-11-04).
  env: (({ ELECTRON_RUN_AS_NODE, ...e }) => ({
    ...e, NODE_ENV: 'test', LHM_FLV_URL: `http://127.0.0.1:${PORT}/live.flv`,
    ...(process.env.BLANK_PAGE === '1' ? { LHM_TEST_BLANK_LIVE_PAGE: '999' } : {}),
  }))(process.env),
});
const win = await app.firstWindow({ timeout: 180_000 });
await win.waitForLoadState('domcontentloaded').catch(() => {});
await win.waitForTimeout(12_000);

const body = async () => { try { return await win.evaluate(() => document.body.innerText || ''); } catch { return ''; } };
const shot = async (n) => { try { await win.screenshot({ path: join(OUT, n + '.png'), timeout: 25_000, fullPage: true }); } catch {} };
const dump = (n, t) => { try { writeFileSync(join(OUT, n + '.txt'), t ?? '', 'utf8'); } catch {} };
const go = async (hash, ms = 5000) => { await win.evaluate((h) => { location.hash = h; }, hash); await win.waitForTimeout(ms); };

/** Record every Telegram call the app makes, then forward it unchanged. */
const armTap = () => app.evaluate(async ({ net }) => {
  const g = globalThis;
  g.__qaTg = g.__qaTg || [];
  if (g.__qaTapped) return 'already';
  g.__qaTapped = true;
  const wrap = (holder, key) => {
    const orig = holder[key];
    holder[key] = async function (input, init) {
      const url = typeof input === 'string' ? input : (input && input.url) || '';
      if (/api\.telegram\.org/.test(url)) {
        let body = null;
        try {
          const b = init && init.body;
          if (typeof b === 'string') body = b;
          else if (b) body = '(binary ' + (b.byteLength || b.length || '?') + ' bytes)';
        } catch {}
        const method = (url.split('/').pop() || '').split('?')[0];
        const rec = { at: Date.now(), method, body };
        g.__qaTg.push(rec);
        const res = await orig.call(this, input, init);
        try { rec.status = res.status; } catch {}
        return res;
      }
      return orig.call(this, input, init);
    };
  };
  wrap(g, 'fetch');
  if (net && net.fetch) wrap(net, 'fetch');
  return 'armed';
});
const readTap = () => app.evaluate(() => (globalThis.__qaTg || []).slice());

const switchRows = () => win.evaluate(() => Array.from(document.querySelectorAll('[role="switch"]')).map((s, i) => {
  let n = s.closest('div');
  for (let k = 0; k < 4 && n; k++) { if ((n.innerText || '').trim().length > 12) break; n = n.parentElement; }
  return { i, checked: s.getAttribute('aria-checked'), disabled: s.disabled || s.getAttribute('aria-disabled') === 'true',
    near: ((n && n.innerText) || '').replace(/\s+/g, ' ').trim().slice(0, 110) };
})).catch(() => []);

const setSwitch = async (i, want) => {
  const rows = await switchRows();
  const row = rows[i];
  if (!row || row.disabled || row.checked === String(want)) return row;
  await win.locator('[role="switch"]').nth(i).click({ timeout: 15_000 });
  await win.waitForTimeout(4000);
  return (await switchRows())[i];
};

try {
  R.tap = await armTap();
  log('telegram tap:', R.tap);

  // ───────── preconditions ─────────
  await go('#/settings/privacy', 6000);
  const priv = await body();
  dump('00-privacy', priv);
  R.audioConsent = /ฟังเสียงพูด/.test(priv) ? (/กำลังใช้งาน/.test(priv) ? 'active' : 'present-but-not-active') : 'not-found';
  log('audio consent:', R.audioConsent);
  await shot('00-privacy');

  await go('#/settings/telegram', 6000);
  dump('01-telegram-before', await body());
  R.switchesBefore = await switchRows();
  log('switches before:', JSON.stringify(R.switchesBefore));
  // the case: delivery ON, "แนบภาพโฮสต์ตอนเกิดเรื่อง" OFF
  const delivery = R.switchesBefore.findIndex((s) => /ส่งแจ้งเตือน|เข้ากลุ่ม/.test(s.near));
  const photo = R.switchesBefore.findIndex((s) => /แนบภาพโฮสต์/.test(s.near));
  R.idx = { delivery, photo };
  log('switch indexes =>', JSON.stringify(R.idx));
  if (delivery >= 0) R.deliveryAfter = await setSwitch(delivery, true);
  else R.deliveryAfter = await setSwitch(0, true);
  if (photo >= 0) R.photoAfter = await setSwitch(photo, false);
  R.switchesAfter = await switchRows();
  log('switches after:', JSON.stringify(R.switchesAfter));
  await shot('01-telegram');
  save();

  // ───────── pick a live: TikTok first (as Mac did), Shopee as the fallback ─────────
  const tryLive = async (url, kind) => {
    log(`--- trying ${kind}: ${url}`);
    await go('#/dashboard', 4000);
    const box = win.locator('input[placeholder*="วางลิงก์ไลฟ์"]').first();
    if (!(await box.count())) { log('    no link box on the dashboard'); return false; }
    await box.fill(url);
    const open = win.getByRole('button', { name: 'เปิดดูไลฟ์' }).first();
    if (!(await open.count())) { log('    no "เปิดดูไลฟ์" button'); return false; }
    await open.click({ timeout: 15_000 });
    let sawFollow = false;
    for (let i = 0; i < 25; i++) {
      await win.waitForTimeout(3000);
      const t = await body();
      if (/เริ่มติดตาม/.test(t)) { sawFollow = true; break; }
    }
    dump(`live-${kind}-prescreen`, await body());
    await shot(`live-${kind}-prescreen`);
    if (!sawFollow) { log('    never offered "เริ่มติดตาม"'); return false; }
    await win.getByRole('button', { name: 'เริ่มติดตาม' }).first().click({ timeout: 15_000 }).catch(() => {});
    await win.waitForTimeout(5000);
    const rec = win.getByRole('button', { name: 'เริ่มบันทึก' }).first();
    if (!(await rec.count())) { log('    no "เริ่มบันทึก" button'); return false; }
    await rec.click({ timeout: 15_000 });
    await win.waitForTimeout(15_000);
    await go('#/live', 8000);
    const t = await body();
    const started = !/ยังไม่มีไลฟ์ที่กำลังบันทึก/.test(t);
    log(`    recording started: ${started}`);
    dump(`live-${kind}-after-start`, t);
    await shot(`live-${kind}-after-start`);
    return started;
  };

  let used = null;
  for (const url of TIKTOK_LIVES.slice(0, 3)) {
    if (await tryLive(url, 'tiktok-' + url.split('@')[1].split('/')[0])) { used = { platform: 'tiktok', url }; break; }
  }
  if (!used && await tryLive(SHOPEE, 'shopee')) used = { platform: 'shopee', url: SHOPEE };
  if (!used) throw new Error('no live could be recorded on this machine');
  R.live = used;
  R.recordingStartedAt = new Date().toISOString();
  log(`*** recording a ${used.platform} live with the simulated feed — ${used.url}`);
  save();

  // ───────── watch for the alert ─────────
  const t0 = Date.now();
  const samples = [];
  let firstAlert = null;
  let firstTelegram = null;
  while ((Date.now() - t0) / 60000 < WATCH_MIN) {
    await new Promise((r) => setTimeout(r, 10_000));
    const txt = await body();
    const tg = await readTap();
    const min = +((Date.now() - t0) / 60000).toFixed(2);
    const onCard = /เสียงไลฟ์หาย/.test(txt);
    samples.push({ min, onCard, tgCalls: tg.length });
    if (onCard && !firstAlert) {
      firstAlert = { min, at: new Date().toISOString() };
      log(`*** "เสียงไลฟ์หาย" on screen at +${min} min`);
      dump('alert-card', txt);
      await shot('alert-card');
    }
    const alertSend = tg.find((c) => /sendMessage|sendPhoto/.test(c.method || '')
      && /%E0%B9%80%E0%B8%AA%E0%B8%B5%E0%B8%A2|เสียงไลฟ์หาย/.test(String(c.body || '')));
    if (alertSend && !firstTelegram) {
      firstTelegram = { min, at: new Date(alertSend.at).toISOString(), method: alertSend.method, status: alertSend.status };
      log(`*** Telegram ${alertSend.method} with the audio-lost message at +${min} min (HTTP ${alertSend.status})`);
      await shot('alert-sent');
    }
    if (samples.length % 3 === 0) {
      R.samples = samples; R.firstAlert = firstAlert; R.firstTelegram = firstTelegram;
      R.telegramCalls = tg; save();
      log(`  +${min} min  card=${onCard}  telegram calls=${tg.length}`);
    }
  }
  R.samples = samples;
  R.firstAlert = firstAlert;
  R.firstTelegram = firstTelegram;
  R.telegramCalls = await readTap();
  writeFileSync(join(OUT, 'telegram-outbox.json'), JSON.stringify(R.telegramCalls, null, 2), 'utf8');
  dump('zz-final-body', await body());
  await shot('zz-final');
  save();

  // ───────── stop, leaving the machine usable ─────────
  await go('#/session/recording', 6000);
  for (const n of ['หยุดบันทึก', 'หยุดติดตาม']) {
    try {
      const b = win.getByRole('button', { name: n }).first();
      if (await b.count()) {
        await b.click({ timeout: 10_000 });
        await win.waitForTimeout(2500);
        const yes = win.getByRole('button', { name: n }).last();
        if (await yes.count()) await yes.click({ timeout: 8000 }).catch(() => {});
        log('stopped:', n);
        break;
      }
    } catch {}
  }
  await win.waitForTimeout(12_000);
  await shot('zz-stopped');
} catch (e) {
  log('FATAL', String((e && e.message) || e));
  R._error = String((e && e.message) || e);
  await shot('fatal');
  try { R.telegramCalls = await readTap(); } catch {}
} finally {
  R.finishedAt = new Date().toISOString();
  save();
  log('closing');
  try { await app.close(); } catch {}
  server.close();
}
