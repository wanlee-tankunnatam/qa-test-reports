#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ takra-ai — ใบงาน Jira ที่แจ้งเข้ามา 22 ก.ย. 2569 (TAKRA-1223..1230) · 1 ไฟล์ต่อ 1 ใบงาน

ข้อมูลเคสอยู่ที่ tools/build/takra-ai-tickets-1223-sources/cases.json (แก้ที่นั่นแล้ว build ใหม่)
build ทีละใบ: python3 tools/build/build_hub_report.py ai1224   (ai1223 … ai1230)
build_hub_report.py เรียก select('t1224') ก่อนอ่าน EPICS/META

1224 · 1225 · 1229 มีโค้ดแล้ว · 1227 · 1223 · 1226 · 1228 · 1230 ยังไม่มีหน้าจอ → เคสล่วงหน้า ui=False
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-ai-tickets-1223-sources'
PAGES = 'https://wanlee-tankunnatam.github.io/qa-test-reports/'

# ต่อใบ: slug ของไฟล์ · หัวข้อ · สถานะโค้ด ณ 23 ก.ย. 2569 · ที่มาเพิ่มเติม
TICKETS = {
    't1224': ('voice-style', 'อวตารพูดแบบมีอารมณ์ — น้ำเสียงใน Studio',
              'ขึ้น <code>uat</code> แล้ว → เทสได้เลย', ''),
    't1225': ('script-editor', 'หน้าสร้างสคริปต์ใช้งานง่ายขึ้น',
              'merge เข้า <code>develop</code> แล้วแต่ยังไม่ขึ้น <code>uat</code> → รอ deploy ก่อน', ''),
    't1229': ('on-air-preview', 'preview ภาพที่กำลังออกอากาศในห้องคุมไลฟ์',
              'ขึ้น <code>uat</code> แล้ว → เทสได้เลย',
              ' · story <code>_bmad-output/implementation-artifacts/takra-1229-control-room-on-air-preview.md</code>'),
    't1227': ('live-list', 'รายการไลฟ์แสดงช่องทาง / บัญชี / อวาตาร์',
              'ยังไม่มีโค้ด → เคสเขียนตาม AC ไว้ล่วงหน้า (ติดป้าย ⛔)', ''),
    't1223': ('notification-sound', 'เสียงกระดิ่งเมื่อมีการแจ้งเตือนใหม่ในไลฟ์',
              'ยังไม่ groom · ยังไม่มีโค้ด → เคสล่วงหน้า (⛔)', ''),
    't1226': ('remote-setup', 'Setup takra-live บนเครื่อง remote',
              'งาน infra ยังไม่ groom → เคส smoke ผ่านหน้าเว็บหลังติดตั้ง · เคสล่วงหน้า (⛔)', ''),
    't1228': ('risk-category', 'จัดหมวดหมู่คำเสี่ยงใหม่',
              'ยังไม่ groom · ยังไม่มีรายการหมวดใหม่และยังไม่มีโค้ด → เคส regression ก่อน/หลังย้ายหมวด · เคสล่วงหน้า (⛔)', ''),
    't1230': ('co-host-voice', 'เสียงอีกคนพูดแทรกในไลฟ์',
              'Spike ยังไม่มีฟีเจอร์ → เคสเกณฑ์ขั้นต่ำเมื่อแตกเป็นตั๋ว dev · เคสล่วงหน้า (⛔)', ''),
}


def out_rel(key):
    return f'projects/takra-ai/2026/09/reports/takra-ai-{key[1:]}-{TICKETS[key][0]}-ui-test-cases-table.html'


def _meta(key):
    n = key[1:]
    slug, topic, status, extra_src = TICKETS[key]
    return dict(
        out_rel=out_rel(key),
        title=f'TAKRA AI — TAKRA-{n} · {topic} UI Manual Test Cases',
        emoji=_groups[key]['chip'].split()[0], uid_start=12301,
        download=f'takra-ai-{n}-{slug}-ui-test-cases.html',
        back=PAGES + '?project=ai',
        sub=f'เทส UI ด้วยมืออย่างเดียว · ใบงาน <b>TAKRA-{n}</b> · {topic} · Target: <b>TAKRA AI Web (UAT)</b> · login ด้วยบัญชี UAT',
        groups_label=f'TAKRA-{n} · {sum(len(f["cases"]) for f in _groups[key]["feats"])} เคส',
        note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA AI</b> รุ่น UAT · ใช้ Chrome บนเดสก์ท็อป · บัญชี UAT ที่ต้องเตรียม: เจ้าของ workspace ที่ผูกบัญชี TikTok สำหรับส่งตรงไว้แล้ว · มีเสียง Google ในคลังเสียง · มีสินค้าและสคริปต์ที่อนุมัติแล้ว<br>'
              f'📎 <b>ที่มาของเคส:</b> Jira <b>TAKRA-{n}</b> + คอมเมนต์ของ dev/PO ในใบ · commit จริงบน <code>origin/develop</code> @ <code>48e17aa0</code> (23 ก.ย. 2569){extra_src} · UI จริงใน <code>apps/web/src</code> · คำ UI ลอกจาก <code>apps/web/src/i18n/locales/th/*.ts</code><br>'
              f'🚦 <b>สถานะโค้ด ณ 23 ก.ย. 2569:</b> {status}<br>'
              '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data'),
        noui_note=('⛔ <b>ยังไม่มีหน้าจอ</b> ณ origin/develop 48e17aa0 (23 ก.ย. 2569) — เคสเขียนตาม AC/ข้อเสนอในใบไว้ล่วงหน้า '
                   'คำของส่วนใหม่ยังไม่มีใน i18n อาจต่างจากของจริงเมื่อ dev ส่งมอบ · ถ้ายังไม่มีให้บันทึกเป็น <b>BLOCKED</b>'),
        noui_badge='⛔ ยังไม่มีหน้าจอ',
        footer=f'UI only (manual) · TAKRA AI Web UAT · ใบงาน TAKRA-{n}',
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

_ORDER = ['t1224', 't1225', 't1229', 't1227', 't1223', 't1226', 't1228', 't1230']

_groups = {g['key']: g for g in json.loads((SRC / 'cases.json').read_text(encoding='utf-8'))['groups']}
assert set(_groups) == set(_ORDER) == set(TICKETS), f'group mismatch: {sorted(set(_groups) ^ set(_ORDER))}'
for _g in _groups.values():
    _g.setdefault('emoji', _g['chip'].split()[0])

EPICS = [_groups[_k] for _k in _ORDER]   # ทุกใบ (ใช้ตรวจความถูกต้องด้านล่าง)
META = None


def select(key):
    """ให้ build_hub_report.py เลือกใบเดียว → EPICS/META ของไฟล์ใบนั้น"""
    global EPICS, META
    assert key in TICKETS, key
    EPICS = [_groups[key]]
    META = _meta(key)


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
