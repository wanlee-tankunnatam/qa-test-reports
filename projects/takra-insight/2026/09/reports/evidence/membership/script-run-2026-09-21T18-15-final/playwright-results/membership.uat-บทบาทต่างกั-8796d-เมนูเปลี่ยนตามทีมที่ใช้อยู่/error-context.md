# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> บทบาทต่างกันในแต่ละทีม (เจ้าของ "ทีมของ QA Tester" · โฮสต์ใน "ทีมของ kachain") >> TC-MEM-D.6 (uat): บัญชีเดียวมีบทบาทต่างกันในแต่ละทีม เมนูเปลี่ยนตามทีมที่ใช้อยู่
- Location: e2e/uat/membership.uat.spec.js:326:3

# Error details

```
TimeoutError: locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'โปรไฟล์และบัญชี' }).first()

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - banner [ref=e4]:
    - button "กลับ" [ref=e5] [cursor=pointer]:
      - img [ref=e6]
    - generic [ref=e8]:
      - heading "สมาชิกและบทบาท" [level=1] [ref=e9]
      - paragraph [ref=e10]: กำหนดบทบาทใน Takra Insight ให้สมาชิกในพื้นที่ทำงานนี้
  - main [ref=e11]:
    - generic [ref=e12]:
      - list [ref=e13]:
        - listitem [ref=e14]:
          - generic [ref=e15]:
            - generic [ref=e16]: QA Tester
            - generic [ref=e17]: qa@takra.ai
            - generic [ref=e18]: "บทบาทใน Hub: owner"
          - generic [ref=e19]: เจ้าของ
        - listitem [ref=e20]:
          - generic [ref=e21]:
            - generic [ref=e22]: wanleeta QA
            - generic [ref=e23]: wanleeta.official@gmail.com
            - generic [ref=e24]: "บทบาทใน Hub: admin"
          - button "โฮสต์" [active] [ref=e27] [cursor=pointer]:
            - generic [ref=e28]: โฮสต์
        - listitem [ref=e29]:
          - generic [ref=e30]:
            - generic [ref=e31]: kachain bumrungta
            - generic [ref=e32]: kachain.b@realfactory.co.th
            - generic [ref=e33]: "บทบาทใน Hub: admin"
          - button "ผู้จัดการแบรนด์" [ref=e36] [cursor=pointer]:
            - generic [ref=e37]: ผู้จัดการแบรนด์
      - paragraph [ref=e38]: การเชิญ ลบสมาชิก และจำนวนที่นั่ง จัดการที่ Takra Hub — บทบาทเจ้าของก็กำหนดจาก Hub เช่นกัน
      - button "จัดการสมาชิกใน Takra Hub" [ref=e39] [cursor=pointer]:
        - img [ref=e40]
        - text: จัดการสมาชิกใน Takra Hub
```

# Test source

```ts
  1   | /**
  2   |  * MVP2 Epic 9 Membership — UI cases that ONE owner account can drive on UAT (TC-MEM-*).
  3   |  * Case source: qa-test-reports …/takra-insight-mvp2-membership-ui-test-cases-table.html
  4   |  *
  5   |  * Prereq (session reuse, same as entitlement.uat.spec.js):
  6   |  *   1. `npm run build:uat` (a build that has LHM_ENGINE_PORT — the engine must be on :8766, never the real app's :8765)
  7   |  *   2. log in once by hand as the OWNER account (qa@takra.ai) through a Playwright-launched window, so auth.bin is
  8   |  *      written with the mock keychain this suite reads
  9   |  *   3. `npx playwright test --config playwright.uat.config.js e2e/uat/membership.uat.spec.js`
  10  |  *
  11  |  * Every other TC-MEM case needs a second account (MULTI / LEGACY / NEW / REMOVED / BM / HOST), a Hub-side action,
  12  |  * a live on air or a network cut, and is NOT here.
  13  |  *
  14  |  * ⚠️ TC-MEM-C.2 WRITES a real role on UAT and puts it back in `finally`.
  15  |  */
  16  | import { test, expect, _electron as electron } from '@playwright/test';
  17  | import { mkdirSync, writeFileSync } from 'node:fs';
  18  | import { join } from 'node:path';
  19  | import { launchApp, closeApp, TECHNICAL_LEAK } from '../_helpers.js';
  20  | 
  21  | const EVID = process.env.EVID_DIR || '';
  22  | if (EVID) mkdirSync(EVID, { recursive: true });
  23  | const shot = (win, name) => (EVID ? win.screenshot({ path: join(EVID, `${name}.png`) }).catch(() => {}) : null);
  24  | 
  25  | const PROFILE_BTN = { name: 'โปรไฟล์และบัญชี' };
  26  | const MEMBERS = '[data-testid="workspace-members"]';
  27  | const ROWS = `${MEMBERS} ul[role="list"] > li`;
  28  | const WS_LIST = '[role="listbox"][aria-label="พื้นที่ทำงาน"]';
  29  | 
  30  | test.describe.configure({ mode: 'serial' });
  31  | 
  32  | let app;
  33  | let window;
  34  | let signedIn = false;
  35  | let workspaces = [];      // option texts in the profile menu's "พื้นที่ทำงาน" section ([] = section absent)
  36  | let isOwner = false;      // "สมาชิกและบทบาท" is in the profile menu
  37  | 
  38  | async function openProfileMenu() {
> 39  |   await window.getByRole('button', PROFILE_BTN).first().click();
      |                                                         ^ TimeoutError: locator.click: Timeout 30000ms exceeded.
  40  |   await window.waitForTimeout(800);
  41  | }
  42  | async function closeMenu() {
  43  |   await window.keyboard.press('Escape');
  44  |   await window.waitForTimeout(300);
  45  | }
  46  | async function openMembers() {
  47  |   // The members page is full-screen (only a "กลับ" button) — leave it first so the profile button exists again.
  48  |   if (await window.locator(MEMBERS).isVisible().catch(() => false)) {
  49  |     await window.getByRole('button', { name: 'กลับ', exact: true }).click();
  50  |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 15_000 });
  51  |   }
  52  |   await openProfileMenu();
  53  |   await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).click();
  54  |   await window.locator(MEMBERS).waitFor({ timeout: 30_000 });
  55  |   await window.locator(`${MEMBERS} [role="status"]`).waitFor({ state: 'detached', timeout: 30_000 }).catch(() => {});
  56  |   await expect(window.locator(ROWS).first()).toBeVisible({ timeout: 30_000 });
  57  | }
  58  | async function rows() {
  59  |   return window.locator(ROWS).evaluateAll((lis) => lis.map((li, i) => ({
  60  |     i,
  61  |     text: (li.innerText || '').replace(/\s+/g, ' ').trim(),
  62  |     owner: !!li.querySelector('[data-member-owner]'),
  63  |     role: li.querySelector('[data-member-role] button')?.innerText.trim() ?? null,
  64  |   })));
  65  | }
  66  | 
  67  | // ── offline simulation (group H) ─────────────────────────────────────────────────────────────────────────
  68  | // Main talks to the cloud two ways: Node's global fetch (auth.js → Hub) and Chromium's net stack (net.fetch →
  69  | // session bind / consent / members). Cut both, keep loopback so the local engine on :8766 still answers.
  70  | const PROXY_OFF = { proxyRules: 'http://127.0.0.1:9', proxyBypassRules: '<local>;127.0.0.1;localhost' };
  71  | async function goOffline() {
  72  |   await app.evaluate(async ({ session }, proxy) => {
  73  |     globalThis.__onlineFetch ||= globalThis.fetch;
  74  |     const LOCAL = /^https?:\/\/(127\.0\.0\.1|localhost|\[::1\])(:\d+)?\//i;
  75  |     globalThis.fetch = async (input, init) => {
  76  |       const url = typeof input === 'string' ? input : input?.url || String(input);
  77  |       if (LOCAL.test(url)) return globalThis.__onlineFetch(input, init);
  78  |       throw new TypeError('fetch failed (TC-MEM offline simulation)');
  79  |     };
  80  |     await session.defaultSession.setProxy(proxy);
  81  |     await session.defaultSession.closeAllConnections();
  82  |   }, PROXY_OFF);
  83  | }
  84  | async function goOnline() {
  85  |   await app.evaluate(async ({ session }) => {
  86  |     if (globalThis.__onlineFetch) globalThis.fetch = globalThis.__onlineFetch;
  87  |     await session.defaultSession.setProxy({ mode: 'direct' });
  88  |     await session.defaultSession.closeAllConnections();
  89  |   });
  90  | }
  91  | const wsState = () => window.evaluate(() => window.liveHost.auth.workspaces());
  92  | 
  93  | test.beforeAll(async () => {
  94  |   expect(process.env.LHM_ENGINE_PORT, 'the engine must run on :8766 — never the real app\'s :8765').toBe('8766');
  95  |   ({ app, window } = await launchApp({ multiSession: 'unset' }));
  96  |   // isVisible() never waits — wait for the signed-in shell, then decide.
  97  |   signedIn = await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 45_000 }).then(() => true, () => false);
  98  |   if (!signedIn) return;
  99  |   expect(await window.evaluate(() => window.liveHost?.enginePort)).toBe(8766);
  100 |   await window.waitForTimeout(3000);
  101 |   await openProfileMenu();
  102 |   workspaces = await window.locator(`${WS_LIST} [role="option"]`).allInnerTexts().catch(() => []);
  103 |   isOwner = await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).isVisible().catch(() => false);
  104 |   await closeMenu();
  105 | });
  106 | 
  107 | test.afterAll(async () => { if (app) await closeApp(app); });
  108 | 
  109 | test.beforeEach(() => {
  110 |   test.skip(!signedIn, 'ยังไม่ได้ login — login มือด้วย qa@takra.ai ในหน้าต่างที่ Playwright เปิดก่อน แล้วรันใหม่');
  111 | });
  112 | 
  113 | test('TC-MEM-D.1 (uat): เจ้าของเห็น "แดชบอร์ดแบรนด์" (เปิดได้) และ "สมาชิกและบทบาท"', async () => {
  114 |   const brand = window.getByRole('link', { name: 'แดชบอร์ดแบรนด์' }).or(window.getByRole('button', { name: 'แดชบอร์ดแบรนด์' })).first();
  115 |   await expect(brand).toBeVisible();
  116 |   await brand.click();
  117 |   await expect(window.getByRole('heading', { name: 'แดชบอร์ดแบรนด์' }).first()).toBeVisible({ timeout: 30_000 });
  118 |   await shot(window, 'D1-brand-dashboard');
  119 |   await openProfileMenu();
  120 |   await expect(window.getByRole('button', { name: 'สมาชิกและบทบาท' })).toBeVisible();
  121 |   await shot(window, 'D1-profile-menu');
  122 |   await closeMenu();
  123 | });
  124 | 
  125 | test('TC-MEM-A.3 (uat): บัญชีทีมเดียว ไม่มีหน้าต่างเลือก และไม่มีส่วน "พื้นที่ทำงาน"', async () => {
  126 |   test.skip(workspaces.length >= 2, `qa@takra.ai มี ${workspaces.length} พื้นที่ทำงาน — เคสนี้ต้องใช้บัญชีทีมเดียว`);
  127 |   await expect(window.locator('[role="dialog"][aria-labelledby="workspace-pick-title"]')).toHaveCount(0);
  128 |   await openProfileMenu();
  129 |   await expect(window.locator(WS_LIST)).toHaveCount(0);
  130 |   await expect(window.getByText('พื้นที่ทำงาน', { exact: true })).toHaveCount(0);
  131 |   await shot(window, 'A3-profile-menu');
  132 |   await closeMenu();
  133 | });
  134 | 
  135 | test('TC-MEM-A.2 (uat): สลับพื้นที่ทำงานจากเมนูโปรไฟล์ แล้วแอปโหลดใหม่ในทีมที่เลือก', async () => {
  136 |   test.skip(workspaces.length < 2, `qa@takra.ai มี ${workspaces.length} พื้นที่ทำงาน — เคสนี้ต้องใช้บัญชีหลายทีม`);
  137 |   const original = (await wsState()).workspaces.find((w) => w.selected);
  138 |   await openProfileMenu();
  139 |   const current = window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`);
```