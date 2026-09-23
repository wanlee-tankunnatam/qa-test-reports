# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> TC-MEM-A.2 (uat): สลับพื้นที่ทำงานจากเมนูโปรไฟล์ แล้วแอปโหลดใหม่ในทีมที่เลือก
- Location: e2e/uat/membership.uat.spec.js:104:1

# Error details

```
TimeoutError: locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'โปรไฟล์และบัญชี' }).first()

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - main [ref=e6]:
    - generic [ref=e7]:
      - img "Takra Insight" [ref=e10]
      - generic [ref=e11]:
        - heading "คุณเข้าร่วมพื้นที่ทำงาน “ทีมของ kachain bumrungta ครับ” แล้ว" [level=2] [ref=e12]
        - paragraph [ref=e13]:
          - text: ก่อนเริ่มไลฟ์ในทีม ขอความยินยอมจากคุณเอง — สิทธิ์นี้เป็นของคุณคนเดียว เจ้าของพื้นที่ทำงานให้หรือเปลี่ยนแทนไม่ได้
          - generic [ref=e14]: ให้ความยินยอมในพื้นที่ทำงานนี้ก่อนเริ่มบันทึก
        - generic [ref=e15]:
          - generic [ref=e17]:
            - img [ref=e19]
            - generic [ref=e25]:
              - generic [ref=e26]:
                - paragraph [ref=e27]: อ่านอารมณ์จากสีหน้า
                - switch "อ่านอารมณ์จากสีหน้า" [ref=e28] [cursor=pointer]
              - paragraph [ref=e30]: ประมวลผลสีหน้าคุณแบบสดๆ ระหว่างไลฟ์ เพื่ออ่านอารมณ์ (ยิ้ม เครียด เหนื่อย) แล้วแนะนำทันที — ประมวลผลบนเครื่องคุณ ไม่ส่งภาพออก
          - generic [ref=e32]:
            - img [ref=e34]
            - generic [ref=e37]:
              - generic [ref=e38]:
                - paragraph [ref=e39]: ฟังเสียงพูดระหว่างไลฟ์
                - switch "ฟังเสียงพูดระหว่างไลฟ์" [checked] [ref=e40] [cursor=pointer]
              - paragraph [ref=e42]: ถอดเสียงพูดในไลฟ์เป็นข้อความในเครื่อง เพื่อจับราคาที่พูดและเตือนคำพูดเสี่ยง · ถ้าไลฟ์มีคนพูดหลายคน ระบบจะถอดเสียงของทุกคนที่พูดในไลฟ์ ไม่ใช่แค่เสียงของคุณ · เสียงไม่ถูกบันทึกและไม่ถูกส่งออกจากเครื่อง · เลือกแยกจากการอ่านสีหน้า ปฏิเสธข้อนี้ได้โดยยังใช้การอ่านสีหน้าต่อ
          - generic [ref=e43]:
            - img [ref=e44]
            - generic [ref=e47]:
              - generic [ref=e48]: โหมดคอมเมนต์อย่างเดียว — ใช้งานได้ปกติ วิเคราะห์จากคอมเมนต์ผู้ชม แต่จะไม่มีการอ่านอารมณ์จากสีหน้า · เปิดทีหลังได้ทุกเมื่อ
              - generic [ref=e49]: ฟังเสียงพูดในไลฟ์แล้วถอดเป็นข้อความในเครื่อง — รวมถึงคนอื่นที่พูดในไลฟ์เดียวกันด้วย · ไม่บันทึกเสียง และเสียงไม่ออกจากเครื่อง
        - status [ref=e50]:
          - img [ref=e52]
          - generic [ref=e54]:
            - paragraph [ref=e55]: ยังลังเลอยู่ไหม?
            - button "ดูวิดีโอ 30 วิ ว่าทำไมข้อมูลคุณถึงปลอดภัย" [ref=e56] [cursor=pointer]:
              - text: ดูวิดีโอ 30 วิ ว่าทำไมข้อมูลคุณถึงปลอดภัย
              - img [ref=e57]
          - button "ปิด" [ref=e59] [cursor=pointer]:
            - img [ref=e60]
        - button "ยินยอมและเริ่มใช้งาน" [ref=e63] [cursor=pointer]
        - paragraph [ref=e64]: เปลี่ยนใจหรือถอนความยินยอมได้ทุกเมื่อที่ ตั้งค่า › ความเป็นส่วนตัว
  - contentinfo [ref=e65]: © 2026 TAKRA · A Real Factory product
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
  106 |   await openProfileMenu();
  107 |   const opts = window.locator(`${WS_LIST} [role="option"]`);
  108 |   const current = window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`);
  109 |   await expect(current).toHaveCount(1);
  110 |   await expect(current).toContainText('ใช้งานอยู่');
  111 |   await expect(current).toBeDisabled();
  112 |   const originalName = (await current.innerText()).split('\n')[0].trim();
  113 |   const other = window.locator(`${WS_LIST} [role="option"][aria-selected="false"]`).first();
  114 |   const otherName = (await other.innerText()).split('\n')[0].trim();
  115 |   await shot(window, 'A2-before');
  116 |   const before = await window.evaluate(() => performance.timeOrigin);
  117 |   await other.click();
  118 |   try {
  119 |     await expect.poll(async () => window.evaluate(() => performance.timeOrigin).catch(() => before), { timeout: 30_000 }).not.toBe(before);
  120 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 });
  121 |     await window.waitForTimeout(2000);
  122 |     await openProfileMenu();
  123 |     await expect(window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`)).toContainText(otherName);
  124 |     await shot(window, 'A2-after');
  125 |     await closeMenu();
  126 |   } finally {
  127 |     // Put the account back where it was.
  128 |     await openProfileMenu();
  129 |     const back = opts.filter({ hasText: originalName }).first();
  130 |     if (await back.isEnabled().catch(() => false)) {
  131 |       await back.click();
  132 |       await window.waitForTimeout(8000);
  133 |       await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 }).catch(() => {});
  134 |     } else await closeMenu();
  135 |   }
  136 | });
  137 | 
  138 | test.describe('หน้า "สมาชิกและบทบาท" (เจ้าของ)', () => {
  139 |   test.beforeEach(() => { test.skip(!isOwner, 'qa@takra.ai ไม่ใช่เจ้าของในพื้นที่ทำงานนี้ — ไม่มีเมนู "สมาชิกและบทบาท"'); });
```