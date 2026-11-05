# -*- coding: utf-8 -*-
"""TAKRA Radar (Trendora) — ความเสถียรของเทสต์ api ใน CI · Manual Test Cases (ไม่มีหน้าจอ)

สั่ง 2026-11-05: นำ TKRD-520 มาออกแบบเคสทดสอบแมนนวล — ใบนี้เป็นงานแก้เทสต์ flaky (Postgres ตัด connection 57P01
ตอนปิด container ใน apps/api/src/queue/queue.service.integration.spec.ts) ไม่มีหน้าจอ เคสจึงเป็นการตรวจ GitHub/CI/รันเทสต์ด้วยมือ
- โค้ด: takra-radar PR #395 · merge 0eb34b48 (31 ต.ค. 2569) · อยู่ใน develop + uat
- ข้อมูลเคสอยู่ที่ tools/build/takra-radar-ci-sources/cases.json · uid ตรึงด้วย uid_map.json (22701–)
- ตั้งชื่อชีตตามเรื่อง (ความเสถียรเทสต์ api) ไม่ตามเลขตั๋ว — ใบ flaky อื่นของ radar (เช่น TKRD-515) เพิ่มเป็นเมนูใหม่ในไฟล์นี้ได้
build: python3 tools/build/build_hub_report.py radarci
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-radar-ci-sources'

META = dict(
    out_rel='projects/takra-radar/2026/11/reports/takra-radar-ci-api-test-stability-test-cases-table.html',
    title='TAKRA Radar — ความเสถียรของเทสต์ api ใน CI · Manual Test Cases',
    emoji='🧪', uid_start=22701,
    download='takra-radar-ci-api-test-stability-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub=('ตรวจด้วยมือ · ไม่มีหน้าจอ — ตรวจผ่าน GitHub (PR · Actions) + รันเทสต์บนเครื่อง QA · '
         'TKRD-520 · PR #395 (merge 0eb34b48 · 31 ต.ค. 2569) · เฉพาะ P0 + P1'),
    groups_label='',
    noui_badge='🧪 CI / โค้ด', noui_ready=True,
    noui_note=('🧪 <b>ไม่มีหน้าจอ</b> — เคสนี้ตรวจผ่าน GitHub และ Terminal บนเครื่อง QA · ห้ามแก้ไฟล์ของ dev แม้ชั่วคราว'),
    note=('🧪 <b>Test target:</b> repo <b>Real-Factory/takra-radar</b> — GitHub PR #395 · GitHub Actions workflow \"CI\" ของ branch develop · '
          'รันเทสต์ในโฟลเดอร์ทดสอบแยกของ QA (checkout origin/develop · เปิด Docker ไว้) ไม่ใช้โฟลเดอร์ทำงานของ dev · '
          '🔄 <b>Full loop (กลุ่ม D):</b> เว็บ Trendora UAT https://uat-radar.takra.ai → คิว → ระบบ aff (Realfactory UAT) · บัญชีเตรียมเหมือนชีต TKRD-404<br>'
          '🐞 <b>อาการเดิม:</b> job \"typecheck / lint / test / build\" แดงที่ @trendora/api ทั้งที่เทสต์ผ่านครบ เพราะ Uncaught Exception '
          '<code>terminating connection due to administrator command</code> (Postgres 57P01) จาก <code>queue.service.integration.spec.ts</code> '
          '(<a href="https://kitdi.atlassian.net/browse/TKRD-520" target="_blank">TKRD-520</a> · '
          '<a href="https://github.com/Real-Factory/takra-radar/pull/395" target="_blank">PR #395</a>)<br>'
          '📎 <b>ที่มา:</b> \"ต้องได้\" ในใบ TKRD-520 + คอมเมนต์ dev 30 ต.ค. · ห้ามแก้ไฟล์ของ dev แม้ชั่วคราว'),
    footer='Manual (ไม่มีหน้าจอ) · takra-radar CI · TKRD-520',
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
    return dict(id=c['id'], title=c['title'], prio=c['prio'], kind=c['kind'], level=c.get('level') or 'ui', ui=bool(c.get('ui', False)),
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
