#!/usr/bin/env node
// ตรวจการโต้ตอบของรายงาน e2e ของ takra-hub (hub_e2e_run_report.py) ในเบราว์เซอร์จริง
//
// มีไว้กันบัคซ้ำ: 27 ต.ค. 2569 รายงานเปิดดูรายละเอียดตัวที่ไม่ผ่านไม่ได้ หลังกดตัวกรอง/ฟีเจอร์
// (สองที่แก้คลาส hide/show ขัดกัน) ⇒ **รันทุกครั้งที่แก้ HTML/JS ใน hub_e2e_run_report.py**
//
// ใช้:
//   node tools/build/check_hub_report_ui.mjs
//   PLAYWRIGHT_MODULE=/path/to/node_modules/playwright node tools/build/check_hub_report_ui.mjs
// ผ่าน = exit 0 · ไม่ผ่าน = exit 1 พร้อมบอกว่าข้อไหนพัง
import { execFileSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
const PW_CANDIDATES = [
  process.env.PLAYWRIGHT_MODULE,
  "playwright",
  "/Users/ice/Documents/rf/takra-hub/node_modules/.pnpm/node_modules/playwright",
].filter(Boolean);
let chromium;
for (const c of PW_CANDIDATES) {
  try { ({ chromium } = require(c)); break; } catch { /* ลองตัวถัดไป */ }
}
if (!chromium) {
  console.error("หา playwright ไม่เจอ — ตั้ง PLAYWRIGHT_MODULE=<path ของ node_modules/playwright>");
  process.exit(2);
}

// ผลตัวอย่าง: 2 ฟีเจอร์ · fail 2 · pass 1 · skip 1 (มีเหตุผลยาว → มีแถวรายละเอียด)
const fixture = {
  stats: { startTime: "2026-10-27T19:06:40.000Z", expected: 1, unexpected: 2, flaky: 0, skipped: 1, duration: 60000 },
  suites: [
    { file: "alpha/ui.spec.ts", specs: [
      { title: "TC-A-UI-POS-01 · ผ่าน @ui", file: "alpha/ui.spec.ts", tests: [{ status: "expected", results: [{ duration: 10 }] }] },
      { title: "TC-A-UI-NEG-01 · ตก @ui", file: "alpha/ui.spec.ts", tests: [{ status: "unexpected", results: [{ duration: 10, error: { message: "Error: expect(received).toBe(expected)" } }] }] },
    ] },
    { file: "beta/ui.spec.ts", specs: [
      { title: "TC-B-UI-NEG-01 · ตก @ui", file: "beta/ui.spec.ts", tests: [{ status: "unexpected", results: [{ duration: 10, error: { message: "Error: element(s) not found" } }] }] },
      { title: "TC-B-UI-EDGE-01 · ข้าม @ui", file: "beta/ui.spec.ts", tests: [{ status: "skipped", annotations: [{ type: "skip", description: "ยังไม่มีบัญชี · ต้องขอ infra · รอ TKH-000" }], results: [] }] },
    ] },
  ],
};

const dir = mkdtempSync(join(tmpdir(), "hub-report-check-"));
const results = join(dir, "results.json");
const out = join(dir, "report.html");
writeFileSync(results, JSON.stringify(fixture));
execFileSync("python3", ["-I", join(HERE, "hub_e2e_run_report.py"), "--results", results, "--tier", "check", "--out", out], { stdio: "ignore" });

const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto("file://" + out);
const failures = [];
const check = async (name, cond) => { if (!(await cond())) failures.push(name); };

const failRow = page.locator('tr.trow[data-st="fail"]').first();
const uid = await failRow.getAttribute("data-uid");
const detail = page.locator(`tr.detail[data-uid="${uid}"]`);
const chip = (v) => page.locator(`.fchip[data-f="st"][data-v="${v}"]`);
const fsrow = page.locator("tr.fsrow").first();

await check("แถวรายละเอียดต้องปิดอยู่ตอนเปิดหน้า", async () => !(await detail.isVisible()));
await failRow.click();
await check("1) กดแถวที่ตก → รายละเอียดต้องขึ้น", () => detail.isVisible());
await failRow.click();
await check("1) กดซ้ำ → รายละเอียดต้องปิด", async () => !(await detail.isVisible()));

await chip("fail").click();
await failRow.click();
await check("2) กดตัวกรอง FAIL แล้วกดแถว → รายละเอียดต้องขึ้น", () => detail.isVisible());
await chip("pass").click();
await check("2) เปลี่ยนตัวกรองเป็น PASS → รายละเอียดของแถวที่ตกต้องหาย", async () => !(await detail.isVisible()));
await chip("pass").click();
await failRow.click();

if (await fsrow.count()) {
  await fsrow.click();
  await fsrow.click();
  await failRow.click();
  await check("3) กดฟีเจอร์ในตารางสรุป (เปิด/ปิด) แล้วกดแถว → รายละเอียดต้องขึ้น", () => detail.isVisible());
} else {
  failures.push("3) ไม่พบแถวฟีเจอร์ในตารางสรุป (tr.fsrow)");
}

await browser.close();
if (failures.length) {
  console.error("❌ รายงานพัง:\n" + failures.map((f) => "  • " + f).join("\n"));
  process.exit(1);
}
console.log("✅ รายงาน hub: เปิด/ปิดรายละเอียดได้ทุกเส้นทาง (ตรง · หลังกรอง · หลังกดฟีเจอร์)");
