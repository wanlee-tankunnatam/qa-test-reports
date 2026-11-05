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
    title='TAKRA Radar — หน้าจอที่ใช้ระบบคิว (หลังแก้ TKRD-520) · UI Manual Test Cases',
    emoji='📬', uid_start=22701,
    download='takra-radar-queue-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub=('เทส UI ด้วยมือ · เว็บ Trendora UAT · full loop ถึงระบบ aff (Realfactory UAT) · TKRD-520 (PR #395 · merge 0eb34b48) · '
         'full loop + หาบั๊ก UI (สถานะ · กดซ้ำ · มือถือ · ออฟไลน์ · aff ล่ม) · P0 + P1 · ตรวจผลทั้งฝั่ง Trendora และฝั่ง aff'),
    groups_label='',
    note=('🖥️ <b>Test target:</b> เว็บ Trendora (takra-radar) UAT <b>https://uat-radar.takra.ai</b> (ล็อกอิน Cloudflare Access ก่อน) ต่อกับระบบ aff <b>Realfactory UAT</b><br>'
          '📬 <b>ทำไมต้องเทส:</b> <a href="https://kitdi.atlassian.net/browse/TKRD-520" target="_blank">TKRD-520</a> แก้เทสต์ของระบบคิว (pg-boss) '
          '— ชีตนี้ตรวจจากหน้าจอว่างานที่วิ่งผ่านคิวยังไปถึงปลายทางครบวง: ส่งยอดขาย/คืนเงินถึงระบบ aff · ขอข้อมูลใหม่ของสินค้าเฝ้าดู<br>'
          '🗺️ <b>เมนูที่กระทบ (งานที่ส่งผ่านระบบคิว):</b><br>'
          '&nbsp;• <b>Trendora ฝั่งลูกค้า:</b> "แพ็กเกจ" (ส่งสลิป → แจ้งเตือนแอดมิน · ตรวจสลิปอัตโนมัติ) · "ตั้งค่า" › การ์ด "ชวนเพื่อน" (เข้าร่วมค่าคอม → สร้างสมาชิกบนระบบ aff · ปุ่ม "ดูค่าคอม / ถอนเงิน") · "สินค้าที่บันทึกไว้" ("ขอข้อมูลใหม่")<br>'
          '&nbsp;• <b>Trendora โซนผู้ดูแลระบบ:</b> "แจ้งชำระเงิน" (อนุมัติ/ยกเลิกการอนุมัติ → ส่งยอดขาย/คืนเงินไประบบ aff · ใบเสร็จ) · "คำขอใบเสร็จ" · "ตรวจสลิปอัตโนมัติ" · "ค่าคอมชวนเพื่อน" ("ทดสอบการเชื่อมต่อ" · การ์ด "ค่าคอมต้องดูแล")<br>'
          '&nbsp;• <b>ระบบ aff (Realfactory UAT):</b> Project Admin โปรเจกต์ takra-radar หน้า "Orders" · "Audit Log" · สมาชิกผู้ชวน · พอร์ทัลค่าคอมของผู้ชวน — ชีตนี้เทสเส้นทางส่งยอดขาย/คืนเงิน + ขอข้อมูลใหม่ (happy path) ส่วนเมนูอื่นเทสในชีต TKRD-404 / MVP1<br>'
          '👥 <b>บัญชี:</b> เตรียมเหมือนชีต TKRD-404 (ผู้ชวน A พร้อมใช้งาน · ผู้ซื้อ B สมัครผ่านลิงก์ A · แอดมิน qa01) · ห้ามใช้บัญชี/สลิปที่คนอื่นกำลังทดสอบ (เช่น qa.radar.20261027.* / tkrd426-* ของ Gong)<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจาก <code>packages/shared/src/messages/th-*.ts</code> + <code>apps/web/src</code> (ใช้ชุดเดียวกับชีต TKRD-404 / MVP1) · Expected ยึด Epic TKRD-404 + Story 5.9'),
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
