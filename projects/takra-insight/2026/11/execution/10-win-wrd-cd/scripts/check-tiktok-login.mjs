// Is the INSTALLED UAT profile signed in to TikTok?
//
// TI-650 refuses recording unless it is (e2e/_helpers.js requireTikTokLogin), and the login lives in
// the `persist:tiktok` partition. Every WRD C/D case needs a TikTok session, so this decides whether
// those cases are runnable at all — and it distinguishes "Windows cannot load TikTok" from "this
// profile is simply signed out", which nobody had checked.
//
// Read-only. Reports cookie NAMES, counts and expiry only — never a value.

import { createRequire } from 'node:module';
import { writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const PROJ = 'C:\\Users\\Desktop\\Documents\\GitHub\\takra-insight\\apps\\desktop\\desktop\\';
const { _electron: electron } = createRequire(PROJ)('@playwright/test');
const OUT = process.env.OUT_DIR;
mkdirSync(OUT, { recursive: true });

const app = await electron.launch({
  executablePath: 'C:\\Program Files\\Takra Insight UAT\\Takra Insight UAT.exe',
  timeout: 180_000,
  env: (({ ELECTRON_RUN_AS_NODE, ...e }) => ({
    ...e, NODE_ENV: 'test', LHM_ENGINE_PORT: process.env.LHM_ENGINE_PORT || '8769',
  }))(process.env),
});
const win = await app.firstWindow({ timeout: 180_000 });
await win.waitForLoadState('domcontentloaded').catch(() => {});
await win.waitForTimeout(9000);

const info = await app.evaluate(async ({ session, app: electronApp }) => {
  const now = Date.now() / 1000;
  const out = { version: electronApp.getVersion(), userData: electronApp.getPath('userData'), partitions: {} };
  for (const part of ['persist:tiktok', 'persist:shopee']) {
    try {
      const s = session.fromPartition(part);
      const all = await s.cookies.get({});
      const tt = all.filter((c) => /tiktok\.com$/.test((c.domain || '').replace(/^\./, ''))
        || /shopee/.test(c.domain || ''));
      const named = (n) => {
        const hit = all.filter((c) => c.name === n && c.value && c.value.length > 0);
        if (!hit.length) return null;
        const c = hit[0];
        return {
          present: true, valueLength: c.value.length, domain: c.domain, httpOnly: !!c.httpOnly,
          expiresInHours: c.expirationDate ? +(((c.expirationDate - now) / 3600).toFixed(1)) : 'session',
        };
      };
      out.partitions[part] = {
        cookiesTotal: all.length, cookiesForDomain: tt.length,
        sessionid: named('sessionid'), sid_tt: named('sid_tt'), ttwid: named('ttwid'),
        names: [...new Set(all.map((c) => c.name))].slice(0, 30),
      };
    } catch (e) { out.partitions[part] = { error: String((e && e.message) || e).slice(0, 80) }; }
  }
  return out;
});

// the app's own rule, as e2e/_helpers.js signedInFromCookies applies it: a live sessionid with
// more than 24 h left
const tt = info.partitions['persist:tiktok'] || {};
const sid = tt.sessionid;
const signedIn = !!(sid && sid.present && (sid.expiresInHours === 'session' || sid.expiresInHours > 24));

console.log(JSON.stringify(info, null, 2));
console.log('\n================ VERDICT ================');
console.log(`build            : ${info.version}`);
console.log(`userData         : ${info.userData}`);
console.log(`tiktok cookies   : ${tt.cookiesTotal ?? '?'} (for tiktok.com: ${tt.cookiesForDomain ?? '?'})`);
console.log(`sessionid        : ${sid ? `present, ${sid.valueLength} chars, expires in ${sid.expiresInHours} h` : 'ABSENT'}`);
console.log(`sid_tt           : ${tt.sid_tt ? 'present' : 'ABSENT'}`);
console.log(`=> TikTok login  : ${signedIn ? 'SIGNED IN' : 'NOT SIGNED IN'}`);
console.log(signedIn
  ? '   so TI-650 is satisfied and a failure to start is NOT a login problem'
  : '   so TI-650 alone explains why no TikTok session can start on this profile');

writeFileSync(join(OUT, 'tiktok-login.json'), JSON.stringify({ ...info, signedIn }, null, 2), 'utf8');
try { await win.screenshot({ path: join(OUT, 'login-check.png'), fullPage: true, timeout: 20_000 }); } catch {}
await app.close();
