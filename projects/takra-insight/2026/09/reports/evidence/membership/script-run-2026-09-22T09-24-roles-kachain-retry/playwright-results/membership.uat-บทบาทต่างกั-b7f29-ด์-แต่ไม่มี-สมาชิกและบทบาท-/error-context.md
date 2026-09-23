# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> บทบาทต่างกันในแต่ละทีม (หาทีมตามบทบาทของบัญชีที่ login) >> TC-MEM-D.2 (uat): ผู้จัดการแบรนด์เห็น "แดชบอร์ดแบรนด์" แต่ไม่มี "สมาชิกและบทบาท"
- Location: e2e/uat/membership.uat.spec.js:349:3

# Error details

```
TimeoutError: locator.waitFor: Timeout 60000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'โปรไฟล์และบัญชี' }).first() to be visible

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - complementary "เมนูหลัก" [ref=e4]:
    - link "TAKRA Insight — หน้าหลัก" [ref=e6] [cursor=pointer]:
      - /url: "#/dashboard"
      - img "Takra Insight" [ref=e9]
    - navigation "เมนูหลัก" [ref=e10]:
      - generic [ref=e11]: เมนูหลัก
      - list [ref=e12]:
        - listitem [ref=e13]:
          - link "หน้าหลัก" [ref=e15] [cursor=pointer]:
            - /url: "#/dashboard"
            - img [ref=e16]
            - generic [ref=e21]: หน้าหลัก
        - listitem [ref=e22]:
          - link "หลายไลฟ์พร้อมกัน" [ref=e24] [cursor=pointer]:
            - /url: "#/live"
            - img [ref=e25]
            - generic [ref=e31]: หลายไลฟ์พร้อมกัน
        - listitem [ref=e32]:
          - link "แดชบอร์ดแบรนด์" [ref=e34] [cursor=pointer]:
            - /url: "#/brand-dashboard"
            - img [ref=e35]
            - generic [ref=e37]: แดชบอร์ดแบรนด์
        - listitem [ref=e38]:
          - link "แชนเนลที่ติดตาม" [ref=e40] [cursor=pointer]:
            - /url: "#/channels"
            - img [ref=e41]
            - generic [ref=e43]: แชนเนลที่ติดตาม
        - listitem [ref=e44]:
          - link "เซสชัน" [ref=e46] [cursor=pointer]:
            - /url: "#/sessions"
            - img [ref=e47]
            - generic [ref=e49]: เซสชัน
        - listitem [ref=e50]:
          - link "รายงานประจำวัน" [ref=e52] [cursor=pointer]:
            - /url: "#/reports"
            - img [ref=e53]
            - generic [ref=e56]: รายงานประจำวัน
    - button "โปรไฟล์และบัญชี" [ref=e59] [cursor=pointer]:
      - generic [ref=e60]: K
      - generic [ref=e61]:
        - generic [ref=e62]:
          - generic [ref=e63]: kachain bumrungta
          - generic [ref=e64]: ใช้งานอยู่
        - generic [ref=e65]: kachain.b@realfactory.co.th
      - img [ref=e66]
  - generic [ref=e68]:
    - banner [ref=e69]:
      - generic [ref=e70]:
        - button "ย่อเมนู" [ref=e71] [cursor=pointer]:
          - img [ref=e72]
        - navigation "breadcrumb" [ref=e75]:
          - link "หน้าหลัก" [ref=e76] [cursor=pointer]:
            - /url: "#/dashboard"
            - img [ref=e77]
    - generic [ref=e82]:
      - heading "ภาพรวม" [level=1] [ref=e83]
      - paragraph [ref=e84]: เริ่มวิเคราะห์ไลฟ์ใหม่ หรือกลับไปดู insight จากไลฟ์ที่ผ่านมา
    - main [ref=e85]:
      - generic [ref=e86]:
        - generic [ref=e87]:
          - img [ref=e89]
          - generic [ref=e95]:
            - heading "วิเคราะห์ไลฟ์ใหม่" [level=2] [ref=e96]
            - paragraph [ref=e97]: วาง URL ของไลฟ์ — ระบบเปิดในเบราว์เซอร์ในตัว แล้วเก็บ insight แบบเรียลไทม์
        - generic [ref=e98]:
          - generic [ref=e99]:
            - img [ref=e100]
            - textbox "วาง URL ไลฟ์ หรือค้นหาชื่อช่อง…" [ref=e103]
          - button "เปิดดูไลฟ์" [ref=e104] [cursor=pointer]:
            - text: เปิดดูไลฟ์
            - img [ref=e105]
        - generic [ref=e107]:
          - generic [ref=e108]: รองรับ
          - generic [ref=e109]:
            - generic "TikTok" [ref=e110]:
              - img [ref=e111]
            - text: TikTok
      - generic [ref=e114]:
        - generic [ref=e115]:
          - img [ref=e117]
          - generic [ref=e120]:
            - generic [ref=e121]: เซสชันที่บันทึก
            - generic [ref=e123]: "0"
        - generic [ref=e124]:
          - img [ref=e126]
          - generic [ref=e129]:
            - generic [ref=e130]: เฟรมที่วิเคราะห์
            - generic [ref=e132]: "0"
        - generic [ref=e133]:
          - img [ref=e135]
          - generic [ref=e137]:
            - generic [ref=e138]: คอมเมนต์ที่บันทึก
            - generic [ref=e140]: "0"
        - generic [ref=e141]:
          - img [ref=e143]
          - generic [ref=e146]:
            - generic [ref=e147]: อารมณ์โฮสต์เป็นบวก
            - generic [ref=e148]:
              - generic [ref=e149]: —
              - generic [ref=e150]: เซสชัน
      - generic [ref=e151]:
        - generic [ref=e152]:
          - generic [ref=e153]:
            - heading "แชนเนลที่ติดตาม" [level=2] [ref=e154]
            - link "ดูทั้งหมด" [ref=e155] [cursor=pointer]:
              - /url: "#/channels"
          - link "ยังไม่ได้ติดตามแชนเนล เพิ่มแชนเนลเพื่อกลับมาวิเคราะห์ได้เร็วขึ้น" [ref=e156] [cursor=pointer]:
            - /url: "#/channels"
            - generic [ref=e157]:
              - generic [ref=e158]: ยังไม่ได้ติดตามแชนเนล
              - generic [ref=e159]: เพิ่มแชนเนลเพื่อกลับมาวิเคราะห์ได้เร็วขึ้น
        - generic [ref=e160]:
          - generic [ref=e161]:
            - heading "เซสชันล่าสุด" [level=2] [ref=e162]
            - link "ดูทั้งหมด" [ref=e163] [cursor=pointer]:
              - /url: "#/sessions"
          - generic [ref=e166]: ยังไม่มีเซสชัน
```

# Test source

```ts
  215 |     await editable.locator('button').first().click();
  216 |     await window.waitForTimeout(500);
  217 |     const menu = editable.locator('div.absolute button');
  218 |     await expect(menu).toHaveCount(2);
  219 |     const labels = (await menu.allInnerTexts()).map((s) => s.trim());
  220 |     expect(labels.sort()).toEqual(['ผู้จัดการแบรนด์', 'โฮสต์'].sort());
  221 |     await shot(window, 'C5-role-options');
  222 |     await window.keyboard.press('Escape');
  223 |     await editable.locator('button').first().click().catch(() => {}); // close the dropdown if Esc did not
  224 |   });
  225 | 
  226 |   test('TC-MEM-C.6 (uat): ไม่มีปุ่มเชิญ/ลบ/ที่นั่ง และ "จัดการสมาชิกใน Takra Hub" เปิดเว็บ Hub', async () => {
  227 |     await openMembers();
  228 |     // The footer sentence itself names เชิญ/ลบ/ที่นั่ง, so the check is on CONTROLS and on a seat COUNT, not on words.
  229 |     const text = await window.locator(MEMBERS).innerText();
  230 |     expect(text).not.toMatch(/ที่นั่ง\s*\d|\d+\s*(\/\s*\d+\s*)?ที่นั่ง/);
  231 |     await expect(window.getByRole('button', { name: /เชิญ|ลบ|เอาออก/ })).toHaveCount(0);
  232 |     await expect(window.getByText('การเชิญ ลบสมาชิก และจำนวนที่นั่ง จัดการที่ Takra Hub — บทบาทเจ้าของก็กำหนดจาก Hub เช่นกัน')).toBeVisible();
  233 |     await app.evaluate(({ shell }) => {
  234 |       globalThis.__opened = [];
  235 |       globalThis.__origOpenExternal ||= shell.openExternal.bind(shell);
  236 |       shell.openExternal = async (url) => { globalThis.__opened.push(url); return true; };
  237 |     });
  238 |     try {
  239 |       await window.getByRole('button', { name: 'จัดการสมาชิกใน Takra Hub' }).click();
  240 |       await expect.poll(() => app.evaluate(() => globalThis.__opened.length), { timeout: 15_000 }).toBeGreaterThan(0);
  241 |       const [url] = await app.evaluate(() => globalThis.__opened);
  242 |       expect(new URL(url).hostname).toBe('uat-hub.takra.ai');
  243 |       await expect(window.getByText('เปิด Takra Hub ไม่สำเร็จ')).toHaveCount(0);
  244 |       test.info().annotations.push({ type: 'opened', description: new URL(url).origin + new URL(url).pathname });
  245 |       await shot(window, 'C6-members-footer');
  246 |     } finally {
  247 |       await app.evaluate(({ shell }) => { if (globalThis.__origOpenExternal) shell.openExternal = globalThis.__origOpenExternal; });
  248 |     }
  249 |   });
  250 | 
  251 |   test('TC-MEM-C.2 (uat): เปลี่ยน "โฮสต์" → "ผู้จัดการแบรนด์" แล้วค่าคงอยู่ (คืนค่าเดิมท้ายเทส)', async () => {
  252 |     await openMembers();
  253 |     const r = await rows();
  254 |     const host = r.find((x) => !x.owner && x.role === 'โฮสต์');
  255 |     test.skip(!host, 'ไม่มีสมาชิกบทบาท "โฮสต์" ในทีมนี้ให้เปลี่ยน');
  256 |     // Re-find the row by its email: name and email sit in adjacent divs, so their joined text has no space.
  257 |     const id = (host.text.match(/[^\s@]+@[^\s@]+\.[a-z]{2,}/i) || [host.text.split(' บทบาทใน Hub:')[0]])[0];
  258 |     test.info().annotations.push({ type: 'member', description: id });
  259 |     const rowOf = () => window.locator(ROWS).filter({ hasText: id }).first();
  260 |     const pick = async (label) => {
  261 |       await rowOf().locator('[data-member-role] button').first().click();
  262 |       await rowOf().locator('div.absolute button', { hasText: label }).click();
  263 |     };
  264 |     try {
  265 |       await pick('ผู้จัดการแบรนด์');
  266 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์', { timeout: 20_000 });
  267 |       await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  268 |       await shot(window, 'C2-after-change');
  269 |       await openMembers();   // leaves via "กลับ" and re-enters, so the value is read back from the backend
  270 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์');
  271 |       await shot(window, 'C2-reopened');
  272 |     } finally {
  273 |       await openMembers().catch(() => {});
  274 |       if ((await rowOf().locator('[data-member-role] button').first().innerText().catch(() => '')).trim() !== 'โฮสต์') {
  275 |         await pick('โฮสต์').catch(() => {});
  276 |         await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('โฮสต์', { timeout: 20_000 }).catch(() => {});
  277 |       }
  278 |     }
  279 |   });
  280 | });
  281 | 
  282 | test.describe('บทบาทต่างกันในแต่ละทีม (หาทีมตามบทบาทของบัญชีที่ login)', () => {
  283 |   const brandLink = () => window.getByRole('link', { name: 'แดชบอร์ดแบรนด์' });
  284 |   let home;     // a team this account OWNS — where the run starts and ends
  285 |   let host;     // a team where it is a HOST
  286 |   let bm;       // a team where it is a BRAND MANAGER
  287 |   let OWNER_TEAM;
  288 | 
  289 |   test.beforeAll(async () => {
  290 |     if (!signedIn) return;
  291 |     const list = (await wsState()).workspaces.filter((w) => w.state === 'active');
  292 |     home = list.find((w) => w.productRole === 'owner' && w.selected) || list.find((w) => w.productRole === 'owner');
  293 |     host = list.find((w) => w.productRole === 'host');
  294 |     bm = list.find((w) => w.productRole === 'brand_manager');
  295 |     OWNER_TEAM = home?.name;
  296 |     // Start from the owner team whatever the account last used.
  297 |     if (home && !list.find((w) => w.selected && w.workspaceId === home.workspaceId)) {
  298 |       await window.evaluate((id) => window.liveHost.auth.selectWorkspace(id), home.workspaceId);
  299 |       await window.waitForTimeout(6000);
  300 |       await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 });
  301 |     }
  302 |   });
  303 |   test.beforeEach(({}, testInfo) => {
  304 |     const needsBm = /TC-MEM-D\.2/.test(testInfo.title);
  305 |     test.skip(!home, 'บัญชีนี้ไม่ได้เป็นเจ้าของทีมไหน');
  306 |     test.skip(needsBm ? !bm : !host, needsBm ? 'บัญชีนี้ไม่ได้เป็นผู้จัดการแบรนด์ในทีมไหน' : 'บัญชีนี้ไม่ได้เป็นโฮสต์ในทีมไหน');
  307 |   });
  308 | 
  309 |   /** Switch through the profile menu, the way a user does, and wait for the reloaded shell. */
  310 |   async function switchVia(name) {
  311 |     const before = await window.evaluate(() => performance.timeOrigin);
  312 |     await openProfileMenu();
  313 |     await window.locator(`${WS_LIST} [role="option"]`).filter({ hasText: name }).first().click();
  314 |     await expect.poll(async () => window.evaluate(() => performance.timeOrigin).catch(() => before), { timeout: 60_000 }).not.toBe(before);
> 315 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 60_000 });
      |                                                           ^ TimeoutError: locator.waitFor: Timeout 60000ms exceeded.
  316 |     await window.waitForTimeout(3000);
  317 |     // A team this account never consented in stops at its consent screen — that is a precondition, not a result.
  318 |     const gate = await window.getByRole('heading', { name: /คุณเข้าร่วมพื้นที่ทำงาน/ }).isVisible().catch(() => false);
  319 |     test.skip(gate, `ยังไม่ได้ให้ความยินยอมใน "${name}" — ให้ความยินยอมด้วยมือก่อน`);
  320 |     expect((await wsState()).workspaces.find((w) => w.selected)?.name).toBe(name);
  321 |   }
  322 |   async function restoreHome() {
  323 |     await window.evaluate((id) => window.liveHost.auth.selectWorkspace(id), home.workspaceId).catch(() => {});
  324 |     await window.waitForTimeout(6000);
  325 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 }).catch(() => {});
  326 |     expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'คืนทีมเดิมไม่สำเร็จ').toBe(home.workspaceId);
  327 |   }
  328 |   async function menus() {
  329 |     await openProfileMenu();
  330 |     const members = await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).isVisible().catch(() => false);
  331 |     await closeMenu();
  332 |     return { brand: (await brandLink().count()) > 0, members };
  333 |   }
  334 | 
  335 |   test('TC-MEM-D.6 (uat): บัญชีเดียวมีบทบาทต่างกันในแต่ละทีม เมนูเปลี่ยนตามทีมที่ใช้อยู่', async () => {
  336 |     expect((await wsState()).workspaces.find((w) => w.selected)?.name).toBe(OWNER_TEAM);
  337 |     expect(await menus(), `ใน "${OWNER_TEAM}" (เจ้าของ)`).toEqual({ brand: true, members: true });
  338 |     await shot(window, 'D6-owner-team');
  339 |     try {
  340 |       await switchVia(host.name);
  341 |       expect(await menus(), `ใน "${host.name}" (โฮสต์)`).toEqual({ brand: false, members: false });
  342 |       await shot(window, 'D6-host-team');
  343 |     } finally {
  344 |       await restoreHome();
  345 |     }
  346 |     expect(await menus(), 'กลับทีมเจ้าของแล้วเมนูกลับมา').toEqual({ brand: true, members: true });
  347 |   });
  348 | 
  349 |   test('TC-MEM-D.2 (uat): ผู้จัดการแบรนด์เห็น "แดชบอร์ดแบรนด์" แต่ไม่มี "สมาชิกและบทบาท"', async () => {
  350 |     try {
  351 |       await switchVia(bm.name);
  352 |       expect(await menus(), `ใน "${bm.name}" (ผู้จัดการแบรนด์)`).toEqual({ brand: true, members: false });
  353 |       await brandLink().first().click();
  354 |       await expect(window.getByRole('heading', { name: 'แดชบอร์ดแบรนด์' }).first()).toBeVisible({ timeout: 30_000 });
  355 |       await shot(window, 'D2-bm-brand-dashboard');
  356 |       await window.evaluate(() => { location.hash = '#/settings/members'; });
  357 |       await window.waitForTimeout(2000);
  358 |       await expect(window.locator(MEMBERS)).toHaveCount(0);
  359 |       await shot(window, 'D2-bm-members-url');
  360 |     } finally {
  361 |       await restoreHome();
  362 |     }
  363 |   });
  364 | 
  365 |   test('TC-MEM-D.3 (uat): โฮสต์ไม่มี "แดชบอร์ดแบรนด์" และ "สมาชิกและบทบาท" · เมนูของตัวเองใช้ได้', async () => {
  366 |     try {
  367 |       await switchVia(host.name);
  368 |       expect(await menus()).toEqual({ brand: false, members: false });
  369 |       // Typing the owner-only URL does not open it either.
  370 |       await window.evaluate(() => { location.hash = '#/settings/members'; });
  371 |       await window.waitForTimeout(2000);
  372 |       await expect(window.locator(MEMBERS)).toHaveCount(0);
  373 |       for (const [name, hash] of [['หน้าหลัก', '#/dashboard'], ['เซสชัน', '#/sessions'], ['รายงานประจำวัน', null]]) {
  374 |         await window.getByRole('link', { name, exact: true }).first().click();
  375 |         await window.waitForTimeout(2500);
  376 |         if (hash) expect(await window.evaluate(() => location.hash)).toBe(hash);
  377 |         const text = await window.locator('body').innerText();
  378 |         expect(text.length, `หน้า "${name}" ว่าง`).toBeGreaterThan(50);
  379 |         expect(TECHNICAL_LEAK.test(text), `หน้า "${name}" มี error ทางเทคนิครั่ว`).toBe(false);
  380 |         await shot(window, `D3-${hash ? hash.slice(2) : 'reports'}`);
  381 |       }
  382 |     } finally {
  383 |       await restoreHome();
  384 |     }
  385 |   });
  386 | 
  387 |   test('TC-MEM-A.6 (uat): ข้อมูลแต่ละทีมแยกกัน — แดชบอร์ดแบรนด์ของทีมเจ้าของไม่ปนไปทีมที่เป็นโฮสต์', async () => {
  388 |     await brandLink().first().click();
  389 |     await expect(window.getByRole('heading', { name: 'แดชบอร์ดแบรนด์' }).first()).toBeVisible({ timeout: 30_000 });
  390 |     await window.waitForTimeout(4000);
  391 |     const ownerText = await window.locator('main').innerText();
  392 |     const summary = (ownerText.match(/\d+\s*โฮสต์\s*·\s*\d+\s*ไลฟ์[^\n]*/) || [''])[0];
  393 |     // Live titles on the owner team's dashboard (e.g. "shop_21092026") — the fingerprints to look for elsewhere.
  394 |     const lives = [...new Set(ownerText.match(/[A-Za-z0-9_.]+_\d{8}/g) || [])];
  395 |     test.info().annotations.push({ type: 'owner-team', description: `${summary} · lives=${lives.join(', ')}` });
  396 |     await shot(window, 'A6-owner-brand-dashboard');
  397 |     try {
  398 |       await switchVia(host.name);
  399 |       await expect(brandLink()).toHaveCount(0);
  400 |       for (const hash of ['#/dashboard', '#/sessions', '#/reports']) {
  401 |         await window.evaluate((h) => { location.hash = h; }, hash);
  402 |         await window.waitForTimeout(3000);
  403 |         const text = await window.locator('body').innerText();
  404 |         for (const live of lives) expect(text, `ไลฟ์ "${live}" ของ "${OWNER_TEAM}" โผล่ในทีม "${host.name}" ที่ ${hash}`).not.toContain(live);
  405 |         await shot(window, `A6-host-${hash.slice(2)}`);
  406 |       }
  407 |       test.skip(lives.length === 0, `แดชบอร์ดของ "${OWNER_TEAM}" ไม่มีไลฟ์ให้ใช้เทียบ`);
  408 |     } finally {
  409 |       await restoreHome();
  410 |     }
  411 |   });
  412 | });
  413 | 
  414 | test.describe('ไม่มีเน็ต (จำลอง: ตัดคลาวด์ คง localhost)', () => {
  415 |   test('TC-MEM-H.2 (uat): เปิด "สมาชิกและบทบาท" ตอนไม่มีเน็ต ขึ้นข้อความดึงรายชื่อไม่ได้', async () => {
```