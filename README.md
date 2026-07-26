# TAKRA QA — Reports Hub

รายงานผลการทดสอบ QA ของโปรเจค TAKRA เผยแพร่เป็นเว็บผ่าน GitHub Pages

**🔗 https://wanlee-tankunnatam.github.io/qa-test-reports/**

หน้า hub (`index.html`) รวมรายงานทุกโปรเจคไว้ที่เดียว — ค้นหาได้ กรองตามประเภท/ช่วงวันที่ได้
และมีคอลัมน์ **Status** ที่ดึง % ความคืบหน้าจากตัวรายงานแต่ละไฟล์มาแสดงแบบสด

---

## โครงสร้าง repo

```
qa-test-reports/
├── index.html                      ← หน้า hub (entry point ของ GitHub Pages — ห้ามย้าย)
├── README.md                       ← ไฟล์นี้
│
├── projects/                       ← รายงานจริงทั้งหมด
│   └── <project>/
│       ├── <YYYY>/<MM>/            ← ปี / เดือน ที่ออกรายงาน
│       │   ├── reports/            ← ตาราง test cases (มีปุ่ม ☁️ เซฟผลขึ้น GitHub)
│       │   └── summary/            ← สรุปผลการทดสอบ (static)
│       ├── dod/mvp<N>/             ← Definition of Done checklist — แยกตาม MVP ไม่แบ่งเดือน
│       └── archive/                ← รายงานรุ่นเก่าที่เลิกใช้แล้ว (ไม่แบ่งเดือน ไม่ลิงก์จาก hub)
│
├── notes/                          ← เอกสารประกอบ .md (hub ลิงก์ผ่าน github.com/blob/master)
│
├── reports/ · summary/ · dod/      ← ⚠️ ไม่ใช่เนื้อหา — ไฟล์ redirect ของ URL เก่าเท่านั้น
│                                      (เช่นเดียวกับ projects/<project>/{reports,summary,dod}/*.html
│                                       ที่อยู่นอก <YYYY>/<MM>)
│
└── tools/                          ← เครื่องมือที่รันในเครื่อง (ไม่ได้ deploy)
    ├── make-redirects.py           ← สร้าง redirect ของ URL เก่า
    └── README.md                   ← QA dashboard (แยกขาด ไม่เกี่ยวกับเว็บนี้)
```

โปรเจคปัจจุบัน: `takra-ai` · `takra-insight` · `takra-rerun`

### แกนของแต่ละประเภทไม่เหมือนกัน

| ประเภท | จัดตาม | เพราะ |
|---|---|---|
| `reports/` · `summary/` | **ปี/เดือนที่ออกรายงาน** | ออกใหม่ได้เรื่อย ๆ ตามรอบทดสอบ |
| `dod/` | **MVP** (`dod/mvp1/`, `dod/mvp2/`) | DoD ผูกกับ milestone ไม่ใช่เดือน — 1 MVP มีชุดเดียว ใช้ยาว |
| `archive/` | ไม่จัด | ของเลิกใช้ ไม่ลิงก์จาก hub |

**ปี/เดือน = เดือนที่ "ออก" รายงาน ไม่ใช่เดือนที่แก้ล่าสุด** — พอวางไฟล์ลงเดือนไหนแล้ว **ห้ามย้ายอีก**
แม้จะมากดเซฟผลทดสอบเพิ่มในเดือนถัดไป เพราะ path ของไฟล์ถูกฝังอยู่ในตัวไฟล์เอง
(`GH_PATH` — ดูข้างล่าง) ถ้าย้ายตามวันแก้ล่าสุด ปุ่มเซฟจะเขียนกลับไป path เก่าและเกิดไฟล์ผีขึ้นมา

---

## กฎตั้งชื่อไฟล์

```
<project>-mvp<N>-<kind>[-<platform>].html
```

| ส่วน | ค่าที่ใช้ได้ |
|---|---|
| `project` | ชื่อโฟลเดอร์โปรเจคเป๊ะ ๆ — `takra-ai` / `takra-insight` / `takra-rerun` |
| `N` | `0.5` `1` `2` … หรือช่วง `0.5-1` `1-2` สำหรับรายงานที่คร่อม MVP |
| `kind` | `ui-test-cases-table` · `e2e-test-cases-table` · `full-test-cases-table` · `qa-summary` · `qa-dod-checklist` |
| `platform` | `mac` / `windows` — ใส่เฉพาะรายงานที่แยกตาม OS |

ตัวอย่าง:
- `projects/takra-ai/2026/07/reports/takra-ai-mvp2-ui-test-cases-table.html`
- `projects/takra-ai/dod/mvp2/takra-ai-mvp2-qa-dod-checklist.html`

> ⚠️ ไฟล์ตาราง test case **ต้องลงท้ายด้วย `-test-cases-table.html`** เสมอ
> `index.html` ใช้ regex `/-test-cases-table[\w-]*\.html($|[?#])/` คัดว่าแถวไหนต้องไปดึง % มาแสดง
> ตั้งชื่อผิดกฎ = คอลัมน์ Status ของแถวนั้นจะขึ้น `—` เงียบ ๆ โดยไม่มี error

---

## เพิ่มรายงานใหม่ — checklist

1. **วางไฟล์** ตามกฎตั้งชื่อข้างบน — โฟลเดอร์ที่ยังไม่มีสร้างใหม่ได้เลย
   - test case / summary → `projects/<project>/<YYYY>/<MM>/{reports,summary}/`
   - DoD checklist → `projects/<project>/dod/mvp<N>/` (ไม่ต้องมีปี/เดือน)
2. **ตั้ง `GH_PATH`** ในไฟล์ให้ตรงกับ path จริง — เฉพาะรายงานที่มีปุ่ม ☁️ เซฟ
   ```js
   var GH_PATH = 'projects/takra-ai/2026/07/reports/takra-ai-mvp2-ui-test-cases-table.html';
   ```
   ค่านี้คือ path ที่ปุ่มเซฟจะเขียนกลับผ่าน GitHub API ถ้าไม่ตรง = เซฟไปผิดที่
3. **ตั้ง back-link** ให้ตรงโปรเจค — `?project=` รับได้แค่ `rerun` · `ai` · `insight` · `notes`
   ```html
   <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai">
   ```
   ใส่ค่าอื่น (เช่น `live`) hub จะ fallback ไป `rerun` เงียบ ๆ
4. **เพิ่มแถวใน `index.html`** ในกลุ่มโปรเจคที่ถูก — URL ต้องใส่ **2 ที่**: `data-href` บน `<tr>` และ `href` บน `<a>`
   อย่าลืมอัปเดตตัวเลข `<span class="count">N reports</span>` ของกลุ่มนั้นด้วย
5. **ตรวจก่อน push** — ดูหัวข้อถัดไป

---

## ตรวจความถูกต้องก่อน push

```bash
# ทุกลิงก์ใน hub ต้องชี้ไปไฟล์ที่มีอยู่จริง
grep -o 'href="[^"]*qa-test-reports/projects/[^"]*\.html"' index.html \
  | sed 's|.*qa-test-reports/||; s|"$||' | sort -u \
  | while read p; do [ -f "$p" ] || echo "MISSING $p"; done

# GH_PATH ของทุกไฟล์ต้องเท่ากับตำแหน่งจริงของตัวเอง
grep -r "var GH_PATH" projects/ | sed "s/:.*'\(.*\)';/ -> \1/" \
  | awk -F' -> ' '{split($1,a,":"); if(a[1]!=$2) print "MISMATCH", a[1], "!=", $2}'

# back-link ต้องมีแค่ ai / insight / rerun
grep -rho "qa-test-reports/?project=[a-z]*" projects/ | sort | uniq -c

# ลองเปิดจริง
python3 -m http.server 8000    # แล้วเปิด http://localhost:8000/
```

---

## หมายเหตุการ deploy

- Pages เสิร์ฟจาก branch **`master`** โฟลเดอร์ราก — **push ขึ้น master = deploy ทันที**
  ปุ่ม ☁️ ในตัวรายงานก็เขียนเข้า `master` โดยตรงเช่นกัน (กดเซฟ = deploy)
- ไม่มี `.nojekyll` → **ห้ามตั้งชื่อโฟลเดอร์/ไฟล์ขึ้นต้นด้วย `_`** เพราะ Jekyll จะไม่ publish ให้
- ปุ่ม ☁️ ต้องใช้ GitHub PAT ที่เก็บใน `localStorage['gh_pat']` ของเบราว์เซอร์แต่ละคน

### ลิงก์เก่ายังใช้ได้ — แต่ให้ใช้ลิงก์ใหม่เป็นหลัก

URL เก่าทุกอัน (44 path · ทั้งชุดที่ราก และชุด `projects/<project>/{reports,summary,dod}/`)
มีไฟล์ redirect วางไว้ที่ path เดิม เด้งไปตำแหน่งใหม่ให้อัตโนมัติ — ลิงก์ที่เคยแชร์ใน Jira/แชตจึงไม่พัง
GitHub Pages ไม่มี server-side redirect ไฟล์พวกนี้จึงต้องอยู่ที่ path เดิมเป๊ะ ๆ ห้ามย้าย/รวมโฟลเดอร์

**เวลาย้ายหรือเปลี่ยนชื่อไฟล์รอบใหม่** ให้เติม path เก่า→ใหม่ใน `MOVES` ของ
[`tools/make-redirects.py`](tools/make-redirects.py) แล้วรัน

```bash
python3 tools/make-redirects.py --check   # ดูว่า mapping ครบไหม
python3 tools/make-redirects.py           # เขียนไฟล์ redirect
```

---

## ของค้างที่ยังต้องตัดสินใจ

`projects/takra-insight/2026/07/reports/takra-insight-mvp1-ui-test-cases-table.html`
มีเนื้อหาเหมือนไฟล์ MVP-2 ทุกไบต์ (ต่างแค่บรรทัด `GH_PATH`) และ `<title>` ข้างในเขียนว่า "MVP-2"
แปลว่า **ยังไม่มีรายงาน Insight MVP-1 จริง** แต่หน้า hub มีแถวนี้อยู่ — ต้องเลือกว่าจะทำรายงาน MVP-1 ของจริง หรือถอดแถวออก
