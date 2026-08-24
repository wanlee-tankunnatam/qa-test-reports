#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ takra-ai — เจาะ 6 ใบงาน Jira ที่ผู้ใช้ระบุ (TAKRA-412/413/416/327/767/755)

ข้อมูลเคสอยู่ที่ tools/build/takra-ai-tickets-sources/ai_tickets_*.json (แก้ที่นั่นแล้ว build ใหม่)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `aitickets`)

คนละไฟล์ปลายทางกับรายงาน MVP1+2 รวม ⇒ store-data แยกกัน สถานะผลเทสเดิมไม่ถูกแตะ
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-ai-tickets-sources'

META = dict(
    out_rel='projects/takra-ai/2026/08/reports/takra-ai-tickets-412-413-416-327-767-755-ui-test-cases-table.html',
    title='[MVP2] TAKRA AI — 6 ใบงาน (412 · 413 · 416 · 327 · 767 · 755) UI Manual Test Cases',
    emoji='🎥', uid_start=7601,
    download='takra-ai-tickets-412-413-416-327-767-755-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='เทส UI ด้วยมืออย่างเดียว · เจาะ 6 ใบงาน: <b>TAKRA-412 · 413 · 416 · 327 · 767 · 755</b> · Target: <b>TAKRA AI Web (UAT)</b> · login ด้วยบัญชี UAT',
    groups_label='6 กลุ่ม (1 กลุ่ม = 1 ใบงาน) + E2E',
    note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA AI</b> รุ่น UAT · บัญชี UAT ที่ต้องเตรียม: เจ้าของ workspace · สมาชิกที่ไม่ใช่เจ้าของ · บัญชีที่เข้าห้องคุมไลฟ์ได้ (operator) · เจ้าหน้าที่แพลตฟอร์ม · workspace ใหม่ที่ยังไม่มีข้อมูล<br>'
          '📎 <b>ที่มาของเคส:</b> commit จริงของทั้ง 6 ใบบน <code>origin/develop</code> + <code>_bmad-output/planning-artifacts/epics-mvp2.md</code> + <code>_bmad-output/test-artifacts/case/notifications-delivery/ui.md</code> + UI จริงบน <code>apps/web/src</code> · คำ UI ลอกจาก <code>apps/web/src/i18n/locales/th/*.ts</code><br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data<br>'
          '🎫 <b>ใบงานในรายงานนี้:</b> <b>TAKRA-412</b> Studio โคลนอวาตาร์ในตัว + ผูก persona เข้าไลฟ์จริง · <b>TAKRA-413</b> ตั้งเป้ารายได้/ออเดอร์ต่อรอบ + โชว์ใน Recap · <b>TAKRA-416</b> แจ้งเตือนทางอีเมล (SES) + กระดิ่งจริง · <b>TAKRA-327</b> ฟอร์มสินค้า/สคริปต์แสดง error รายช่อง · <b>TAKRA-767</b> ลิงก์ยกเลิกแจ้งเตือนของ workspace ที่ถูกลบ · <b>TAKRA-755</b> เส้นลบ 90 วัน + ข้อจำกัด DSAR<br>'
          '⚠️ เคสที่ติดป้าย ⛔ ไม่พบใน UI (อีเมลจริงถึงกล่องจดหมาย · การลบอัตโนมัติ 90 วัน · DSAR รายบุคคล) ให้ลงผล <b>BLOCKED</b> ไม่ใช่ FAIL — จุดตรวจยังไม่มีบนหน้าจอ'),
    footer='UI only (manual) · TAKRA AI Web UAT · 6 ใบงาน MVP-2',
)

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงาน hub/rerun)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

_ORDER = ['t412', 't413', 't416', 't327', 't767', 't755', 'te2e']
_FILES = ['ai_tickets_a.json', 'ai_tickets_b.json']

_groups = {}
for _fn in _FILES:
    _d = json.loads((SRC / _fn).read_text(encoding='utf-8'))
    for _g in _d['groups']:
        assert _g['key'] not in _groups, f'duplicate group key: {_g["key"]}'
        _groups[_g['key']] = _g

assert set(_groups) == set(_ORDER), f'group mismatch: {sorted(set(_groups) ^ set(_ORDER))}'

EPICS = []
for _k in _ORDER:
    _g = _groups[_k]
    _g.setdefault('emoji', _g['chip'].split()[0])
    EPICS.append(_g)

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
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
