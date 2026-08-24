#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส UI manual test ของ TAKRA Hub — MVP-2 เฉพาะ Epic 1 (RBAC/ABAC) + Aff Account

ข้อมูลเคสอยู่ที่ tools/build/takra-hub-mvp2-rbac-sources/hub_rbac_*.json (แก้ที่นั่นแล้ว build ใหม่)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `mvp2rbac`)

ต่างจาก hub_mvp2_cases.py (รายงาน MVP-2 รวม Epic 1–8) ตรงที่เจาะลึกเฉพาะ Epic 1 + เรื่องผู้แนะนำ
⇒ คนละไฟล์ปลายทาง คนละ store-data ⇒ สถานะผลเทสของรายงานรวมไม่ถูกแตะ
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-hub-mvp2-rbac-sources'

META = dict(
    out_rel='projects/takra-hub/2026/08/reports/takra-hub-mvp2-rbac-affiliate-ui-test-cases-table.html',
    title='[MVP2] TAKRA Hub — RBAC/ABAC + Aff Account UI Manual Test Cases',
    emoji='🛡️', uid_start=7501, download='takra-hub-mvp2-rbac-affiliate-ui-test-cases.html',
    sub='เทส UI ด้วยมืออย่างเดียว · MVP-2 <b>Epic 1 สิทธิ์การเข้าถึงที่ตรวจสอบย้อนหลังได้ (RBAC/ABAC)</b> + <b>Aff Account</b> · Target: <b>TAKRA Hub Web (UAT)</b> · login ด้วยบัญชี UAT',
    groups_label='6 กลุ่ม (A–D · L · F–G) + E2E · ทุกเคสทำเองได้บน UI',
    note=('🖥️ <b>Test target:</b> เว็บ <b>TAKRA Hub</b> รุ่น UAT (uat-hub.takra.ai · branch <code>develop</code>) · บัญชี UAT ที่ต้องเตรียม: <b>admin</b> (superuser) · <b>compliance</b> · <b>cs</b> ×2 (คนหนึ่งอยู่ทีมเดียวกับลูกค้า) · <b>finance</b> · <b>marketing</b> · ลูกค้าทั่วไป · ผู้แนะนำที่อนุมัติแล้ว · อีเมลใหม่<br>'
          '📎 <b>ที่มาของเคส:</b> <code>docs/epics-mvp2.md</code> Epic 1 (Story 1.1–1.9) + <code>docs/rbac-abac-spec.md</code> (§2 · §5 · §8) + <code>docs/mvp2-scope-draft.md</code> §1 + <code>docs/affiliate-payment-v2-plan.md</code> + UI จริงบน <code>apps/web/src</code> (origin/develop 2026-08-24) — คัดเฉพาะข้อที่คนกดเองแล้วเห็นผลบนจอได้<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Boundary · Validation · Exception · Permission · Data<br>'
          '✅ <b>ลง develop แล้ว:</b> console บัญชีพนักงาน (/staff) · หน้าจอตามสิทธิ์ + 403 · <b>บันทึกการตัดสินสิทธิ์ (/authz-log)</b> · เอกสารกฎหมาย (/legal-admin) · ABAC ห้ามอนุมัติรายการของตัวเอง · การ์ดโปรแกรมผู้แนะนำบนโปรไฟล์<br>'
          '✅ <b>กติกาของรายงานนี้:</b> ทุกเคสออกแบบจาก <b>UI จริงที่ผู้ใช้กดเองได้</b> เท่านั้น — ไม่มีเคสที่ต้องให้ dev เซ็ตข้อมูล/แก้ค่าคอนฟิก ไม่ใช้ DevTools และไม่มีเคสที่ไม่มีหน้าจอ<br>'
          '🚫 <b>สิ่งที่ตัดออกโดยตั้งใจ:</b> ปรับวัน/ยกเลิก subscription และการจำกัดช่องทาง export (หน้า Admin ยังปิด) · สายงานแม่ทีมของผู้แนะนำ (อยู่นอกเว็บ Hub) · สถานะบัญชีผู้แนะนำที่ผิดปกติและการยิงยอดที่ล้มเหลว (สร้างเองจาก UI ไม่ได้) ⇒ ส่วนเหล่านี้ต้องพิสูจน์ด้วยเทสฝั่งระบบ ไม่ใช่ manual UI'),
    footer='UI only (manual) · TAKRA Hub Web UAT (branch develop) · MVP-2 · Epic 1 RBAC/ABAC + Aff Account',
)

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงาน MVP-1/MVP-2)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

_ORDER = ['r1a', 'r1b', 'r1c', 'r1d', 'r1l', 'raf', 'rag', 're2e']
_FILES = ['hub_rbac_a.json', 'hub_rbac_b.json', 'hub_rbac_c.json']

_groups = {}
for _fn in _FILES:
    _d = json.loads((SRC / _fn).read_text(encoding='utf-8'))
    for _g in _d['groups']:
        assert _g['key'] not in _groups, f'duplicate group key: {_g["key"]}'
        _groups[_g['key']] = _g

assert set(_groups) == set(_ORDER), f'group mismatch: {sorted(set(_groups) ^ set(_ORDER))}'

EPICS = []
for _k in _ORDER:
    _g = _groups[_k]
    _g.setdefault('emoji', _g['chip'].split()[0])
    EPICS.append(_g)

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
for _e in EPICS:
    for _f in _e['feats']:
        for _c in _f['cases']:
            assert _c['kind'] in KINDS, (_c['id'], _c['kind'])
            assert _c['prio'] in ('P0', 'P1', 'P2'), (_c['id'], _c['prio'])
            assert _c['steps'] and _c['expected'] and _c['src'], _c['id']
            _c.setdefault('pre', [])
            _c.setdefault('data', [])
            _c.setdefault('note', None)
            _c.setdefault('ui', True)
            _c.setdefault('level', 'ui')
