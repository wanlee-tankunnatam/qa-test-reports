#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""เคส manual test ของ TAKRA Post (takra-farm) — TF-155 [Epic] วอร์มช่อง + ตารางเวลาหลักของเครื่อง + ภาพรวม "ตอนนี้ / ถัดไป"

ข้อมูลเคสอยู่ที่ tools/build/takra-farm-tf155-sources/cases.json (แปลงจาก TF-155-test-cases.md ในโฟลเดอร์เดียวกัน)
โมดูลนี้แค่ประกอบ EPICS/KINDS/META ให้ build_hub_report.py (เรียกด้วย argument `farmtf155`)
"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'takra-farm-tf155-sources'

META = dict(
    out_rel='projects/takra-farm/2026/10/reports/takra-farm-tf155-warm-channel-ui-test-cases-table.html',
    title='[TF-155] TAKRA Post (farm) — วอร์มช่อง + ตารางเวลาหลักของเครื่อง + ภาพรวม "ตอนนี้ / ถัดไป"',
    emoji='🔥', uid_start=19001, download='takra-farm-tf155-warm-channel-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=farm',
    sub='เทสด้วยมือ · Epic <b>TF-155</b> · Takra Post UAT 1.1.0 · build 1148 (+7 · uat) · 53 เคส · หมวด UI / Function / Device',
    groups_label='7 กลุ่ม (A–G)',
    jira_browse='https://kitdi.atlassian.net/browse/',
    note=('🖥️ <b>Build ที่ใช้ทดสอบ:</b> Takra Post UAT 1.1.0 · build 1148 (+7 · uat) · flow pack 1148 (Central UAT ช่อง beta) · Hub UAT ส่ง <code>features.warm: true</code><br>'
          '📱 <b>เครื่อง:</b> U1 (S8+ boxphone) และ A15 ตาม AC ข้อ 8 — <b>ทุกเคสหมวด Device ต้องผ่านบนทั้งสองรุ่น</b> · POCO M7 ถ้ามี · '
          'ใช้ช่องทดสอบเท่านั้น (ไม่ใช่ช่องลูกค้า) · มีช่อง TikTok และ Shopee บนเครื่องเดียวกันอย่างน้อย 1 เครื่อง<br>'
          '📎 <b>ที่มาของเคส:</b> Description ของ TF-155 (อ่าน 27 ต.ค. 2026) · ประกอบ <code>docs/WARM-CHANNEL-SPEC.md</code> (branch uat b307f91) · '
          'ข้อความในแอป <code>src/i18n/locales/th-TH.yml</code> (uat) · checklist ของ TF-163<br>'
          '⚠️ <b>จุดที่ต้องยืนยันกับ Book:</b> WC-C.2 (ค่าเริ่มต้นระดับ "เบา" vs สเปก §8 <code>off</code>) · WC-D.10 (วอร์มเดี๋ยวนี้ระหว่างช่วงพัก)<br>'
          '🏷️ <b>ประเภทเคส (กรองได้):</b> Happy Path · Negative · Edge Case · Regression · Priority: P0 = เกณฑ์รับงานของ epic · P1 = สำคัญ · P2 = รอง'),
    footer='Manual · TAKRA Post desktop (takra-farm) · TF-155 วอร์มช่อง',
)

KINDS = {
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ถูกปฏิเสธ/ใส่ผิด'),
    'boundary':   ('Edge Case', 'กรณีขอบ'),
    'regression': ('Regression', 'ของเดิมต้องไม่เปลี่ยน'),
}

_groups = json.loads((SRC / 'cases.json').read_text(encoding='utf-8'))['groups']

EPICS = []
for _g in _groups:
    _cases = [dict(id=c['id'], title=c['title'], prio=c['prio'], level='ui', kind=c['kind'], ui=True,
                   pre=c['pre'], steps=c['steps'], data=c['data'], expected=c['expected'], src=c['src'], note=None)
              for c in _g['cases']]
    EPICS.append(dict(key=_g['key'], chip=_g['chip'], emoji=_g['emoji'], title=_g['title'], jira='TF-155',
                      feats=[dict(featkey=_g['key'], title=_g['title'], cases=_cases)]))

# ── validation (fail fast ตอน build) ──
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted({i for i in _ids if _ids.count(i) > 1})}'
assert len(_ids) == 53, len(_ids)
for _e in EPICS:
    for _f in _e['feats']:
        for _c in _f['cases']:
            assert _c['kind'] in KINDS and _c['prio'] in ('P0', 'P1', 'P2'), _c['id']
            assert _c['steps'] and _c['expected'] and _c['src'], _c['id']
