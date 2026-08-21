# qa-test-reports — คู่มือเขียน/แก้ Test Case (บังคับ)

repo นี้เก็บรายงาน manual test case (UI) ของทุกโปรเจกต์ไว้ใต้ `projects/<proj>/reports/`
(บางชุดของ takra-rerun อยู่ `projects/takra-rerun/2026/07/reports/`)

**ทุกครั้งที่สร้าง/แก้ Test Case** ให้ทำตาม 3 ชั้นนี้เสมอ:
ชั้น 1 กติกากลาง (ใช้ทุกโปรเจกต์) · ชั้น 2 ตารางต่อโปรเจกต์ (path ต่างกัน) · ชั้น 3 scope ราย task

---

## ชั้น 1 — กติกากลาง (ทุกโปรเจกต์ ทุกเคส)

### Test Steps = Steps to Reproduce (self-contained)
- ทุกเคสเริ่มจากต้นเสมอ: `เปิดแอป → เข้าสู่ระบบ(บัญชี UAT) → ไปที่เมนู/หน้า "…" → ลงมือทำ`
- ห้ามเริ่มกลางทาง (ห้ามขึ้นต้นด้วย action ลอยๆ เช่น "กดปุ่มเพิ่ม") — ห้ามฝากทางเข้าไว้ใน Precondition
- เป็นภาษาคน อ่านแล้วทำตามได้จริง ไม่ใช่ศัพท์เทคนิค
- **รวม step ย่อยสั้นๆ เป็นประโยคเดียวธรรมชาติ** (ทั้งเคส ~3–6 steps)
- ปิดท้ายด้วย step สังเกตผล ถ้า step สุดท้ายยังเป็น action (เช่น "สังเกตว่ารายการใหม่ขึ้นในตาราง")

### คำศัพท์ UI — ลอกจริง ห้ามคิดเอง
- ชื่อปุ่ม/เมนู/แท็บ/ข้อความ/ป้าย ต้องลอก **คำจริงจากแหล่งในชั้น 2** ใส่ในเครื่องหมายคำพูด "…"
- ห้ามแปลจาก en เอง ห้ามแต่งคำเอง
- หา UI จริง/คีย์ข้อความไม่เจอ → บอกว่า "ไม่พบใน UI" คงของเดิมไว้ อย่าเดา

### Expected Result — อ้างเอกสาร
- เขียนให้ตรงกับ Test Steps ล่าสุด และวัดผลได้ (สังเกตเห็นจริงบนจอ)
- ยึดพฤติกรรมตาม **เอกสารสเปก** ไม่ใช่เดาจากโค้ด
- ปิดท้ายด้วยที่มา เช่น `ที่มา: Epic X · Story Y.Z · FRnn`

### ขอบเขตเนื้อหา
- **UI เท่านั้น** — ไม่แตะ backend/API/ฐานข้อมูล/โครงสร้างภายใน
- ก่อนเขียน/แก้ ต้องเปิดโค้ด UI จริงดู flow ก่อนเสมอ

---

## ชั้น 2 — ตารางต่อโปรเจกต์ (เลือกตามโปรเจกต์ของรายงานที่กำลังทำ)

| โปรเจกต์ | โค้ด (repo) | UI source | คำ UI จริงมาจาก | เอกสาร (`_bmad-output/planning-artifacts/`) |
|---|---|---|---|---|
| **takra-ai** | `/Users/ice/Documents/rf/takra-ai` | `apps/web/src` | **i18n** — `apps/web/src/i18n/locales/th/*.ts` (namespace: auth · live · liveRoom · products · settings · studio · schedule · scripts · pages · pagesLive · home · entitlement · voices · avatars …) | `epics.md` · `epics-mvp2.md` · `prd.md` |
| **takra-rerun** | `/Users/ice/Documents/rf/takra-rerun` | `web/src` | **ฝังไทยในโค้ด** — grep คำใน `web/src/features/**` (ไม่มี i18n) | `epics.md` · `epics-mvp2.md` · `prd.md` |
| **takra-insight** | `/Users/ice/Documents/rf/takra-insight` | `apps/web/src` | **ฝังไทยในโค้ด** — grep คำใน `apps/web/src/**` (ไม่มี i18n) | `epics.md` · `epics-th.md` · `prd.md` · `prd-th.md` (มีเวอร์ชันไทย) |
| **takra-hub** | `/Users/ice/Documents/rf/takra-hub` (local develop ตามหลัง origin มาก — อ่านจาก `origin/develop` ผ่าน worktree/`git show`) | `apps/web/src` | **ฝังไทยในโค้ด** — grep คำใน `apps/web/src/**` (ไม่มี i18n) | ⚠️ อยู่ที่ `docs/` ไม่ใช่ `_bmad-output/planning-artifacts/` — `docs/epics.md` (MVP-1 Epic 1–4) · `docs/epics-mvp2.md` · `docs/prd.md` · เคส UI เดิม `_bmad-output/test-artifacts/case/*/ui.md` · รายงาน generate จาก `tools/build/hub_cases.py` (ดู README) |

> ก่อนเริ่มทุกครั้ง: ยืนยันว่ากำลังทำ **โปรเจกต์ไหน** แล้วใช้ path จากแถวนั้น — อย่าเอา path ข้ามโปรเจกต์

### ทะเบียนกลาง — path + Jira ของทุกโปรเจกต์ (ไม่ต้องแปะซ้ำทุกครั้ง)

ค่าจริงเก็บเป็นไฟล์เดียวที่ [`tools/project-paths.json`](tools/project-paths.json) (แก้ที่นั่นที่เดียว · เครื่องมือ/สคริปต์อ่านไฟล์นี้ได้เลย)

| โปรเจกต์ | repo โค้ด | Jira key | Jira board timeline | รายงานใน repo นี้ | hub |
|---|---|---|---|---|---|
| **takra-ai** | `/Users/ice/Documents/rf/takra-ai` | `TAKRA` | https://kitdi.atlassian.net/jira/software/projects/TAKRA/boards/1593/timeline | `projects/takra-ai/` | `?project=ai` |
| **takra-rerun** | `/Users/ice/Documents/rf/takra-rerun` | `TAK` | https://kitdi.atlassian.net/jira/software/projects/TAK/boards/1661/timeline | `projects/takra-rerun/` | `?project=rerun` |
| **takra-insight** | `/Users/ice/Documents/rf/takra-insight` | `TI` | https://kitdi.atlassian.net/jira/software/projects/TI/boards/1660/timeline | `projects/takra-insight/` | `?project=insight` |
| **takra-hub** | `/Users/ice/Documents/rf/takra-hub` | `TKH` | https://kitdi.atlassian.net/jira/software/projects/TKH/boards/1733/timeline | `projects/takra-hub/` | `?project=hub` |

> Jira เป็นลิงก์อ้างอิงสำหรับคน — ไม่มี API token ใน repo นี้ ถ้าต้องดึงสถานะใบงานให้ผู้ใช้ export/แปะข้อมูลมา

---

## ชั้น 3 — scope ราย task (ระบุทุกครั้ง ห้ามล้ำ)

- ทำงานตาม scope ที่สั่ง **เป๊ะ** ไม่ลามไปแตะส่วนที่ไม่ได้สั่ง
- **MVP / Epic:** ถ้าสั่ง "แก้เฉพาะ MVP-1" หรือ "เฉพาะ Epic N" → เคสนอก scope ห้ามแตะเลย
  (เอกสารก็ใช้เฉพาะที่ตรง scope เช่น MVP-1 ไม่เปิด `epics-mvp2.md`)
- **ฟิลด์ที่แก้:** ถ้าสั่ง "แก้แค่ Test Steps + Expected Result" → ห้ามแตะ ID · ชื่อเคส · Priority · Epic/Feature · Precondition · Test Data · สถานะผลเทส · โครง HTML/harness · จำนวน/ลำดับเคส

### 2 โหมดการแก้ — ถามถ้าไม่ชัด
- **แก้ในที่เดิม (edit-in-place):** เคสยังตรงกับ flow ปัจจุบัน แค่ปรับถ้อยคำ/สไตล์ → คง ID + จำนวนเคสเท่าเดิม แก้เฉพาะฟิลด์ที่สั่ง
- **Recreate (เขียนใหม่ เพราะ flow เปลี่ยน):** UI/flow เปลี่ยนจน step เดิมใช้ไม่ได้ → เขียนเคสใหม่จาก UI ปัจจุบัน แต่ **คงโครงไฟล์/harness + ธรรมเนียม ID เดิม** และระบุชัดว่าเคสไหน recreate/เพิ่ม/ลบ

---

## เทคนิคไฟล์รายงาน (harness)
- แต่ละไฟล์ self-contained: `<script id="store-data">` เก็บสถานะผลเทส (key = uid `tc-N`), `<textarea class="actualbox">`, auto-save ขึ้น GitHub
- Actual Result เป็น `<textarea>` (ไม่ใช่ contenteditable)
- uid ใหม่ต้องไม่ชนของเดิม (การเพิ่มเคสไม่ควรกระทบสถานะที่บันทึกไว้)
- ลิงก์ให้ผู้ใช้ = GitHub Pages: `https://wanlee-tankunnatam.github.io/qa-test-reports/projects/<proj>/reports/<file>.html` (cache ~10 นาที)
- เครื่องมือปรับสไตล์ steps: `tools/build/normalize_steps.py` (idempotent)
