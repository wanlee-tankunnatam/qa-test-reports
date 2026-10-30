#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAKRA AI (Live) — UI ใหม่ (redesign TAKRA-1500 / TAKRA-1586) · UI Manual Test Cases แบ่งตามเมนู

สั่ง 2026-10-30: takra-ai อัปเดต UI → ทำ test case ใหม่ แบ่งตามเมนู · ไฟล์ใหม่ (regaimenu เดิมคงไว้ไม่แตะ) · ทุกเมนู P0+P1
- โค้ด: takra-ai origin/uat @ d20046bc (30 ต.ค. 2569) · apps/web/src · คำ UI จาก apps/web/src/i18n/locales/th/*.ts
- เมนูเรียงตามแถบซ้ายของแอปใหม่ (components/shell/app-shell.tsx · i18n th/shell.ts) แล้วต่อด้วยเมนูบัญชี
- ข้อมูลเคสอยู่ที่ tools/build/takra-ai-bymenu-sources/<CODE>.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
- uid ตรึงด้วย takra-ai-bymenu-sources/uid_map.json · เคสใหม่ได้ uid ต่อท้ายอัตโนมัติ (เขียนกลับลงไฟล์ตอน build)
- ไลฟ์จริง = ทดสอบด้วยมือเท่านั้น (note 🔴) · ไลฟ์ทุกครั้งใช้อวาตาร์ "Graham (พื้นหลังเขียว)" + ข้อความ "AI Live" หน้าสุด + สุ่มฉากหลัง
build: python3 tools/build/build_hub_report.py aimenu
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-ai-bymenu-sources'

# ลำดับไฟล์ = ลำดับเมนูบนแถบซ้าย → เครื่องมือ → เมนูบัญชี
_FILES = ['SHELL', 'DASH', 'DRAFT', 'STUDIO', 'STP', 'STB', 'MLR', 'MYLIVE', 'QAV', 'QAC', 'QAR', 'LIBP', 'LIBS', 'SCR', 'LIBW', 'SET', 'SETB']
# ลำดับเมนูในรายงาน (key จากไฟล์ JSON) — เมนูที่ไม่อยู่ในรายการนี้ต่อท้ายตามลำดับไฟล์
_ORDER = ['m-shell', 'm-dash', 'm-draft', 'm-studio', 'm-mylive', 'm-quality',
          'm-lib-people', 'm-lib-products', 'm-lib-scripts', 'm-lib-media',
          'm-lib-words', 'm-lib-readings', 'm-lib-talk', 'm-lib-scenes',
          'm-preflight', 'm-settings', 'm-staff']

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-new-ui-bymenu-ui-test-cases-table.html',
    title='TAKRA AI (Live) — UI ใหม่ · Test Cases แบ่งตามเมนู',
    emoji='🧭', uid_start=21001,
    download='takra-ai-new-ui-bymenu-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub=('เทส UI ด้วยมือ · เว็บ TAKRA AI Live <b>หน้าตาใหม่</b> (redesign TAKRA-1500 / TAKRA-1586) แบ่งตามเมนูของแถบซ้าย · '
         'โค้ด <b>origin/uat @ d20046bc</b> (30 ต.ค. 2569) · เฉพาะ P0 + P1 · Target: <b>UAT</b> https://uat-live.takra.ai'),
    groups_label='',   # เติมตอนโหลด
    note=('🧭 <b>เมนูใหม่:</b> ทั่วไป ("แดชบอร์ด" · "ร่างไลฟ์" · "ไลฟ์ของฉัน" · "คลัง" 7 แท็บ) · เครื่องมือ ("สร้างอวาตาร์" · "โคลนเสียง" · "เขียนสคริปต์ AI" · "เตรียมพร้อมก่อนไลฟ์") · '
          'เมนูบัญชี ("การตั้งค่า" · "งานตั้งต้น") · "ประวัติการทำงาน AI" เฉพาะทีมแพลตฟอร์ม<br>'
          '🔐 <b>เข้าระบบ:</b> ผ่านหน้า TAKRA Hub ด้วยบัญชี UAT เจ้าของ workspace (เคสสิทธิ์ใช้บัญชีบทบาทอื่นตามที่ระบุในเคส)<br>'
          '🔴 <b>ไลฟ์จริง = manual เท่านั้น:</b> ใช้อวาตาร์ "Graham (พื้นหลังเขียว)" เท่านั้น · มีข้อความ "AI Live" หน้าสุด · สุ่มฉากหลัง · '
          'ห้ามใช้บัญชี TikTok/ห้องไลฟ์เดียวกับรอบทดสอบอื่นพร้อมกัน · การเรนเดอร์อวาตาร์/ติดตั้งแอปเดสก์ท็อปอยู่ในรายงาน "แอปเดสก์ท็อป Takra Live (Windows)"<br>'
          '📎 <b>ที่มา:</b> คำ UI ลอกจาก <code>apps/web/src/i18n/locales/th/*.ts</code> (ยืนยันว่าใช้จริงในหน้าจอ) · Expected ยึด <code>epics.md</code> · <code>epics-mvp2.md</code> · <code>prd.md</code> และใบ Jira ที่โค้ดอ้าง<br>'
          '🗂️ <b>ชุดเดิม:</b> รายงานรอบ regression 5–9 ต.ค. แบบแบ่งตามเมนู (regaimenu) คงไว้พร้อมผลเทสเดิม — ไฟล์นี้เป็นชุดใหม่ตาม UI ปัจจุบัน'),
    footer='UI only (manual) · TAKRA AI Live · UI ใหม่ แบ่งตามเมนู · UAT',
)

KINDS = {
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}


def _case(c):
    return dict(id=c['id'], title=c['title'], prio=c['prio'], kind=c['kind'], level=c.get('level') or 'ui', ui=True,
                pre=list(c.get('pre') or []), steps=list(c['steps']), data=list(c.get('data') or []),
                expected=list(c['expected']), src=c['src'], note=c.get('note') or None)


_menus = {}
for _fn in _FILES:
    _p = SRC / f'{_fn}.json'
    if not _p.exists():
        continue
    for _m in json.loads(_p.read_text(encoding='utf-8'))['menus']:
        # เมนูเดียวกันแบ่งเขียนได้หลายไฟล์ — ต่อชุดฟีเจอร์ตามลำดับไฟล์ (ชื่อ/chip ใช้ของไฟล์แรก)
        if _m['key'] in _menus:
            _menus[_m['key']]['feats'] += _m['feats']
        else:
            _menus[_m['key']] = _m
_keys = [k for k in _ORDER if k in _menus] + [k for k in _menus if k not in _ORDER]

EPICS = [dict(key=k, chip=_menus[k]['chip'], emoji=_menus[k]['chip'].split(' ', 1)[0], title=_menus[k]['title'],
              jira=_menus[k].get('jira') or 'TAKRA-1586',
              feats=[dict(featkey=f['featkey'], title=f['title'], cases=[_case(c) for c in f['cases']])
                     for f in _menus[k]['feats']])
         for k in _keys]
META['groups_label'] = f'{len(EPICS)} เมนู · ' + ' · '.join(_menus[k]['chip'] for k in _keys)

_ALL = [c for e in EPICS for f in e['feats'] for c in f['cases']]
_ids = [c['id'] for c in _ALL]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
_fk = [f['featkey'] for e in EPICS for f in e['feats']]
assert len(_fk) == len(set(_fk)), f'duplicate featkeys: {sorted({i for i in _fk if _fk.count(i) > 1})}'
for _c in _ALL:
    assert _c['kind'] in KINDS and _c['prio'] in ('P0', 'P1'), (_c['id'], _c['kind'], _c['prio'])
    assert _c['steps'] and _c['expected'] and _c['src'], _c['id']
    assert _c['level'] in ('ui', 'e2e'), _c['id']

# uid ตรึง: id เดิมได้ uid เดิมเสมอ · id ใหม่ได้ uid ถัดจากตัวสูงสุด แล้วเขียน map กลับ
_map_p = SRC / 'uid_map.json'
UID_MAP = json.loads(_map_p.read_text(encoding='utf-8')) if _map_p.exists() else {}
_next = max(UID_MAP.values(), default=META['uid_start'] - 1) + 1
_new = [i for i in _ids if i not in UID_MAP]
for _i in _new:
    UID_MAP[_i] = _next
    _next += 1
if _new:
    _map_p.write_text(json.dumps(UID_MAP, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
