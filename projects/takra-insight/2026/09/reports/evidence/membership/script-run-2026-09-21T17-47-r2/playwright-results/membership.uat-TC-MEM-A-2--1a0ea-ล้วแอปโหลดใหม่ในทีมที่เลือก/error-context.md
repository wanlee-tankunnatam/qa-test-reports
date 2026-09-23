# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> TC-MEM-A.2 (uat): สลับพื้นที่ทำงานจากเมนูโปรไฟล์ แล้วแอปโหลดใหม่ในทีมที่เลือก
- Location: e2e/uat/membership.uat.spec.js:104:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: /Wanlee Qa/ })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('heading', { name: /Wanlee Qa/ })

```

```yaml
- banner:
  - img "Takra Insight"
  - button "ออกจากระบบ"
- main:
  - heading "แพ็กเกจของพื้นที่ทำงานนี้หมดอายุแล้ว" [level=1]
  - paragraph: ต่ออายุเพื่อกลับมาวิเคราะห์ไลฟ์ในพื้นที่ทำงานนี้ หรือใช้พื้นที่ทำงานอื่นด้านล่าง
  - text: แพ็กเกจล่าสุด TAKRA Insight · Pro (รายเดือน) หมดอายุเมื่อ 9/18/2026 (2 วันที่แล้ว)
  - button "ต่ออายุแพ็กเกจ"
  - button "ฉันต่ออายุแล้ว · เช็กอีกครั้ง"
  - text: ใช้พื้นที่ทำงานอื่นแทน
  - listbox "พื้นที่ทำงาน":
    - listitem:
      - option "ทีมของ kachain bumrungta ครับ"
    - listitem:
      - option "ทีมของ QA Tester"
    - listitem:
      - option "Wanlee Qa ใช้งานอยู่" [disabled] [selected]
    - listitem:
      - option "wanlee 01"
  - paragraph:
    - text: มีปัญหาเรื่องการชำระเงิน?
    - link "ติดต่อทีมงาน":
      - /url: "#"
```

# Test source

```ts
  34  | let signedIn = false;
  35  | let workspaces = [];      // option texts in the profile menu's "พื้นที่ทำงาน" section ([] = section absent)
  36  | let isOwner = false;      // "สมาชิกและบทบาท" is in the profile menu
  37  | 
  38  | async function openProfileMenu() {
  39  |   await window.getByRole('button', PROFILE_BTN).first().click();
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
> 134 |       await expect(window.getByRole('heading', { name: new RegExp(target.name) })).toBeVisible();
      |                                                                                    ^ Error: expect(locator).toBeVisible() failed
  135 |       test.info().annotations.push({ type: 'consent-gate', description: `ทีม "${target.name}" ขึ้นหน้าขอความยินยอมของทีมก่อนเข้าใช้` });
  136 |       await shot(window, 'A2-after-consent-gate');
  137 |     }
  138 |   } finally {
  139 |     // Back to the original team through the same IPC the menu uses — it works from the consent screen too.
  140 |     await window.evaluate((id) => window.liveHost.auth.selectWorkspace(id), original.workspaceId).catch(() => {});
  141 |     await window.waitForTimeout(6000);
  142 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 }).catch(() => {});
  143 |     expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'คืนทีมเดิมไม่สำเร็จ').toBe(original.workspaceId);
  144 |   }
  145 | });
  146 | 
  147 | test.describe('หน้า "สมาชิกและบทบาท" (เจ้าของ)', () => {
  148 |   test.beforeEach(() => { test.skip(!isOwner, 'qa@takra.ai ไม่ใช่เจ้าของในพื้นที่ทำงานนี้ — ไม่มีเมนู "สมาชิกและบทบาท"'); });
  149 | 
  150 |   test('TC-MEM-C.1 (uat): เห็นรายชื่อ บทบาทใน Hub และบทบาทใน Insight', async () => {
  151 |     await openMembers();
  152 |     await expect(window.getByRole('heading', { name: 'สมาชิกและบทบาท' }).first()).toBeVisible();
  153 |     await expect(window.getByText('กำหนดบทบาทใน Takra Insight ให้สมาชิกในพื้นที่ทำงานนี้')).toBeVisible();
  154 |     const r = await rows();
  155 |     expect(r.length).toBeGreaterThan(0);
  156 |     for (const row of r) {
  157 |       expect(row.text, `แถว ${row.i} ไม่มีบรรทัด "บทบาทใน Hub:"`).toContain('บทบาทใน Hub:');
  158 |       if (row.owner) expect(row.text).toContain('เจ้าของ');
  159 |       else expect(['ผู้จัดการแบรนด์', 'โฮสต์', 'ยังไม่กำหนด'], `แถว ${row.i} บทบาท "${row.role}"`).toContain(row.role);
  160 |     }
  161 |     expect(r.filter((x) => x.owner).length, 'ต้องมีแถวเจ้าของ').toBeGreaterThan(0);
  162 |     await shot(window, 'C1-members');
  163 |     test.info().annotations.push({ type: 'rows', description: JSON.stringify(r.map((x) => ({ owner: x.owner, role: x.role }))) });
  164 |   });
  165 | 
  166 |   test('TC-MEM-C.5 (uat): ตั้ง "เจ้าของ" จากแอปไม่ได้ และแถวเจ้าของเปลี่ยนไม่ได้', async () => {
  167 |     await openMembers();
  168 |     const ownerRow = window.locator(ROWS).filter({ has: window.locator('[data-member-owner]') }).first();
  169 |     await expect(ownerRow.locator('[data-member-owner]')).toHaveText('เจ้าของ');
  170 |     await expect(ownerRow.locator('button')).toHaveCount(0);
  171 |     await ownerRow.locator('[data-member-owner]').click();
  172 |     await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  173 |     const editable = window.locator(`${ROWS} [data-member-role]`).first();
  174 |     test.skip(await editable.count() === 0, 'ไม่มีสมาชิกที่ไม่ใช่เจ้าของให้เปิดช่องบทบาท');
  175 |     await editable.locator('button').first().click();
  176 |     await window.waitForTimeout(500);
  177 |     const menu = editable.locator('div.absolute button');
  178 |     await expect(menu).toHaveCount(2);
  179 |     const labels = (await menu.allInnerTexts()).map((s) => s.trim());
  180 |     expect(labels.sort()).toEqual(['ผู้จัดการแบรนด์', 'โฮสต์'].sort());
  181 |     await shot(window, 'C5-role-options');
  182 |     await window.keyboard.press('Escape');
  183 |     await editable.locator('button').first().click().catch(() => {}); // close the dropdown if Esc did not
  184 |   });
  185 | 
  186 |   test('TC-MEM-C.6 (uat): ไม่มีปุ่มเชิญ/ลบ/ที่นั่ง และ "จัดการสมาชิกใน Takra Hub" เปิดเว็บ Hub', async () => {
  187 |     await openMembers();
  188 |     // The footer sentence itself names เชิญ/ลบ/ที่นั่ง, so the check is on CONTROLS and on a seat COUNT, not on words.
  189 |     const text = await window.locator(MEMBERS).innerText();
  190 |     expect(text).not.toMatch(/ที่นั่ง\s*\d|\d+\s*(\/\s*\d+\s*)?ที่นั่ง/);
  191 |     await expect(window.getByRole('button', { name: /เชิญ|ลบ|เอาออก/ })).toHaveCount(0);
  192 |     await expect(window.getByText('การเชิญ ลบสมาชิก และจำนวนที่นั่ง จัดการที่ Takra Hub — บทบาทเจ้าของก็กำหนดจาก Hub เช่นกัน')).toBeVisible();
  193 |     await app.evaluate(({ shell }) => {
  194 |       globalThis.__opened = [];
  195 |       globalThis.__origOpenExternal ||= shell.openExternal.bind(shell);
  196 |       shell.openExternal = async (url) => { globalThis.__opened.push(url); return true; };
  197 |     });
  198 |     try {
  199 |       await window.getByRole('button', { name: 'จัดการสมาชิกใน Takra Hub' }).click();
  200 |       await expect.poll(() => app.evaluate(() => globalThis.__opened.length), { timeout: 15_000 }).toBeGreaterThan(0);
  201 |       const [url] = await app.evaluate(() => globalThis.__opened);
  202 |       expect(new URL(url).hostname).toBe('uat-hub.takra.ai');
  203 |       await expect(window.getByText('เปิด Takra Hub ไม่สำเร็จ')).toHaveCount(0);
  204 |       test.info().annotations.push({ type: 'opened', description: new URL(url).origin + new URL(url).pathname });
  205 |       await shot(window, 'C6-members-footer');
  206 |     } finally {
  207 |       await app.evaluate(({ shell }) => { if (globalThis.__origOpenExternal) shell.openExternal = globalThis.__origOpenExternal; });
  208 |     }
  209 |   });
  210 | 
  211 |   test('TC-MEM-C.2 (uat): เปลี่ยน "โฮสต์" → "ผู้จัดการแบรนด์" แล้วค่าคงอยู่ (คืนค่าเดิมท้ายเทส)', async () => {
  212 |     await openMembers();
  213 |     const r = await rows();
  214 |     const host = r.find((x) => !x.owner && x.role === 'โฮสต์');
  215 |     test.skip(!host, 'ไม่มีสมาชิกบทบาท "โฮสต์" ในทีมนี้ให้เปลี่ยน');
  216 |     const id = host.text.split(' บทบาทใน Hub:')[0];        // name + email, used to re-find the row after reload
  217 |     const rowOf = () => window.locator(ROWS).filter({ hasText: id }).first();
  218 |     const pick = async (label) => {
  219 |       await rowOf().locator('[data-member-role] button').first().click();
  220 |       await rowOf().locator('div.absolute button', { hasText: label }).click();
  221 |     };
  222 |     try {
  223 |       await pick('ผู้จัดการแบรนด์');
  224 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์', { timeout: 20_000 });
  225 |       await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  226 |       await shot(window, 'C2-after-change');
  227 |       await window.goBack?.().catch(() => {});
  228 |       await window.getByRole('button', { name: /ย้อนกลับ|กลับ/ }).first().click().catch(() => {});
  229 |       await openMembers();
  230 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์');
  231 |       await shot(window, 'C2-reopened');
  232 |     } finally {
  233 |       await openMembers().catch(() => {});
  234 |       if ((await rowOf().locator('[data-member-role] button').first().innerText().catch(() => '')).trim() !== 'โฮสต์') {
```