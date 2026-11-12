# -*- coding: utf-8 -*-
"""TAKRA Radar (Trendora) — ฟอร์มขอใบเสร็จ / ใบกำกับภาษี · UI Manual Test Cases

สั่ง 2026-11-12: "ออกแบบ test case TKRD-579" — ติ๊ก "ต้องการใบเสร็จ / ใบกำกับภาษี" แล้วทุกช่องแสดงว่าบังคับกรอกตั้งแต่ฟอร์มเปิด
- ตั๋วยัง To Do: คำบนจอ/ข้อความแจ้งผิดลอกจาก develop @ ff123368 (packages/shared/src/messages/th-payment.ts receiptMessagesTh ·
  apps/web/src/components/payment/CheckoutReceipt.tsx · ReceiptRequestModal.tsx) · ตัวเครื่องหมายบังคับยังไม่มีในโค้ด
- ตั้งชื่อชีตตามฟีเจอร์ (ฟอร์มขอใบเสร็จ) — ใบที่เกี่ยวกัน เช่น TKRD-576 (ช่องเลขผู้เสียภาษีบอกหลักที่ขาด) เพิ่มเป็นกลุ่มใหม่ในไฟล์นี้ได้
- ข้อมูลเคสอยู่ที่ tools/build/takra-radar-receiptform-sources/cases.json · uid ตรึงด้วย uid_map.json (23401–)
build: python3 tools/build/build_hub_report.py radarreceipt
"""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parent / 'takra-radar-receiptform-sources'

META = dict(
    out_rel='projects/takra-radar/2026/11/reports/takra-radar-receipt-form-ui-test-cases-table.html',
    title='TAKRA Radar — ฟอร์มขอใบเสร็จ / ใบกำกับภาษี · UI Manual Test Cases',
    emoji='🧾', uid_start=23401,
    download='takra-radar-receipt-form-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub=('เทส UI ด้วยมือ · เว็บ Trendora UAT · '
         '<a href="https://kitdi.atlassian.net/browse/TKRD-579" target="_blank">TKRD-579</a> ช่องบังคับกรอก · P0 + P1'),
    groups_label='',
    note=('🖥️ <b>เว็บที่เทส:</b> Trendora UAT <b>https://uat-radar.takra.ai</b> (ล็อกอิน Cloudflare Access ก่อน)<br>'
          '⏳ <b>เทสเมื่อ:</b> TKRD-579 ขึ้น UAT แล้ว (ตั๋วเป็น "Ready to test") — ตอนออกแบบเคส (12 พ.ย.) ตั๋วยัง To Do '
          'เครื่องหมายบังคับกรอกยังไม่มีบนจอ · ตัวเครื่องหมาย (เช่น *) ให้ดูตามที่ dev ทำ แล้วจดไว้ใน Actual<br>'
          '👥 <b>ตัวละคร:</b> <b>ลูกค้า C</b> = บัญชีลูกค้าทดสอบที่<b>ยังไม่เคยขอใบเสร็จ</b> '
          '(บัญชีที่เคยขอ ฟอร์มจะเติมข้อมูลครั้งก่อนให้ · บัญชีใหม่เติมแค่อีเมลของบัญชี) · <b>แอดมิน</b> = แอดมิน Trendora (เช่น qa01)<br>'
          '📋 <b>ก่อนเริ่ม:</b> เตรียมไฟล์สลิปทดสอบ (รูป jpg/png) · เคสที่ส่งสลิปสำเร็จ (A.6–A.8) ลูกค้าจะซื้อใหม่ไม่ได้จนกว่าแอดมินตัดสินสลิป — '
          'ให้แอดมินกด "ไม่อนุมัติ" ในเมนู "แจ้งชำระเงิน" ก่อนเคสถัดไป · '
          'ห้ามใช้บัญชี qa.radar.20261027.* / tkrd426-* ของ Gong · ห้ามเทสบน PROD<br>'
          '🗺️ <b>เมนูที่กระทบ:</b> ลูกค้า — "แพ็กเกจ" › หน้าชำระเงิน · ประวัติการชำระเงิน › หน้าต่าง "ขอใบเสร็จ / ใบกำกับภาษี"<br>'
          '📎 <b>ที่มา:</b> คำบนจอลอกจากโค้ด Trendora (<code>packages/shared/src/messages/th-payment.ts</code> + <code>apps/web/src</code>) · '
          'Expected ยึด AC ใน TKRD-579'),
    footer='UI only (manual) · Trendora (takra-radar) UAT · TKRD-579',
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
