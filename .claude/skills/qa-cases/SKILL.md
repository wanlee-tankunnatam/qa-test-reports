---
name: qa-cases
description: เขียน/แก้ manual UI test case ในรายงาน qa-test-reports ให้เป็นสไตล์ Steps to Reproduce จาก UI จริง + Expected Result อ้างเอกสาร รองรับ takra-ai / takra-rerun / takra-insight แยก MVP/Epic และโหมดแก้ในที่เดิม vs recreate ใช้เมื่อจะสร้างเคสใหม่ รีไรต์ Test Steps/Expected หรือกู้เคสให้ตรง UI ปัจจุบัน
---

# qa-cases — เขียน/แก้ Test Case

Playbook นี้เป็นเวอร์ชันลงมือทำของมาตรฐานใน [CLAUDE.md](../../../CLAUDE.md) —
ใช้ได้ทั้งตอนทำเองและตอนส่งให้ subagent (จึง self-contained)

## ก่อนเริ่ม — ยืนยัน 3 ข้อ
1. **โปรเจกต์ไหน** (takra-ai / takra-rerun / takra-insight) → เลือกแถวในตารางข้างล่าง
2. **scope** — MVP/Epic ไหน, ไฟล์รายงานไหน (`projects/<proj>/reports/…`)
3. **โหมด** — *แก้ในที่เดิม* (คง ID/จำนวนเคส) หรือ *recreate* (flow เปลี่ยน เขียนใหม่)
   ถ้าไม่ชัด → ถามก่อน อย่าเดา

## ตารางต่อโปรเจกต์

| โปรเจกต์ | โค้ด (repo) | UI source | คำ UI จริงมาจาก | เอกสาร (`_bmad-output/planning-artifacts/`) |
|---|---|---|---|---|
| **takra-ai** | `/Users/ice/Documents/rf/takra-ai` | `apps/web/src` | **i18n** `apps/web/src/i18n/locales/th/*.ts` | `epics.md` · `epics-mvp2.md` · `prd.md` |
| **takra-rerun** | `/Users/ice/Documents/rf/takra-rerun` | `web/src` | **ฝังไทยในโค้ด** grep `web/src/features/**` | `epics.md` · `epics-mvp2.md` · `prd.md` |
| **takra-insight** | `/Users/ice/Documents/rf/takra-insight` | `apps/web/src` | **ฝังไทยในโค้ด** grep `apps/web/src/**` | `epics.md` · `epics-th.md` · `prd.md` · `prd-th.md` |

## ขั้นตอน
1. เปิด **UI source** ของโปรเจกต์นั้น อ่าน flow จริงของฟีเจอร์/เคสที่จะทำ
2. ดึง **คำ UI จริง** จากแหล่งในตาราง (takra-ai = locale th, ที่เหลือ = grep ในโค้ด) — ลอกใส่ "…"
3. อ่าน **เอกสาร** ที่ตรง scope เพื่อกำหนด Expected Result (MVP-1 ไม่เปิด `epics-mvp2.md`)
4. เขียน/แก้เคสตามกติกา ↓
5. ตรวจ: HTML parse ได้, uid ไม่ชน, จำนวน/ลำดับเคสถูกตาม scope, สถานะผลเทสเดิมไม่ถูกแตะ

## กติกาเขียน (บังคับ)
**Test Steps = Steps to Reproduce**
- เริ่มจากต้นเสมอ: `เปิดแอป → เข้าสู่ระบบ(UAT) → ไปที่เมนู/หน้า "…" → ลงมือทำ` ห้ามเริ่มกลางทาง
- ภาษาคน, รวม step ย่อยเป็นประโยคเดียวธรรมชาติ (~3–6 steps), ปิดท้ายด้วย step สังเกตผล

**คำ UI** — ลอกจริงจากแหล่งในตาราง ใส่ "…" ห้ามแปล/แต่งเอง · หาไม่เจอ → บอก "ไม่พบใน UI" คงของเดิม อย่าเดา

**Expected Result** — ตรงกับ Test Steps, วัดผลได้, ยึดเอกสาร (ไม่เดาจากโค้ด), ปิดท้าย `ที่มา: Epic X · Story Y.Z · FRnn`

**ขอบเขต** — UI เท่านั้น · ทำตาม scope ที่สั่งเป๊ะ ไม่ล้ำ

## ห้ามแตะ (เมื่อสั่ง "แก้แค่ Test Steps + Expected")
ID · ชื่อเคส · Priority · Epic/Feature · Precondition · Test Data · สถานะผลเทส · โครง harness · จำนวน/ลำดับเคส

## harness / ลิงก์
- ไฟล์ self-contained: `<script id="store-data">` (key = uid `tc-N`), `<textarea class="actualbox">`, auto-save ขึ้น GitHub
- uid ใหม่ห้ามชนของเดิม
- ลิงก์ผู้ใช้ = `https://wanlee-tankunnatam.github.io/qa-test-reports/projects/<proj>/reports/<file>.html` (cache ~10 นาที, Cmd+Shift+R)
- ปรับสไตล์ steps เป็นชุด: `tools/build/normalize_steps.py` (idempotent)
