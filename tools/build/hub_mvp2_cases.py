#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ TAKRA Hub — MVP-2 (Epic 1–8 ตาม docs/epics-mvp2.md + affiliate ฝั่ง Hub)

ข้อมูลเคสอยู่ที่ tools/build/takra-hub-mvp2-sources/hub_m2_*.json (ผลิต/แก้ที่นั่นแล้ว build ใหม่)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `mvp2`)
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-hub-mvp2-sources'

META = dict(
    out_rel='projects/takra-hub/2026/08/reports/takra-hub-mvp2-ui-test-cases-table.html',
    title='[MVP2] TAKRA Hub — MVP-2 UI Manual Test Cases',
    emoji='🏢', uid_start=7001, download='takra-hub-mvp2-ui-test-cases.html',
    sub='เทส UI ด้วยมืออย่างเดียว · MVP-2 (Epic 1–8 ตาม epics-mvp2.md + affiliate ฝั่ง Hub) · Target: <b>TAKRA Hub Web (UAT)</b> · login ด้วยบัญชี UAT',
    groups_label='11 กลุ่ม (A–H·L·X) + E2E',
    note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA Hub</b> รุ่น UAT (uat-hub.takra.ai · branch <code>develop</code>) · บัญชี UAT ที่ต้องเตรียม: ลูกค้า (เจ้าของทีม) · UAT-B (สมาชิกทีม) · พนักงาน role <b>cs</b> · <b>finance</b> · <b>marketing</b> · <b>legal</b> · admin (superuser) · อีเมลใหม่<br>'
          '📎 <b>ที่มาของเคส:</b> <code>docs/epics-mvp2.md</code> (Epic 1–8 · Story AC) + <code>docs/mvp2-addendum-payment-promotion-rbac.md</code> + UI จริงบน <code>apps/web/src</code> (origin/develop 2026-08-20) — คัดเฉพาะข้อที่คนกดเองแล้วเห็นผลบนหน้าจอได้<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data<br>'
          '⚠️ <b>สถานะ dev (2026-08-20):</b> Epic 1 RBAC + legal-admin + affiliate ฝั่ง Hub <b>ลง develop แล้ว</b> · QR/PromptPay (Epic 2) · Payment recovery (Epic 3) · Refund console (Epic 4) · Campaign console (Epic 6) <b>ยังไม่ build</b> · Coupon (Epic 5 · TKH-69) <b>เคย merge แล้วถูก revert #326</b> — เคสที่ติดป้าย ⛔ ไม่พบใน UI ให้ลงผล <b>BLOCKED</b> จนกว่า dev จะส่งมอบ แล้วค่อยกลับมาปรับคำ UI'),
    footer='UI only (manual) · TAKRA Hub Web UAT (branch develop) · MVP-2',
)

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงาน MVP-1)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

_ORDER = ['m2a', 'm2l', 'm2b', 'm2c', 'm2x', 'm2d', 'm2e', 'm2f', 'm2g', 'm2h']
_FILES = ['hub_m2_a.json', 'hub_m2_b.json', 'hub_m2_d.json', 'hub_m2_g.json']

_groups = {}
_e2e_cases = []
for _fn in _FILES:
    _d = json.loads((SRC / _fn).read_text(encoding='utf-8'))
    for _g in _d['groups']:
        if _g['key'].startswith('m2e2e'):
            for _f in _g['feats']:
                _e2e_cases.extend(_f['cases'])
        else:
            _groups[_g['key']] = _g

EPICS = []
for _k in _ORDER:
    if _k in _groups:
        _g = _groups[_k]
        _g.setdefault('emoji', _g['chip'].split()[0])
        EPICS.append(_g)

if _e2e_cases:
    _e2e_cases.sort(key=lambda c: c['id'])
    EPICS.append(dict(
        key='m2e2e', chip='🔄 E2E', emoji='🔄',
        title='🔄 MVP-2 · Full E2E Flow — วิ่งครบลูป (RBAC มอบสิทธิ์ · จ่ายเงิน QR)',
        feats=[dict(featkey='fullflow-mvp2', title='fullflow — ครบลูป MVP-2', cases=_e2e_cases)],
    ))

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {[i for i in _ids if _ids.count(i) > 1]}'
for _e in EPICS:
    for _f in _e['feats']:
        for _c in _f['cases']:
            assert _c['kind'] in KINDS, (_c['id'], _c['kind'])
            assert _c['prio'] in ('P0', 'P1', 'P2'), (_c['id'], _c['prio'])
            _c.setdefault('pre', [])
            _c.setdefault('data', [])
            _c.setdefault('note', None)
            _c.setdefault('ui', True)
            _c.setdefault('level', 'ui')
