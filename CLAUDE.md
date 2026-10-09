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
| **takra-clip** | `/Users/ice/Documents/rf/takra-clip-main` (repo ของกลาง — โค้ดจริงเป็น submodule ใต้ `apps/`: `takra-clip-service` Go+Postgres · `takra-clip-backoffice` Vue 3 · `takra-clip-extension` · ต้อง `git submodule update --init --recursive` ก่อน) | `apps/takra-clip-backoffice/src` | **i18n** — `apps/takra-clip-backoffice/src/i18n/messages.ts` (`export const th` · ห้ามใช้ข้อความเป็น key ใช้ path เช่น `nav.dashboard`) · แบบ UI ก่อนมีโค้ดอยู่ที่ `design/*.dc.html` (30 ไฟล์) | ⚠️ อยู่ที่ `docs/` — `docs/planning-artifacts/prd/full.md` · `docs/planning-artifacts/architecture/index.md` · `docs/planning-artifacts/flow-01..03` · `docs/epic/ep-01..05` · `docs/implementation-artifacts/` · `docs/test-artifacts/` · `docs/api/index.md` |
| **takra-farm** (TAKRA Post) | `/Users/ice/Documents/rf/takra-farm` (แอปเดสก์ท็อป Tauri 2 · Rust + Vue 3 · ต้องมี `adb` บน PATH) | `src` (Vue 3 + Naive UI) · `src-tauri` (Rust) | **i18n** — `src/i18n/locales/th-TH.yml` (คู่กับ `en.yml`) | ⚠️ อยู่ที่ `docs/` — `docs/prd.md` (Brownfield PRD) · `AUTO-SCHEDULE-SPEC.md` · `CONTENT-DISPATCH.md` · `CONTENT-STUDIO-PRD.md` · `TIKTOK-QUEUE-SYSTEM.md` · `LICENSING.md` |
| **takra-lipsync** (TAKRA Lib-Sync) | `/Users/ice/Documents/other/takra-lib-sync` (repo production `Real-Factory/takra-lib-sync` · branch `develop` → `uat` (QA/RC) → `prod` · **QA อ่านจาก `origin/uat`** · repo POC `poc-local` เลิกใช้แล้ว) | `app/` (Electron) · `web/console/src` (Svelte 5 + TS — หน้า Console) | **ฝังไทยในโค้ด** — grep `app/**` + `web/console/src/**` (ไม่มี i18n · ข้าม `*.test.*`) | ⚠️ อยู่ที่ `_bmad-output/planning-artifacts/` — `prd.md` · `epics.md` (Epic M1 + Jira TLS) · `backlog/epic-1..6` · root `DECISIONS.md` · `CUSTOMER_READY.md` · `INSTALL_GUIDE.md` · `TECH_STACK.md` · `docs/stories/ux-design-stories.md` |
| **takra-radar** (Trendora) | `/Users/ice/Documents/rf/takra-radar` (branch develop · เว็บ trend radar สำหรับนักทำ affiliate ไทย) | `apps/web/src` (React SPA) + ข้อความระบบใน `packages/shared/src/messages/th-*.ts` | **ฝังไทยในโค้ด** — grep `apps/web/src/**` + `packages/shared/src/messages/**` (ไม่มี i18n) | ⚠️ สเปก BMad ถูกถอดจาก tree (2026-08-18) — อ่านผ่าน `git show ac885d7:_bmad-output/planning-artifacts/epics.md` (Epic 1–8) · `prd.md` · story spec `_bmad-output/implementation-artifacts/` · เอกสารปัจจุบันใน `docs/` |

> ก่อนเริ่มทุกครั้ง: ยืนยันว่ากำลังทำ **โปรเจกต์ไหน** แล้วใช้ path จากแถวนั้น — อย่าเอา path ข้ามโปรเจกต์

### ทะเบียนกลาง — path + Jira ของทุกโปรเจกต์ (ไม่ต้องแปะซ้ำทุกครั้ง)

ค่าจริงเก็บเป็นไฟล์เดียวที่ [`tools/project-paths.json`](tools/project-paths.json) (แก้ที่นั่นที่เดียว · เครื่องมือ/สคริปต์อ่านไฟล์นี้ได้เลย)

| โปรเจกต์ | repo โค้ด | Jira key | Jira board timeline | รายงานใน repo นี้ | hub |
|---|---|---|---|---|---|
| **takra-ai** | `/Users/ice/Documents/rf/takra-ai` | `TAKRA` | https://kitdi.atlassian.net/jira/software/projects/TAKRA/boards/1593/timeline | `projects/takra-ai/` | `?project=ai` |
| **takra-rerun** | `/Users/ice/Documents/rf/takra-rerun` | `TAK` | https://kitdi.atlassian.net/jira/software/projects/TAK/boards/1661/timeline | `projects/takra-rerun/` | `?project=rerun` |
| **takra-insight** | `/Users/ice/Documents/rf/takra-insight` | `TI` | https://kitdi.atlassian.net/jira/software/projects/TI/boards/1660/timeline | `projects/takra-insight/` | `?project=insight` |
| **takra-hub** | `/Users/ice/Documents/rf/takra-hub` | `TKH` | https://kitdi.atlassian.net/jira/software/projects/TKH/boards/1733/timeline | `projects/takra-hub/` | `?project=hub` |
| **takra-clip** | `/Users/ice/Documents/rf/takra-clip-main` | `ACL` | https://kitdi.atlassian.net/jira/software/projects/ACL/list | `projects/takra-clip/` | `?project=clip` |
| **takra-farm** | `/Users/ice/Documents/rf/takra-farm` | *ยังไม่พบใน repo* | — | `projects/takra-farm/` | `?project=farm` |
| **takra-lipsync** | `/Users/ice/Documents/other/takra-lib-sync` | `TLS` (เคสชุดแรกจัดกลุ่มตาม epic `RA` ของ POC) | — | `projects/takra-lipsync/` | `?project=lipsync` |
| **takra-radar** | `/Users/ice/Documents/rf/takra-radar` | `TKRD` | https://kitdi.atlassian.net/jira/software/projects/TKRD/ | `projects/takra-radar/` | `?project=radar` |

> **takra-ai คุณภาพไลฟ์รีรัน** (9 ก.ย. 2026) — 15 เคส 3 รอบ อยู่ที่ `tools/build/ai_quality_cases.py` → `python3 tools/build/build_hub_report.py aiquality`
>
> **takra-rerun คุณภาพ/ประสิทธิภาพการไลฟ์รีรัน** (9 ก.ย. 2026) — 14 เคส 3 รอบ อยู่ที่ `tools/build/rerun_quality_cases.py` → `python3 tools/build/build_hub_report.py rerunquality`
>
> **takra-insight Live Readiness** (9 ก.ย. 2026) — เคสคุณภาพข้าม epic 33 เคส 8 มิติ อยู่ที่ `tools/build/insight_live_readiness_cases.py` → `python3 tools/build/build_hub_report.py lrready`
>
> **takra-insight MVP-2 Epic 4 + Epic 6** (9 ก.ย. 2026) — เคสอยู่ที่ `tools/build/insight_mvp2_e46_cases.py` → `python3 tools/build/build_hub_report.py insighte46` (แก้ที่ไฟล์ cases แล้ว build ใหม่ อย่าแก้ HTML ตรง ๆ)
>
> **takra-lipsync** เข้าทะเบียน 14 ก.ย. 2026 · **ย้าย repo เป็น `takra-lib-sync` (production) วันเดียวกัน** — เคสชุดแรกเขียนจาก POC `poc-local` @ `fcfba85` ยังไม่ได้เทียบคำกับ repo ใหม่ · รายงานชุดแรก Desktop UI 69 เคส (37 เคสหน้า Console ติดป้าย "🔎 คำ UI รอยืนยัน") (`tools/build/lipsync_cases.py` → `python3 tools/build/build_hub_report.py lipsync`)
>
> **takra-farm** เข้าทะเบียน 7 ก.ย. 2026 · รายงานชุดแรก Desktop UI 59 เคส (ยังไม่รวม license — ยังไม่มีในรอบนี้) (`tools/build/farm_cases.py` → `python3 tools/build/build_hub_report.py farm`)
>
> **takra-clip** เข้าทะเบียน 7 ก.ย. 2026 · รายงานชุดแรกคือ Back Office UI 70 เคส (`tools/build/clip_bo_cases.py` → `python3 tools/build/build_hub_report.py clipbo`) — แก้เคสที่ไฟล์ cases แล้ว build ใหม่ อย่าแก้ HTML ตรง ๆ
>
> **takra-clip · Takra Clip Cut (แอปเดสก์ท็อป)** (9 ต.ค. 2026) — โค้ดอยู่คนละ repo กับ takra-clip-main: `Real-Factory/takra-clip-editor` (Electron + Vue · คำ UI ไทยรวมที่ `packages/i18n/src/catalog/th.ts` · รุ่น 1.0.0 = `855862b`) · รายงาน E2E 191 เคส 14 หมวด (A–N) แปลงจากเอกสาร "Takra Clip Cut 1.0.0 — E2E Test Cases" (8 ต.ค.) · ID คง `TC-<หมวด>-NN` · Priority เอกสาร P1/P2/P3 → hub P0/P1/P2 · 💰 = เสียเงินจริง · B01–B23 อยู่ในบรรทัดที่มา (`tools/build/clip_cut_cases.py` → `python3 tools/build/build_hub_report.py clipcut`) — แก้เคสที่ไฟล์ cases แล้ว build ใหม่ อย่าแก้ HTML ตรง ๆ
>
> **takra-radar (Trendora)** เข้าทะเบียน 15 ก.ย. 2026 · รายงานชุดแรก Web UI 120 เคส (เฉพาะ P0+P1) แยก 2 ระบบ ลูกค้า (กลุ่ม A–H) + แอดมิน (กลุ่ม ADM) · UAT = uat.trendora.watch · uid ตรึงด้วย `takra-radar-sources/uid_map.json` (จัดกลุ่มใหม่ได้โดยผลเทสไม่หลุด) (`tools/build/radar_cases.py` โหลดจาก `tools/build/takra-radar-sources/*.json` → `python3 tools/build/build_hub_report.py radar`) — แก้เคสที่ JSON แล้ว build ใหม่ อย่าแก้ HTML ตรงๆ · ✅ แคตตาล็อกย้ายไป ClickHouse แล้ว (ยืนยัน 18 ก.ย. 2026) — เงื่อนไข TKRD-161 ปิดแล้ว เหลือจับตาค่าคอม (TKRD-165 To Do)
>
> **ปฏิทินทดสอบ + ภาพรวม (ทุกโปรเจกต์)** (16 ก.ย. 2026) — `timeline/index.html?project=timeline` (ชีต: Epic + Story/Task ลูก · สถานะ · เริ่ม DEV/กำหนด DEV **จาก Jira ที่ BA/PM ปัก** · แก้ในหน้าแล้ว auto-save ขึ้น GitHub ผ่าน store-data) และ `timeline/overview.html` (Gantt อ่านสดจาก index.html · แท่ง = เริ่ม DEV → กำหนด DEV) · ขั้นตอน: `python3 tools/build/fetch_jira_snapshot.py` (ดึง Jira → `tools/build/jira-snapshot/<KEY>.json` · auth จาก `~/.config/jira-auth` ผ่าน `~/.claude/scripts/jira.py` · ห้าม print token) แล้ว `python3 tools/build/build_timeline_calendar.py` (แทนที่เฉพาะระหว่าง `<!-- CAL:START -->…<!-- CAL:END -->` ไม่แตะ store-data) · takra-farm ไม่มี Jira → อ่านจาก `docs/prd.md` · ฟิลด์ Jira: Start date = `customfield_10015` · Due = `duedate` · Sprint = `customfield_10020`

> **แผน Regression ทุกโปรเจกต์ (รอบ 5–9 ต.ค. 2569)** (29 ก.ย. 2026) — `timeline/regression-plan.html` (#timeline Gantt สัปดาห์ · #plan ตารางแผน) ดีไซน์เดียวกับ feature-status · ข้อมูลแก้มือใน array `PLAN` ในไฟล์ · ยังไม่ผูก Jira/test case ตามที่ตกลง — จะผูกตอนใกล้รอบ
>
> **รายงานรอบ regression 5–9 ต.ค.** (29 ก.ย.) — 6 ไฟล์ใต้ `projects/<proj>/2026/10/reports/*-regression-oct0509-*` (store แยกจากชุดหลัก) build ด้วย `python3 tools/build/build_hub_report.py <key>`: regai1 (Live — **รวม 6 ต.ค. เป็นไฟล์เดียว 490 เคส**: happy 258 + fail+ฟีเจอร์ ก.ย. 165 (uid 13501–13665 · id ซ้ำเติม `-RF`) + 🆕 อัปเดตตาม UAT 6 ต.ค. 213 เคส `TC-OCT-*` (ตรวจทั้งโปรเจกต์ A–U + คลังสินค้าตรวจซ้ำ H.4–H.13) จาก `ai_reg_oct_new_cases.py` (uid 13666–13878 · เคสเดิมที่ถูกแทน + `-RF` ที่ซ้ำ ถูกเอาออกตอน build เฉพาะที่ยังไม่มีผลใน store + กลุ่ม "จุดที่เคย FAIL" ทั้งกลุ่ม (`RETIRED` · 146 เคส · คงไว้ 33 เคสที่มีผล · Epic 14 RTMP ใส่กลับได้ตอน TAKRA-783 merge) · UI ที่เปลี่ยนให้**เพิ่มเคสใหม่ต่อท้าย ไม่แก้เคสเดิม**) · ไฟล์ > 1 MB: build แพตช์ auto-save ให้ดึงไฟล์ raw — ก่อนแพตช์ แท็บค้างเคยเขียนทับโครงรายงาน) · **regaimenu** (6 ต.ค. · ใช้บันทึกผลแทน regai1 — เคส/uid ชุดเดียวกับ regai1 จัดใหม่เป็น 24 เมนู → 63 ชุดฟีเจอร์ตามแถบเมนูของแอป · ตัดซ้ำ/ถูกแทน/P2 ที่ `DROP` (454 เคส) · กติกา Graham + "AI Live" + สุ่มฉากหลังครอบเคสไลฟ์ที่ regex จับไม่ได้ผ่าน `SCENE_EXTRA_PRE` ใน reg_ai_happy_oct_cases.py · ผังเมนูอยู่ `MENUS` ใน `reg_ai_bymenu_oct_cases.py` · เคสใหม่ต้องใส่ชุดก่อนไม่งั้น build ล้ม · regai1 ติดป้ายย้ายแล้ว) · regai2 (ไฟล์ fail-features เดิม เลิกใช้บันทึกผลแล้ว) · regrerun (80 · os_cols) · reginsight (66 · os_cols) · regradar (130) · regfarm (54) — โมดูล `tools/build/reg_*_oct_cases.py` คัดจากชุดหลัก อย่าแก้เคสในโมดูล reg ให้แก้ชุดหลักแล้ว build ใหม่ · ลิงก์แปะครบทุกแถวในหน้าแผนแล้ว · Lib-Sync + Clip + Hub ถูกตัดออกจากรอบ (29 ก.ย.)
>
> Jira เป็นลิงก์อ้างอิงสำหรับคน — ไม่มี API token ใน repo นี้ ถ้าต้องดึงสถานะใบงานให้ผู้ใช้ export/แปะข้อมูลมา

**2 index แยกกัน:** รายงานผลทดสอบ = `index.html` (`/?project=<id>`) · เอกสาร timeline/แผนเดินงาน = `timeline/index.html` (`/timeline/?project=<id>`) — เอกสาร timeline ไม่ต้องใส่ในหน้ารายงาน

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
