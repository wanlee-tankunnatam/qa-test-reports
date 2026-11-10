# -*- coding: utf-8 -*-
"""TAKRA Radar (Trendora) — ตรวจสลิปอัตโนมัติด้วย GoSaaS (TKRD-532) · UI Manual Test Cases

สั่ง 2026-11-10: "TKRD-532 ทำ test case" — ระบบส่งสลิปไปตรวจกับธนาคาร (GoSaaS) แสดงผลให้แอดมิน และอนุมัติเองเฉพาะผล "ผ่าน"
- โค้ด: takra-radar PR #425 (ตรวจ+แสดงผล) · #426 (อนุมัติอัตโนมัติ + Telegram) · #434 (ป้ายผลตรวจในคิว) · อยู่ใน origin/uat @ 4674d2c0
- คำบนจอลอกจาก packages/shared/src/messages/th-shell.ts · th-payment.ts + apps/web/src/components/admin/* · ข้อความ Telegram จาก apps/worker/src/jobs/slip-notify
- Expected ยึด AC ในตั๋ว + ข้อตกลงใน comment 4 พ.ย. + docs/RUNBOOK-slip-verify.md
- ข้อมูลเคสอยู่ที่ tools/build/takra-radar-slipverify-sources/cases.json · uid ตรึงด้วย uid_map.json (23001–)
build: python3 tools/build/build_hub_report.py radarslip
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-radar-slipverify-sources'

META = dict(
    out_rel='projects/takra-radar/2026/11/reports/takra-radar-slip-auto-verify-ui-test-cases-table.html',
    title='TAKRA Radar — ตรวจสลิปอัตโนมัติด้วย GoSaaS · UI Manual Test Cases',
    emoji='🏦', uid_start=23001,
    download='takra-radar-slip-auto-verify-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub=('เทส UI ด้วยมือ · เว็บ Trendora UAT + กลุ่ม Telegram แจ้งสลิป · '
         '<a href="https://kitdi.atlassian.net/browse/TKRD-532" target="_blank">TKRD-532</a> · '
         'โค้ด <b>uat @ 4674d2c0</b> · P0 + P1'),
    groups_label='',
    note=('🖥️ <b>เว็บที่เทส:</b> Trendora UAT <b>https://uat-radar.takra.ai</b> (ล็อกอิน Cloudflare Access ก่อน) · '
          'ดูข้อความ Telegram ในกลุ่มที่ตั้งไว้ในเมนู "การแจ้งเตือนทีมงาน"<br>'
          '👥 <b>ตัวละครในเคส:</b> <b>ลูกค้า C</b> = บัญชีลูกค้าทดสอบ (ใช้บัญชีใหม่ต่อเคสได้) · <b>D</b> = ลูกค้าอีกบัญชี · '
          '<b>A / B</b> = ผู้ชวน / เพื่อนที่ A ชวน (เฉพาะ C.2) · <b>แอดมิน</b> = แอดมิน Trendora (เช่น qa01)<br>'
          '🏦 <b>สลิปจริง:</b> ผล "ผ่าน" ได้เฉพาะสลิปที่<b>โอนเงินจริง</b>เข้าบัญชีแรกใน "ข้อมูลการรับเงิน" ของ UAT · '
          'ยอดเท่าราคาแพ็กเกจ · โอนไม่เกิน 7 วัน · ใช้ได้ครั้งเดียว (ส่งซ้ำ = "สลิปซ้ำ") — '
          'ต้องเตรียม <b>สลิปใหม่ 5 ใบ</b> (B.1 · C.1 · C.2 · C.5 · C.6) แนะนำแพ็กเกจทดสอบราคาต่ำ · '
          'ทุกครั้งที่ส่งสลิปจริงเสียเครดิต GoSaaS 1 ครั้ง (รูปที่ไม่ใช่สลิปไม่เสีย)<br>'
          '📋 <b>ก่อนเริ่ม:</b> สวิตช์ในเมนู "ตรวจสลิปอัตโนมัติ" มีชุดเดียวทั้งระบบ — นัดคนที่เทสสลิปบน UAT อยู่ก่อนเปลี่ยน แล้วตั้งกลับหลังจบ · '
          'เคสอนุมัติอัตโนมัติ <b>ห้ามใครเปิดสลิปนั้น</b>จากคิวหรือลิงก์ Telegram ภายใน 2 นาที (เปิดแล้ว = ให้แอดมินตัดสิน) · '
          'ลูกค้าที่มีสลิปรอตรวจซื้อแพ็กเกจใหม่ไม่ได้ จบเคสให้แอดมินกด "ไม่อนุมัติ" · '
          'ห้ามใช้บัญชี qa.radar.20261027.* / tkrd426-* ของ Gong · ห้ามเทสบน PROD<br>'
          '⚠️ <b>ทำบนจอไม่ได้:</b> ป้าย "ไม่พบรายการ" · "ตรวจไม่สำเร็จ" และ "ยังไม่ได้ตรวจ" จากเหตุที่ระบบไม่พร้อม (เครดิตหมด · ไม่ได้ตั้งเลขบัญชี) — dev ทดสอบด้วยสคริปต์แล้ว<br>'
          '🗺️ <b>เมนูที่กระทบ:</b> ลูกค้า — "แพ็กเกจ" · "ประวัติการชำระเงิน" | '
          'แอดมิน — "ตรวจสลิปอัตโนมัติ" (ใหม่) · "แจ้งชำระเงิน" · "สิทธิ์ลูกค้า" · "รางวัลชวนเพื่อน" | Telegram แจ้งสลิป<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจากโค้ด Trendora (<code>packages/shared/src/messages/th-*.ts</code> + <code>apps/web/src</code>) · '
          'Expected ยึด AC ใน TKRD-532 + ข้อตกลงใน comment 4 พ.ย.'),
    footer='UI only (manual) · Trendora (takra-radar) UAT · TKRD-532',
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
