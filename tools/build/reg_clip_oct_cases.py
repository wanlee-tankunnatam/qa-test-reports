#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-clip · Back Office รอบแรก smoke P0
คัดจากชุดหลัก clip_bo_cases.py: เฉพาะ P0 (27 เคส)
build: python3 tools/build/build_hub_report.py regclip"""
import clip_bo_cases as _base

KINDS = _base.KINDS

EPICS = []
for _e in _base.EPICS:
    _feats = []
    for _f in _e['feats']:
        _cs = [c for c in _f['cases'] if c['prio'] == 'P0']
        if _cs:
            _feats.append(dict(_f, cases=_cs))
    if _feats:
        EPICS.append(dict(_e, feats=_feats))

META = dict(
    out_rel='projects/takra-clip/2026/10/reports/takra-clip-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Clip — Back Office Smoke P0 Test Cases',
    emoji='🎬', uid_start=17001, download='takra-clip-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=clip',
    sub='รอบ <b>ศ 9 ต.ค. 2569</b> · Back Office รอบแรก — smoke เฉพาะ P0 (ไม่ใช่ regression แท้ ชุดหลักยังไม่เคยเทส)',
    groups_label=_base.META.get('groups_label', ''),
    note=('🧪 <b>รอบ 5–9 ต.ค. 2569</b> — Back Office ยังไม่เคยเทสเลย รอบนี้เดินเส้นหลักก่อน: <b>เฉพาะเคส P0</b> จากชุดหลัก 70 เคส'
          '<br>📎 เคสคัดจากชุดหลัก (<code>clip_bo_cases.py</code>) · แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-clip',
)
