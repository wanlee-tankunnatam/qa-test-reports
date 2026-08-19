# งานรอบ 2 — ปรับ taxonomy ประเภทเคส MVP-2 เป็น 7 ประเภท + เติมเคสให้ครบตามนิยาม

อ่าน `RULES.md` (โฟลเดอร์เดียวกัน) ให้จบก่อน — กติกา Steps to Reproduce / คำ UI จริง / Expected อ้างเอกสาร / ui_status / รูปแบบ JSON **ยังบังคับทั้งหมด** ยกเว้นส่วน "ประเภทเคส (type)" ที่ **แทนที่ด้วยตารางใหม่นี้**

## taxonomy ใหม่ (7 type) — ค่า `type` ต้องเป๊ะ · ทุกเคสต้องมี `sub` (ข้อความสั้นจากคอลัมน์ sub)
| type | ชื่อ | นิยาม (ของผู้ใช้) | ค่า `sub` ที่ใช้ได้ |
|---|---|---|---|
| `happy` | Happy Path | Flow ปกติ | `Flow ปกติ` |
| `negative` | Negative | ข้อมูลผิด / Action ผิด (ผู้ใช้ทำสิ่งที่ระบบต้องปฏิเสธ/กั้น — ไม่ใช่เรื่องสิทธิ์ · ไม่ใช่รูปแบบ/ความยาว input · ไม่ใช่ระบบล้ม) | `ข้อมูลผิด` · `Action ผิด` |
| `boundary` | Boundary / Edge | Min / Max / ก่อนขอบ / ตรงขอบ / เกินขอบ (ค่าสุดขอบของขีดจำกัดที่สเปก/UI กำหนด · รวม edge พิเศษ เช่น รายการเยอะมาก · รีเฟรช/หลายแท็บ ให้ใช้ sub `Edge`) | `Min` · `Max` · `ก่อนขอบ` · `ตรงขอบ` · `เกินขอบ` · `Edge` |
| `validation` | Validation | Format, Required, Character, Length (ตรวจ input บนฟอร์ม) | `Format` · `Required` · `Character` · `Length` |
| `error` | Exception / Error | API fail, Network fail, Server error, Timeout (ระบบ/บริการล้ม ผู้ใช้ต้องเห็นข้อความ+ทางไปต่อ ไม่ค้าง/ไม่เงียบ · รวม degrade ของบริการภายนอก) | `API fail` · `Network fail` · `Server error` · `Timeout` |
| `permission` | Permission | Role ไหนทำได้ / ทำไม่ได้ (Owner · Live Operator · Platform Admin · ข้าม workspace) | `Owner` · `Live Operator` · `Platform Admin` · `ข้าม workspace` (ใช้ role ที่เป็นตัวเอกของเคส) |
| `data` | Data | Empty, Null, Duplicate, Existing, Non-existing (สถานะของข้อมูล — ไม่มีข้อมูล · ค่า null/ไม่มีค่า · ซ้ำ · มีอยู่แล้ว · ไม่มีอยู่/ถูกลบไปแล้ว) | `Empty` · `Null` · `Duplicate` · `Existing` · `Non-existing` |

### กติกา re-tag ของเดิม
- `edge` → `boundary` (เลือก sub ให้ตรง: ถ้าเป็นจำนวน/ความยาวสุดขอบ → Min/Max/ก่อนขอบ/ตรงขอบ/เกินขอบ · ถ้าเป็น edge อื่น เช่น รีเฟรชกลางทาง/หลายแท็บ/รายการเยอะ → `Edge`)
- `empty` → ส่วนใหญ่ `data` sub `Empty` (empty state · ผลค้นหาศูนย์) **ยกเว้น** "ไม่กรอกช่องบังคับแล้วกดบันทึก" → `validation` sub `Required`
- `duplicate` → `data` sub `Duplicate`
- เคสที่เคยเป็น `edge` เรื่อง "อักขระพิเศษ/อีโมจิ" → `validation` sub `Character` · เรื่อง "ข้อความยาวมาก/เกิน max" → `validation` sub `Length` ถ้าเป็นการตรวจฟอร์ม หรือ `boundary` ถ้าเป็นการทดสอบค่าขอบของขีดจำกัด (เลือกอันที่ตรงเจตนาของเคส)
- `negative` ที่แท้จริงเป็นเรื่องสิทธิ์ → `permission` · ที่เป็นระบบล้ม → `error` · ที่เป็นข้อมูลไม่มี/ถูกลบ → `data` sub `Non-existing`
- เคสเดิมที่ไม่เข้าข่ายอะไรเลยให้คงไว้ใน type ที่ใกล้ที่สุด — **ห้ามลบเคสเดิม · ห้ามเปลี่ยน id เดิม**

### เติมเคสใหม่ (append ต่อท้าย id เดิมของ feature นั้น · ไม่รีเซ็ตเลข)
ไล่ทุก feature แล้วถามตามนิยาม — ถ้ายังขาดและมีความหมายจริงใน UI/สเปก ให้เพิ่ม:
- **Boundary:** มีขีดจำกัดอะไรบ้างใน feature นี้ (จำนวนสูงสุด เช่น เสียง 3/workspace · ไฟล์ 10MB · ความยาวชื่อ · จำนวนฉาก/สคริปต์ · จำนวนปลายทาง · ช่วงเวลา · เพจเนชัน) → ควรมีอย่างน้อยชุด **ก่อนขอบ / ตรงขอบ / เกินขอบ** (รวมเป็นเคสเดียวได้ถ้าทำต่อเนื่องกันธรรมชาติ เช่น "มี 2 → เพิ่มตัวที่ 3 ได้ → เพิ่มตัวที่ 4 ถูกกั้น") และ Min ถ้ามีความหมาย
- **Validation:** ฟอร์มมีช่องอะไร → Format (URL/อีเมล/ตัวเลข) · Required (ว่างแล้วบันทึก) · Character (อักขระพิเศษ/อีโมจิ/ช่องว่างล้วน) · Length (เกิน max)
- **Error:** อย่างน้อย API fail หรือ Network fail 1 เคส และ Timeout/Server error ถ้า flow มีการรอผล (clone · สรุปไลฟ์ · โหลดรายการ) — step ให้ระบุวิธีจำลอง (เช่น ปิดเน็ต/บล็อกคำขอด้วย DevTools) แบบที่ manual tester ทำได้
- **Data:** Existing (ทำซ้ำกับของที่มีอยู่แล้ว เช่น clone template เดิมอีกครั้ง · เพิ่มชื่อที่มีอยู่) · **Non-existing** (เปิดลิงก์/ID ของรายการที่ถูกลบหรือไม่มีจริง → หน้าว่าง/404 ที่สุภาพ ไม่ค้าง) · Null (ข้อมูลที่ไม่มีค่า เช่น ไม่ได้ตั้งเป้า · ไม่มีรูป · ไม่มี output snapshot) · Empty · Duplicate
- **Permission:** อย่างน้อย Owner ทำได้ vs Live Operator ทำไม่ได้/ไม่เห็น 1 คู่ต่อ feature ที่เกี่ยว · ข้าม workspace ถ้ามีข้อมูล scoped
- **Negative:** ข้อมูลผิด (กรอกข้อมูลที่ถูก format แต่ไม่ถูกต้องตามเงื่อนไขธุรกิจ) · Action ผิด (ทำลำดับผิด · ยกเลิกกลางคัน · กดซ้ำระหว่างรอ)
- ไม่ฝืนเพิ่มเคสที่ไม่มีความหมายจริง · เป้ารวมหลังเติม ≈ เดิม +20–40% ต่อ epic
- เคสที่เขียนสำหรับหน้าจอที่ยังไม่มีใน UI → ยังต้องตั้ง `ui_status: "not-in-ui"` + `ui_note` ตาม RULES.md

### รูปแบบ JSON — เหมือนเดิมทุกอย่าง + เพิ่มฟิลด์ `sub` ในทุกเคส
```json
{ "id": "TC-E10-VLB-19", "title": "...", "type": "boundary", "sub": "เกินขอบ", "prio": "P1", "level": "ui", "story": "10.2", "ui_status": "in-ui", "ui_note": "", "precondition": [...], "steps": [...], "test_data": [...], "expected": [... , "ที่มา: Epic 10 · Story 10.2 · FR9"] }
```
- เรียงเคสใน feature ตามลำดับ type ใหม่: happy → negative → boundary → validation → error → permission → data
- เขียนทับไฟล์เดิม (path เดียวกัน) แล้วตรวจ parse ได้ + ไม่มี id ซ้ำ + ทุกเคสมี `sub` ที่อยู่ในตารางเท่านั้น
- ข้อความตอบกลับสุดท้าย: สรุปจำนวนเดิม→ใหม่ · จำนวนต่อ type · เคสใหม่ที่เพิ่ม (id + หัวข้อสั้น)
