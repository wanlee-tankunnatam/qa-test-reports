#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ takra-ai — 8 ใบงาน Jira ที่แจ้งเข้ามา 22 ก.ย. 2569 (TAKRA-1223..1230)

ข้อมูลเคสอยู่ที่ tools/build/takra-ai-tickets-1223-sources/cases.json (แก้ที่นั่นแล้ว build ใหม่)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `aitickets1223`)

มีเคสเฉพาะใบที่มีหน้าจอให้ทดสอบ: 1224 · 1225 · 1229 (มีโค้ดแล้ว) + 1227 (AC ครบ แต่ยังไม่มีโค้ด → ui=False)
ใบที่ไม่มีเคส (1223 · 1226 · 1228 · 1230) อธิบายเหตุผลไว้ใน META['note']
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-ai-tickets-1223-sources'

META = dict(
    out_rel='projects/takra-ai/2026/09/reports/takra-ai-tickets-1223-1230-ui-test-cases-table.html',
    title='TAKRA AI — ใบงาน 1223–1230 (1224 · 1225 · 1227 · 1229) UI Manual Test Cases',
    emoji='🎙️', uid_start=12301,
    download='takra-ai-tickets-1223-1230-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='เทส UI ด้วยมืออย่างเดียว · ใบงานที่แจ้งเข้ามา 22 ก.ย. 2569: <b>TAKRA-1223 – 1230</b> · Target: <b>TAKRA AI Web (UAT)</b> · login ด้วยบัญชี UAT',
    groups_label='4 กลุ่ม (1 กลุ่ม = 1 ใบงาน) · อีก 4 ใบไม่มีหน้าจอให้เทส (ดูหมายเหตุ)',
    note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA AI</b> รุ่น UAT · ใช้ Chrome บนเดสก์ท็อป · บัญชี UAT ที่ต้องเตรียม: เจ้าของ workspace ที่ผูกบัญชี TikTok สำหรับส่งตรงไว้แล้ว · มีเสียง Google ในคลังเสียง · มีสินค้าและสคริปต์ที่อนุมัติแล้ว<br>'
          '📎 <b>ที่มาของเคส:</b> Jira ทั้ง 8 ใบ + คอมเมนต์ของ dev/PO ในใบ · commit จริงบน <code>origin/develop</code> @ <code>48e17aa0</code> (23 ก.ย. 2569) · story <code>_bmad-output/implementation-artifacts/takra-1229-control-room-on-air-preview.md</code> · UI จริงใน <code>apps/web/src</code> · คำ UI ลอกจาก <code>apps/web/src/i18n/locales/th/*.ts</code><br>'
          '🚦 <b>สถานะโค้ด ณ 23 ก.ย. 2569:</b> <b>1224</b> และ <b>1229</b> ขึ้น <code>uat</code> แล้ว → เทสได้เลย · <b>1225</b> merge เข้า <code>develop</code> แล้วแต่ยังไม่ขึ้น <code>uat</code> → รอ deploy ก่อน · <b>1227</b> ยังไม่มีโค้ด → เคสเขียนตาม AC ไว้ล่วงหน้า (ติดป้าย ⛔)<br>'
          '🚫 <b>ใบที่ไม่มีเคสในรายงานนี้:</b> '
          '<b>TAKRA-1223</b> เสียงกระดิ่งแจ้งเตือน — ยังไม่ groom · คำถามหลักยังไม่ได้เคาะ (ดังทุกประเภทไหม · ค่าเริ่มต้น · เงียบระหว่างไลฟ์ไหม) และยังไม่มีโค้ด ⇒ เขียน Expected ไม่ได้โดยไม่เดา · '
          '<b>TAKRA-1226</b> ติดตั้ง takra-live บนเครื่อง remote — งาน infra ไม่มีหน้าจอ · '
          '<b>TAKRA-1228</b> จัดหมวดคำเสี่ยงใหม่ — ยังไม่มีรายการหมวดใหม่และตาราง mapping ยังไม่เคาะ และยังไม่มีโค้ด · '
          '<b>TAKRA-1230</b> เสียงอีกคนพูดแทรก — เป็น spike ผลลัพธ์คือเอกสาร ห้าม implement จากใบนี้ ⇒ จะเพิ่มเคสเมื่อใบเหล่านี้มี AC/หน้าจอ<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data'),
    noui_note=('⛔ <b>ยังไม่มีหน้าจอ</b> ณ origin/develop 48e17aa0 (23 ก.ย. 2569) — เคสเขียนตาม AC ใน TAKRA-1227 ไว้ล่วงหน้า '
               'คำบนการ์ด/หน้ารายละเอียดยังไม่มีใน i18n อาจต่างจากของจริงเมื่อ dev ส่งมอบ · ถ้ายังไม่มีให้บันทึกเป็น <b>BLOCKED</b>'),
    noui_badge='⛔ ยังไม่มีหน้าจอ',
    footer='UI only (manual) · TAKRA AI Web UAT · ใบงาน TAKRA-1223–1230',
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

_ORDER = ['t1224', 't1225', 't1229', 't1227']

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
