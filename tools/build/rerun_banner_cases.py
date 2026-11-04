# -*- coding: utf-8 -*-
"""TAKRA Rerun — แบนเนอร์โปรโมชันจาก TAKRA Hub (TAK-836) · UI Manual Test Cases

สั่ง 2026-11-04: ทำ test case เรื่องแบนเนอร์ของ live (takra-ai) และ rerun — ไฟล์นี้เป็นฝั่ง rerun
(ฝั่ง live อยู่ในรายงาน "UI ใหม่ แบ่งตามเมนู" เมนู "แดชบอร์ด" ชุด TC-DASH-H.*)
- โค้ด: takra-rerun origin/develop @ 819183d0 (4 พ.ย. 2569) · ฟีเจอร์อยู่ใน uat แล้ว · web/src/features/promo/*
- คำบนจอ = ภาษาไทยที่ฝังใน web/src/** (ไม่มี i18n)
- ข้อมูลเคสอยู่ที่ tools/build/takra-rerun-banner-sources/cases.json · uid ตรึงด้วย uid_map.json (22501–)
- rerun ต้องแยก Status เป็น Mac / Windows เสมอ (os_cols=True)
build: python3 tools/build/build_hub_report.py rerunbanner
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-rerun-banner-sources'

META = dict(
    out_rel='projects/takra-rerun/2026/11/reports/takra-rerun-hub-banner-ui-test-cases-table.html',
    title='TAKRA Rerun — แบนเนอร์โปรโมชันจาก TAKRA Hub · UI Manual Test Cases',
    emoji='📢', uid_start=22501, os_cols=True,
    download='takra-rerun-hub-banner-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=rerun',
    sub=('เทส UI ด้วยมือ · แอป TAKRA Rerun · แถบโปรโมชันบนหน้า "บัญชีไลฟ์" + หน้า "โปรโมชั่น / อะไรใหม่" (TAK-836) · '
         'โค้ด <b>develop @ 819183d0</b> (4 พ.ย. 2569) · เฉพาะ P0 + P1 · Target: แอป TAKRA Rerun (รุ่น UAT)'),
    groups_label='',
    note=('🖥️ <b>Test target:</b> แอป <b>TAKRA Rerun</b> รุ่น UAT · บันทึกผลแยก 🍎 Mac / 🪟 Windows<br>'
          '📢 <b>ฟีเจอร์:</b> แบนเนอร์โปรโมชันที่ทีม Hub ตั้งไว้ใน TAKRA Hub แสดงในแอป Rerun '
          '(<a href="https://kitdi.atlassian.net/browse/TAK-836" target="_blank">TAK-836</a> · PRD FR-A7 / INT-5)<br>'
          '🧪 <b>Test data:</b> เคสที่ต้องมี/ไม่มีแบนเนอร์ ให้ทีม Hub/แอดมินตั้งแบนเนอร์ใน TAKRA Hub (UAT) ให้ก่อน ไม่มีเคสไลฟ์จริง<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจากภาษาไทยในโค้ด <code>web/src/features/promo/*</code> · Expected ยึด PRD + spec/AC ของ TAK-836'),
    footer='UI only (manual) · TAKRA Rerun · แบนเนอร์โปรโมชันจาก Hub',
)

KINDS = {
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'เน็ตหลุด · ระบบภายนอกผิดปกติ · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · duplicate · ไม่ปนข้ามทีม/แพลตฟอร์ม'),
}


def _case(c):
    return dict(id=c['id'], title=c['title'], prio=c['prio'], kind=c['kind'], level=c.get('level') or 'ui', ui=True,
                pre=list(c.get('pre') or []), steps=list(c['steps']), data=list(c.get('data') or []),
                expected=list(c['expected']), src=c['src'], note=c.get('note') or None)


_menus = json.loads((SRC / 'cases.json').read_text(encoding='utf-8'))['menus']

EPICS = [dict(key=m['key'], chip=m['chip'], emoji=m['chip'].split(' ', 1)[0], title=m['title'], jira=m.get('jira'),
              feats=[dict(featkey=f['featkey'], title=f['title'], cases=[_case(c) for c in f['cases']]) for f in m['feats']])
         for m in _menus]
META['groups_label'] = f'{sum(len(e["feats"]) for e in EPICS)} กลุ่ม (A–{chr(64 + sum(len(e["feats"]) for e in EPICS))})'

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
