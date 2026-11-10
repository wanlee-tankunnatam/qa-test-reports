# -*- coding: utf-8 -*-
"""TAKRA Insight — UI ใหม่ (re-design 5 พ.ย. 2569) · UI Manual Test Cases แบ่งตามหมวด

สั่ง 2026-11-10: สร้าง test case ตาม UI ใหม่ · ชีตแยก (ชีต "ฟีเจอร์ใหม่ พ.ย." มีผลครบแล้ว ไม่แก้) · P0 + P1
- โค้ด: takra-insight origin/uat @ 0d937314 (5 พ.ย. 2569) — PR #834 re-design (TI-700 · TI-713 · TI-714)
  + TI-717 แท็ก · TI-740 คลิป · TI-741 เสียงที่อัดไว้ · TI-719 อัดเสียงไลฟ์
- คำบนจอลอกจาก apps/desktop/desktop/src/renderer/src/i18n/th.js + ข้อความไทยใน renderer .jsx
- ข้อมูลเคสอยู่ที่ tools/build/takra-insight-ui-nov-sources/<CODE>.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
- uid ตรึงด้วย takra-insight-ui-nov-sources/uid_map.json (23101–) · เคสใหม่ได้ uid ต่อท้ายอัตโนมัติ
- insight ต้องแยก Status เป็น Mac / Windows เสมอ (os_cols=True)
build: python3 tools/build/build_hub_report.py insightui
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-insight-ui-nov-sources'

# 10 พ.ย. (รอบ 2) ผู้ใช้สั่ง "เอาที่เป็นจอร์นี่" → ชีตเป็น user journey 15 เคส (J-*.json)
# เคสย่อยรอบแรก (PAST/TAG/CLIP/SET/ALRT.json) คงไว้เฉพาะเคสที่มีผลใน store แล้ว (เช็กทุกครั้งที่ build)
_JOURNEYS = [
    ('m-jrn-clip', '🎬 วิเคราะห์คลิป', 'Journey วิเคราะห์คลิป TikTok / Facebook — วางลิงก์ถึงรายงาน · ลิงก์มีปัญหา · อัปโหลดเอง', 'TI-713',
     'jrn-clip', 'A · วิเคราะห์คลิปตั้งแต่วางลิงก์จนหาเจอในวิเคราะห์ย้อนหลัง', ['J-A', 'J-A2']),
    ('m-jrn-past', '📚 ย้อนดู + แท็ก', 'Journey ย้อนดูไลฟ์/คลิป และจัดระเบียบด้วยแท็ก', 'TI-700',
     'jrn-past', 'B · จบไลฟ์แล้วย้อนดู · หาของเก่า · ติดแท็ก · สลับพื้นที่ทำงาน', ['J-B1', 'J-B2']),
    ('m-jrn-alert', '🚨 ไลฟ์มีปัญหา + ตั้งค่า', 'Journey แจ้งเตือน Telegram · ไลฟ์มีปัญหาบนจอ · เสียงที่อัดไว้ · หน้าตั้งค่า', 'TI-714',
     'jrn-alert', 'C · ตั้งแจ้งเตือน · ไลฟ์มีปัญหาระหว่างเฝ้า · เคลียร์เสียงที่อัดไว้', ['J-C1', 'J-C2', 'J-C3']),
]
_FILES = ['PAST', 'TAG', 'CLIP', 'SET', 'ALRT']

META = dict(
    out_rel='projects/takra-insight/2026/11/reports/takra-insight-ui-redesign-nov-ui-test-cases-table.html',
    title='TAKRA Insight — UI ใหม่ แบบ User Journey (คลิป · ย้อนดู + แท็ก · ไลฟ์มีปัญหา + ตั้งค่า) · Manual Test Cases',
    emoji='🎨', uid_start=23101, os_cols=True,
    download='takra-insight-ui-redesign-nov-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=insight',
    sub=('เทสด้วยมือแบบ user journey (เดินครบเส้นทางข้ามหลายหน้า) · แอปเดสก์ท็อป TAKRA Insight · UI ใหม่หลัง re-design 5 พ.ย. · โค้ด <b>uat @ 0d937314</b> (5 พ.ย. 2569) · '
         'เฉพาะ P0 + P1 · Target: แอปเดสก์ท็อป TAKRA Insight (บิลด์ UAT)'),
    groups_label='',   # เติมตอนโหลด
    note=('🖥️ <b>Test target:</b> แอปเดสก์ท็อป <b>TAKRA Insight</b> บิลด์ UAT ที่มีโค้ด uat @ 0d937314 ขึ้นไป · '
          'ทดสอบทั้ง 🍎 Mac และ 🪟 Windows (บันทึกผลแยกคอลัมน์)<br>'
          '🎨 <b>UI ใหม่:</b> re-design <a href="https://kitdi.atlassian.net/browse/TI-700" target="_blank">TI-700</a> วิเคราะห์ย้อนหลัง · '
          '<a href="https://kitdi.atlassian.net/browse/TI-713" target="_blank">TI-713</a> คลิป · '
          '<a href="https://kitdi.atlassian.net/browse/TI-714" target="_blank">TI-714</a> ตั้งค่า/Telegram/ป้ายสถานะไลฟ์ · '
          '<a href="https://kitdi.atlassian.net/browse/TI-717" target="_blank">TI-717</a> แท็ก · '
          '<a href="https://kitdi.atlassian.net/browse/TI-740" target="_blank">TI-740</a> · '
          '<a href="https://kitdi.atlassian.net/browse/TI-741" target="_blank">TI-741</a> เสียงที่อัดไว้<br>'
          '👤 <b>บัญชี:</b> "บัญชีเจ้าของ / โฮสต์ / ผู้จัดการแบรนด์ / MULTI" ในขั้นตอน = บัญชีทดสอบ UAT ตามบรรทัด "บัญชีที่ใช้" ในช่อง Test Data<br>'
          '🧭 <b>Journey:</b> 1 เคส = ผู้ใช้ทำงานจริง 1 เป้าหมาย เดินตามขั้นตอนครบเส้นทาง · Expected 1 ข้อ = 1 จุดตรวจระหว่างทาง (เรียงตามขั้น) — จุดไหนไม่ผ่านให้ลง FAIL และบอกจุดนั้นใน Actual<br>'
          '🔁 <b>ครอบเคสเดิม:</b> "ที่มา" บอกว่า journey ครอบเคสย่อยตัวไหน · ชีต "ฟีเจอร์ใหม่ พ.ย." คงผลไว้ ไม่แก้ · เคสย่อยรอบแรกที่บันทึกผลแล้วอยู่กลุ่ม Z ท้ายชีต<br>'
          '🔴 <b>ไลฟ์จริง = ทดสอบด้วยมือ:</b> ห้ามใช้ห้องไลฟ์เดียวกับรอบทดสอบอื่นพร้อมกัน · '
          'เคสที่ต้องให้ไลฟ์มีปัญหา (หลุด ภาพค้าง เสียงหาย) ใช้บัญชีทดสอบของ QA เปิดไลฟ์เอง<br>'
          '📨 <b>Telegram:</b> ใช้กลุ่มทดสอบของ QA + บอททดสอบเท่านั้น ห้ามใช้กลุ่มลูกค้า/กลุ่มทีมจริง<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจาก <code>apps/desktop/desktop/src/renderer/src/i18n/th.js</code> (uat) · Expected ยึด <code>prd.md</code> · '
          '<code>prd-m3.md</code> · AC ในใบ Jira'),
    footer='UI only (manual) · TAKRA Insight desktop · UI ใหม่ re-design พ.ย. 2569',
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


def _idkey(i):
    g, n = i.rsplit('-', 1)[1].split('.')
    return (g, int(n))


def _load_list(name):
    p = SRC / f'{name}.json'
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else []


EPICS = []
for key, chip, title, jira, fk, ftitle, files in _JOURNEYS:
    cs = sorted((c for fn in files for c in _load_list(fn)), key=lambda c: _idkey(c['id']))
    if cs:
        EPICS.append(dict(key=key, chip=chip, emoji=chip.split(' ', 1)[0], title=title, jira=jira,
                          feats=[dict(featkey=fk, title=ftitle, cases=[_case(c) for c in cs])]))

# เคสย่อยรอบแรกที่มีผลบันทึกแล้ว → คงไว้ท้ายชีต (ผลต้องตรงกับเนื้อเคสตอนที่เทส)
import re as _re  # noqa: E402
_out = Path(__file__).resolve().parents[2] / META['out_rel']
_store = {}
if _out.exists():
    _m = _re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', _out.read_text(encoding='utf-8'))
    _store = json.loads(_m.group(1)) if _m and _m.group(1).strip() else {}
_old_map = json.loads((SRC / 'uid_map.json').read_text(encoding='utf-8'))


def _has_result(cid):
    v = _store.get(f'tc-{_old_map.get(cid)}') or {}
    return any(v.get(k) for k in ('st', 'stw', 'actual', 'actualw', 'jira', 'bug'))


_kept = []
for _fn in _FILES:
    for m in json.loads((SRC / f'{_fn}.json').read_text(encoding='utf-8'))['menus']:
        for f in m['feats']:
            _kept += [c for c in f['cases'] if _has_result(c['id'])]
if _kept:
    EPICS.append(dict(key='m-old', chip='🗂️ เคสย่อยเดิม', emoji='🗂️',
                      title='เคสย่อยรอบแรกที่บันทึกผลไว้แล้ว — คงไว้ให้ผลตรงกับเนื้อเคส (ไม่ต้องเทสซ้ำ)', jira='TI-700',
                      feats=[dict(featkey='old-kept', title='Z · เคสย่อยเดิมที่มีผลแล้ว', cases=[_case(c) for c in _kept])]))
_menus = [dict(chip=e['chip']) for e in EPICS]
META['groups_label'] = f'{len(EPICS)} กลุ่ม · ' + ' · '.join(m['chip'] for m in _menus)

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
