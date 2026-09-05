# AFFTECH #2 — Exclusive Networking Night check-in

หน้าเช็คอิน 30 คนที่ซื้อกิจกรรมเสริม ใช้ที่หน้างานวันเสาร์ 5 ก.ย. 2569
ทุกเครื่องเห็นข้อมูลชุดเดียวกัน เพราะสถานะทั้งหมดอยู่ใน `state.json` ในโฟลเดอร์นี้ (หน้าเว็บอ่าน/เขียนผ่าน GitHub API)

- หน้าเว็บ: https://wanlee-tankunnatam.github.io/qa-test-reports/afftech-checkin/
- `index.html` — หน้าเว็บ + รายชื่อ 30 คนฝังอยู่ในไฟล์ (สร้างจาก CSV ด้วย `build.py`) ไม่ถูกแก้ตอนใช้งาน
- `state.json` — การติ๊ก / รายชื่อที่เพิ่ม / ข้อมูลที่แก้ / คนที่ลบ (ทุกการกดในหน้าเว็บ = 1 commit ลงไฟล์นี้)
- `template.html` + `build.py` — ต้นแบบและสคริปต์สร้าง `index.html`

## ให้ทีมใช้

1. สร้าง fine-grained token ที่ GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Repository access: **Only select repositories → qa-test-reports**
   - Permissions → Repository permissions → **Contents: Read and write** (อย่างเดียว)
   - Expiration: 7 วัน
2. ส่งลิงก์นี้ให้ทีม (เปิดครั้งเดียวต่อเครื่อง หน้าจะจำ token ไว้ในเครื่องนั้นแล้วลบออกจาก URL)

   `https://wanlee-tankunnatam.github.io/qa-test-reports/afftech-checkin/#token=github_pat_xxxx`

   หรือเปิดหน้าเปล่าแล้ววาง token ในกล่องใต้แถบความคืบหน้าก็ได้
3. ไม่มี token ก็เปิดดูได้ (อ่านอย่างเดียว) แต่ติ๊กแล้วจะไม่บันทึก
4. จบงานแล้ว **revoke token** ที่หน้าเดิม (ใครมี token เขียนไฟล์ใน repo นี้ได้ทั้ง repo)

## เริ่มใหม่ / ดูข้อมูล

- เริ่มใหม่ทั้งหมด: แก้ `state.json` ให้เหลือ `{"version": 0, ...}` ว่าง ๆ แล้ว commit (ดูรูปแบบในไฟล์ปัจจุบัน)
- ประวัติการติ๊กทุกครั้งอยู่ใน git log ของ `state.json`
- หน้าเว็บดึงข้อมูลใหม่ทุก 4 วินาที (ใช้ ETag จึงไม่กินโควตา API ถ้าไม่มีอะไรเปลี่ยน)
