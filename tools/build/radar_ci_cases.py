# -*- coding: utf-8 -*-
"""TAKRA Radar (Trendora) — หน้าจอที่ใช้ระบบคิว หลังแก้ TKRD-520 · UI Manual Test Cases

5 พ.ย. ผู้ใช้สั่ง: ออกแบบเฉพาะ UI เท่านั้น + full loop ต้องไปถึงระบบ aff — ตัดเคสตรวจ CI/โค้ดเดิม (TC-CI-A–C) ออก

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
    title='TAKRA Radar — ค่าคอมชวนเพื่อน + ขอข้อมูลใหม่ (หลังแก้ TKRD-520) · UI Manual Test Cases',
    emoji='📬', uid_start=22701,
    download='takra-radar-queue-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub=('เทส UI ด้วยมือ · เว็บ Trendora UAT ต่อกับระบบ aff (Realfactory UAT) · '
         '<a href="https://kitdi.atlassian.net/browse/TKRD-520" target="_blank">TKRD-520</a> · P0 + P1'),
    groups_label='',
    note=('🖥️ <b>เว็บที่เทส:</b> Trendora UAT <b>https://uat-radar.takra.ai</b> (ล็อกอิน Cloudflare Access ก่อน) · '
          'ระบบ aff = <b>Realfactory UAT</b> โปรเจกต์ takra-radar (บัญชีแอดมิน)<br>'
          '👥 <b>ตัวละครในเคส:</b> <b>A</b> = ผู้ชวน (บัญชีรับค่าคอม "พร้อมใช้งาน") · <b>B</b> = เพื่อนที่ A ชวน · '
          '<b>E</b> = ผู้ชวนที่ยังไม่เข้าร่วมค่าคอม · <b>แอดมิน</b> = แอดมิน Trendora (เช่น qa01)<br>'
          '📋 <b>ก่อนเริ่ม:</b> UAT ต้องมีงานแก้ TKRD-520 แล้ว (PR #395) · ห้ามใช้บัญชีที่คนอื่นกำลังเทส '
          '(qa.radar.20261027.* / tkrd426-* ของ Gong) · ห้ามแก้ค่าการเชื่อมต่อ และห้ามเลือก "PROD (ใช้งานจริง)" · '
          'สมาชิกและ order บนระบบ aff ลบไม่ได้ ใช้บัญชีใหม่และจดไว้ทุกครั้ง<br>'
          '⚠️ <b>ชื่อหน้าฝั่งระบบ aff</b> (Orders · Audit Log · สมาชิก · อัปไลน์/ดาวน์ไลน์) ยังไม่ได้เทียบกับจอจริง '
          'ถ้าไม่ตรง ให้จดชื่อที่เห็นจริงในช่อง Actual<br>'
          '🗺️ <b>เมนูที่กระทบ:</b> ลูกค้า — "แพ็กเกจ" · "ตั้งค่า" › "ชวนเพื่อน" · "สินค้าที่บันทึกไว้" · หน้าสมัครสมาชิก | '
          'แอดมิน — "แจ้งชำระเงิน" · "แพคเกจที่ขาย" · "ค่าคอมชวนเพื่อน" | ระบบ aff — Orders · Audit Log · สมาชิก/อัปไลน์ · พอร์ทัลของผู้ชวน<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจากโค้ด Trendora (<code>packages/shared/src/messages/th-*.ts</code> + <code>apps/web/src</code>) · '
          'Expected ยึด Epic TKRD-404 + Story 5.9'),
    footer='UI only (manual) · Trendora (takra-radar) UAT · TKRD-520',
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
