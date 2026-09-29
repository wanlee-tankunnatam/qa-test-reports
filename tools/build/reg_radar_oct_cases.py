#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-radar · คัดจากชุดหลัก radar_cases.py (อย่าแก้เคสที่นี่ แก้ที่ชุดหลักแล้ว build ใหม่)
build: python3 tools/build/build_hub_report.py regradar"""
import radar_cases as _base

KINDS = _base.KINDS
EPICS = _base.EPICS

META = dict(
    out_rel='projects/takra-radar/2026/10/reports/takra-radar-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Radar (Trendora) — Regression Test Cases',
    emoji='📡', uid_start=15501, download='takra-radar-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=radar',
    sub='รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · ชุดเต็ม 130 เคส (ลูกค้า A–H + แอดมิน ADM) รอบยืนยัน 8 ต.ค. · ✅ ข้อมูลแคตตาล็อกบน UAT มีแล้ว (ClickHouse)',
    groups_label=_base.META.get('groups_label', ''),
    note='🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — ชุดเต็ม 130 เคส (ลูกค้า A–H + แอดมิน ADM) รอบยืนยัน 8 ต.ค. · ✅ ข้อมูลแคตตาล็อกบน UAT มีแล้ว (ClickHouse)<br>📎 เคสคัดจากชุดหลัก (<code>radar_cases.py</code>) · ผลรอบนี้บันทึกแยกจากรายงานชุดหลัก · แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>',
    footer='Regression 5–9 ต.ค. 2569 · takra-radar',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]
