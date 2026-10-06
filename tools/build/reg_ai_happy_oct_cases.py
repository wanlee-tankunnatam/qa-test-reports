#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-ai (Live) · รายการที่ 1: MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4) + avatar/voice self-service 10 เคส (เพิ่ม 5 ต.ค.)

ข้อมูลเคสอยู่ที่ tools/build/reg-oct-sources/regai1.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
คัดจากรายงานรวม MVP1+2: projects/takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html
(เฉพาะแถว data-mvp="mvp1" · happy path ทั้งหมด · จัดกลุ่มตามขั้นที่ 1–6 + Full E2E เดิม)
build: python3 tools/build/build_hub_report.py regai1"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'reg-oct-sources'

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงานอื่นใน repo — รอบนี้มีแต่ happy)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role/สิทธิ์ ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

_DATA = json.loads((SRC / 'regai1.json').read_text(encoding='utf-8'))
EPICS = _DATA['epics']
# uid ตรึงต่อเคส (ตั้ง 5 ต.ค. ตอนแทรกเคส avatar/voice self-service) — เพิ่มเคสกลางไฟล์ได้โดยผลเทสเดิมไม่เลื่อน
# เคสใหม่: build จะพิมพ์ uid ที่แจกให้ → เพิ่มลง uid_map ใน regai1.json ด้วย
UID_MAP = _DATA.get('uid_map', {})

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression MVP-1 Happy Path',
    emoji='🎥', uid_start=13001,
    download='takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4) + avatar/voice self-service 10 เคส (เพิ่ม 5 ต.ค.) · ขั้นที่ 1 เข้าระบบ → ขั้นที่ 6 AI + Full E2E · Target: <b>UAT</b> https://uat-live.takra.ai',
    groups_label='ตามขั้น MVP-1: ขั้นที่ 1–6 + Full E2E',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — takra-ai (Live) รายการที่ 1: <b>MVP-1 happy path ทั้งเส้น 141 เคส</b> (UI 137 + E2E 4) '
          'เดินตามขั้นที่ 1 เข้าระบบ → ขั้นที่ 6 AI ช่วยเขียน Script แล้วปิดท้ายด้วย Full E2E ครบลูป'
          '<br>📎 เคสคัดจากรายงานรวม MVP1+2 (เฉพาะฝั่ง MVP-1 · happy path) · ผลรอบนี้บันทึกแยกจากรายงานชุดหลัก · '
          'แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · MVP-1 happy path',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]

# ── รวมรายการที่ 2 (จุดเคย FAIL + ใบงาน ก.ย. + tool-calling) เข้ารายงานนี้ — สั่ง 2026-10-06 ให้เหลือลิงก์เดียว ──
# ต่อท้ายเสมอ · uid ของก้อนนี้ตรึงไว้ที่ค่าเดิมจากรายงาน fail-features (tc-13501–13665) ใน uid_map ของ regai1.json
# id ในก้อน "เคย FAIL" ที่ซ้ำกับเคส happy ด้านบน (23 เคส) เติม "-RF" (re-test FAIL) ให้ id/uid ไม่ชนกันในรายงานเดียว
import reg_ai_failfeat_oct_cases as _ff

for _k, _v in _ff.KINDS.items():
    KINDS.setdefault(_k, _v)
_HAPPY_IDS = {c['id'] for e in EPICS for f in e['feats'] for c in f['cases']}
_N_HAPPY = len(_HAPPY_IDS)
for _e in _ff.EPICS:
    EPICS.append(dict(_e, feats=[dict(_f, cases=[dict(_c, id=_c['id'] + '-RF') if _c['id'] in _HAPPY_IDS else _c
                                                 for _c in _f['cases']]) for _f in _e['feats']]))
_N_FF = sum(len(f['cases']) for e in _ff.EPICS for f in e['feats'])

# ── ก้อนที่ 3: 🆕 UI/ฟีเจอร์ที่เปลี่ยน/เพิ่มบน UAT (ตรวจ 6 ต.ค.) — ต่อท้ายเสมอ · ไม่แก้เคสเดิม ──
# uid ตรึงใน uid_map ของ regai1.json ตั้งแต่ tc-13666 · เคสเดิมที่ถูกแทนยังอยู่ครบ (ลง SKIP ที่เคสเดิมถ้าทำบน UI ไม่ได้แล้ว)
import ai_reg_oct_new_cases as _new

for _k, _v in _new.KINDS.items():
    KINDS.setdefault(_k, _v)
EPICS.append(_new.EPIC)
_N_NEW = sum(len(f['cases']) for f in _new.EPIC['feats'])
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), 'duplicate ids หลังรวม'
assert all(i in UID_MAP for i in _ids), f'uid ยังไม่ตรึง: {[i for i in _ids if i not in UID_MAP]}'

META.update(
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression (Happy Path + จุดเคย FAIL + ฟีเจอร์ ก.ย.)',
    sub=('รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · รายงานเดียวรวมทุกเคสของ takra-ai (Live) · '
         f'MVP-1 happy path + avatar/voice self-service {_N_HAPPY} เคส + จุดเคย FAIL · ใบงาน TAKRA-1223–1230 · '
         f'tool-calling auto-reply {_N_FF} เคส + 🆕 อัปเดตตาม UAT 6 ต.ค. {_N_NEW} เคส = {_N_HAPPY + _N_FF + _N_NEW} เคส · '
         'Target: <b>UAT</b> https://uat-live.takra.ai'),
    groups_label='ขั้นที่ 1–6 + Full E2E · ❌ เคย FAIL · ใบงาน 1223–1230 · tool-calling (ARS · SRF · RPL · RSK · COM · RCP) · 🆕 อัปเดต UAT 6 ต.ค.',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — takra-ai (Live) <b>รายงานเดียว</b> (รวม 6 ต.ค.): '
          f'① <b>MVP-1 happy path ทั้งเส้น</b> + avatar/voice self-service ({_N_HAPPY} เคส) เดินตามขั้นที่ 1 → ขั้นที่ 6 แล้วปิดท้ายด้วย Full E2E · '
          f'② <b>จุดเคย FAIL + ฟีเจอร์ ก.ย.</b> ({_N_FF} เคส · เดิมอยู่รายงาน fail-features) — ก้อน FAIL re-test เฉพาะใบที่ dev ปิดแล้ว '
          'ใบที่ยังไม่ปิดให้ลง <b>SKIP</b> พร้อมเหตุผล · ใบงาน TAKRA-1223–1230 และ tool-calling รันทั้งชุด · '
          f'③ <b>🆕 อัปเดตตาม UAT 6 ต.ค.</b> ({_N_NEW} เคส · ต่อท้าย) — ตรวจโค้ดทั้งโปรเจกต์ (origin/uat 5e79e582 = develop) ทุกหน้าเทียบทุกเคส: UI/ฟีเจอร์ที่เปลี่ยน → เคสแทน · ฟีเจอร์ที่ยังไม่มีเคส → เคสใหม่ (เฉพาะ P0/P1) '
          'เขียนเป็นเคสใหม่ <b>ไม่แก้เคสเดิม</b> · ที่มาของแต่ละเคสบอกว่า "แทนเคสเดิม" ตัวไหน — เคสเดิมที่ทำบน UI ไม่ได้แล้วให้ลง <b>SKIP</b>'
          '<br>🆔 เคสในก้อน "เคย FAIL" ที่ id ซ้ำกับเคส happy ด้านบนเติม <code>-RF</code> ท้าย id (re-test FAIL) — เนื้อหาเป็นฉบับของก้อน FAIL'
          '<br>📎 เคสคัดจาก: รายงานรวม MVP1+2 (<code>regai1.json</code> · <code>regai2_fails.json</code>) · '
          '<code>ai_tickets_1223_cases.py</code> · <code>ai_autoreply_cases.py</code> · แผนรวม: '
          '<a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    noui_note=_ff.META['noui_note'], noui_badge=_ff.META['noui_badge'],
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · Happy Path + จุดเคย FAIL + ฟีเจอร์ ก.ย.',
)
