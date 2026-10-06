#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-radar · คัดจากชุดหลัก radar_cases.py (อย่าแก้เคสที่นี่ แก้ที่ชุดหลักแล้ว build ใหม่)
build: python3 tools/build/build_hub_report.py regradar

ก้อน 🆕 rdoct (เพิ่ม 6 ต.ค.) — เคสใหม่ตรงที่ UI เปลี่ยนหลังเคสชุดหลักปรับล่าสุด (29 ก.ย. ตามโค้ด develop c9d683b)
อิงโค้ด dev origin/develop 835aea4 (5 ต.ค. · โค้ด UI = origin/uat 2dc1c91) เท่านั้น · เคสอยู่ที่ takra-radar-sources/radar_reg_oct_new.json
ต่อท้ายรายงาน — เคสเดิมไม่แก้ (โฟลว์เดิมที่ UI เปลี่ยนก็ออกเคสใหม่ให้เทสซ้ำ ตามที่สั่ง 6 ต.ค.)"""
import json
import pathlib

import radar_cases as _base

_SRC = pathlib.Path(__file__).resolve().parent / 'takra-radar-sources'
# uid ตรึงต่อเคส (ตั้ง 6 ต.ค. จากลำดับเดิม tc-15501..15630) — เพิ่มเคสได้โดยผลเทสเดิมไม่เลื่อน
# เคสใหม่: build จะพิมพ์ uid ที่แจกให้ → เพิ่มลง reg_oct_uid_map.json ด้วย
UID_MAP = json.loads((_SRC / 'reg_oct_uid_map.json').read_text(encoding='utf-8'))

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

# ── ก้อน 🆕 UI เปลี่ยนหลัง 29 ก.ย. (เพิ่ม 6 ต.ค.) — ต่อท้ายสุด ──
_NEW = json.loads((_SRC / 'radar_reg_oct_new.json').read_text(encoding='utf-8'))
_new_feats = []
for _f in _NEW['feats']:
    _cases = []
    for _c in _f['cases']:
        _c = dict(_c)
        # note ไม่มีช่องแสดงของตัวเอง → ต่อท้ายบรรทัดที่มา (hint ใต้ Expected) ให้เห็นตอนเทส
        if _c.get('note'):
            _c['src'] = f"{_c['src']} · {_c['note']}"
        _cases.append(_c)
    _new_feats.append(dict(featkey=_f['featkey'], title=_f['title'], cases=_cases))
EPICS.append(dict(key='rdoct', chip='🆕 RD·OCT', emoji='🆕', title=_NEW['title'], feats=_new_feats))

_N_OLD = sum(len(f['cases']) for e in EPICS[:-1] for f in e['feats'])
_N_NEW = sum(len(f['cases']) for f in _new_feats)
META['sub'] = (f'รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · ชุดเต็ม {_N_OLD} เคส (ลูกค้า A–H + แอดมิน ADM) '
               f'+ 🆕 UI เปลี่ยนหลัง 29 ก.ย. {_N_NEW} เคส = {_N_OLD + _N_NEW} เคส · รอบยืนยัน 8 ต.ค. · ✅ ข้อมูลแคตตาล็อกบน UAT มีแล้ว (ClickHouse)')
META['note'] = META['note'].replace('ชุดเต็ม 130 เคส (ลูกค้า A–H + แอดมิน ADM)', f'ชุดเต็ม {_N_OLD} เคส (ลูกค้า A–H + แอดมิน ADM)') + (
    f'<br>🆕 <b>UI เปลี่ยนหลัง 29 ก.ย. {_N_NEW} เคส (เพิ่ม 6 ต.ค. · ก้อนท้ายตาราง):</b> เคสชุดเต็มเขียนตามโค้ด develop 29 ก.ย. — '
    'หน้าที่ UI เปลี่ยนหลังจากนั้นออกเคสใหม่ให้เทสซ้ำแม้โฟลว์เดิม · อิงโค้ด dev <code>origin/develop 835aea4</code> (5 ต.ค. = UAT) เท่านั้น · '
    'แต่ละเคสบอกเคสเดิมที่เกี่ยวไว้ใต้ Expected · uid เคสเดิมตรึงไว้ — ผลเทสเดิมไม่เลื่อน')

