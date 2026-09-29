#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-lipsync · smoke เส้นหลัก (ครึ่งวันศุกร์)
คัดจากชุดหลัก lipsync_cases.py: P0 ทั้งหมด + P1 ของกลุ่ม Installer (RA-4077) และ เปิด/ปิดไม่ค้าง (RA-4058)
build: python3 tools/build/build_hub_report.py reglipsync"""
import lipsync_cases as _base

KINDS = _base.KINDS

def _keep(e, c):
    return c['prio'] == 'P0' or (c['prio'] == 'P1' and e['key'] in ('ra4077', 'ra4058', 'ra4027'))

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
    out_rel='projects/takra-lipsync/2026/10/reports/takra-lipsync-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Lib-Sync — Regression Smoke Test Cases',
    emoji='🎙️', uid_start=16501, download='takra-lipsync-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=lipsync',
    sub='รอบ Regression <b>ศ 9 ต.ค. 2569 (ครึ่งวัน)</b> · smoke เส้นหลัก: ติดตั้ง → login TikTok → Console → เปิดไลฟ์ → ปิดไม่ค้าง',
    groups_label=_base.META.get('groups_label', ''),
    noui_badge=_base.META.get('noui_badge', None) or '⛔ ไม่พบใน UI',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — smoke เส้นหลักครึ่งวันศุกร์ · คัดจากชุดหลัก 69 เคส: <b>P0 ทั้งหมด + P1 กลุ่ม ส่งไลฟ์ TikTok (RA-4027) · เปิด/ปิดไม่ค้าง (RA-4058) · Installer ลูกค้า (RA-4077)</b>'
          '<br>📎 ระหว่างเทสถือโอกาสยืนยัน "คำ UI รอยืนยัน" ของหน้า Console กับจอจริงด้วย · แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-lipsync',
)
