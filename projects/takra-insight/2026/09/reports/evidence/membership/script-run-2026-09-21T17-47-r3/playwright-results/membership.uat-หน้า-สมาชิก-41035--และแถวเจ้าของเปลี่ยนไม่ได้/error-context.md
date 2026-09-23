# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> หน้า "สมาชิกและบทบาท" (เจ้าของ) >> TC-MEM-C.5 (uat): ตั้ง "เจ้าของ" จากแอปไม่ได้ และแถวเจ้าของเปลี่ยนไม่ได้
- Location: e2e/uat/membership.uat.spec.js:177:3

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
          - button "โฮสต์" [ref=e27] [cursor=pointer]:
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
  16  | import { test, expect } from '@playwright/test';
  17  | import { mkdirSync } from 'node:fs';
  18  | import { join } from 'node:path';
  19  | import { launchApp, closeApp } from '../_helpers.js';
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
  47  |   await openProfileMenu();
  48  |   await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).click();
  49  |   await window.locator(MEMBERS).waitFor({ timeout: 30_000 });
  50  |   await window.locator(`${MEMBERS} [role="status"]`).waitFor({ state: 'detached', timeout: 30_000 }).catch(() => {});
  51  |   await expect(window.locator(ROWS).first()).toBeVisible({ timeout: 30_000 });
  52  | }
  53  | async function rows() {
  54  |   return window.locator(ROWS).evaluateAll((lis) => lis.map((li, i) => ({
  55  |     i,
  56  |     text: (li.innerText || '').replace(/\s+/g, ' ').trim(),
  57  |     owner: !!li.querySelector('[data-member-owner]'),
  58  |     role: li.querySelector('[data-member-role] button')?.innerText.trim() ?? null,
  59  |   })));
  60  | }
  61  | 
  62  | test.beforeAll(async () => {
  63  |   expect(process.env.LHM_ENGINE_PORT, 'the engine must run on :8766 — never the real app\'s :8765').toBe('8766');
  64  |   ({ app, window } = await launchApp({ multiSession: 'unset' }));
  65  |   // isVisible() never waits — wait for the signed-in shell, then decide.
  66  |   signedIn = await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 45_000 }).then(() => true, () => false);
  67  |   if (!signedIn) return;
  68  |   expect(await window.evaluate(() => window.liveHost?.enginePort)).toBe(8766);
  69  |   await window.waitForTimeout(3000);
  70  |   await openProfileMenu();
  71  |   workspaces = await window.locator(`${WS_LIST} [role="option"]`).allInnerTexts().catch(() => []);
  72  |   isOwner = await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).isVisible().catch(() => false);
  73  |   await closeMenu();
  74  | });
  75  | 
  76  | test.afterAll(async () => { if (app) await closeApp(app); });
  77  | 
  78  | test.beforeEach(() => {
  79  |   test.skip(!signedIn, 'ยังไม่ได้ login — login มือด้วย qa@takra.ai ในหน้าต่างที่ Playwright เปิดก่อน แล้วรันใหม่');
  80  | });
  81  | 
  82  | test('TC-MEM-D.1 (uat): เจ้าของเห็น "แดชบอร์ดแบรนด์" (เปิดได้) และ "สมาชิกและบทบาท"', async () => {
  83  |   const brand = window.getByRole('link', { name: 'แดชบอร์ดแบรนด์' }).or(window.getByRole('button', { name: 'แดชบอร์ดแบรนด์' })).first();
  84  |   await expect(brand).toBeVisible();
  85  |   await brand.click();
  86  |   await expect(window.getByRole('heading', { name: 'แดชบอร์ดแบรนด์' }).first()).toBeVisible({ timeout: 30_000 });
  87  |   await shot(window, 'D1-brand-dashboard');
  88  |   await openProfileMenu();
  89  |   await expect(window.getByRole('button', { name: 'สมาชิกและบทบาท' })).toBeVisible();
  90  |   await shot(window, 'D1-profile-menu');
  91  |   await closeMenu();
  92  | });
  93  | 
  94  | test('TC-MEM-A.3 (uat): บัญชีทีมเดียว ไม่มีหน้าต่างเลือก และไม่มีส่วน "พื้นที่ทำงาน"', async () => {
  95  |   test.skip(workspaces.length >= 2, `qa@takra.ai มี ${workspaces.length} พื้นที่ทำงาน — เคสนี้ต้องใช้บัญชีทีมเดียว`);
  96  |   await expect(window.locator('[role="dialog"][aria-labelledby="workspace-pick-title"]')).toHaveCount(0);
  97  |   await openProfileMenu();
  98  |   await expect(window.locator(WS_LIST)).toHaveCount(0);
  99  |   await expect(window.getByText('พื้นที่ทำงาน', { exact: true })).toHaveCount(0);
  100 |   await shot(window, 'A3-profile-menu');
  101 |   await closeMenu();
  102 | });
  103 | 
  104 | test('TC-MEM-A.2 (uat): สลับพื้นที่ทำงานจากเมนูโปรไฟล์ แล้วแอปโหลดใหม่ในทีมที่เลือก', async () => {
  105 |   test.skip(workspaces.length < 2, `qa@takra.ai มี ${workspaces.length} พื้นที่ทำงาน — เคสนี้ต้องใช้บัญชีหลายทีม`);
  106 |   const wsState = () => window.evaluate(() => window.liveHost.auth.workspaces());
  107 |   const original = (await wsState()).workspaces.find((w) => w.selected);
  108 |   await openProfileMenu();
  109 |   const current = window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`);
  110 |   await expect(current).toHaveCount(1);
  111 |   await expect(current).toContainText('ใช้งานอยู่');
  112 |   await expect(current).toBeDisabled();
  113 |   await expect(current).toContainText(original.name);
  114 |   // Prefer a team this account OWNS — the menu is then fully usable after the reload. A team it has never
  115 |   // consented in lands on that team's own consent screen (Story 9.4), which is the reload into the new team too.
  116 |   const others = (await wsState()).workspaces.filter((w) => !w.selected);
  117 |   const target = others.find((w) => w.productRole === 'owner') || others[0];
  118 |   await shot(window, 'A2-before');
  119 |   const before = await window.evaluate(() => performance.timeOrigin);
  120 |   await window.locator(`${WS_LIST} [role="option"]`).filter({ hasText: target.name }).first().click();
  121 |   try {
  122 |     await expect.poll(async () => window.evaluate(() => performance.timeOrigin).catch(() => before), { timeout: 30_000 }).not.toBe(before);
  123 |     await window.waitForTimeout(3000);
  124 |     const after = await wsState();
  125 |     expect(after.workspaces.find((w) => w.selected)?.name, 'ทีมที่ใช้งานอยู่หลังสลับ').toBe(target.name);
  126 |     const shell = await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 20_000 }).then(() => true, () => false);
  127 |     if (shell) {
  128 |       await openProfileMenu();
  129 |       await expect(window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`)).toContainText(target.name);
  130 |       await expect(window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`)).toContainText('ใช้งานอยู่');
  131 |       await shot(window, 'A2-after-menu');
  132 |       await closeMenu();
  133 |     } else {
  134 |       // The new team's own gate instead of the shell — still the reload into the chosen team:
  135 |       //  · never consented there → that team's consent screen, named after it (Story 9.4)
  136 |       //  · its package expired  → the expired screen, which carries the "ใช้พื้นที่ทำงานอื่นแทน" switcher
  137 |       const consentGate = window.getByRole('heading', { name: new RegExp(`คุณเข้าร่วมพื้นที่ทำงาน.*${target.name}`) });
  138 |       const expiredGate = window.getByRole('heading', { name: 'แพ็กเกจของพื้นที่ทำงานนี้หมดอายุแล้ว' });
  139 |       await expect(consentGate.or(expiredGate).first()).toBeVisible();
```