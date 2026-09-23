# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: membership.uat.spec.js >> หน้า "สมาชิกและบทบาท" (เจ้าของ) >> TC-MEM-C.2 (uat): เปลี่ยน "โฮสต์" → "ผู้จัดการแบรนด์" แล้วค่าคงอยู่ (คืนค่าเดิมท้ายเทส)
- Location: e2e/uat/membership.uat.spec.js:227:3

# Error details

```
TimeoutError: locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator('[data-testid="workspace-members"] ul[role="list"] > li').filter({ hasText: 'wanleeta QA wanleeta.official@gmail.com' }).first().locator('[data-member-role] button').first()

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
  135 |       await expect(window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`)).toContainText('ใช้งานอยู่');
  136 |       await shot(window, 'A2-after-menu');
  137 |       await closeMenu();
  138 |     } else {
  139 |       // The new team's own gate instead of the shell — still the reload into the chosen team:
  140 |       //  · never consented there → that team's consent screen, named after it (Story 9.4)
  141 |       //  · its package expired  → the expired screen, which carries the "ใช้พื้นที่ทำงานอื่นแทน" switcher
  142 |       const consentGate = window.getByRole('heading', { name: new RegExp(`คุณเข้าร่วมพื้นที่ทำงาน.*${target.name}`) });
  143 |       const expiredGate = window.getByRole('heading', { name: 'แพ็กเกจของพื้นที่ทำงานนี้หมดอายุแล้ว' });
  144 |       await expect(consentGate.or(expiredGate).first()).toBeVisible();
  145 |       const gate = (await expiredGate.isVisible()) ? 'expired' : 'consent';
  146 |       if (gate === 'expired') {
  147 |         const sel = window.locator(`${WS_LIST} [role="option"][aria-selected="true"]`);
  148 |         await expect(sel).toContainText(target.name);
  149 |         await expect(sel).toContainText('ใช้งานอยู่');
  150 |       }
  151 |       test.info().annotations.push({ type: 'landed-on', description: `${gate} gate of "${target.name}"` });
  152 |       await shot(window, `A2-after-${gate}-gate`);
  153 |     }
  154 |   } finally {
  155 |     // Back to the original team through the same IPC the menu uses — it works from the consent screen too.
  156 |     await window.evaluate((id) => window.liveHost.auth.selectWorkspace(id), original.workspaceId).catch(() => {});
  157 |     await window.waitForTimeout(6000);
  158 |     await window.getByRole('button', PROFILE_BTN).first().waitFor({ timeout: 30_000 }).catch(() => {});
  159 |     expect((await wsState()).workspaces.find((w) => w.selected)?.workspaceId, 'คืนทีมเดิมไม่สำเร็จ').toBe(original.workspaceId);
  160 |   }
  161 | });
  162 | 
  163 | test.describe('หน้า "สมาชิกและบทบาท" (เจ้าของ)', () => {
  164 |   test.beforeEach(() => { test.skip(!isOwner, 'qa@takra.ai ไม่ใช่เจ้าของในพื้นที่ทำงานนี้ — ไม่มีเมนู "สมาชิกและบทบาท"'); });
  165 | 
  166 |   test('TC-MEM-C.1 (uat): เห็นรายชื่อ บทบาทใน Hub และบทบาทใน Insight', async () => {
  167 |     await openMembers();
  168 |     await expect(window.getByRole('heading', { name: 'สมาชิกและบทบาท' }).first()).toBeVisible();
  169 |     await expect(window.getByText('กำหนดบทบาทใน Takra Insight ให้สมาชิกในพื้นที่ทำงานนี้')).toBeVisible();
  170 |     const r = await rows();
  171 |     expect(r.length).toBeGreaterThan(0);
  172 |     for (const row of r) {
  173 |       expect(row.text, `แถว ${row.i} ไม่มีบรรทัด "บทบาทใน Hub:"`).toContain('บทบาทใน Hub:');
  174 |       if (row.owner) expect(row.text).toContain('เจ้าของ');
  175 |       else expect(['ผู้จัดการแบรนด์', 'โฮสต์', 'ยังไม่กำหนด'], `แถว ${row.i} บทบาท "${row.role}"`).toContain(row.role);
  176 |     }
  177 |     expect(r.filter((x) => x.owner).length, 'ต้องมีแถวเจ้าของ').toBeGreaterThan(0);
  178 |     await shot(window, 'C1-members');
  179 |     test.info().annotations.push({ type: 'rows', description: JSON.stringify(r.map((x) => ({ owner: x.owner, role: x.role }))) });
  180 |   });
  181 | 
  182 |   test('TC-MEM-C.5 (uat): ตั้ง "เจ้าของ" จากแอปไม่ได้ และแถวเจ้าของเปลี่ยนไม่ได้', async () => {
  183 |     await openMembers();
  184 |     const ownerRow = window.locator(ROWS).filter({ has: window.locator('[data-member-owner]') }).first();
  185 |     await expect(ownerRow.locator('[data-member-owner]')).toHaveText('เจ้าของ');
  186 |     await expect(ownerRow.locator('button')).toHaveCount(0);
  187 |     await ownerRow.locator('[data-member-owner]').click();
  188 |     await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  189 |     const editable = window.locator(`${ROWS} [data-member-role]`).first();
  190 |     test.skip(await editable.count() === 0, 'ไม่มีสมาชิกที่ไม่ใช่เจ้าของให้เปิดช่องบทบาท');
  191 |     await editable.locator('button').first().click();
  192 |     await window.waitForTimeout(500);
  193 |     const menu = editable.locator('div.absolute button');
  194 |     await expect(menu).toHaveCount(2);
  195 |     const labels = (await menu.allInnerTexts()).map((s) => s.trim());
  196 |     expect(labels.sort()).toEqual(['ผู้จัดการแบรนด์', 'โฮสต์'].sort());
  197 |     await shot(window, 'C5-role-options');
  198 |     await window.keyboard.press('Escape');
  199 |     await editable.locator('button').first().click().catch(() => {}); // close the dropdown if Esc did not
  200 |   });
  201 | 
  202 |   test('TC-MEM-C.6 (uat): ไม่มีปุ่มเชิญ/ลบ/ที่นั่ง และ "จัดการสมาชิกใน Takra Hub" เปิดเว็บ Hub', async () => {
  203 |     await openMembers();
  204 |     // The footer sentence itself names เชิญ/ลบ/ที่นั่ง, so the check is on CONTROLS and on a seat COUNT, not on words.
  205 |     const text = await window.locator(MEMBERS).innerText();
  206 |     expect(text).not.toMatch(/ที่นั่ง\s*\d|\d+\s*(\/\s*\d+\s*)?ที่นั่ง/);
  207 |     await expect(window.getByRole('button', { name: /เชิญ|ลบ|เอาออก/ })).toHaveCount(0);
  208 |     await expect(window.getByText('การเชิญ ลบสมาชิก และจำนวนที่นั่ง จัดการที่ Takra Hub — บทบาทเจ้าของก็กำหนดจาก Hub เช่นกัน')).toBeVisible();
  209 |     await app.evaluate(({ shell }) => {
  210 |       globalThis.__opened = [];
  211 |       globalThis.__origOpenExternal ||= shell.openExternal.bind(shell);
  212 |       shell.openExternal = async (url) => { globalThis.__opened.push(url); return true; };
  213 |     });
  214 |     try {
  215 |       await window.getByRole('button', { name: 'จัดการสมาชิกใน Takra Hub' }).click();
  216 |       await expect.poll(() => app.evaluate(() => globalThis.__opened.length), { timeout: 15_000 }).toBeGreaterThan(0);
  217 |       const [url] = await app.evaluate(() => globalThis.__opened);
  218 |       expect(new URL(url).hostname).toBe('uat-hub.takra.ai');
  219 |       await expect(window.getByText('เปิด Takra Hub ไม่สำเร็จ')).toHaveCount(0);
  220 |       test.info().annotations.push({ type: 'opened', description: new URL(url).origin + new URL(url).pathname });
  221 |       await shot(window, 'C6-members-footer');
  222 |     } finally {
  223 |       await app.evaluate(({ shell }) => { if (globalThis.__origOpenExternal) shell.openExternal = globalThis.__origOpenExternal; });
  224 |     }
  225 |   });
  226 | 
  227 |   test('TC-MEM-C.2 (uat): เปลี่ยน "โฮสต์" → "ผู้จัดการแบรนด์" แล้วค่าคงอยู่ (คืนค่าเดิมท้ายเทส)', async () => {
  228 |     await openMembers();
  229 |     const r = await rows();
  230 |     const host = r.find((x) => !x.owner && x.role === 'โฮสต์');
  231 |     test.skip(!host, 'ไม่มีสมาชิกบทบาท "โฮสต์" ในทีมนี้ให้เปลี่ยน');
  232 |     const id = host.text.split(' บทบาทใน Hub:')[0];        // name + email, used to re-find the row after reload
  233 |     const rowOf = () => window.locator(ROWS).filter({ hasText: id }).first();
  234 |     const pick = async (label) => {
> 235 |       await rowOf().locator('[data-member-role] button').first().click();
      |                                                                  ^ TimeoutError: locator.click: Timeout 30000ms exceeded.
  236 |       await rowOf().locator('div.absolute button', { hasText: label }).click();
  237 |     };
  238 |     try {
  239 |       await pick('ผู้จัดการแบรนด์');
  240 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์', { timeout: 20_000 });
  241 |       await expect(window.locator(`${MEMBERS} [role="alert"]`)).toHaveCount(0);
  242 |       await shot(window, 'C2-after-change');
  243 |       await openMembers();   // leaves via "กลับ" and re-enters, so the value is read back from the backend
  244 |       await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('ผู้จัดการแบรนด์');
  245 |       await shot(window, 'C2-reopened');
  246 |     } finally {
  247 |       await openMembers().catch(() => {});
  248 |       if ((await rowOf().locator('[data-member-role] button').first().innerText().catch(() => '')).trim() !== 'โฮสต์') {
  249 |         await pick('โฮสต์').catch(() => {});
  250 |         await expect(rowOf().locator('[data-member-role] button').first()).toHaveText('โฮสต์', { timeout: 20_000 }).catch(() => {});
  251 |       }
  252 |     }
  253 |   });
  254 | });
  255 | 
```