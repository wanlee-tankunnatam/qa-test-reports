# กติกาเขียน Manual UI Test Case (takra-ai · MVP-2) — อ่านให้ครบก่อนลงมือ

คุณกำลังออกแบบ **manual UI test case ภาษาไทย** สำหรับโปรเจกต์ **takra-ai** (เว็บ https://uat-live.takra.ai/)
ผลลัพธ์ของคุณ = ไฟล์ JSON 1 ไฟล์ (ระบุ path ใน prompt) — ห้ามส่งเป็นข้อความยาว ให้เขียนลงไฟล์ด้วย Write tool เท่านั้น
ข้อความสุดท้ายที่ตอบกลับ = สรุปสั้นๆ 5–10 บรรทัด: จำนวนเคสต่อ feature/ประเภท · feature ไหน "ไม่พบใน UI" · ข้อสังเกต

## แหล่งข้อมูล (ลำดับความน่าเชื่อถือ)
1. **UI จริง (โค้ด)** — `/Users/ice/Documents/rf/takra-ai/apps/web/src` (Next.js app router: `app/**/page.tsx`, `components/**`, `hooks/**`, `stores/**`)
   - **คำ UI จริง** (ชื่อปุ่ม/เมนู/แท็บ/ป้าย/ข้อความ error/empty state/toast) **ต้องลอกจาก i18n ไทย**: `apps/web/src/i18n/locales/th/*.ts`
     (namespace: auth · live · liveRoom · avatars · voices · aiHistory · settings · studio · studioPanels · schedule · scripts · pages · pagesLive · home · entitlement · riskWords · products · users · ui …)
   - หาคีย์ด้วย grep เช่น `grep -rn "คำที่คาด" apps/web/src/i18n/locales/th/` หรือ grep คีย์ที่ component ใช้ `t('xxx.yyy')` แล้วไปเปิดค่าไทยใน locale
   - ชื่อเมนูในแถบข้าง (sidebar) ให้ดู `components/live/live-sidebar.tsx` + locale `live.ts`/`pagesLive.ts`; หน้า home sidebar ดู `components/home/**` + `home.ts`/`pages.ts`
2. **สเปก** — `/Users/ice/Documents/rf/takra-ai/_bmad-output/planning-artifacts/epics-mvp2.md` (story + AC ของ Epic 8–16 · **อ่าน section ของ epic ที่ได้รับมอบหมายให้ครบ รวม note RE-BASELINE / ⛔ ย้ายไป Hub**) และ `prd.md` (FR/NFR · grep "FRnn")
3. **Test design เดิมของ QA** (ไอเดียเคส · ไม่ใช่ความจริงของ UI) — `/Users/ice/Documents/rf/takra-ai/_bmad-output/test-artifacts/mvp-2/epic-{N}/{N}-test-plan.md` · `{N}-gaps-tcs.md` และ `/Users/ice/Documents/rf/takra-ai/_bmad-output/test-artifacts/case/<feature>/ui.md` · `fullloop-e2e.md`
   - เอกสารชุดนี้เขียน 2026-07-16/21 (ก่อน dev) — ถ้าขัดกับ UI จริงหรือ epics-mvp2.md ฉบับล่าสุด **ให้ยึด UI จริง > epics-mvp2.md > test design**

## ขอบเขต
- **UI เท่านั้น** — ห้ามเขียนเคสที่ต้องดู API / DB / log ฝั่ง server / โค้ด · ทุกอย่างต้องสังเกตเห็นบนจอได้
- ทำเฉพาะ epic/feature ที่ได้รับมอบหมาย ห้ามล้ำไป epic อื่น
- **ก่อนเขียนต้องเปิดโค้ด UI จริงดู flow ก่อนเสมอ** (page → component → locale) เพื่อให้ step ตรงกับหน้าจอจริง

## Test Steps = Steps to Reproduce (self-contained)
- **ทุกเคสเริ่มจากต้นเสมอ**: `เปิดเบราว์เซอร์ไปที่ https://uat-live.takra.ai แล้วเข้าสู่ระบบด้วยบัญชี <บทบาท> (UAT)` → `ไปที่เมนู "…"` / เปิดหน้า … → ลงมือทำ → สังเกตผล
- ห้ามเริ่มกลางทาง (ห้ามขึ้นต้นด้วย action ลอยๆ เช่น "กดปุ่มเพิ่ม") — ห้ามฝากทางเข้าไว้ใน Precondition
- ภาษาคน อ่านแล้วทำตามได้จริง ไม่ใช่ศัพท์เทคนิค (ห้ามเขียน `goto /avatars`, `click selector`, `assert`)
- รวม step ย่อยสั้นๆ เป็นประโยคเดียวธรรมชาติ — ทั้งเคส **3–6 steps**
- step สุดท้ายต้องเป็น step สังเกตผล ("สังเกตว่า…") ถ้า step ก่อนหน้ายังเป็น action
- route ให้เขียนเป็น path ต่อท้าย base URL (เช่น `/ai-history`) ได้เมื่อเป็นการพิมพ์ URL ตรง

## คำศัพท์ UI — ลอกจริง ห้ามคิดเอง
- ชื่อปุ่ม/เมนู/แท็บ/ข้อความ/ป้าย ต้องลอก **คำจริงจาก locale th** ใส่ในเครื่องหมายคำพูด "…" — ห้ามแปลจาก en เอง ห้ามแต่งคำเอง
- ถ้า feature/หน้าจอ **ยังไม่มีใน UI** (ไม่พบโค้ด/locale) → ยังเขียนเคสได้จากสเปก แต่:
  - ตั้ง `"ui_status": "not-in-ui"` ที่เคสนั้น และใส่ `"ui_note": "ไม่พบใน UI (as of 2026-08-19) — เขียนจากสเปก …"`
  - **ห้ามใส่ชื่อปุ่ม/ข้อความในเครื่องหมายคำพูดที่คิดเอง** ให้บรรยายกลางๆ แทน (เช่น "ปุ่มสำหรับเพิ่มปลายทาง RTMP" ไม่ใช่ "เพิ่มปลายทาง") หรือถ้าจะอ้างคำจากสเปก ให้วงเล็บ (ตามสเปก)
- ถ้าเจอใน UI แต่บางข้อความหาไม่เจอ → บรรยายกลางๆ อย่าเดา

## Expected Result — อ้างเอกสาร
- ตรงกับ Test Steps วัดผลได้ (สังเกตเห็นจริงบนจอ) 2–5 bullet
- ยึดพฤติกรรมตาม **สเปก** (epics-mvp2.md story/AC · prd FR) ไม่ใช่เดาจากโค้ด — โค้ดใช้เพื่อรู้ flow/คำ UI
- bullet สุดท้ายต้องเป็นที่มา รูปแบบ: `ที่มา: Epic 10 · Story 10.1 · FR7` (ใส่ NFR/UX-DR ได้ถ้าเกี่ยว เช่น `· NFR-005` · `· UX-DR1`)

## ประเภทเคส (type) — ต้องใช้ค่าต่อไปนี้เป๊ะ
| type | ความหมาย | ตัวอย่าง |
|---|---|---|
| `happy` | Happy Path — flow หลักทำงานตามสเปก | เปิดหน้า/สร้าง/แก้/ลบ สำเร็จ · ดูข้อมูลครบ |
| `negative` | Negative Case — ผู้ใช้ทำสิ่งที่ระบบต้องปฏิเสธ/กั้น (ไม่ใช่เรื่องสิทธิ์, ไม่ใช่ค่าว่าง/รูปแบบผิด) | ทำ action ก่อนเงื่อนไขครบ · ยกเลิกกลางคัน · กดซ้ำระหว่างรอ · ทำกับรายการที่ถูกลบไปแล้ว |
| `edge` | Edge Case — ค่าสุดขอบ/สภาวะพิเศษ | จำนวนสูงสุด/ต่ำสุด · ข้อความยาวมาก · รายการเยอะมาก · รีเฟรชกลางทาง · หลายแท็บ · อักขระพิเศษ/อีโมจิ |
| `validation` | Validation — ตรวจรูปแบบ/ขนาด/ชนิดของ input บนฟอร์ม | ไฟล์ผิดชนิด/ใหญ่เกิน · รูปแบบ URL/stream key ผิด · ตัวเลขติดลบ · เกิน max length |
| `error` | Error Handling — ระบบ/เครือข่าย/บริการภายนอกล้ม ผู้ใช้ต้องเห็นข้อความ+ทางไปต่อ ไม่เงียบ ไม่ค้าง | โหลดไม่สำเร็จ+ปุ่มลองใหม่ · บริการไม่พร้อม · degrade (viewer unavailable) · timeout |
| `empty` | Empty / Null — ไม่มีข้อมูล / ไม่กรอก / ค่าว่าง | empty state ของรายการ · กดบันทึกโดยไม่กรอกช่องบังคับ · ผลค้นหาเป็นศูนย์ |
| `duplicate` | Duplicate — ซ้ำ | ชื่อซ้ำ · clone/เพิ่มซ้ำรายการเดิม · ส่งซ้ำ (double submit) · ปลายทางซ้ำ |
| `permission` | Permission / Authorization — บทบาท/สิทธิ์/ข้าม workspace | Live Operator ไม่เห็นปุ่มของ Owner · ผู้ใช้ทั่วไปเข้า /ai-history ไม่ได้ · ข้อมูล workspace อื่นไม่โผล่ |
- ไม่ต้องฝืนให้ครบทุก type ทุก feature — เขียนเฉพาะที่ **มีความหมายจริง** แต่ทั้ง epic ควรครอบให้มากที่สุด
- เป้าต่อ feature โดยประมาณ: happy 3–5 · negative 1–3 · edge 1–3 · validation 0–3 · error 1–2 · empty 1–2 · duplicate 0–2 · permission 1–2

## บทบาท/บัญชี UAT ที่ใช้อ้างใน step (ใช้ชื่อบทบาทตามนี้)
- **Owner** — เจ้าของ workspace (สิทธิ์เต็มใน workspace)
- **Live Operator** — สมาชิกที่เป็นคนคุมไลฟ์ (สิทธิ์จำกัด · ดู `proxy.ts`/`capability` ว่าถูกกั้นอะไร)
- **Platform Admin (ทีมภายใน TAKRA · isPlatformAdmin)** — ใช้กับ `/ai-history`
- workspace ทดสอบ: "WS-A" (หลัก) และ "WS-B" (ใช้เช็ค isolation) · ใส่ชื่อ/ค่า test data ให้เป็นรูปธรรม เช่น `QA Avatar 01`

## Priority
- P0 = flow หลัก/compliance/isolation/บล็อกงานสำคัญ · P1 = ฟีเจอร์สำคัญรองลงมา · P2 = UX/edge เล็กน้อย

## รูปแบบ JSON ที่ต้องเขียน (เป๊ะ)
```json
{
  "epic": 10,
  "epic_title": "คลัง Avatar / Voice self-service",
  "epic_ref": "Epic 10 · FR7-11",
  "features": [
    {
      "key": "avatar-self-service",
      "code": "AVT",
      "label": "Avatar self-service — browse/clone Persona Template + แก้ 3 ฟิลด์",
      "story": "10.1",
      "ui_status": "in-ui",
      "cases": [
        {
          "id": "TC-E10-AVT-01",
          "title": "เปิดคลังอวาตาร์แล้วเห็นแค็ตตาล็อก Persona Template ที่โคลนได้",
          "type": "happy",
          "prio": "P0",
          "level": "ui",
          "story": "10.1",
          "ui_status": "in-ui",
          "ui_note": "",
          "precondition": ["ล็อกอินด้วย Owner ของ WS-A ได้", "แค็ตตาล็อกมี Persona Template อย่างน้อย 1 ตัว"],
          "steps": ["เปิดเบราว์เซอร์ไปที่ https://uat-live.takra.ai แล้วเข้าสู่ระบบด้วยบัญชี Owner (UAT)", "ไปที่เมนู \"คลังอวาตาร์\" ...", "สังเกตว่า ..."],
          "test_data": ["บัญชี: Owner ของ WS-A", "Template: ..."],
          "expected": ["...", "...", "ที่มา: Epic 10 · Story 10.1 · FR7"]
        }
      ]
    }
  ]
}
```
- `id` รูปแบบ `TC-E{epic}-{CODE}-{nn}` (nn = 01,02,… ต่อเนื่องใน feature) · CODE = ตัวอักษรพิมพ์ใหญ่ 2–4 ตัว ไม่ซ้ำกันใน epic
- `level` = `"ui"` เสมอ (ยกเว้นสั่งให้ทำ e2e)
- `ui_status` ที่ feature = `"in-ui"` / `"partial"` / `"not-in-ui"` · ที่เคส = `"in-ui"` / `"not-in-ui"`
- ข้อความทั้งหมดเป็นภาษาไทย (ศัพท์เฉพาะ/ชื่อ UI ภาษาอังกฤษคงไว้ได้ตามที่ปรากฏจริง) · ห้ามใส่ HTML tag ใน string
- เรียงเคสใน feature: happy ก่อน แล้วตามด้วย negative · edge · validation · error · empty · duplicate · permission
- ตรวจ JSON ให้ parse ได้ก่อนจบ (`python3 -c "import json;json.load(open('<path>'))"`)
