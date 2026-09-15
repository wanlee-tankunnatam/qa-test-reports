#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ takra-radar (Trendora) — เว็บ trend radar สำหรับนักทำ affiliate ไทย · ชุดแรก (ครบ 8 Epic)

ข้อมูลเคสอยู่ที่ tools/build/takra-radar-sources/radar_*.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
build:  python3 tools/build/build_hub_report.py radar

ที่มา: repo /Users/ice/Documents/rf/takra-radar (branch develop @ 2026-09-13 ตรง origin) · Jira TKRD
· สเปกถูกถอดจาก tree (2026-08-18) — อ่านผ่าน `git show ac885d7:_bmad-output/planning-artifacts/epics.md` (8 Epics) + prd.md
· คำ UI ฝังไทยในโค้ด apps/web/src (React SPA · ไม่มี i18n) + packages/shared (Thai message catalogs)
· ⚠️ แคตตาล็อกสินค้า `product` ว่างทั้ง prod/uat (ท่อ CSV ปิด · กำลังย้าย ClickHouse · TKRD-161) —
  เคสที่ต้องมีข้อมูลสินค้าใส่ note ให้ลง BLOCKED จนกว่าจะมีข้อมูล
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-radar-sources'

META = dict(
    out_rel='projects/takra-radar/2026/09/reports/takra-radar-mvp1-ui-test-cases-table.html',
    title='[MVP1] TAKRA Radar (Trendora) — UI Manual Test Cases',
    emoji='📡', uid_start=8501, download='takra-radar-mvp1-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub='เทส UI ด้วยมืออย่างเดียว · เว็บ Trendora (takra-radar) แยกสองระบบ: 👤 ลูกค้า (A–H) · 🛠️ แอดมิน (ADM) · Target: <b>UAT</b> https://uat.trendora.watch',
    groups_label='2 ระบบ: ลูกค้า (A–H) + แอดมิน (ADM)',
    note=('🖥️ <b>Test target:</b> เว็บ <b>Trendora (takra-radar)</b> รุ่น UAT ที่ <b>uat.trendora.watch</b> (React SPA ภาษาไทย) · <b>แยกสองระบบ:</b> 👤 โซนลูกค้า (กลุ่ม A–H) · 🛠️ โซนแอดมิน (กลุ่ม ADM ท้ายตาราง — ใช้บัญชี admin) · '
          'บัญชีที่ต้องเตรียม: ผู้ใช้เปิดสิทธิ์แล้ว · ผู้ใช้ใหม่ยังไม่เปิดสิทธิ์ · ผู้ใช้เกิน cap (read-only) · admin · อีเมลใหม่<br>'
          '📎 <b>ที่มาของเคส:</b> สเปก BMad ถูกถอดจาก repo (2026-08-18) — อ่านจาก <code>git show ac885d7:_bmad-output/planning-artifacts/epics.md</code> (Epic 1–8) + <code>prd.md</code> · '
          'คำ UI ลอกจากโค้ดจริง <code>apps/web/src</code> + <code>packages/shared</code> (origin/develop 2026-09-13) — คัดเฉพาะข้อที่คนกดเองแล้วเห็นผลบนหน้าจอได้ (Epic 1 = ท่อข้อมูล backend ไม่มีเคส UI)<br>'
          '🔴 <b>ข้อจำกัดใหญ่ตอนนี้ (TKRD-161):</b> ตาราง <code>product</code> ว่างทั้ง prod และ uat — หน้าค้นหาคืนผลว่างทุกคำค้น "และนั่นถูกต้อง" (ท่อ CSV ปิด · แคตตาล็อกกำลังย้ายไป ClickHouse) → '
          'เคสที่ต้องมีข้อมูลสินค้า (ค้นหาเจอ · ติดตาม · สร้างลิงก์ · เช็คจอ) มี note กำกับ ให้ลงผล <b>BLOCKED</b> จนกว่าข้อมูลจะมา · เช็คสถานะแหล่งข้อมูลได้ที่ <code>GET /api/v1/source-status</code> (ไม่ต้อง login)<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data'),
    footer='UI only (manual) · Trendora (takra-radar) Web UAT · Jira TKRD',
)

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงานอื่นใน repo)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role/สิทธิ์ ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

# uid คงที่ต่อเคส — สร้างครั้งแรกจากไฟล์ที่เผยแพร่ 2026-09-15 · เพิ่มเคสใหม่ให้เติม id ลงไฟล์นี้ด้วย (builder จะพิมพ์เลขให้)
UID_MAP = json.loads((SRC / 'uid_map.json').read_text(encoding='utf-8'))

_ORDER = ['rda', 'rdb', 'rdc', 'rdd', 'rde', 'rdf', 'rdg', 'rdh']
_FILES = ['radar_ab.json', 'radar_cd.json', 'radar_ef.json', 'radar_gh.json']

_groups = {}
for _fn in _FILES:
    for _g in json.loads((SRC / _fn).read_text(encoding='utf-8'))['groups']:
        _groups[_g['key']] = _g

# ── แยกสองระบบ: โซนลูกค้า (A–H) · โซนแอดมิน (ADM) — ย้ายเคสที่ต้องใช้บัญชี admin/เรื่องโซนผู้ดูแลไปกลุ่มท้าย ──
_ADMIN_IDS = {'RD-A.10', 'RD-B.5', 'RD-G.14', 'RD-G.15', 'RD-G.16', 'RD-G.18', 'RD-G.19', 'RD-H.15'}
_admin_feats = {}
for _k, _g in _groups.items():
    for _f in _g['feats']:
        _moved = [c for c in _f['cases'] if c['id'] in _ADMIN_IDS]
        if _moved:
            _f['cases'] = [c for c in _f['cases'] if c['id'] not in _ADMIN_IDS]
            _admin_feats.setdefault(_f['featkey'], dict(featkey='adm-' + _f['featkey'], title=_f['title'], cases=[]))['cases'].extend(_moved)
    _g['feats'] = [f for f in _g['feats'] if f['cases']]

EPICS = []
for _k in _ORDER:
    if _k in _groups and _groups[_k]['feats']:
        _g = _groups[_k]
        _g.setdefault('emoji', _g['chip'].split()[0])
        _g['title'] = '👤 ลูกค้า · ' + _g['title']
        EPICS.append(_g)

if _admin_feats:
    EPICS.append(dict(
        key='rdadm', chip='🛠️ RD·ADM', emoji='🛠️',
        title='🛠️ แอดมิน · โซนผู้ดูแลระบบ — เข้าโซน/กันคนนอก · ตรวจสลิป · สิทธิ์ผู้ใช้ · ตั้งค่าระบบ · โปรโม (Epic 7 Story 7.3/7.4/7.6 · Epic 8 Story 8.3)',
        feats=list(_admin_feats.values()),
    ))

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted(set(i for i in _ids if _ids.count(i) > 1))}'
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
