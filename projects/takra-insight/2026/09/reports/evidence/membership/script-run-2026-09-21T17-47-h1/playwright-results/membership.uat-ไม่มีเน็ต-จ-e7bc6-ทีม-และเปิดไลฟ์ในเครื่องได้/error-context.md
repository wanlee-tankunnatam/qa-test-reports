# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> ไม่มีเน็ต (จำลอง: ตัดคลาวด์ คง localhost) >> TC-MEM-H.3 (uat): เปิดแอปตอนไม่มีเน็ต ยังเข้าทีมเดิม ไม่ถูกถามเลือกทีม และเปิดไลฟ์ในเครื่องได้
- Location: e2e/uat/membership.uat.spec.js:344:3

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "blocked"
Received: "reached"
```

# Page snapshot

```yaml
- img [ref=e4]
```

# Test source

```ts
  257 |     // Re-find the row by its email: name and email sit in adjacent divs, so their joined text has no space.
  258 |     const id = (host.text.match(/[^\s@]+@[^\s@]+\.[a-z]{2,}/i) || [host.text.split(' บทบาทใน Hub:')[0]])[0];
  259 |     test.info().annotations.push({ type: 'member', description: id });
  260 |     const rowOf = () => window.locator(ROWS).filter({ hasText: id }).first();
  261 |     const pick = async (label) => {
  262 |       await rowOf().locator('[data-member-role] button').first().click();
  263 |       await rowOf().locator('div.absolute button', { hasText: label }).click();
  264 |     };
  265 |     try {
  266 |       await pick('ผู้จัดการแบรนด์');
  267 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์', { timeout: 20_000 });
  268 |       await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  269 |       await shot(window, 'C2-after-change');
  270 |       await openMembers();   // leaves via "กลับ" and re-enters, so the value is read back from the backend
  271 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์');
  272 |       await shot(window, 'C2-reopened');
  273 |     } finally {
  274 |       await openMembers().catch(() => {});
  275 |       if ((await rowOf().locator('[data-member-role] button').first().innerText().catch(() => '')).trim() !== 'โฮสต์') {
  276 |         await pick('โฮสต์').catch(() => {});
  277 |         await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('โฮสต์', { timeout: 20_000 }).catch(() => {});
  278 |       }
  279 |     }
  280 |   });
  281 | });
  282 | 
  283 | test.describe('ไม่มีเน็ต (จำลอง: ตัดคลาวด์ คง localhost)', () => {
  284 |   test('TC-MEM-H.2 (uat): เปิด "สมาชิกและบทบาท" ตอนไม่มีเน็ต ขึ้นข้อความดึงรายชื่อไม่ได้', async () => {
  285 |     test.skip(!isOwner, 'qa@takra.ai ไม่ใช่เจ้าของในพื้นที่ทำงานนี้');
  286 |     if (await window.locator(MEMBERS).isVisible().catch(() => false)) {
  287 |       await window.getByRole('button', { name: 'กลับ', exact: true }).click();
  288 |       await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 15_000 });
  289 |     }
  290 |     await goOffline();
  291 |     try {
  292 |       await openProfileMenu();
  293 |       await window.getByRole('button', { name: 'สมาชิกและบทบาท' }).click();
  294 |       const alert = window.locator(`${MEMBERS} [role="alert"]`);
  295 |       await expect(alert).toHaveText('ยังดึงรายชื่อสมาชิกไม่ได้ในขณะนี้ ลองใหม่อีกครั้ง', { timeout: 45_000 });
  296 |       await expect(window.locator(`${MEMBERS} [role="status"]`)).toHaveCount(0);   // not stuck on "กำลังโหลด…"
  297 |       await expect(window.locator(ROWS)).toHaveCount(0);                             // no stale list
  298 |       await shot(window, 'H2-members-offline');
  299 |     } finally {
  300 |       await goOnline();
  301 |       if (await window.locator(MEMBERS).isVisible().catch(() => false)) {
  302 |         await window.getByRole('button', { name: 'กลับ', exact: true }).click().catch(() => {});
  303 |       }
  304 |     }
  305 |   });
  306 | 
  307 |   test('TC-MEM-H.1 (uat): สลับพื้นที่ทำงานตอนไม่มีเน็ต ขึ้นข้อความและยังอยู่ทีมเดิม · เน็ตกลับแล้วสลับได้', async () => {
  308 |     test.skip(workspaces.length < 2, 'ต้องมีพื้นที่ทำงาน ≥ 2 ที่');
  309 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 15_000 });
  310 |     const st = await wsState();
  311 |     const original = st.workspaces.find((w) => w.selected);
  312 |     const target = st.workspaces.find((w) => !w.selected && w.productRole === 'owner') || st.workspaces.find((w) => !w.selected);
  313 |     await goOffline();
  314 |     try {
  315 |       await openProfileMenu();
  316 |       await window.locator(`${WS_LIST} [role="option"]`).filter({ hasText: target.name }).first().click();
  317 |       const err = window.getByRole('alert').filter({ hasText: /ตรวจสอบสิทธิ์ของพื้นที่ทำงานนี้ไม่ได้ในขณะนี้ ลองใหม่อีกครั้ง|สลับพื้นที่ทำงานไม่สำเร็จ ลองใหม่อีกครั้ง/ });
  318 |       await expect(err.first()).toBeVisible({ timeout: 45_000 });
  319 |       await shot(window, 'H1-switch-offline');
  320 |       expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'ทีมที่ใช้งานอยู่ต้องไม่เปลี่ยน').toBe(original.workspaceId);
  321 |       await expect(window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`)).toContainText(original.name);
  322 |       await closeMenu();
  323 |     } finally {
  324 |       await goOnline();
  325 |     }
  326 |     // Back online: the same switch goes through.
  327 |     const before = await window.evaluate(() => performance.timeOrigin);
  328 |     await openProfileMenu();
  329 |     await window.locator(`${WS_LIST} [role="option"]`).filter({ hasText: target.name }).first().click();
  330 |     try {
  331 |       await expect.poll(async () => window.evaluate(() => performance.timeOrigin).catch(() => before), { timeout: 45_000 }).not.toBe(before);
  332 |       await window.waitForTimeout(3000);
  333 |       expect((await wsState()).workspaces.find((w) => w.selected)?.name).toBe(target.name);
  334 |       await shot(window, 'H1-switch-online');
  335 |     } finally {
  336 |       await window.evaluate((id) => window.liveHost.auth.selectWorkspace(id), original.workspaceId).catch(() => {});
  337 |       await window.waitForTimeout(6000);
  338 |       await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 }).catch(() => {});
  339 |       expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'คืนทีมเดิมไม่สำเร็จ').toBe(original.workspaceId);
  340 |     }
  341 |   });
  342 | 
  343 |   // Runs LAST: closes the shared app and cold-starts one that is offline from its first line.
  344 |   test('TC-MEM-H.3 (uat): เปิดแอปตอนไม่มีเน็ต ยังเข้าทีมเดิม ไม่ถูกถามเลือกทีม และเปิดไลฟ์ในเครื่องได้', async () => {
  345 |     const st = await wsState();
  346 |     const selected = st.workspaces.find((w) => w.selected);
  347 |     await closeApp(app); app = null;
  348 |     ({ app, window } = await launchApp({
  349 |       multiSession: 'unset',
  350 |       env: { NODE_OPTIONS: `--require ${join(import.meta.dirname, '_offline-main.cjs')}` },
  351 |     }));
  352 |     await app.evaluate(async ({ session }, proxy) => {
  353 |       await session.defaultSession.setProxy(proxy);
  354 |       await session.defaultSession.closeAllConnections();
  355 |     }, PROXY_OFF);
  356 |     // The Hub really is unreachable from this main process.
> 357 |     expect(await app.evaluate(async () => { try { await fetch('https://uat-hub.takra.ai/'); return 'reached'; } catch { return 'blocked'; } })).toBe('blocked');
      |                                                                                                                                                 ^ Error: expect(received).toBe(expected) // Object.is equality
  358 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 60_000 });
  359 |     await window.waitForTimeout(5000);
  360 |     await expect(window.locator('[role="dialog"][aria-labelledby="workspace-pick-title"]')).toHaveCount(0);
  361 |     await expect(window.locator('[role="dialog"]')).toHaveCount(0);
  362 |     expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'ยังอยู่ทีมเดิม').toBe(selected.workspaceId);
  363 |     await shot(window, 'H3-offline-start');
  364 |     await window.getByRole('link', { name: 'เซสชัน' }).or(window.getByRole('button', { name: 'เซสชัน' })).first().click();
  365 |     const firstSession = window.locator('a[href*="/sessions/"], [data-testid="session-row"], [role="row"]').first();
  366 |     await expect(firstSession, 'ไม่มีไลฟ์ที่บันทึกไว้ในเครื่องให้เปิด').toBeVisible({ timeout: 30_000 });
  367 |     await firstSession.click();
  368 |     await window.waitForTimeout(4000);
  369 |     const text = await window.locator('body').innerText();
  370 |     expect(text).not.toMatch(/ต่อระบบไม่ได้.*สมาชิก|เลือกพื้นที่ทำงาน/);
  371 |     expect(await window.evaluate(() => location.hash)).toMatch(/#\/session/);
  372 |     await shot(window, 'H3-offline-session');
  373 |   });
  374 | });
  375 | 
```