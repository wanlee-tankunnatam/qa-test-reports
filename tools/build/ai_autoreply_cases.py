#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ takra-ai — Tool-calling auto-reply (Epic 13 · AI ตอบคอมเมนต์อัตโนมัติ)

ข้อมูลเคสอยู่ที่ tools/build/takra-ai-autoreply-sources/cases.json (แก้ที่นั่นแล้ว build ใหม่)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `aiautoreply`)

อ่าน UI จากสาขา feature/TAKRA-375 (ยังไม่ merge เข้า develop/uat ณ 23 ก.ย. 2569)
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-ai-autoreply-sources'

META = dict(
    out_rel='projects/takra-ai/2026/09/reports/takra-ai-tool-calling-auto-reply-ui-test-cases-table.html',
    title='TAKRA AI — Tool-calling auto-reply (Epic 13 · AI ตอบคอมเมนต์อัตโนมัติ) UI Manual Test Cases',
    emoji='🤖', uid_start=13001,
    download='takra-ai-tool-calling-auto-reply-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='เทส UI ด้วยมืออย่างเดียว · <b>Tool-calling auto-reply</b> (Epic 13 · FR73) · Target: <b>TAKRA AI Web (UAT)</b> · login ด้วยบัญชี UAT',
    groups_label='6 กลุ่ม · สวิตช์ · การ์ดสถานะ · ตอบคอมเมนต์ · คำเสี่ยง · ด่านการขาย · สรุปหลังไลฟ์',
    note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA AI</b> รุ่น UAT · บัญชีที่ต้องเตรียม: Owner และ Live Operator ของ workspace ทดสอบ · workspace อื่นสำหรับเคสข้าม workspace · '
          '<b>บัญชี TikTok ทดสอบของทีม</b> สำหรับพิมพ์คอมเมนต์ (ห้ามใช้บัญชีลูกค้า · Story 13.0 AC1)<br>'
          '📎 <b>ที่มาของเคส:</b> <code>_bmad-output/planning-artifacts/epics-mvp2.md</code> Epic 13 (Story 13.0–13.11) + <code>prd.md</code> FR73 · FR42 · FR43a-c · FR44 · '
          'แผนทดสอบของ dev <code>_bmad-output/TAKRA-375-ui-test-plan-S2.md</code> · UI จริงบนสาขา <code>feature/TAKRA-375</code> · คำ UI ลอกจาก <code>apps/web/src/i18n/locales/th/*.ts</code><br>'
          '🚦 <b>สถานะโค้ด ณ 23 ก.ย. 2569:</b> ทั้งหมดอยู่บนสาขา <code>feature/TAKRA-375</code> ยังไม่ merge เข้า <code>develop</code>/<code>uat</code> · '
          'เคสที่ต้องไลฟ์จริงต้องรอรอบไลฟ์พิสูจน์ (TAKRA-896 AC1) — ถ้ายังไม่เปิดให้บันทึก <b>BLOCKED</b><br>'
          '🚫 <b>สิ่งที่ไม่มีเคสโดยตั้งใจ:</b> tool-calling จริง / tool-trace (ตัดออกตามมติ TL-7 · Story 13.2) · การวัดเวลาตอบ (13.7 · 13.9 ไม่มีหน้าจอ) · log / prompt ฝั่งระบบ<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data'),
    footer='UI only (manual) · TAKRA AI Web UAT · Tool-calling auto-reply (Epic 13)',
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

_ORDER = ['ars', 'srf', 'rpl', 'rsk', 'com', 'rcp']

_groups = {g['key']: g for g in json.loads((SRC / 'cases.json').read_text(encoding='utf-8'))['groups']}
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
