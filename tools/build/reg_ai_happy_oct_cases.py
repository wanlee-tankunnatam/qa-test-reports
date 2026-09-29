#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-ai (Live) · รายการที่ 1: MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4)

ข้อมูลเคสอยู่ที่ tools/build/reg-oct-sources/regai1.json (แก้ที่นั่นแล้ว build ใหม่ — อย่าแก้ HTML ตรงๆ)
คัดจากรายงานรวม MVP1+2: projects/takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html
(เฉพาะแถว data-mvp="mvp1" · happy path ทั้งหมด · จัดกลุ่มตามขั้นที่ 1–6 + Full E2E เดิม)
build: python3 tools/build/build_hub_report.py regai1"""
import json
import pathlib

SRC = pathlib.Path(__file__).resolve().parent / 'reg-oct-sources'

KINDS = {  # ประเภทเคส (กรอบเดียวกับรายงานอื่นใน repo — รอบนี้มีแต่ happy)
    'happy':      ('Happy Path', 'flow ปกติ'),
    'negative':   ('Negative', 'ข้อมูลผิด / action ผิด'),
    'boundary':   ('Boundary', 'min · max · ก่อนขอบ · ตรงขอบ · เกินขอบ'),
    'validation': ('Validation', 'format · required · character · length'),
    'exception':  ('Exception', 'API fail · network fail · server error · timeout'),
    'permission': ('Permission', 'role/สิทธิ์ ไหนทำได้ / ทำไม่ได้'),
    'data':       ('Data', 'empty · null · duplicate · existing · non-existing'),
}

EPICS = json.loads((SRC / 'regai1.json').read_text(encoding='utf-8'))['epics']

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression MVP-1 Happy Path',
    emoji='🎥', uid_start=13001,
    download='takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4) · ขั้นที่ 1 เข้าระบบ → ขั้นที่ 6 AI + Full E2E · Target: <b>UAT</b> https://uat-live.takra.ai',
    groups_label='ตามขั้น MVP-1: ขั้นที่ 1–6 + Full E2E',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — takra-ai (Live) รายการที่ 1: <b>MVP-1 happy path ทั้งเส้น 141 เคส</b> (UI 137 + E2E 4) '
          'เดินตามขั้นที่ 1 เข้าระบบ → ขั้นที่ 6 AI ช่วยเขียน Script แล้วปิดท้ายด้วย Full E2E ครบลูป'
          '<br>📎 เคสคัดจากรายงานรวม MVP1+2 (เฉพาะฝั่ง MVP-1 · happy path) · ผลรอบนี้บันทึกแยกจากรายงานชุดหลัก · '
          'แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · MVP-1 happy path',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]
