#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-ai (Live) · ชุดเดียวกับ regai1 (490 เคส) แต่จัดกลุ่มใหม่ "ตามเมนู → ชุดฟีเจอร์"

สั่ง 2026-10-06: ทำไฟล์ใหม่ จัดเป็นเมนู/ฟีเจอร์ให้เป็นชุด · ย้ายผลเทสเดิมมา (uid เดิม) แล้วใช้ไฟล์นี้บันทึกผลแทนไฟล์ happy
- เคส/เนื้อหา/uid มาจาก reg_ai_happy_oct_cases ทั้งหมด (คัดออก · จัดฉากก่อนไลฟ์ · กติกา Graham ทำที่นั่นแล้ว) — ที่นี่แค่ย้ายกลุ่ม
- เมนูเรียงตามแถบซ้ายของแอปจริง (takra-ai origin/uat · i18n th/index.ts nav · live.ts sidebar · settings.ts nav)
- แก้เนื้อเคสที่ชุดหลัก (regai1.json / ai_reg_oct_new_cases.py / reg_ai_failfeat_oct_cases.py) แล้ว build ไฟล์นี้ใหม่ — อย่าแก้ HTML ตรงๆ
- เคสใหม่ที่ไม่มีใน MENUS → build ล้มพร้อมบอก id ให้ใส่ชุดก่อน (กันเคสหล่นหาย)
build: python3 tools/build/build_hub_report.py regaimenu"""
import reg_ai_happy_oct_cases as _src

KINDS = _src.KINDS
UID_MAP = _src.UID_MAP

# เมนู = (key, emoji, chip, title, [ชุด]) · ชุด = (ชื่อชุด, [featkey ทั้งชุด หรือ case id])
MENUS = [
    ('m-login', '🔐', 'เข้าสู่ระบบ', 'เข้าสู่ระบบ · เลือก Workspace', [
        ('เข้าสู่ระบบผ่าน TAKRA Hub · ออกจากระบบ', ['login', 'entitlement-gate']),
        ('สลับ Workspace · จำ Workspace ที่เลือกไว้', ['switch-workspace', 'TC-OCT-G.7', 'TC-OCT-G.8']),
    ]),
    ('m-home', '🏠', 'ภาพรวม', 'พื้นที่ทำงาน › "ภาพรวม"', [
        ('หน้า "ภาพรวม" — ตัวเลข Workspace · ชั่วโมงอวาตาร์ · ตารางไลฟ์ย่อ', ['TC-W1.6', 'TC-Q1.2', 'TC-OCT-G.17']),
        ('เช็กลิสต์เริ่มต้นใช้งาน · ลิงก์ "วิธีใช้งาน"', ['onboarding', 'TC-OCT-G.13']),
    ]),
    ('m-ws', '🏢', 'แก้ไข Workspace', 'พื้นที่ทำงาน › "แก้ไข Workspace"', [
        ('ตั้งค่า Workspace — โทนแบรนด์ · ค่าเริ่มต้น · ข้อมูลจาก TAKRA Hub · สิทธิ์ดูอย่างเดียว',
         ['TC-W1.1', 'TC-W1.2', 'TC-W1.3', 'TC-W1.4', 'TC-W1.5', 'TC-OCT-G.6']),
    ]),
    ('m-team', '👥', 'ทีมงาน', 'พื้นที่ทำงาน › "ทีมงาน"', [
        ('สมาชิก · บทบาท', ['users-roles', 'TC-OCT-G.1', 'TC-OCT-G.2']),
        ('สิทธิ์ Script Approve', ['script-approve-delegate', 'TC-OCT-G.3', 'TC-OCT-G.4', 'TC-OCT-G.5']),
    ]),
    ('m-plan', '💳', 'แพ็กเกจ', 'พื้นที่ทำงาน › "แพ็กเกจและการใช้งาน"', [
        ('โควตา · สถานะแพ็กเกจ · ทางไป TAKRA Hub', ['TC-Q1.1', 'TC-Q1.3', 'ranew-g-plan']),
    ]),
    ('m-voice', '🎙️', 'คลังเสียง', 'คลังข้อมูล › "คลังเสียง"', [
        ('เสียงของระบบ — รายการ · ตัวกรอง · อัปเดตคลัง · เสียงที่เลือกใช้ไม่ได้',
         ['TC-V2.1', 'TC-V2.2', 'TC-V2.3', 'TC-V2.5', 'TC-V2.14', 'TC-V2.16',
          'TC-OCT-J.3', 'TC-OCT-J.4', 'TC-OCT-J.6', 'TC-OCT-J.9']),
        ('"เสียงของฉัน" — อัปโหลด · อัดเสียง · แก้ไข · ตัวกรอง',
         ['TC-V2.6', 'TC-V2.7', 'TC-V2.9', 'TC-V2.10', 'ranew-voice', 'TC-OCT-J.5', 'TC-OCT-J.10', 'TC-OCT-J.11']),
        ('ความยินยอม PDPA — ยืนยัน · clone · ถอนความยินยอม',
         ['TC-V2.8', 'TC-V2.11', 'TC-V2.12', 'TC-V2.13', 'TC-V2.15',
          'TC-OCT-J.1', 'TC-OCT-J.2', 'TC-OCT-J.7', 'TC-OCT-J.8']),
    ]),
    ('m-avatar', '🧑', 'คลังอวาตาร์', 'คลังข้อมูล › "คลังอวาตาร์"', [
        ('อวาตาร์จาก Ops — รายการ · ตัวกรอง · พรีวิว · อัปเดตคลัง · พื้นเขียว',
         ['TC-A2.1', 'TC-A2.2', 'TC-A2.3', 'TC-A2.5', 'TC-A2.11',
          'TC-OCT-I.1', 'TC-OCT-I.2', 'TC-OCT-I.4', 'TC-OCT-I.6']),
        ('อวาตาร์ของร้าน — สร้างจากวิดีโอ · โคลน · แก้ไข · ลบ',
         ['TC-A2.6', 'TC-A2.7', 'TC-A2.8', 'TC-OCT-I.3', 'TC-OCT-I.5', 'TC-OCT-I.7']),
    ]),
    ('m-product', '🛍️', 'คลังสินค้า', 'คลังข้อมูล › "คลังสินค้า"', [
        ('รายการสินค้า — การ์ดสรุป · ค้นหา · กรอง · เรียง · เลือกหลายรายการ',
         ['TC-P2.1', 'TC-P2.7', 'TC-OCT-H.3', 'TC-OCT-H.4', 'TC-OCT-H.5', 'TC-OCT-H.6', 'TC-OCT-H.7']),
        ('เพิ่ม/แก้ไขสินค้า — ข้อมูล · SKU · รูป · หมวด · ทำซ้ำ',
         ['TC-P2.2', 'TC-P2.3', 'TC-P2.4', 'TC-P2.5', 'TC-P2.8', 'TC-P2.9', 'TC-P2.10', 'TC-P2.11', 'TC-P2.12',
          'TC-OCT-H.1', 'TC-OCT-H.9', 'TC-OCT-H.10', 'TC-OCT-H.13']),
        ('เก็บถาวร · เปิดใช้กลับ', ['TC-P2.6', 'TC-P2.13', 'TC-OCT-H.8']),
        ('จุดเด่น · Claims · FAQ · คำเสี่ยงเฉพาะสินค้า · ความพร้อมขาย',
         ['product-enrich', 'TC-OCT-H.2', 'TC-OCT-H.11', 'TC-OCT-H.12']),
    ]),
    ('m-script', '📝', 'คลังสคริปต์', 'คลังข้อมูล › "คลังสคริปต์"', [
        ('รายการสคริปต์ — ตัวเลขสรุป · ค้นหา · โฟลเดอร์ · ทำซ้ำ · ลบ',
         ['TC-SL.1', 'TC-SL.1-RF', 'TC-SL.2', 'TC-SL.5', 'TC-SL.6', 'TC-SL.7', 'TC-SL.8', 'TC-SL.9', 'TC-SB.2', 'TC-SB.7']),
        ('หน้าสร้าง/แก้สคริปต์ — ทางเริ่ม · 4 ขั้น · บันทึก · กู้ร่าง',
         ['TC-OCT-B.1', 'TC-SL.3', 'TC-SL.4', 'TC-SL.10', 'TC-SL.13', 'ranew-l-editor']),
        ('บล็อก · Content · กระดิ่ง — เปิดทีละบล็อก (TAKRA-1225)',
         ['TC-SL.11', 'TC-SL.12', 'TC-SL.14', 'TC-SL.15', 'TC-OCT-B.2', 'TC-OCT-B.3', 'TC-OCT-B.4',
          'T1225.2', 'T1225.3', 'T1225.4', 'T1225.8', 'T1225.9']),
        ('AI ช่วยร่างสคริปต์ — สั่งร่าง · ภาษา · โควตา/แพ็กเกจ · หลายสคริปต์ต่อบล็อก',
         ['ai-generate', 'TC-GC.3', 'multi-content', 'building-blocks',
          'TC-OCT-L.6', 'TC-OCT-L.7', 'TC-OCT-L.10', 'TC-OCT-L.11', 'TC-OCT-L.12', 'TC-OCT-L.13']),
        ('AI ช่วยร่าง — ตัวเลือกก่อนร่าง: โทน · กลุ่มเป้าหมาย · เพศผู้พูด · กำหนดบล็อกเอง',
         ['TC-GC.1', 'TC-GC.2', 'TC-GC.4', 'TC-GC.5', 'TC-GC.6', 'TC-GC.7', 'TC-GC.8', 'TC-GC.9', 'TC-GC.10',
          'TC-OCT-L.8', 'TC-OCT-L.9']),
        ('ส่งขออนุมัติ · อนุมัติ · ตีกลับ · เก็บถาวร · ตรวจเนื้อหาที่ห้ามออกอากาศ',
         ['script-lifecycle', 'ranew-l-approval', 'TC-OCT-R.2', 'ranew-r-approval']),
    ]),
    ('m-risk', '⚠️', 'คำเสี่ยง', 'คลังข้อมูล › "คำเสี่ยง"', [
        ('หน้าหลัก · ประเภทธุรกิจ · คำกลาง · ชุดคำที่สแกนจริง · สถิติ',
         ['TC-R2.1', 'TC-R2.5', 'TC-R2.6', 'TC-R2.7',
          'TC-OCT-K.1', 'TC-OCT-K.2', 'TC-OCT-K.3', 'TC-OCT-K.7', 'TC-OCT-K.10']),
        ('เพิ่ม/แก้/ลบคำเสี่ยง · คำห้ามทั่วทั้ง Workspace · ค้นหา',
         ['TC-R2.3', 'TC-R2.4', 'TC-R2.8', 'TC-R2.9', 'TC-R2.10', 'TC-R2.11', 'TC-R2.12', 'TC-R2.13',
          'TC-OCT-K.4', 'TC-OCT-K.5', 'TC-OCT-K.6', 'TC-OCT-K.8', 'TC-OCT-K.9']),
        ('สิทธิ์ — ผู้ที่ไม่ใช่ Owner ดูได้อย่างเดียว', ['TC-R2.14', 'RSK-06']),
        ('จัดหมวดหมู่คำเสี่ยงใหม่ (TAKRA-1228)', ['risk-category-migration']),
    ]),
    ('m-schedule', '📅', 'ตารางไลฟ์', 'ระบบไลฟ์ › "ตารางไลฟ์"', [
        ('ปฏิทิน · ช่องทาง + บัญชี', ['TC-OCT-Q.3', 'TC-OCT-Q.4']),
        ('ตั้งรอบไลฟ์ · แก้ไข · ลบ · ทำซ้ำ',
         ['TC-OCT-Q.1', 'TC-OCT-Q.2', 'TC-OCT-Q.5', 'TC-OCT-Q.6', 'TC-OCT-Q.7', 'TC-OCT-Q.8', 'TC-OCT-Q.9', 'TC-OCT-Q.10']),
    ]),
    ('m-dash', '📊', 'แดชบอร์ด', 'แพลตฟอร์มไลฟ์ › "แดชบอร์ด"', [
        ('แดชบอร์ด — กำลังออกอากาศ · คิวไลฟ์ถัดไป · สรุปวันนี้ · ไลฟ์ล่าสุด · ขัดข้อง',
         ['ranew-m-dashboard', 'TC-CT.8', 'SRF-02']),
        ('บรรทัดองค์ประกอบไลฟ์บนการ์ด/แถว — ช่องทาง · บัญชี · อวาตาร์ · เสียง · สินค้า · สคริปต์ (TAKRA-1227)',
         ['live-list-composition', 'TC-OCT-M.2', 'TC-OCT-M.3', 'TC-OCT-M.4', 'TC-OCT-M.5', 'TC-OCT-M.6', 'TC-OCT-M.7']),
    ]),
    ('m-mylives', '📺', 'ไลฟ์ของฉัน', 'แพลตฟอร์มไลฟ์ › "ไลฟ์ของฉัน"', [
        ('แท็บ · ป้ายสถานะ · หน้ารายละเอียดรอบ · เลยกำหนด · ยกเลิกอัตโนมัติ',
         ['ranew-q-mylives', 'TC-ML.5', 'TC-ML.6']),
    ]),
    ('m-projects', '📁', 'โปรเจกต์ของฉัน', 'แพลตฟอร์มไลฟ์ › "โปรเจกต์ของฉัน"', [
        ('ร่างไลฟ์ — แก้ไขต่อ · ลบร่าง · รายการว่าง · ร่างครบ 20',
         ['TC-ML.3', 'TC-OCT-A.3', 'TC-OCT-M.1', 'ranew-m-projects']),
    ]),
    ('m-studio', '🎬', 'Studio', 'Studio — สร้าง/แก้ไลฟ์', [
        ('โครงหน้าจอ · บันทึกอัตโนมัติ · ชื่อโปรเจกต์ · แผงฉาก',
         ['studio-shell', 'TC-OCT-A.1', 'TC-OCT-A.2', 'ranew-p-shell', 'ranew-p-scenes']),
        ('"ผู้นำเสนอ" — อวาตาร์ · เสียง · อวาตาร์ของไลฟ์นี้',
         ['studio-avatar-voice', 'TC-AV.5', 'TC-OCT-N.1', 'TC-OCT-N.2', 'TC-OCT-N.3', 'TC-OCT-N.4',
          'TC-OCT-N.6', 'TC-OCT-N.7', 'TC-OCT-N.8', 'TC-OCT-N.9']),
        ('"ผู้นำเสนอ" › "น้ำเสียง" — อวตารพูดแบบมีอารมณ์ (TAKRA-1224)',
         ['studio-voice-style', 'TC-AV.7', 'TC-AV.8', 'TC-OCT-N.5']),
        ('Layer — ข้อความ "AI Live" · สื่อ · การ์ดสินค้า · นับถอยหลัง · เครื่องมือบนแคนวาส',
         ['layer-content', 'scene-products', 'ranew-p-layers', 'ranew-p-widgets']),
        ('เขตปลอดภัย 9:16 · ย้อนกลับ/ทำซ้ำ · หน้าต่าง Preview',
         ['studio-preview', 'ranew-p-safe', 'ranew-p-preview']),
        ('สคริปต์ในฉาก — ผูก · ปลด · เพดาน · จำนวนรอบ · เรียง/ย้ายข้ามฉาก',
         ['TC-SB.1', 'TC-SB.3', 'TC-SB.4', 'TC-SB.5', 'TC-SB.6', 'script-reorder-move', 'T1225.10',
          'TC-OCT-R.3', 'TC-OCT-R.4', 'TC-OCT-R.5', 'ranew-r-move']),
        ('สคริปต์ในฉาก — สร้างใหม่ใน Studio · ตรวจคำเสี่ยง · บันทึกเข้าคลัง · snapshot',
         ['TC-OCT-R.1', 'TC-OCT-R.6', 'TC-OCT-R.7', 'TC-OCT-R.8', 'TC-OCT-R.9', 'risk-check-inline', 'script-two-way-sync']),
    ]),
    ('m-preflight', '✅', 'เริ่มไลฟ์', 'Studio › หน้าต่าง "เริ่มไลฟ์" — ตรวจก่อนไลฟ์ · ตั้งเวลา', [
        ('"ตรวจก่อนไลฟ์" — รายการตรวจ · ปุ่ม "แก้" · ความยาวไลฟ์ · ข้อเตือนฝั่งจอ',
         ['preflight-launch', 'TC-OCT-R.14', 'TC-OCT-R.15', 'TC-OCT-R.16', 'TC-OCT-R.17', 'TC-OCT-R.18',
          'TC-OCT-R.19', 'TC-OCT-R.20', 'TC-OCT-R.21', 'COM-04']),
        ('ตั้งเวลาไลฟ์จาก Studio', ['ranew-r-schedule']),
        ('กระดิ่งคอมเมนต์ — ตั้งค่าในฟอร์มสร้างไลฟ์ (TAKRA-1223)', ['bell-setup']),
    ]),
    ('m-broadcast', '📡', 'ออกอากาศ', 'หน้าเริ่มออกอากาศ — วิธีออกอากาศ · บัญชี TikTok · สวิตช์ AI', [
        ('วิธีออกอากาศ · ขั้นตอนอุปกรณ์ · จอ Display Device · หยุดไลฟ์',
         ['TC-BR.1', 'TC-BR.2', 'TC-BR.4', 'TC-BR.5', 'TC-BR.7',
          'TC-OCT-S.3', 'TC-OCT-S.4', 'TC-OCT-S.5', 'TC-OCT-S.6', 'TC-OCT-S.7', 'TC-OCT-S.8', 'TC-OCT-S.9', 'TC-OCT-U.4']),
        ('บัญชี TikTok ที่เพิ่มเอง (โหมดส่งตรง)', ['tiktok-account']),
        ('สวิตช์ "ให้ AI ตอบคอมเมนต์ผู้ชม" · โหมดพื้นฐาน',
         ['TC-BR.3', 'TC-RA.1', 'auto-reply-switch', 'ranew-switch', 'TC-OCT-S.1', 'TC-OCT-S.2']),
    ]),
    ('m-control', '🎛️', 'ห้องคุมไลฟ์', 'แพลตฟอร์มไลฟ์ › "ห้องคุมไลฟ์"', [
        ('แถบสถานะ · บังคับปิดไลฟ์ · บรรทัดที่อวาตาร์พูด · คอมเมนต์สด',
         ['TC-CT.2', 'TC-CT.3', 'TC-CT.5', 'TC-CT.6', 'TC-CT.7',
          'TC-OCT-T.1', 'TC-OCT-T.2', 'TC-OCT-T.3', 'TC-OCT-T.5', 'TC-OCT-T.7', 'TC-OCT-T.8']),
        ('"ภาพที่กำลังออกอากาศ" · Preview บนมือถือ (TAKRA-1229)',
         ['control-room-on-air-preview', 'broadcast-display', 'TC-OCT-T.4', 'TC-OCT-T.6']),
        ('การ์ด "AI ตอบ" · แผง "บล็อกล่าสุด" · แจ้งเตือนระหว่างคุมไลฟ์',
         ['SRF-01', 'SRF-03', 'SRF-04', 'TC-RA.4', 'TC-RA.5', 'TC-OCT-U.5']),
    ]),
    ('m-reply', '🤖', 'AI ตอบคอมเมนต์', 'ระหว่างไลฟ์ — AI ตอบคอมเมนต์ · เสียงกระดิ่ง · เสียงที่สอง', [
        ('คิวตอบ · จังหวะ · ตอบรวบ · งบเวลา',
         ['RPL-01', 'TC-OCT-D.1', 'TC-OCT-D.2', 'TC-OCT-D.4', 'TC-OCT-T.12', 'TC-OCT-T.13', 'TC-OCT-T.14']),
        ('ข้อมูลสินค้า · FAQ · ด่านการขาย (ราคา/โปร/ของคงเหลือ/จัดส่ง/ช่องทางนอกไลฟ์)',
         ['RPL-02', 'RPL-10', 'RPL-13', 'TC-OCT-D.3', 'COM-05', 'COM-08',
          'TC-OCT-T.9', 'TC-OCT-T.10', 'TC-OCT-T.11', 'TC-OCT-T.15']),
        ('คำเสี่ยงขาเข้า/ขาออก · ชั้นคำเสี่ยงบังคับของระบบ', ['RSK-01', 'RSK-05', 'TC-OCT-T.16', 'TC-OCT-T.17']),
        ('ต้อนรับคนเข้าห้อง · ขอบคุณคนกดแชร์', ['ranew-greet']),
        ('เสียงกระดิ่ง — คอมเมนต์ใหม่ (TAKRA-1223) · {{bell}} ในสคริปต์', ['bell-behaviour', 'TC-BR.6', 'TC-OCT-S.10']),
        ('เสียงที่สองในไลฟ์ (TAKRA-1230 · Spike)', ['co-host-voice']),
    ]),
    ('m-recap', '📈', 'สรุปไลฟ์', 'หน้า "สรุปไลฟ์" หลังจบรอบ', [
        ('หัวข้อรอบ · แถบเวลา · คำบอกลา · สาเหตุที่จบ',
         ['session-report', 'TC-OCT-U.1', 'TC-OCT-U.2']),
        ('ผลงาน AI — โหมดตอบของรอบ · การ์ด AI · "ระบบระงับ n ครั้ง" · คำตอบทั้งหมด',
         ['post-live-reply-recap', 'TC-OCT-U.3']),
    ]),
    ('m-tools', '🛠️', 'เครื่องมือ', 'แพลตฟอร์มไลฟ์ › "เครื่องมือ"', [
        ('เครื่องมือเตรียมพร้อมก่อนไลฟ์ — เครือข่าย · เสียง · AI · เครื่อง', ['pre-live-tools']),
    ]),
    ('m-settings', '⚙️', 'ตั้งค่า', '"ตั้งค่าบัญชี" · "การตั้งค่า" ของแอปไลฟ์', [
        ('ตั้งค่าบัญชี — "โปรไฟล์" · "ลบบัญชี"', ['pdpa-dsar', 'ranew-g-account']),
        ('"การแจ้งเตือน" — ตั้งค่า · อีเมลยกเลิก · กระดิ่งแจ้งเตือนในแอป', ['notification-prefs', 'ranew-g-notif']),
        ('"การตั้งค่า" ของแอปไลฟ์', ['live-settings']),
    ]),
    ('m-remote', '🖧', 'เครื่อง remote', 'เครื่อง remote (TAKRA-1226 · งาน infra)', [
        ('ใช้งานผ่านเว็บบนเครื่อง remote ได้เหมือน UAT', ['remote-smoke']),
    ]),
    ('m-e2e', '🔄', 'Full E2E', 'Full E2E — วิ่งครบลูปตั้งแต่ต้นจนจบ', [
        ('เข้าระบบ → เตรียมคลัง → สร้างไลฟ์ใน Studio → ออกอากาศ → สรุปไลฟ์', ['fullflow']),
    ]),
]


# ── ตัดเคสออก (สั่ง 2026-10-06) — ผลที่บันทึกไว้ยังอยู่ใน store-data (uid ตรึง) ใส่กลับได้โดยเอา id ออกจากชุดนี้ ──
# ① ซ้ำตรงตัว: -RF = รอบ re-test ของเคสเดียวกัน · BR.3 ตรวจแบนเนอร์ "โหมดพื้นฐานของรอบนี้:" เดียวกับ RA.1 (RA.1 ครอบกว่า: เช็กแบนเนอร์ค้างด้วย)
DROP_DUP = {'TC-SL.1-RF': 'TC-SL.1', 'TC-BR.3': 'TC-RA.1'}
# ② เคสเดิมที่มีเคส 🆕 TC-OCT-* แทนแล้ว (replaces= ใน ai_reg_oct_new_cases) — เดิมคงไว้เพราะมีผลบันทึก · ตอนนี้ตัด เทสที่เคส 🆕
_NEW_IDS = {c['id'] for f in _src._new.EPIC['feats'] for c in f['cases']}
DROP_REPLACED = sorted(i for e in _src.EPICS for f in e['feats'] for c in f['cases']
                       for i in [c['id']] if i in _src._new.REPLACED and i not in _NEW_IDS)
# ③ Priority P2 — รอบนี้เอาเฉพาะ P0/P1
DROP_P2 = sorted(c['id'] for e in _src.EPICS for f in e['feats'] for c in f['cases'] if c['prio'] == 'P2')
DROP = set(DROP_DUP) | set(DROP_REPLACED) | set(DROP_P2)


def _regroup():
    by_id, by_feat = {}, {}
    for e in _src.EPICS:
        for f in e['feats']:
            by_feat[f['featkey']] = [c['id'] for c in f['cases'] if c['id'] not in DROP]
            for c in f['cases']:
                if c['id'] not in DROP:
                    by_id[c['id']] = c
    used, epics = {}, []
    for key, emoji, chip, title, sets in MENUS:
        feats = []
        for i, (stitle, refs) in enumerate(sets, 1):
            ids = []
            for r in refs:
                if r in DROP:
                    continue
                got = by_feat[r] if r in by_feat else ([r] if r in by_id else None)
                assert got is not None, f'{key}: ไม่รู้จัก "{r}" (ไม่ใช่ featkey หรือ case id ในชุดหลัก)'
                ids += got
            for cid in ids:
                assert cid not in used, f'{cid} อยู่ 2 ชุด: {used[cid]} และ {key}#{i}'
                used[cid] = f'{key}#{i}'
            if ids:
                feats.append(dict(featkey=f'{key}-{len(feats) + 1}', title=f'ชุด {len(feats) + 1} · {stitle}', cases=[by_id[c] for c in ids]))
        n = sum(len(f['cases']) for f in feats)
        epics.append(dict(key=key, emoji=emoji, chip=f'{emoji} {chip}', title=title, feats=feats))
    missing = [c for c in by_id if c not in used]
    assert not missing, f'เคสยังไม่มีชุด (ใส่ลง MENUS ก่อน): {missing}'
    return epics


EPICS = _regroup()
_N = sum(len(f['cases']) for e in EPICS for f in e['feats'])
_N_SETS = sum(len(e['feats']) for e in EPICS)
OLD_URL = 'https://wanlee-tankunnatam.github.io/qa-test-reports/' + _src.META['out_rel']

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-bymenu-ui-test-cases-table.html',
    # ไฟล์ใหม่ยังไม่มี store → ตั้งต้นด้วยผลจากไฟล์ happy (uid เดิม) ครั้งเดียวตอนสร้างไฟล์
    seed_store_from=_src.META['out_rel'],
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression แยกตามเมนู/ฟีเจอร์',
    emoji='🎥', uid_start=13001,
    download='takra-ai-regression-oct0509-bymenu-ui-test-cases-table.html',
    # ปุ่มมุมขวาบนพาไปหน้าแผน regression (สั่ง 2026-10-06) แทนหน้า hub
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan',
    back_label='🗓️ แผน Regression', back_title='ไปหน้าแผน Regression 5–9 ต.ค. (ตารางแผน)',
    sub=(f'รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · เคสชุดเดียวกับรายงาน Happy ({_N} เคส) จัดใหม่เป็น '
         f'<b>{len(EPICS)} เมนู · {_N_SETS} ชุดฟีเจอร์</b> เรียงตามแถบเมนูของแอป · Target: <b>UAT</b> https://uat-live.takra.ai'),
    groups_label=f'{len(EPICS)} เมนู → {_N_SETS} ชุดฟีเจอร์ (ตามแถบเมนูของแอป)',
    note=(f'✂️ <b>ตัดเคสออก {len(DROP)} เคส (6 ต.ค.)</b>: ซ้ำตรงตัว {len(DROP_DUP)} ('
          + ' · '.join(f'{k} ซ้ำ {v}' for k, v in DROP_DUP.items())
          + f') · เคสเดิมที่มีเคส 🆕 TC-OCT-* แทนแล้ว {len(DROP_REPLACED)} — เทสที่เคส 🆕 แทน · P2 {len(DROP_P2)} ({", ".join(DROP_P2)}) '
          '— ผลที่เคยบันทึกของเคสที่ตัดยังเก็บอยู่ในไฟล์ ไม่หาย<br>'
          '🧭 <b>รายงานนี้ใช้บันทึกผลแทนรายงาน Happy ตั้งแต่ 6 ต.ค. 2569</b> — เคส/เนื้อหา/uid ชุดเดียวกันทุกเคส '
          f'แค่จัดกลุ่มใหม่ตามเมนูของแอป (เข้าสู่ระบบ → พื้นที่ทำงาน → คลังข้อมูล → ระบบไลฟ์ → แพลตฟอร์มไลฟ์ → Studio → ออกอากาศ → สรุปไลฟ์ → ตั้งค่า) '
          'แล้วแบ่งแต่ละเมนูเป็น <b>ชุดฟีเจอร์</b> — เคสเดิมกับเคส 🆕 TC-OCT-* ของเรื่องเดียวกันอยู่ชุดเดียวกัน · '
          'ผลเทส/Actual/Jira ที่บันทึกในรายงาน Happy ถึง 6 ต.ค. ย้ายมาครบแล้ว'
          f'<br>📎 รายงานเดิม (จัดตามขั้นที่ 1–6 · เลิกบันทึกผลแล้ว): <a href="{OLD_URL}">รายงาน Happy</a> · '
          'ใช้เลือกเทสทีละเมนูได้ที่ตัวกรอง "กลุ่ม" · มอบผู้รับผิดชอบรายชุดได้ที่ 👤 บนหัวชุด'
          '<br>' + _src.NOTE_BODY),
    noui_note=_src.META['noui_note'], noui_badge=_src.META['noui_badge'],
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · แยกตามเมนู/ฟีเจอร์',
)
