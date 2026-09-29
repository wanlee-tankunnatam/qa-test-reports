#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-ai (Live) รายการที่ 2: จุดที่เคย FAIL + ฟีเจอร์รอบ ก.ย.

ประกอบจาก 3 ก้อน (ตามลำดับ):
1. rgfail — เคสที่สถานะปัจจุบัน = FAIL ในรายงาน MVP1+2
   (snapshot จาก projects/takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html
    → tools/build/reg-oct-sources/regai2_fails.json · สถานะ ณ วันสร้าง 29 ก.ย. 2569)
2. ใบงาน ก.ย. TAKRA-1223–1230 — ทั้ง EPICS จาก ai_tickets_1223_cases.py (ไม่แก้เนื้อหา)
3. Tool-calling auto-reply (Epic 13) — ทั้ง EPICS จาก ai_autoreply_cases.py (ไม่แก้เนื้อหา)

build: python3 tools/build/build_hub_report.py regai2
"""
import json
import pathlib

import ai_tickets_1223_cases as _t1223
import ai_autoreply_cases as _autoreply

SRC = pathlib.Path(__file__).resolve().parent / 'reg-oct-sources' / 'regai2_fails.json'

# KINDS ชุดรวม 7 ค่า — merge จากโมดูลต้นทาง (ทั้งคู่ใช้กรอบเดียวกัน)
KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงาน hub/rerun)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}
KINDS = {**_t1223.KINDS, **_autoreply.KINDS, **KINDS}

# ── ก้อน 1: rgfail จาก JSON ──
_fail_groups = json.loads(SRC.read_text(encoding='utf-8'))['groups']
# note "ผลรอบก่อน: …" ต่อเคส — harness ไม่ render note รายเคส จึงผนวกเข้า src (โผล่ใต้ Expected)
for _g in _fail_groups:
    for _f in _g['feats']:
        for _c in _f['cases']:
            if _c.get('note'):
                _c['src'] = f"{_c['src']} · {_c['note']}"
                _c['note'] = None
for _g in _fail_groups:
    _g.setdefault('emoji', _g['chip'].split()[0])

# ── รวม 3 ก้อนตามลำดับ · กัน key/featkey ชนกัน ──
EPICS = []
_seen_keys, _seen_fk = set(), set()
for _src_epics, _prefix in ((_fail_groups, 'rg'), (_t1223.EPICS, 'rg1223'), (_autoreply.EPICS, 'rgar')):
    for _e in _src_epics:
        if _e['key'] in _seen_keys:                      # key กลุ่มซ้ำ → เติม prefix (ไม่แก้ของต้นทาง)
            _e = dict(_e, key=f"{_prefix}-{_e['key']}")
        _seen_keys.add(_e['key'])
        for _f in _e['feats']:
            assert _f['featkey'] not in _seen_fk, f"featkey ชน: {_f['featkey']}"
            _seen_fk.add(_f['featkey'])
        EPICS.append(_e)

_N_FAIL = sum(len(f['cases']) for f in _fail_groups[0]['feats'])
_N_1223 = sum(len(f['cases']) for e in _t1223.EPICS for f in e['feats'])
_N_AR = sum(len(f['cases']) for e in _autoreply.EPICS for f in e['feats'])

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-fail-features-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression จุดเคย FAIL + ฟีเจอร์ ก.ย.',
    emoji='🎥', uid_start=13501,
    download='takra-ai-regression-oct0509-fail-features-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub=('รอบ Regression <b>อ 6 ต.ค. 2569</b> · จุดที่เคย FAIL ในรายงาน MVP1+2 + ฟีเจอร์รอบ ก.ย. '
         '(ใบงาน TAKRA-1223–1230 · Tool-calling auto-reply) · Target: <b>TAKRA AI Web (UAT)</b>'),
    groups_label=(f'3 ก้อน · เคย FAIL {_N_FAIL} เคส · ใบงาน 1223–1230 {_N_1223} เคส · '
                  f'tool-calling {_N_AR} เคส = {_N_FAIL + _N_1223 + _N_AR} เคส'),
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569 (อ 6 ต.ค.)</b> — รายการที่ 2 ของ takra-ai (Live): '
          f'<b>❌ จุดที่เคย FAIL ในรายงาน MVP1+2 ({_N_FAIL} เคส · สถานะ ณ 29 ก.ย. 2569)</b> + '
          f'<b>ฟีเจอร์รอบ ก.ย.</b> — ใบงาน TAKRA-1223–1230 ({_N_1223} เคส) และ Tool-calling auto-reply Epic 13 ({_N_AR} เคส)'
          '<br>⚠️ <b>ก้อน FAIL:</b> re-test เฉพาะใบที่ dev ปิดแล้ว — ใบที่ยังไม่ปิดให้ลง <b>SKIP</b> พร้อมเหตุผลใน Actual · '
          'ผลรอบก่อนของแต่ละเคสดูจากรายงาน MVP1+2 · <b>ฟีเจอร์ ก.ย.:</b> รันทั้งชุด'
          '<br>📎 เคสคัดจาก: รายงาน MVP1+2 (<code>regai2_fails.json</code>) · <code>ai_tickets_1223_cases.py</code> · '
          '<code>ai_autoreply_cases.py</code> · แผนรวม: '
          '<a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'
          '<br>🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data'),
    noui_note=('⛔ <b>ยังไม่มีหน้าจอ</b> ณ วันเขียนเคส — เคสเขียนตาม AC/สเปกไว้ล่วงหน้า คำ UI อาจต่างจากของจริงเมื่อ dev ส่งมอบ · '
               'ถ้ายังไม่มีหน้าจอให้บันทึกเป็น <b>BLOCKED</b>'),
    noui_badge='⛔ ยังไม่มีหน้าจอ',
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · จุดเคย FAIL + ฟีเจอร์ ก.ย.',
)

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
_keys = [e['key'] for e in EPICS]
assert len(_keys) == len(set(_keys)), f'duplicate epic keys: {_keys}'
for _e in EPICS:
    for _f in _e['feats']:
        for _c in _f['cases']:
            assert _c['kind'] in KINDS, (_c['id'], _c['kind'])
            assert _c['prio'] in ('P0', 'P1', 'P2'), (_c['id'], _c['prio'])
            assert _c['steps'] and _c['expected'] and _c['src'], _c['id']
            _c.setdefault('pre', [])
            _c.setdefault('data', [])
            _c.setdefault('note', None)
            _c.setdefault('ui', True)
            _c.setdefault('level', 'ui')
