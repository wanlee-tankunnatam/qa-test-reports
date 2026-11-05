// TC-WRD C/D/G runner on the INSTALLED UAT build.
//
// The cases ask QA to broadcast and speak. We never broadcast (standing QA ruling: we watch other
// people's lives only), so the words come from real Thai speech fed through LHM_FLV_URL while a
// real third-party room supplies the session and its platform. That is the same method Mac used.
//
// Two things this runner does that the earlier one got wrong:
//   1. It dumps the PRE-SCREEN right after the press, BEFORE navigating away, so a refusal banner
//      (`sessionPre.liveEndedBlock`) is captured instead of lost.
//   2. It re-probes the room's live status in the seconds before pressing and computes the verdict
//      in-script, so "the room had ended" and "the app misread a live room" cannot be conflated
//      after the fact.
//
// env: FLV_PATH FLV_PORT OUT_DIR TOTAL_S PLATFORM(tiktok|shopee) HANDLES SHOPEE_URL WATCH_S

import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { writeFileSync, appendFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const PROJ = 'C:\\Users\\Desktop\\Documents\\GitHub\\takra-insight\\apps\\desktop\\desktop\\';
const { _electron: electron } = createRequire(PROJ)('@playwright/test');
const FFMPEG = 'C:\\Program Files\\Takra Insight UAT\\resources\\ffmpeg\\ffmpeg.exe';
const APP = 'C:\\Program Files\\Takra Insight UAT\\Takra Insight UAT.exe';

const OUT = process.env.OUT_DIR;
const FLV = process.env.FLV_PATH;
const PORT = Number(process.env.FLV_PORT || 9500);
const TOTAL_S = Number(process.env.TOTAL_S || 500);
const PLATFORM = process.env.PLATFORM || 'tiktok';
const WATCH_S = Number(process.env.WATCH_S || TOTAL_S + 60);
const HANDLES = (process.env.HANDLES || '').split(',').map((s) => s.trim().replace(/^@/, '')).filter(Boolean);
mkdirSync(OUT, { recursive: true });

const env = {};
for (const line of readFileSync(PROJ + '.env.development', 'utf8').split(/\r?\n/)) {
  const m = /^([A-Z0-9_]+)=(.*)$/.exec(line.trim());
  if (m) env[m[1]] = m[2];
}
const SHOPEE = process.env.SHOPEE_URL || env.SHOPEE_LIVE_URL;

const R = { startedAt: new Date().toISOString(), flv: FLV, platform: PLATFORM, totalS: TOTAL_S, streams: [], attempts: [] };
const log = (...a) => {
  const l = `[${new Date().toISOString().slice(11, 19)}] ` + a.join(' ');
  console.log(l);
  try { appendFileSync(join(OUT, 'run.log'), l + '\n', 'utf8'); } catch {}
};
const save = () => writeFileSync(join(OUT, 'results.json'), JSON.stringify(R, null, 2), 'utf8');

// ───────── live-status probe (read-only, TikTok's own endpoint) ─────────
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
async function probe(handle) {
  const url = `https://www.tiktok.com/api-live/user/room/?aid=1988&sourceType=54&uniqueId=${encodeURIComponent(handle)}`;
  try {
    const res = await fetch(url, { headers: { 'User-Agent': UA, Accept: 'application/json' } });
    const j = await res.json();
    const room = (j && j.data && j.data.liveRoom) || {};
    return { handle, status: room.status ?? null, title: (room.title || '').slice(0, 40), at: new Date().toISOString() };
  } catch (e) {
    return { handle, status: null, error: String((e && e.message) || e).slice(0, 60), at: new Date().toISOString() };
  }
}

// ───────── the simulated live, paced in real time ─────────
const server = createServer((req, res) => {
  const at = Date.now();
  R.streams.push({ connectedAt: new Date(at).toISOString(), url: req.url });
  log(`>>> stream pulled (${req.url}) — t0 for THIS connection`);
  res.writeHead(200, { 'Content-Type': 'video/x-flv', 'Cache-Control': 'no-store' });
  const ff = spawn(FFMPEG, ['-hide_banner', '-loglevel', 'error', '-re', '-i', FLV, '-c', 'copy', '-f', 'flv', 'pipe:1']);
  ff.stdout.pipe(res);
  ff.stderr.on('data', (d) => { try { appendFileSync(join(OUT, 'mockflv.log'), String(d), 'utf8'); } catch {} });
  res.on('close', () => { try { ff.kill('SIGKILL'); } catch {} });
});
await new Promise((r) => server.listen(PORT, '127.0.0.1', r));
log(`serving the simulated live on http://127.0.0.1:${PORT}/live.flv`);

const app = await electron.launch({
  executablePath: APP,
  timeout: 180_000,
  env: (({ ELECTRON_RUN_AS_NODE, ...e }) => ({
    ...e, NODE_ENV: 'test', LHM_FLV_URL: `http://127.0.0.1:${PORT}/live.flv`,
  }))(process.env),
});
const win = await app.firstWindow({ timeout: 180_000 });
await win.waitForLoadState('domcontentloaded').catch(() => {});
await win.waitForTimeout(12_000);

const body = async () => { try { return await win.evaluate(() => document.body.innerText || ''); } catch { return ''; } };
const shot = async (n) => { try { await win.screenshot({ path: join(OUT, n + '.png'), timeout: 25_000, fullPage: true }); } catch {} };
const dump = (n, t) => { try { writeFileSync(join(OUT, n + '.txt'), t ?? '', 'utf8'); } catch {} };
const go = async (hash, ms = 5000) => { await win.evaluate((h) => { location.hash = h; }, hash); await win.waitForTimeout(ms); };

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
        let b = null;
        try { const x = init && init.body; if (typeof x === 'string') b = x; else if (x) b = '(binary)'; } catch {}
        const rec = { at: Date.now(), method: (url.split('/').pop() || '').split('?')[0], body: b };
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

try {
  R.tap = await armTap();
  log('telegram tap:', R.tap);

  // ───────── preconditions ─────────
  await go('#/settings/privacy', 6000);
  const priv = await body();
  dump('00-privacy', priv);
  R.audioConsentText = /ฟังเสียงพูด/.test(priv) ? (/กำลังใช้งาน/.test(priv) ? 'active' : 'present-not-active') : 'not-found';
  log('audio consent (screen):', R.audioConsentText);

  await go('#/settings/telegram', 6000);
  const rows = await switchRows();
  R.switchesBefore = rows;
  const delivery = rows.findIndex((s) => /ส่งแจ้งเตือน|เข้ากลุ่ม/.test(s.near));
  const photo = rows.findIndex((s) => /แนบภาพโฮสต์/.test(s.near));
  if (delivery >= 0 && rows[delivery].checked !== 'true' && !rows[delivery].disabled) {
    await win.locator('[role="switch"]').nth(delivery).click({ timeout: 15_000 }); await win.waitForTimeout(3500);
  }
  if (photo >= 0 && rows[photo].checked === 'true' && !rows[photo].disabled) {
    await win.locator('[role="switch"]').nth(photo).click({ timeout: 15_000 }); await win.waitForTimeout(3500);
  }
  R.switchesAfter = await switchRows();
  log('switches after:', JSON.stringify(R.switchesAfter));
  save();

  // ───────── start a session, with the probe/press race recorded ─────────
  const tryOne = async (url, kind, handle) => {
    const att = { kind, url, handle: handle || null };
    log(`--- attempt ${kind}: ${url}`);
    await go('#/dashboard', 4000);
    const box = win.locator('input[placeholder*="วางลิงก์ไลฟ์"]').first();
    if (!(await box.count())) { att.fail = 'no link box'; R.attempts.push(att); return false; }
    await box.fill(url);
    const open = win.getByRole('button', { name: 'เปิดดูไลฟ์' }).first();
    if (!(await open.count())) { att.fail = 'no เปิดดูไลฟ์ button'; R.attempts.push(att); return false; }
    await open.click({ timeout: 15_000 });

    let ready = false;
    for (let i = 0; i < 22; i++) {
      await win.waitForTimeout(3000);
      if (/เริ่มติดตาม/.test(await body())) { ready = true; break; }
    }
    att.ctaOffered = ready;
    dump(`att-${kind}-prescreen`, await body());
    await shot(`att-${kind}-prescreen`);
    if (!ready) { att.fail = 'never offered เริ่มติดตาม'; R.attempts.push(att); return false; }

    await win.getByRole('button', { name: 'เริ่มติดตาม' }).first().click({ timeout: 15_000 }).catch(() => {});
    // the name modal ("ตั้งชื่อเซสชัน") can take a few seconds; the run that worked waited 5 s, so
    // poll instead of guessing a single delay
    let rec = null;
    for (let i = 0; i < 8; i++) {
      await win.waitForTimeout(2500);
      const cand = win.getByRole('button', { name: 'เริ่มบันทึก' }).first();
      if (await cand.count()) { rec = cand; break; }
    }
    if (!rec) {
      att.fail = 'no เริ่มบันทึก button after 20s';
      att.modalBody = (await body()).replace(/\s+/g, ' ').slice(0, 400);
      dump(`att-${kind}-no-modal`, await body());
      await shot(`att-${kind}-no-modal`);
      R.attempts.push(att); return false;
    }

    // re-probe in the seconds immediately before the press
    if (handle) { att.probeBeforePress = await probe(handle); log('   probe before press:', JSON.stringify(att.probeBeforePress)); }
    att.pressedAt = new Date().toISOString();
    await rec.click({ timeout: 15_000 });

    // THE FIX: read the pre-screen before going anywhere
    await win.waitForTimeout(3000);
    const afterPress = await body();
    dump(`att-${kind}-after-press`, afterPress);
    await shot(`att-${kind}-after-press`);
    att.refusalBannerShown = /ยังไม่ได้เปิดหน้าไลฟ์ของช่องที่ต้องการ|ไลฟ์จบแล้ว/.test(afterPress);

    await win.waitForTimeout(10_000);
    await go('#/live', 8000);
    const liveTxt = await body();
    att.started = !/ยังไม่มีไลฟ์ที่กำลังบันทึก/.test(liveTxt);
    dump(`att-${kind}-live`, liveTxt);

    const st = att.probeBeforePress ? att.probeBeforePress.status : undefined;
    att.verdict = att.started ? 'started'
      : st === 2 && att.refusalBannerShown ? 'APP-MISREADS-LIVE-STATUS'
      : st === 4 ? 'room-really-ended (TI-652 consistent)'
      : 'refused, probe inconclusive';
    log(`   started=${att.started}  banner=${att.refusalBannerShown}  verdict=${att.verdict}`);
    R.attempts.push(att);
    save();
    return att.started;
  };

  let used = null;
  if (PLATFORM === 'shopee') {
    // env carries three Shopee lives; a shop whose live has ended never reaches the name modal, so
    // try each rather than failing on the first
    const urls = [SHOPEE, env.SHOPEE_LIVE_URL_2, env.SHOPEE_LIVE_URL_3].filter(Boolean);
    for (const u of urls) {
      const id = (/session=(\d+)/.exec(u) || [, 'x'])[1];
      if (await tryOne(u, 'shopee-' + id, null)) { used = { platform: 'shopee', url: u }; break; }
    }
  } else {
    const probes = [];
    for (const h of HANDLES) probes.push(await probe(h));
    R.probeSweep = probes;
    log('probe sweep:', JSON.stringify(probes));
    const ordered = [...HANDLES].sort((a, b) => {
      const sa = (probes.find((p) => p.handle === a) || {}).status === 2 ? 0 : 1;
      const sb = (probes.find((p) => p.handle === b) || {}).status === 2 ? 0 : 1;
      return sa - sb;
    });
    for (const h of ordered) {
      if (await tryOne(`https://www.tiktok.com/@${h}/live`, 'tiktok-' + h, h)) { used = { platform: 'tiktok', url: `https://www.tiktok.com/@${h}/live`, handle: h }; break; }
    }
  }
  if (!used) throw new Error('no live could be recorded');
  R.live = used;
  R.recordingStartedAt = new Date().toISOString();
  log(`*** recording ${used.platform} ${used.url}`);
  save();

  // ───────── watch the live page for the risk warnings ─────────
  const WATCH_FOR = PLATFORM === 'shopee'
    ? ['พาลูกค้าออกนอก Shopee', 'คำเสี่ยงต่อกฎแพลตฟอร์ม', 'พูดคำหยาบ']
    : ['คำต้องห้าม TikTok', 'พาลูกค้าออกนอก TikTok', 'พูดคำหยาบ'];
  const firstSeen = {};
  const samples = [];
  const t0 = Date.now();
  while ((Date.now() - t0) / 1000 < WATCH_S) {
    await new Promise((r) => setTimeout(r, 15_000));
    const txt = await body();
    const el = +((Date.now() - t0) / 1000).toFixed(0);
    const hits = WATCH_FOR.filter((w) => txt.includes(w));
    samples.push({ atS: el, hits, tg: (await readTap()).length });
    for (const w of hits) {
      if (!firstSeen[w]) {
        firstSeen[w] = { atS: el, at: new Date().toISOString() };
        log(`*** "${w}" on the live page at +${el}s`);
        dump(`seen-${WATCH_FOR.indexOf(w)}`, txt);
        await shot(`seen-${WATCH_FOR.indexOf(w)}`);
      }
    }
    if (samples.length % 4 === 0) {
      R.samples = samples; R.firstSeen = firstSeen; R.telegramCalls = await readTap(); save();
      log(`  +${el}s  hits=${JSON.stringify(hits)}  tg=${samples[samples.length - 1].tg}`);
    }
  }
  R.samples = samples;
  R.firstSeen = firstSeen;
  R.telegramCalls = await readTap();
  writeFileSync(join(OUT, 'telegram-outbox.json'), JSON.stringify(R.telegramCalls, null, 2), 'utf8');
  dump('zz-live-final', await body());
  await shot('zz-live-final');
  save();

  // ───────── stop, then read the transcript page ─────────
  await go('#/session/recording', 6000);
  for (const n of ['หยุดบันทึก', 'หยุดติดตาม']) {
    try {
      const b = win.getByRole('button', { name: n }).first();
      if (await b.count()) {
        await b.click({ timeout: 10_000 });
        await win.waitForTimeout(2500);
        const yes = win.getByRole('button', { name: n }).last();
        if (await yes.count()) await yes.click({ timeout: 8000 }).catch(() => {});
        log('stopped via', n);
        break;
      }
    } catch {}
  }
  await win.waitForTimeout(20_000);

  await go('#/sessions', 9000);
  dump('10-sessions', await body());
  await shot('10-sessions');
  // open the newest session row
  const links = await win.evaluate(() => Array.from(document.querySelectorAll('a[href*="/sessions/"],a[href*="/session/"]'))
    .map((a) => a.getAttribute('href')).filter(Boolean).slice(0, 12));
  R.sessionLinks = links;
  log('session links:', JSON.stringify(links.slice(0, 5)));
  if (links.length) {
    await go(links[0].replace(/^#/, ''), 10_000);
    dump('11-session-detail', await body());
    await shot('11-session-detail');
    const tr = win.getByRole('button', { name: 'บทพูด' }).first();
    if (await tr.count()) {
      await tr.click({ timeout: 15_000 });
      await win.waitForTimeout(8000);
      const txt = await body();
      dump('12-transcript', txt);
      await shot('12-transcript');
      R.transcriptLabels = ['คำหยาบ', 'คำต้องห้าม', 'นอก TikTok'].filter((w) => txt.includes(w));
      R.transcriptReasons = [
        'TikTok ห้ามใช้คำหยาบหรือคำลามกดูถูกผู้อื่นในไลฟ์',
        'TikTok Shop ห้ามโฆษณาเกินจริงหรืออ้างผลที่พิสูจน์ไม่ได้',
        'TikTok Shop ห้ามชวนลูกค้าไปซื้อหรือโอนเงินนอกแพลตฟอร์ม',
      ].filter((w) => txt.includes(w));
      log('transcript labels present:', JSON.stringify(R.transcriptLabels));
      // hover each risk badge to pull its tooltip (title attr or rendered tip)
      const tips = await win.evaluate(() => {
        const out = [];
        for (const el of Array.from(document.querySelectorAll('[title]'))) {
          const t = (el.getAttribute('title') || '').trim();
          if (t.length > 8) out.push({ title: t.slice(0, 160), text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 60) });
        }
        return out.slice(0, 40);
      }).catch(() => []);
      R.titleTooltips = tips;
      dump('13-tooltips', JSON.stringify(tips, null, 2));
    } else {
      log('no "บทพูด" button on the session detail page');
      R.transcriptMissing = true;
    }
  }
  save();
  await shot('zz-done');
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
