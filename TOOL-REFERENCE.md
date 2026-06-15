# Test Reports Tool — Reference

> 📌 นี่คือ **เอกสารอ้างอิงเชิงลึก** (API, schema, project-specific UI)
> สำหรับ **การติดตั้ง/รันครั้งแรก** ให้ดู [README.md](README.md) ก่อน

เครื่องมือบันทึก/ดูผลการทดสอบของทุก project (Kiosk Avatar, Chat AI, Backoffice, …) — local HTTP server + UI

## TL;DR

```bash
# tool นี้อ่าน data จาก main repo (realfact) — ต้องบอก path ของมัน
python3 server.py --repo-root /path/to/realfact
# หรือ:  REALFACT_REPO_ROOT=/path/to/realfact python3 server.py
# เปิด http://localhost:8088/
```

หน้าเริ่มต้นจะแสดงรายชื่อ projects จาก [projects.json](projects.json)

## URL Map

| URL | สิ่งที่เห็น |
|-----|------------|
| `http://localhost:8088/` | หน้า index — เลือก project |
| `http://localhost:8088/{project_id}/runs` | รายการ run ทั้งหมดของ project |
| `http://localhost:8088/{project_id}/collections` | รายการ Collection ทั้งหมดของ project |
| `http://localhost:8088/{project_id}/collections/{col_id}` | รายละเอียด Collection (results table + status) |

ตัวอย่างใช้งานจริง:

- Kiosk Avatar runs → http://localhost:8088/kiosk-avatar/runs
- **Backoffice collections** → **http://localhost:8088/backoffice/collections**
- Backoffice collection ตัวอย่าง → http://localhost:8088/backoffice/collections/col-YYYYMMDD-HHMMSS-XXXXXX

## โครงสร้างไฟล์

```
tools/test-reports/
├── README.md                ← (ไฟล์นี้)
├── server.py                ← Python HTTP server (port 8088)
├── projects.json            ← นิยาม projects ที่ tool รู้จัก
├── scripts/                 ← helper scripts (CLI runners)
└── ui/
    └── index.html           ← Single-page UI (vanilla JS)
```

## projects.json — Schema

```jsonc
{
  "projects": [
    {
      "id": "backoffice",                          // unique key สำหรับ URL /backoffice/...
      "name": "Backoffice",                        // ชื่อแสดงใน UI
      "results_dir": "...path/results",            // root ของ run output
      "collections_dir": "...path/results/collections",
      "csv_dirs": [                                // โฟลเดอร์ที่มี xlsx test-case ให้เลือกใน modal
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/login/ui",
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/login/e2e",
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/member/ui",
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/member/e2e",
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/context-switcher/ui",
        "docs/implementation-artifacts/tests/backoffice/test-cases/backoffice/context-switcher/e2e"
      ],
      "run_cmd": {
        "cwd": "services/backoffice/frontend",
        "presets":   ["login", "member", "context-switcher"],
        "types":     ["ui", "e2e", "manual"],
        "categories": ["ui", "e2e", "integration"]  // Backoffice เท่านั้น — ใช้แทน Preset/Type สำหรับ filter
      }
    }
  ]
}
```

## Project-specific UI

UI มี logic แยกตาม `project.id`:

| project.id | ฟิลด์ใน Create Collection modal |
|------------|--------------------------------|
| `kiosk-avatar`, `chat-ai`, ... | Preset, Type (crawl/walk/run/manual), Preset URL, KB Path, Excel path, Test Case path |
| **`backoffice`** | **Category (UI/E2E/Integration), Test Case paths (multi-select), Excel path (optional)** — ไม่มี Preset/Type/Preset URL/KB |

ดูรายละเอียด Backoffice ที่ section ถัดไป

---

## Backoffice — Customizations

### เปิด UI

http://localhost:8088/backoffice/collections

### Create Collection — Modal

แตกต่างจาก project อื่น (Avatar/Chat):

| Field | Behavior |
|-------|----------|
| **Name** | บังคับ — ชื่อ Collection (เช่น "Sprint 5 — Identity & Access P0") |
| **Description** | optional |
| **Category** | `UI` / `E2E` / `Integration` (แทนที่ฟิลด์ Preset+Type ของ Avatar) |
| **URL (optional)** | URL อ้างอิงภายนอก เช่น JIRA dashboard |
| **Test Case paths** | **Checkbox list** — เลือกได้หลายไฟล์ กรองตาม Category (`/ui/`, `/e2e/`, `/integration/`) |
| **Excel path** | **optional** สำหรับ Backoffice (Avatar บังคับ) — ถ้าไม่ใส่ ใช้ test-case xlsx ที่เลือกไว้ |
| **Result URL** | auto-generate หลังกดบันทึก = `http://localhost:8088/backoffice/collections/{col_id}?runInstr=summary` |
| **JIRA Epic / Run** | optional |

ไฟล์ที่ขึ้นมาในรายการ Test Case paths มาจาก `csv_dirs` ใน projects.json โดยเรียก endpoint `GET /api/projects/backoffice/test-cases`

### Collection Detail — Preview Table

ถ้า Collection ยังไม่มีผลการรัน (`results` ว่าง) UI จะ render **preview table จาก xlsx test-case ที่เลือก** 8 คอลัมน์:

| # | คอลัมน์ | ที่มาจาก xlsx |
|---|--------|---------------|
| 1 | **ID** | col A (เช่น `BO-LGN-E2E-001`) |
| 2 | **Scenario** | col I |
| 3 | **Pre-conditions** | col J |
| 4 | **Test Data** | col K |
| 5 | **Step** | col L (1, 2, 3, …) |
| 6 | **Test Step** | col M |
| 7 | **Expected Result** | col N |
| 8 | **Status** | dropdown (PENDING/PASS/FAIL/SKIP/REOPEN) — แสดงเฉพาะแถวแรกของแต่ละ case ID |

หมายเหตุ:
- หนึ่ง case ID มีหลายแถว step (continuation rows) — col A ว่าง แต่ col L มีค่า → preview ใส่ ID/Scenario/Pre-conditions/Test Data จาก row หลักให้อัตโนมัติ
- Step `1.0` ใน xlsx แสดงเป็น `1` (ตัด float → int)

### Status Values

| Status | สี | ไอคอน | ความหมาย |
|--------|------|------|----------|
| PENDING (default) | เหลือง | ⏳ | ยังไม่ได้รัน |
| PASS | เขียว | ✅ | ผ่าน |
| FAIL | แดง | ❌ | ไม่ผ่าน |
| SKIP | เทา | ⊘ | ข้าม (ไม่ใน scope รอบนี้) |
| REOPEN | ชมพู | 🔁 | เคยปิดแล้วเปิดใหม่ |

Status เก็บใน collection JSON ที่ key **`case_statuses`** เป็น dict `{ "BO-LGN-E2E-001": "PASS", ... }`

### Mutate Status — API Pattern

UI ใช้ `PATCH /api/projects/backoffice/collections/{col_id}` ส่ง body:

```json
{ "case_status_update": { "case_id": "BO-LGN-E2E-001", "status": "PASS" } }
```

Server merge เข้า `collection.case_statuses[case_id]` แล้วบันทึก ไม่ต้องอ่าน/เขียนทั้ง dict

---

## REST API

ทุก endpoint อยู่ใต้ `/api/`

### Projects

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects` | List ทุก project (จาก projects.json) |

### Runs

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects/{id}/runs` | List runs |
| GET | `/api/projects/{id}/runs/{run_id}` | Run detail |
| DELETE | `/api/projects/{id}/runs/{run_id}` | ลบ run |

### Collections

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects/{id}/collections` | List collections |
| GET | `/api/projects/{id}/collections/{col_id}` | Collection detail |
| POST | `/api/projects/{id}/collections` | Create collection |
| PATCH | `/api/projects/{id}/collections/{col_id}` | Update collection (fields หรือ `case_status_update`) |
| DELETE | `/api/projects/{id}/collections/{col_id}` | ลบ collection |
| POST | `/api/projects/{id}/collections/{col_id}/runs` | Attach run เข้า collection |
| DELETE | `/api/projects/{id}/collections/{col_id}/runs/{run_id}` | Detach run |
| POST | `/api/projects/{id}/collections/{col_id}/screenshot` | Upload screenshot |
| GET | `/api/projects/{id}/collections/{col_id}/jira-issues` | JIRA issues ที่ link |

### Test Cases (xlsx)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/projects/{id}/test-cases` | List xlsx ใน `csv_dirs` (สำหรับ dropdown ตอน create collection) |
| GET | `/api/projects/{id}/test-cases-content?paths=p1\np2` | อ่านเนื้อ xlsx — return rows 7 column (ID/Scenario/Pre-conditions/Test Data/Step/Test Step/Expected) |

Query string `paths` คั่นด้วย newline (URL-encoded `%0A`) หรือ comma — server detect ทั้งสอง

---

## Common Tasks

### เพิ่ม project ใหม่

1. Append entry ใน `projects.json`
2. (ถ้าต้องการ custom UI behavior) เพิ่ม `isBackoffice`-style branch ใน `ui/index.html`
3. Restart server (ไม่มี hot-reload — process ต้อง kill + start ใหม่)

### เพิ่ม csv_dir สำหรับ Backoffice

แก้ array `csv_dirs` ใน `projects.json` แล้ว restart server — checkbox list ใน modal จะอ่านใหม่อัตโนมัติ (เพราะ fetch ตอนเปิด modal)

### Restart server หลังแก้ server.py

```bash
ps aux | grep "test-reports/server.py" | grep -v grep
kill <pid>
python3 /Users/wanleeta55/Documents/rf/realfact/tools/test-reports/server.py
```

Python HTTP server ไม่มี hot-reload — ถ้าแก้ server.py แล้วไม่ restart endpoint ใหม่จะไม่ทำงาน (request เก่ายังตอบ 200 แต่ field ใหม่หาย)

### Hard-refresh browser หลังแก้ ui/index.html

`Cmd+Shift+R` (macOS) — bypass cache ถ้าไม่ refresh จะเห็น UI เก่า

---

## Conventions / Gotchas

- **xlsx = source of truth** สำหรับ Backoffice test cases — md เป็น view เพิ่มอ่านง่าย; ห้ามแก้ md อย่างเดียวคาดหวังให้ UI เปลี่ยน
- **Header row detection** — server หา row ที่ col A == `"ID"` (สแกน 20 แถวแรก) ถ้าไม่เจอจะ skip ไฟล์นั้น
- **Continuation rows** — แถวที่ col A ว่าง + col L (Step) มีค่า ถือว่าเป็น step ของ case ก่อนหน้า
- **Status persistence** — เก็บใน `case_statuses` ของ collection JSON ไม่กระทบ xlsx ต้นทาง
- **openpyxl mode** — server โหลด workbook ด้วย `data_only=True` (ไม่ใช่ `read_only=True`) เพราะ `read_only` ทำให้ `max_row` เป็น None
