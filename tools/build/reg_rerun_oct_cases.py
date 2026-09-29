#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-rerun · คู่ 🪟 Windows / 🍎 Mac ใช้รายงานเดียว (os_cols)

ข้อมูลเคสอยู่ที่ tools/build/reg-oct-sources/regrerun.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
คัดจากรายงานหลัก MVP1+2 (Windows เป็นฐาน · จับคู่ Mac ด้วย TC id):
  · rrfail — จุดที่เคย FAIL (union ผลรอบก่อนจากไฟล์ windows + mac · 37 เคส) — note "ผลรอบก่อน (Win/Mac)" ต่อเคส
  · rrcore — flow หลัก P0 ที่ไม่ซ้ำก้อน rrfail — คัดเฉพาะ feature หลัก: login (M1-E1) ·
    สร้าง/รันรีรัน (M1-E4 + ขั้นที่ 8) · playlist (ขั้นที่ 2/5/10) · จอ/overlay (ขั้นที่ 3)
  · rrnew — ฟีเจอร์ใหม่ ก.ย.: auto chat-reply LLM (ขั้นที่ 13 · Epic 22) + keyword ตอบกลับ (Epic 23) — P0+P1
    (ตั้งเวลาอัตโนมัติ + แบนเนอร์วิ่ง: ไม่พบเคสในรายงาน/โมดูลใดของ takra-rerun — ไม่ออกเคสใหม่เอง)
build: python3 tools/build/build_hub_report.py regrerun"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'reg-oct-sources'
_DOC = json.loads((SRC / 'regrerun.json').read_text(encoding='utf-8'))

KINDS = {
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ใส่ของผิด/ทำผิดลำดับ แล้วระบบต้องกัน'),
    'boundary':   ('Boundary/Edge', 'ค่าขอบ · ลิมิต · เพดานแพ็กเกจ'),
    'validation': ('Validation', 'กฎการกรอก/ตรวจข้อมูล'),
    'exception':  ('Exception/Error', 'เน็ตหลุด · โปรเซสตาย · error แล้วต้องกู้คืน'),
    'permission': ('Permission', 'สิทธิ์/ล็อกข้ามเครื่อง/แยก workspace'),
    'data':       ('Data', 'ความถูกต้องของข้อมูล/สถิติ'),
}

_GROUPS = [
    ('rrfail', '❌ จุดที่เคย FAIL', '❌', 'จุดที่เคย FAIL รอบก่อน (union ผล Windows + Mac · ดู note "ผลรอบก่อน" ในแต่ละเคส)'),
    ('rrcore', '🧭 flow หลัก P0', '🧭', 'flow หลัก P0 — login · สร้าง/รันรีรัน · playlist · จอ/overlay (ไม่ซ้ำก้อนที่เคย FAIL)'),
    ('rrnew',  '🆕 ฟีเจอร์ ก.ย.', '🆕', 'ฟีเจอร์ใหม่ ก.ย. — auto chat-reply (LLM · Epic 22) + keyword ตอบกลับอัตโนมัติ (Epic 23) · P0+P1'),
]

EPICS = []
for _key, _chip, _emoji, _title in _GROUPS:
    _feats = []
    for _f in _DOC['groups'][_key]:
        _cases = []
        for _c in _f['cases']:
            _c = dict(_c)
            # note ต่อเคส (เช่น "ผลรอบก่อน (Win/Mac): FAIL / PASS") ไม่มีช่องแสดงของตัวเอง
            # → ต่อท้ายบรรทัดที่มา (hint ใต้ Expected) ให้เห็นตอนเทส
            if _c.get('note'):
                _c['src'] = f"{_c['src']} · {_c['note']}"
            _cases.append(_c)
        _feats.append(dict(featkey=_f['featkey'], title=_f['title'], cases=_cases))
    EPICS.append(dict(key=_key, chip=_chip, emoji=_emoji, title=_title, feats=_feats))

_N = {e['key']: sum(len(f['cases']) for f in e['feats']) for e in EPICS}

META = dict(
    out_rel='projects/takra-rerun/2026/10/reports/takra-rerun-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Rerun — Regression Test Cases (คู่ 🪟/🍎)',
    emoji='🔁', uid_start=14001, download='takra-rerun-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=rerun',
    os_cols=True,
    sub=('รอบ Regression <b>🪟 Windows จ 5 ต.ค.</b> · <b>🍎 Mac อ 6 ต.ค. 2569</b> — สโคปเดียวกัน '
         'บันทึกผลแยกคอลัมน์ Mac/Windows ในรายงานเดียว · '
         f"จุดที่เคย FAIL {_N['rrfail']} + flow หลัก P0 {_N['rrcore']} + ฟีเจอร์ ก.ย. {_N['rrnew']} = {sum(_N.values())} เคส"),
    groups_label='3 ก้อน (เคย FAIL · flow หลัก · ฟีเจอร์ ก.ย.)',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — <b>🪟 Windows จ 5 ต.ค. · 🍎 Mac อ 6 ต.ค.</b> สโคปเดียวกัน บันทึกผลแยกคอลัมน์ Mac/Win ในรายงานเดียว'
          f"<br>📦 <b>3 ก้อน:</b> ❌ จุดที่เคย FAIL {_N['rrfail']} เคส (union ผลรอบก่อนจากรายงาน windows + mac · แต่ละเคสมีบรรทัด \"ผลรอบก่อน (Win/Mac)\" ใต้ Expected) · "
          f"🧭 flow หลัก P0 {_N['rrcore']} เคส · 🆕 ฟีเจอร์ ก.ย. {_N['rrnew']} เคส (ตอบแชทอัตโนมัติ LLM Epic 22 + คีย์เวิร์ดตอบกลับ Epic 23 · P0+P1)"
          '<br>✂️ <b>วิธีคัด flow หลัก:</b> P0 ทั้งหมดของรายงาน MVP1+2 มีเกินงบ จึงคัดเฉพาะ feature หลักตามแผน — '
          'login (MVP-1 E1) · สร้าง/รันรีรัน (MVP-1 E4 + ขั้นที่ 8 เริ่มไลฟ์) · playlist (ขั้นที่ 2/5/10) · จอ/overlay (ขั้นที่ 3) — เคสที่ซ้ำก้อนเคย FAIL ไม่นับซ้ำ'
          '<br>⚠️ <b>ฟีเจอร์ ก.ย. ที่ไม่มีเคส:</b> ตั้งเวลาอัตโนมัติ และ แบนเนอร์วิ่ง — ไม่พบเคสในรายงาน/โมดูลใดของ takra-rerun จึงไม่อยู่ในรอบนี้ (ไม่แต่งเคสเอง)'
          '<br>📝 Test Steps เขียนจากรายงานฐาน Windows — รอบ Mac ให้เดินขั้นตอนเดียวกันบนเครื่อง Mac แล้วบันทึกผลที่คอลัมน์ 🍎'
          '<br>📎 เคสคัดจากรายงานหลัก MVP1+2 (<code>projects/takra-rerun/2026/07/reports/…-windows.html</code> / <code>…-mac.html</code>) · '
          'แก้เคสที่ <code>tools/build/reg-oct-sources/regrerun.json</code> แล้ว build ใหม่ · '
          'แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-rerun · 🪟 จ 5 ต.ค. / 🍎 อ 6 ต.ค.',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]
