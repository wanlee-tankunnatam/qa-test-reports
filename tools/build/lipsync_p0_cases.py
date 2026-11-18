# -*- coding: utf-8 -*-
"""TAKRA Lip-Sync (takra-lipsync) — เคส P0 ตามโค้ดปัจจุบัน · Manual Test Cases

สั่ง 2026-11-18: "ทำ test case projects/takra-lipsync p0"
- โค้ด: takra-lib-sync origin/uat @ c9111736 (16 พ.ย. 2569 · แอป 0.2.38) — ชีตเดิม (ก.ย. · เขียนจาก POC poc-local) คงไว้ ไม่แก้
- จัดกลุ่มตามหน้าในแถบซ้ายของแอป (NAV ใน web/console/src/App.svelte · ดู _bmad-output/qa/feature-map.md) + เส้นทางข้ามหน้า
- คำบนจอลอกจากภาษาไทยที่ฝังในโค้ด web/console/src/** และ app/** · Expected ยึด _bmad-output/planning-artifacts/epics.md (Jira TLS) + prd.md
- เคสเก็บเป็น JSON ต่อชุดกลุ่มที่ tools/build/takra-lipsync-p0-sources/*.json · uid ตรึงใน uid_map.json (23701–)
build: python3 tools/build/build_hub_report.py lipsyncp0
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-lipsync-p0-sources'

GROUPS = {
    'A': 'A · ติดตั้ง ดาวน์โหลดครั้งแรก และเปิดแอป',
    'B': 'B · อัปเดตในแอป',
    'C': 'C · หน้าแรก · ตั้งค่าคีย์ · ค่าใช้จ่าย',
    'D': 'D · หน้าของฉัน — อัดคลิป ปรับโมเดลให้เข้ากับหน้า คลังหน้า',
    'E': 'E · เสียงของฉัน — โคลนเสียงตัวเอง',
    'F': 'F · บทพูด — คลังบท',
    'G': 'G · คลังสินค้า + ข้อมูลร้าน',
    'H': 'H · คลังคำอ่าน + คำห้ามพูด',
    'I': 'I · เตรียมไลฟ์ ตรวจความพร้อม และโหมดไลฟ์',
    'J': 'J · คอมเมนต์ & TikTok — อ่านคอมเมนต์และ AI ตอบ',
}

META = dict(
    out_rel='projects/takra-lipsync/2026/11/reports/takra-lipsync-p0-test-cases-table.html',
    title='TAKRA Lip-Sync — เคส P0 ตามแอปปัจจุบัน (uat 0.2.38) · Manual Test Cases',
    emoji='🎙️', uid_start=23701,
    download='takra-lipsync-p0-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=lipsync',
    sub=('เทสด้วยมือ · แอปเดสก์ท็อป TAKRA Lip-Sync บน Windows · เฉพาะ <b>P0</b> (เส้นหลักที่ต้องใช้ได้) · '
         'จัดกลุ่มตามหน้าในแถบซ้ายของแอป · โค้ด <b>uat @ c9111736</b> (16 พ.ย. 2569 · แอป 0.2.38)'),
    groups_label='',
    note=('🖥️ <b>Test target:</b> แอป <b>TAKRA Lip-Sync</b> รุ่น UAT 0.2.38 ขึ้นไป (ไฟล์ติดตั้งจาก branch <code>uat</code> ของ repo takra-lib-sync)<br>'
          '👥 <b>ตัวละคร/ของที่ใช้ทั้งชีต:</b> <b>เครื่อง W</b> = Windows 11 + การ์ดจอ NVIDIA (VRAM ≥ 6 GB) + RAM ≥ 16 GB + เว็บแคม ที่ลงแอปรุ่น UAT และใส่คีย์ OpenAI/ElevenLabs ของทีมแล้ว · '
          '<b>แม่ค้า</b> = ผู้ทดสอบที่เล่นเป็นคนขาย · <b>TT-QA</b> = บัญชี TikTok ของ QA ที่มีสิทธิ์ใช้ TikTok LIVE Studio · '
          '<b>มือถือ M</b> = มือถืออีกเครื่องใช้ดูไลฟ์และคอมเมนต์ · <b>หน้า F1</b> = หน้าที่เทรนในแอปเสร็จแล้ว · <b>คลิปหน้า</b> = คลิปอัดหน้าของ QA ยาว 60 วินาที<br>'
          '🔑 <b>ก่อนเริ่ม:</b> แอปบังคับเชื่อม TikTok ตอนเปิดครั้งแรก — ทุกเคส (ยกเว้นกลุ่ม A) เริ่มจากแอปที่เชื่อม TT-QA ไว้แล้ว · '
          'ตัวติดตั้งยังไม่เซ็นลายเซ็นดิจิทัล ต้องปิด Smart App Control ของ Windows ก่อนติดตั้ง · '
          'กลุ่ม B ต้องนัด dev ปล่อยรุ่นใหม่บนช่อง UAT · เคส A.3 ต้องให้ dev ช่วยจองพอร์ตของแอปไว้ก่อนเปิด<br>'
          '🔴 <b>ไลฟ์จริง = ทดสอบด้วยมือ:</b> ใช้บัญชี TT-QA เท่านั้น · ห้ามใช้ห้องไลฟ์เดียวกับรอบทดสอบอื่นพร้อมกัน · หยุดไลฟ์ทุกครั้งหลังจบเคส<br>'
          '💸 <b>เสียค่าใช้จ่ายจริง:</b> การปรับโมเดล การโคลนเสียง และ AI คิดบท/ตอบคอมเมนต์ ใช้เครดิตจริงของทีม · โคลนเสียงสร้างเสียงถาวรบนบัญชี ElevenLabs<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจากภาษาไทยในโค้ด <code>web/console/src/**</code> และ <code>app/**</code> (uat) · Expected ยึด <code>epics.md</code> (Jira TLS) + <code>prd.md</code> · '
          'ชีตเดิม (ก.ย. · เขียนจาก POC) ยังอยู่ที่ hub ไม่ได้แก้'),
    footer='UI only (manual) · TAKRA Lip-Sync · P0 · uat 0.2.38',
)

KINDS = {
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'ช่องว่าง · รูปแบบผิด'),
    'exception':  ('Exception', 'เน็ตช้า/หลุด · ระบบภายนอกผิดปกติ'),
    'data':       ('Data', 'ไม่มีข้อมูล · ซ้ำ · ตัวเลขตรงกัน'),
}


def _case(c):
    return dict(id=c['id'], title=c['title'], prio=c['prio'], kind=c['kind'], level='e2e', ui=True,
                pre=list(c.get('pre') or []), steps=list(c['steps']), data=list(c.get('data') or []),
                expected=list(c['expected']), src=c['src'], note=c.get('note') or None, live=bool(c.get('live')))


_by = {}
for f in sorted(SRC.glob('*.json')):
    if f.name == 'uid_map.json':
        continue
    for c in json.loads(f.read_text(encoding='utf-8')):
        _by.setdefault(c['group'], []).append(_case(c))


def _n(c):
    return int(c['id'].rsplit('.', 1)[1])


FEATS = [dict(featkey=f'ls-{g.lower()}', title=t, cases=sorted(_by[g], key=_n)) for g, t in GROUPS.items() if g in _by]
assert set(_by) <= set(GROUPS), f'unknown groups {set(_by) - set(GROUPS)}'

EPICS = [dict(key='m-ls-p0', chip='🎙️ P0', emoji='🎙️', title='TAKRA Lip-Sync — เส้นหลัก P0 ตามหน้าในแอป', jira=None, feats=FEATS)]
META['groups_label'] = f'{len(FEATS)} กลุ่ม ({FEATS[0]["title"][0]}–{FEATS[-1]["title"][0]})' if FEATS else '0 กลุ่ม'

_ALL = [c for f in FEATS for c in f['cases']]
_ids = [c['id'] for c in _ALL]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
for _c in _ALL:
    assert _c['kind'] in KINDS and _c['prio'] == 'P0', (_c['id'], _c['kind'], _c['prio'])
    assert _c['steps'] and _c['expected'] and _c['src'], _c['id']

_map_p = SRC / 'uid_map.json'
UID_MAP = json.loads(_map_p.read_text(encoding='utf-8')) if _map_p.exists() else {}
_next = max(UID_MAP.values(), default=META['uid_start'] - 1) + 1
_new = [i for i in _ids if i not in UID_MAP]
for _i in _new:
    UID_MAP[_i] = _next
    _next += 1
if _new:
    _map_p.write_text(json.dumps(UID_MAP, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
