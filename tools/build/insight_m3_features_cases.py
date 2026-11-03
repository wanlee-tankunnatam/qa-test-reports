# -*- coding: utf-8 -*-
"""TAKRA Insight — ฟีเจอร์ใหม่ (พ.ย. 2569) · UI Manual Test Cases แบ่งตามฟีเจอร์

สั่ง 2026-11-03: ทำ test case 5 ฟีเจอร์ — ไลฟ์ Shopee · วิเคราะห์คลิป · แจ้งเตือน Telegram เมื่อไลฟ์มีปัญหา ·
แจ้งเตือนเมื่อเสียงไลฟ์หายนานเกิน 20 วินาที · ระบบจับคำหยาบ คำต้องห้าม TikTok และการชวนลูกค้าออกนอก TikTok
- โค้ด: takra-insight origin/develop @ 74e035fc (2 พ.ย. 2569 18:11 · ล้ำ uat 6e3d872e 7 commit: TI-684 · TI-715)
- คำบนจอลอกจาก apps/desktop/desktop/src/renderer/src/i18n/th.js + ข้อความไทยใน renderer .jsx
- ข้อมูลเคสอยู่ที่ tools/build/takra-insight-m3-sources/<CODE>.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
- uid ตรึงด้วย takra-insight-m3-sources/uid_map.json · เคสใหม่ได้ uid ต่อท้ายอัตโนมัติ
- insight ต้องแยก Status เป็น Mac / Windows เสมอ (os_cols=True)
build: python3 tools/build/build_hub_report.py insightm3
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-insight-m3-sources'

_FILES = ['SHP', 'CLP', 'TG', 'AUD', 'WRD']

META = dict(
    out_rel='projects/takra-insight/2026/11/reports/takra-insight-new-features-nov-ui-test-cases-table.html',
    title='TAKRA Insight — ฟีเจอร์ใหม่ (Shopee · คลิป · Telegram · เสียงหาย · จับคำ) · UI Manual Test Cases',
    emoji='🆕', uid_start=22001, os_cols=True,
    download='takra-insight-new-features-nov-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=insight',
    sub=('เทส UI ด้วยมือ · แอปเดสก์ท็อป TAKRA Insight · 5 ฟีเจอร์ใหม่ · โค้ด <b>develop @ 74e035fc</b> (2 พ.ย. 2569) · '
         'เฉพาะ P0 + P1 · Target: แอปเดสก์ท็อป TAKRA Insight (บิลด์ UAT)'),
    groups_label='',   # เติมตอนโหลด
    note=('🖥️ <b>Test target:</b> แอปเดสก์ท็อป <b>TAKRA Insight</b> บิลด์ UAT · ทดสอบทั้ง 🍎 Mac และ 🪟 Windows (บันทึกผลแยกคอลัมน์)<br>'
          '🧩 <b>ฟีเจอร์:</b> ไลฟ์ Shopee (<a href="https://kitdi.atlassian.net/browse/TI-681" target="_blank">TI-681</a>) · '
          'วิเคราะห์คลิป TikTok/Facebook (<a href="https://kitdi.atlassian.net/browse/TI-668" target="_blank">TI-668</a>) · '
          'แจ้งเตือน Telegram เมื่อไลฟ์มีปัญหา (<a href="https://kitdi.atlassian.net/browse/TI-701" target="_blank">TI-701</a>) · '
          'เสียงไลฟ์หายเกิน 20 วินาที (<a href="https://kitdi.atlassian.net/browse/TI-699" target="_blank">TI-699</a>) · '
          'จับคำหยาบ/คำต้องห้าม/ชวนออกนอก TikTok (<a href="https://kitdi.atlassian.net/browse/TI-704" target="_blank">TI-704</a>)<br>'
          '🔴 <b>ไลฟ์จริง = ทดสอบด้วยมือ:</b> เคสที่ต้องเปิดดูไลฟ์ที่ออกอากาศจริง ห้ามใช้ห้องไลฟ์เดียวกับรอบทดสอบอื่นพร้อมกัน · '
          'เคสที่ต้องให้ไลฟ์มีปัญหา (เสียงหาย ภาพค้าง หลุด พูดคำทดสอบ) ใช้บัญชีทดสอบของ QA เปิดไลฟ์เอง<br>'
          '📨 <b>Telegram:</b> ใช้กลุ่มทดสอบของ QA + บอททดสอบเท่านั้น ห้ามใช้กลุ่มลูกค้า/กลุ่มทีมจริง<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจาก <code>apps/desktop/desktop/src/renderer/src/i18n/th.js</code> · Expected ยึด <code>prd.md</code> · '
          '<code>prd-m3.md</code> · story spec และ AC ในใบ Jira'),
    footer='UI only (manual) · TAKRA Insight desktop · ฟีเจอร์ใหม่ พ.ย. 2569',
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


_menus = []
for _fn in _FILES:
    _p = SRC / f'{_fn}.json'
    if _p.exists():
        _menus += json.loads(_p.read_text(encoding='utf-8'))['menus']

EPICS = [dict(key=m['key'], chip=m['chip'], emoji=m['chip'].split(' ', 1)[0], title=m['title'], jira=m.get('jira'),
              feats=[dict(featkey=f['featkey'], title=f['title'], cases=[_case(c) for c in f['cases']]) for f in m['feats']])
         for m in _menus]
META['groups_label'] = f'{len(EPICS)} ฟีเจอร์ · ' + ' · '.join(m['chip'] for m in _menus)

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

# ── บัญชีทดสอบ (UAT) — ดู insight_accounts.py ──
from insight_accounts import apply_accounts  # noqa: E402
apply_accounts(EPICS)
