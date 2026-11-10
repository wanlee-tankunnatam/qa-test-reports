# -*- coding: utf-8 -*-
"""TAKRA AI (Takra Live) — E2E ของเรา · สคริปต์ Playwright e2e แปลงเป็นเคสเทสด้วยมือ

สั่ง 2026-11-10: "projects/takra-ai e2e ของเรามีอะไรบ้าง ทำเป็นไฟล์ test case ใหม่ให้หน่อย"
- ต้นทาง: takra-ai origin/develop @ 80b89d94 · apps/web/tests/e2e/*.spec.ts (19 ไฟล์ · ไม่นับ uat-screens.capture.spec.ts ที่ใช้จับภาพหน้าจอ)
- 1 test() ในสคริปต์ = 1 เคส · 1 ไฟล์สคริปต์ = 1 กลุ่ม · บรรทัดที่มาบอกไฟล์สคริปต์ › TC
- คำบนจอลอกจาก i18n th (apps/web/src/i18n/locales/th) · ทางเข้าเมนูตามชีต "UI ใหม่ แบ่งตามเมนู"
- ข้อมูลเคสอยู่ที่ tools/build/takra-ai-e2e-sources/<CODE>.json (ACC · SCR · SCH · LIVE · STU) · uid ตรึงด้วย uid_map.json (22801–)
build: python3 tools/build/build_hub_report.py aie2e
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-ai-e2e-sources'
_FILES = ['ACC', 'SCR', 'SCH', 'LIVE', 'STU']

META = dict(
    out_rel='projects/takra-ai/2026/11/reports/takra-ai-e2e-ui-test-cases-table.html',
    title='TAKRA AI — E2E ของเรา (สคริปต์ e2e → เคสเทสด้วยมือ) · UI Manual Test Cases',
    emoji='🔁', uid_start=22801, script_col=True,
    download='takra-ai-e2e-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub=('เทสด้วยมือในแอป Takra Live (UAT) · ครอบทุกเทสต์ในสคริปต์ e2e ของเรา '
         '(<code>apps/web/tests/e2e</code> · develop @ 80b89d94) · P0 + P1'),
    groups_label='',
    note=('🖥️ <b>เทสที่:</b> แอปเดสก์ท็อป <b>Takra Live</b> (UAT) · เข้าสู่ระบบผ่านหน้า TAKRA Hub · ทดสอบในโปรแกรมเท่านั้น ไม่พิมพ์ URL ไม่ใช้ DevTools<br>'
          '👥 <b>บัญชี:</b> <b>เจ้าของ workspace</b> = บัญชี UAT ของ QA ที่มีแพ็กเกจ TAKRA AI ใช้งานได้ · <b>สมาชิก (Member)</b> = บัญชีที่ถูกเชิญเข้า workspace เดียวกัน (เฉพาะเคสเรื่องสิทธิ์)<br>'
          '🔁 <b>ชีตนี้คืออะไร:</b> ทุกเคสมาจาก 1 เทสต์ในสคริปต์ e2e (Playwright) ของเรา — ช่อง "ที่มา" บอกไฟล์สคริปต์ › TC · '
          'คอลัมน์ Script ใช้จดผลการรันสคริปต์ ส่วน Status ใช้จดผลเทสด้วยมือ<br>'
          '🔴 <b>ไลฟ์จริง:</b> เคสที่ออกอากาศจริงทดสอบด้วยมือเท่านั้น · ห้ามใช้ห้อง/บัญชี TikTok เดียวกับรอบทดสอบอื่นพร้อมกัน<br>'
          '📎 <b>ที่มา:</b> คำบนจอจาก i18n th + โค้ด apps/web/src · Expected ยึดสคริปต์ + เคสกลาง <code>_bmad-output/test-artifacts/case/*/fullloop-e2e.md</code> + epics.md / epics-mvp2.md'),
    footer='UI only (manual) · TAKRA AI · E2E ของเรา',
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
    src = c['src'] + (f" · สคริปต์: {c['script']}" if c.get('script') else '')
    return dict(id=c['id'], title=c['title'], prio=c['prio'], kind=c['kind'], level=c.get('level') or 'e2e', ui=True,
                pre=list(c.get('pre') or []), steps=list(c['steps']), data=list(c.get('data') or []),
                expected=list(c['expected']), src=src, note=c.get('note') or None)


_menus = []
for _fn in _FILES:
    _p = SRC / f'{_fn}.json'
    if _p.exists():
        _menus += json.loads(_p.read_text(encoding='utf-8'))['menus']

EPICS = [dict(key=m['key'], chip=m['chip'], emoji=m['chip'].split(' ', 1)[0], title=m['title'], jira=m.get('jira'),
              feats=[dict(featkey=f['featkey'], title=f['title'], cases=[_case(c) for c in f['cases']]) for f in m['feats']])
         for m in _menus]
META['groups_label'] = f'{len(EPICS)} หมวด · ' + ' · '.join(m['chip'] for m in _menus)

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
