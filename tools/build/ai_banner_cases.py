# -*- coding: utf-8 -*-
"""TAKRA AI (Takra Live) — แบนเนอร์โปรโมชันจาก TAKRA Hub บนแดชบอร์ด · UI Manual Test Cases

สั่ง 2026-11-04: ทำ test case แบนเนอร์ของ live และ rerun · full loop เริ่มที่ Hub · happy path อย่างเดียว ·
ผู้ใช้สั่งให้แยกเป็นชีตใหม่ (ไม่ใส่ในรายงาน "UI ใหม่ แบ่งตามเมนู") — ฝั่ง rerun อยู่ที่ rerun_banner_cases.py
- โค้ด Live: takra-ai develop @ 60d0d782 · apps/web/src dashboard.tsx (PromoBanners · PromoTile) · แอปเดสก์ท็อป apps/desktop/src
- โค้ด Hub: takra-hub origin/develop · content-console.tsx (BannerForm · ItemRow)
- ข้อมูลเคสอยู่ที่ tools/build/takra-ai-banner-sources/cases.json · uid ตรึงด้วย uid_map.json (22601–)
build: python3 tools/build/build_hub_report.py aibanner
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-ai-banner-sources'

META = dict(
    out_rel='projects/takra-ai/2026/11/reports/takra-ai-hub-banner-ui-test-cases-table.html',
    title='TAKRA AI — แบนเนอร์โปรโมชันจาก TAKRA Hub บนแดชบอร์ด · UI Manual Test Cases',
    emoji='📢', uid_start=22601,
    download='takra-ai-hub-banner-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub=('เทส UI ด้วยมือ · full loop เริ่มที่ TAKRA Hub → แอปเดสก์ท็อป Takra Live หน้า "แดชบอร์ด" (TAKRA-1492 · TAKRA-1596) · '
         'happy path · โค้ด <b>develop @ 60d0d782</b> · เฉพาะ P0 + P1 · Target: Hub UAT + แอป Takra Live (Windows)'),
    groups_label='',
    note=('🖥️ <b>Test target:</b> TAKRA Hub UAT (https://uat-hub.takra.ai) + แอปเดสก์ท็อป <b>Takra Live</b> บน Windows<br>'
          '📢 <b>ฟีเจอร์:</b> แบนเนอร์ที่ตั้งใน Hub เมนู "เนื้อหาหน้าเว็บ" แท็บ "แบนเนอร์" แสดงบนหน้า "แดชบอร์ด" ของ Takra Live '
          '(<a href="https://kitdi.atlassian.net/browse/TAKRA-1492" target="_blank">TAKRA-1492</a> · '
          '<a href="https://kitdi.atlassian.net/browse/TAKRA-1596" target="_blank">TAKRA-1596</a>)<br>'
          '⏱️ Hub และแอปจำผลไว้อย่างละ 60 วินาที — หลังบันทึกใน Hub รอประมาณ 2 นาทีก่อนดูในแอป · ลบแบนเนอร์ QA-DASH-BN-… หลังทดสอบ<br>'
          '📎 <b>ที่มา:</b> คำบนจอ Live จาก i18n th + dashboard.tsx · คำบนจอ Hub จาก content-console.tsx · Expected ยึด AC ของ TAKRA-1492 + prd.md ของ Hub'),
    footer='UI only (manual) · TAKRA AI · แบนเนอร์โปรโมชันจาก Hub',
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
