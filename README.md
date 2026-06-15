# QA Test Reports — RealFact

Dashboard ส่วนกลางสำหรับทีม QA ดู/จัดการผลการทดสอบของทุก project
(Kiosk Avatar, Chat AI, Backoffice) — เป็น local HTTP server + UI หน้าเดียว (vanilla JS, ไม่มี build step)

> **สำคัญ:** repo นี้คือ **ตัวเครื่องมือ (tool) อย่างเดียว** — *ไม่มี* ผลการทดสอบจริงอยู่ข้างใน
> ตัว tool จะไป "อ่าน" ผลทดสอบจาก checkout ของ main repo (`realfact`) บนเครื่องคุณ
> ฉะนั้นทุกคนต้องมี main repo อยู่บนเครื่อง และชี้ tool ไปที่ path ของมัน

---

## ความต้องการเบื้องต้น

1. **Python 3.8+** (ใช้ stdlib ล้วน ไม่ต้อง `pip install` อะไรเลย)
2. **main repo (`realfact`) clone ไว้บนเครื่อง** — เพราะ data (`tests/kiosk-avatar/results/…`) อยู่ที่นั่น

---

## เริ่มใช้งาน (Quick Start)

```bash
# 1. clone repo เครื่องมือนี้
git clone <REPO_URL> qa-test-reports
cd qa-test-reports

# 2. รัน server โดยชี้ไปที่ main repo (realfact) บนเครื่องคุณ
python3 server.py --repo-root /path/to/realfact

# 3. เปิด browser
#    http://localhost:8088/
#    http://localhost:8088/kiosk-avatar/collections
```

### บอก path ของ main repo ได้ 4 วิธี (เรียงตามลำดับความสำคัญ)

| ลำดับ | วิธี | ตัวอย่าง |
|------|------|---------|
| 1 | `--repo-root` flag | `python3 server.py --repo-root ~/Documents/rf/realfact` |
| 2 | env var | `REALFACT_REPO_ROOT=~/Documents/rf/realfact python3 server.py` |
| 3 | auto-detect | รันจากข้างใน main repo — tool จะเดินขึ้นหา `tests/kiosk-avatar` เอง |
| 4 | fallback | ถ้าวาง `qa-test-reports` ข้างๆ `realfact` (sibling) จะ default ไป `../realfact` อัตโนมัติ |

> 💡 **แนะนำ layout แบบ sibling** เพื่อความสะดวก — จะรัน `python3 server.py` เปล่าๆ ได้เลย:
> ```
> rf/
> ├── realfact/          ← main repo (มี test data)
> └── qa-test-reports/   ← repo นี้
> ```

ถ้าชี้ path ผิด server จะเตือน (`WARNING: ... ไม่มี tests/kiosk-avatar`) หรือ exit พร้อมข้อความบอกวิธีแก้

---

## ออปชันการรัน

```bash
python3 server.py [--port 8088] [--host 127.0.0.1] [--repo-root PATH]
```

| Flag | Default | ความหมาย |
|------|---------|----------|
| `--port` | `8088` | port ของ server |
| `--host` | `127.0.0.1` | host (ใช้ `0.0.0.0` ถ้าจะให้คนอื่นในวงเข้าถึง) |
| `--repo-root` | auto | path ของ main repo (realfact) |

---

## URL Map

| URL | สิ่งที่เห็น |
|-----|------------|
| `http://localhost:8088/` | หน้า index — เลือก project |
| `http://localhost:8088/{project}/runs` | รายการ run ทั้งหมด |
| `http://localhost:8088/{project}/collections` | รายการ Collection |
| `http://localhost:8088/{project}/collections/{col_id}` | รายละเอียด Collection (results + status) |

Project ที่รองรับ (จาก [projects.json](projects.json)): `kiosk-avatar`, `chat-ai`, `backoffice`

---

## โครงสร้าง repo

```
qa-test-reports/
├── README.md            ← (ไฟล์นี้) การติดตั้ง + quick start
├── TOOL-REFERENCE.md    ← เอกสารอ้างอิงเชิงลึก: REST API, schema, project-specific UI
├── server.py            ← Python HTTP server (stdlib ล้วน)
├── projects.json        ← นิยาม projects ที่ tool รู้จัก (แก้ที่นี่เพื่อเพิ่ม/แก้ path)
├── scripts/             ← helper scripts (CLI runners — optional)
└── ui/
    └── index.html       ← Single-page UI (vanilla JS)
```

---

## การทำงานร่วมกันเป็นทีม

- **Tool (repo นี้):** version-controlled ผ่าน git ตามปกติ — แก้ feature/UI แล้วเปิด PR
- **Data (ใน main repo):** ผลการทดสอบและ collections JSON อยู่ใน `realfact/tests/.../results/`
  ซึ่งปัจจุบัน *ไม่ได้ track ใน git* — ถ้าทีมต้องการแชร์ collections ให้กันได้ ต้องตกลงวิธี sync แยกต่างหาก
  (เช่น track โฟลเดอร์ `results/collections/` ใน main repo, แชร์ผ่าน shared drive ฯลฯ)

> เป้าหมายของการแยก repo นี้: ให้ทีม QA **อัปเดต/ปรับปรุงตัว dashboard ร่วมกันได้** โดยไม่ต้องแตะ main repo

---

## JIRA (optional)

ถ้า main repo มีไฟล์ `.claude/jira_config.md` (รูปแบบ `JIRA_BASE_URL=`, `JIRA_EMAIL=`,
`JIRA_API_TOKEN=`, `JIRA_PROJECT_KEY=`) tool จะเปิดฟีเจอร์ดึง JIRA issues ให้อัตโนมัติ
ถ้าไม่มีก็ทำงานได้ปกติ (JIRA: disabled)

---

ดูรายละเอียด REST API, collection schema, และ behavior เฉพาะแต่ละ project ได้ที่ **[TOOL-REFERENCE.md](TOOL-REFERENCE.md)**
