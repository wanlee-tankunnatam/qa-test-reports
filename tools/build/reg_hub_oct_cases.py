#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-hub · flow เงินครบลูป + P0 ทุกกลุ่ม
คัดจากชุดหลัก hub_cases.py (MVP-1): P0 ทั้งหมด + กลุ่ม D (โอน+สลิป/checkout) เต็มกลุ่ม + E2E ครบลูป
build: python3 tools/build/build_hub_report.py reghub"""
import hub_cases as _base

KINDS = _base.KINDS

def _keep(e, c):
    return c['prio'] == 'P0' or e['key'] in ('m1d', 'e2e')

EPICS = []
for _e in _base.EPICS:
    _feats = []
    for _f in _e['feats']:
        _cs = [c for c in _f['cases'] if _keep(_e, c)]
        if _cs:
            _feats.append(dict(_f, cases=_cs))
    if _feats:
        EPICS.append(dict(_e, feats=_feats))

META = dict(
    out_rel='projects/takra-hub/2026/10/reports/takra-hub-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Hub — Regression Test Cases',
    emoji='🧾', uid_start=15001, download='takra-hub-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=hub',
    sub='รอบ Regression <b>พ 7 ต.ค. 2569</b> · flow เงินครบลูป (สมัคร → แพ็กเกจ → สลิป → CS ตรวจ → เปิดสิทธิ์ → ดาวน์โหลด) + P0 ทุกกลุ่ม + E2E',
    groups_label=_base.META.get('groups_label', ''),
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — คัดจากชุดหลัก MVP-1 (110 เคส): <b>P0 ทุกกลุ่ม + กลุ่ม D โอน+สลิป/checkout เต็มกลุ่ม + E2E ครบลูป</b>'
          '<br>⚠️ ของใหม่ VAT/ใบเสร็จ/รวมสลิป (ปิดไปรอบ 17–18 ก.ย.) ให้ตรวจซ้ำตอนเดิน flow เงิน — บันทึกผลใน Actual ของเคส checkout/CS ที่เกี่ยว · บัคตีกลับ TKH-50/121/239 re-test เมื่อ dev ปิด'
          '<br>📎 เคสคัดจากชุดหลัก (<code>hub_cases.py</code>) · แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-hub',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]
