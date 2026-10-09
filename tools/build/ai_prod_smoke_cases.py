#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TAKRA AI (Live) — Production smoke test · คัดจากชุด regression ตามเมนู (reg_ai_bymenu_oct_cases)

สั่ง 2026-10-09: ทำไฟล์ test case ของโฟลว์หลักที่ต้องทดสอบบน prod
- production = branch `production` @ 24e7188e (8 ต.ค. 23:01 · merge จาก uat @ e1fc420b — โค้ดเดียวกับ UAT รอบ regression)
- prod: https://live.takra.ai · Hub https://hub.takra.ai · auth https://auth.takra.ai (release.yml ของ takra-ai)
- 9 โฟลว์หลัก + 1 ครบลูป · 52 เคส P0 · เนื้อเคสมาจากชุดหลัก แปลงเฉพาะ URL/คำว่า UAT → production ตอน build
- uid = uid เดิมของเคส (UID_MAP ของชุดหลัก) แต่ store แยกไฟล์ — ผลบน prod ไม่ปนกับผล UAT
- แก้เนื้อเคสที่ชุดหลัก แล้ว build ใหม่ทั้งสองไฟล์ — อย่าแก้ HTML ตรง ๆ
build: python3 tools/build/build_hub_report.py aiprod"""
import copy
import json
import pathlib
import re

import reg_ai_bymenu_oct_cases as _src

KINDS = _src.KINDS

# โฟลว์หลัก = (key, emoji, chip, title, [(ชื่อชุด, [case id])]) · เรียงตามลำดับที่เดินจริงบน prod
FLOWS = [
    ('p-entry', '🔐', 'A · เข้าใช้งาน', 'A · เข้าสู่ระบบผ่าน TAKRA Hub · เลือก Workspace · แพ็กเกจ', [
        ('เข้าสู่ระบบผ่าน TAKRA Hub', ['TC-L1.2', 'TC-L1.3']),
        ('Workspace · แพ็กเกจและโควตา', ['TC-SW.1', 'TC-SW.2', 'TC-Q1.1']),
    ]),
    ('p-ws', '🏢', 'B · Workspace & ทีม', 'B · ตั้งค่า Workspace · ทีมงานและสิทธิ์', [
        ('ตั้งค่า Workspace', ['TC-W1.1', 'TC-W1.2']),
        ('ทีมงาน · บทบาท · สิทธิ์ Script Approve', ['TC-UR.3', 'TC-SA.1']),
    ]),
    ('p-lib', '🗂️', 'C · เตรียมคลัง', 'C · เตรียมคลังข้อมูล — สินค้า · คำเสี่ยง · เสียง', [
        ('คลังสินค้า', ['TC-OCT-H.4', 'TC-P2.2', 'TC-PE.1']),
        ('คำเสี่ยง', ['TC-R2.3', 'TC-R2.12']),
        ('คลังเสียง · ความยินยอม PDPA', ['TC-V2.3', 'TC-V2.6']),
    ]),
    ('p-script', '📝', 'D · คลังสคริปต์', 'D · คลังสคริปต์ — สร้าง · AI ช่วยร่าง · ขออนุมัติ · อนุมัติ', [
        ('สร้างสคริปต์ · AI ช่วยร่าง', ['TC-SL.1', 'TC-OCT-L.1', 'TC-OCT-L.6']),
        ('ส่งขออนุมัติ · อนุมัติ', ['TC-SC.1', 'TC-OCT-L.17']),
    ]),
    ('p-studio', '🎬', 'E · Studio', 'E · ประกอบไลฟ์ใน Studio — ฉาก · ผู้นำเสนอ · การ์ดสินค้า · สคริปต์', [
        ('โครง Studio · บันทึกอัตโนมัติ', ['TC-OCT-P.1', 'TC-ST.2']),
        ('ผู้นำเสนอ — อวาตาร์ · น้ำเสียง', ['TC-AV.1', 'TC-AV.7']),
        ('การ์ดสินค้า · ผูกสคริปต์เข้าฉาก', ['TC-SP.1', 'TC-SB.1']),
    ]),
    ('p-plan', '📅', 'F · ตั้งเวลา & ร่าง', 'F · โปรเจกต์ของฉัน · ตั้งเวลาไลฟ์ · ตารางไลฟ์', [
        ('ร่างไลฟ์ใน "โปรเจกต์ของฉัน"', ['TC-OCT-M.1', 'TC-OCT-A.3']),
        ('ตั้งเวลาไลฟ์ · ตารางไลฟ์', ['TC-OCT-R.22', 'TC-OCT-Q.2', 'TC-OCT-Q.5']),
    ]),
    ('p-onair', '📡', 'G · ตรวจก่อนไลฟ์ & ออกอากาศ', 'G · ตรวจก่อนไลฟ์ · เริ่มออกอากาศเข้า TikTok', [
        ('ตรวจก่อนไลฟ์', ['TC-OCT-R.14', 'TC-OCT-R.20']),
        ('หน้าออกอากาศ · บัญชี TikTok · สวิตช์ AI', ['TC-BR.1', 'TC-BR.2', 'TC-TA.2', 'TC-OCT-C.2']),
    ]),
    ('p-live', '🎛️', 'H · ระหว่างไลฟ์', 'H · ระหว่างไลฟ์ — ห้องคุมไลฟ์ · AI ตอบคอมเมนต์ · คำเสี่ยง', [
        ('ห้องคุมไลฟ์', ['T1229.1', 'TC-CT.5']),
        ('AI ตอบคอมเมนต์', ['RPL-01', 'RPL-02', 'TC-OCT-T.9']),
        ('คำเสี่ยงระหว่างไลฟ์', ['RSK-01', 'TC-RA.4']),
        ('ปิดไลฟ์', ['TC-OCT-T.1']),
    ]),
    ('p-after', '📈', 'I · หลังไลฟ์', 'I · หลังไลฟ์ — สรุปไลฟ์ · ไลฟ์ของฉัน · แดชบอร์ด', [
        ('สรุปไลฟ์', ['RCP-02', 'TC-OCT-U.3']),
        ('ไลฟ์ของฉัน · แดชบอร์ด', ['TC-OCT-Q.11', 'TC-OCT-Q.12', 'T1227.3']),
    ]),
    ('p-e2e', '🔄', 'J · ครบลูป', 'J · ครบลูป E2E บน production — เข้าระบบ → เตรียมคลัง → Studio → ออกอากาศ → จบไลฟ์', [
        ('ครบลูป', ['TC-E2E.1']),
    ]),
]

# ── แปลง UAT → production (เฉพาะสำเนาในไฟล์นี้ · ชุดหลักไม่ถูกแตะ) ──
SUBS = [
    ('https://uat-live.takra.ai', 'https://live.takra.ai'),
    ('https://uat-hub.takra.ai', 'https://hub.takra.ai'),
    ('uat-live.takra.ai', 'live.takra.ai'),
    ('uat-hub.takra.ai', 'hub.takra.ai'),
    ('บัญชี Owner (UAT)', 'บัญชี Owner ของ workspace QA บน production'),
    ('TAKRA AI (UAT)', 'TAKRA AI (production)'),
    ('เข้า UAT ได้', 'เข้า production ได้'),
    ('ขึ้น UAT แล้ว', 'ขึ้น production แล้ว'),
    ('เปิดบน UAT แล้ว', 'เปิดบน production แล้ว'),
    ('บน UAT', 'บน production'),
]

def _prod(s):
    for a, b in SUBS:
        s = s.replace(a, b)
    return s

# เคสที่บน prod ทำได้ไม่ครบ — ตัดเฉพาะส่วนที่ต้องทำให้ระบบเสีย (ห้ามบน production)
DROP_LINES = {
    # โปรเจกต์ B ต้องปิดผู้ให้บริการเสียง/ตั้งเสียงที่สังเคราะห์ไม่ได้ — ห้ามทำบน prod · เหลือทางผ่าน (โปรเจกต์ A)
    'TC-OCT-R.20': ('โปรเจกต์ B', 'ข้อ "ผู้ให้บริการเสียง" ในรายการ'),
}
EXTRA_PRE = {
    'TC-OCT-R.20': 'บน production ทดสอบเฉพาะทางผ่าน (โปรเจกต์ A) — ห้ามปิดผู้ให้บริการเสียงหรือแก้ค่าระบบเพื่อทำกรณีไม่ผ่าน (กรณีนั้นเทสที่ UAT)',
    'TC-TA.2': 'ใช้บัญชี TikTok ของทีม QA ที่ตั้งไว้สำหรับ production เท่านั้น — ห้ามใช้บัญชีร้านค้าลูกค้า',
}

TITLE_OVERRIDE = {
    'TC-OCT-R.20': 'กด "ไลฟ์เลย" แล้วระบบลองสังเคราะห์เสียงจริงก่อนเริ่ม — ผ่านแล้วพาไปหน้าเริ่มไลฟ์ (เฉพาะทางผ่านบน production)',
}

PROD_PRE = 'production (live.takra.ai) · ใช้บัญชีและ workspace ของทีม QA เท่านั้น — ห้ามแตะ workspace/ข้อมูลของลูกค้า'

# ผลรอบ regression UAT 5–9 ต.ค. ของเคสเดียวกัน (อ่านจาก store ของรายงานตามเมนู) — FAIL/BLOCKED ติดหมายเหตุไว้ให้รู้ก่อนเทส
_REG = pathlib.Path(__file__).resolve().parents[2] / _src.META['out_rel']
_ST_TH = {'fail': 'FAIL', 'block': 'BLOCKED'}
try:
    _m = re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', _REG.read_text(encoding='utf-8'))
    _UAT = json.loads(_m.group(1).replace('\\u003c', '<')) if _m else {}
except (OSError, ValueError):
    _UAT = {}

_ALL = {c['id']: c for e in _src.EPICS for f in e['feats'] for c in f['cases']}

def _case(cid):
    c = copy.deepcopy(_ALL[cid])
    drop = DROP_LINES.get(cid, ())
    keep = lambda t: not any(d in t for d in drop)
    for k in ('pre', 'data', 'steps', 'expected'):
        c[k] = [_prod(t) for t in c.get(k, []) if keep(t)]
    c['title'] = TITLE_OVERRIDE.get(cid) or _prod(c['title'])
    c['src'] = _prod(c.get('src', ''))
    pre = [PROD_PRE]
    if cid in EXTRA_PRE:
        pre.append(EXTRA_PRE[cid])
    st = (_UAT.get(f'tc-{_src.UID_MAP.get(cid)}') or {}).get('st')
    if st in _ST_TH:
        pre.append(f'⚠️ ผลบน UAT รอบ regression 5–9 ต.ค. 2569 = {_ST_TH[st]} — เช็กว่าแก้แล้วก่อนเทสบน production')
    c['pre'] = pre + c['pre']
    return c

EPICS = [dict(key=k, emoji=em, chip=chip, title=title,
              feats=[dict(featkey=f'{k}-{i}', title=f'ชุด {i} · {name}', cases=[_case(x) for x in ids])
                     for i, (name, ids) in enumerate(sets, 1)])
         for k, em, chip, title, sets in FLOWS]

UID_MAP = {cid: _src.UID_MAP[cid] for _k, _e, _c, _t, sets in FLOWS for _n, ids in sets for cid in ids}

_N = sum(len(ids) for *_x, sets in FLOWS for _n, ids in sets)

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-prod-smoke-test-cases-table.html',
    title='[PROD] TAKRA AI (Live) — Production Smoke Test',
    emoji='🚀', uid_start=18001, download='takra-ai-prod-smoke-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub=(f'ทดสอบโฟลว์หลักบน <b>production</b> · <b>9 โฟลว์หลัก + 1 ครบลูป</b> · {_N} เคส P0 · '
         'Target: <b>https://live.takra.ai</b> (เข้าสู่ระบบผ่าน <b>hub.takra.ai</b>) · branch <code>production</code> @ 24e7188e'),
    groups_label='9 โฟลว์หลัก + ครบลูป (A–J)',
    note=('🚀 <b>Production smoke:</b> เดินโฟลว์หลักของ TAKRA AI (Live) บนระบบจริงหลังปล่อย <code>production</code> @ <code>24e7188e</code> (8 ต.ค. 2569 · โค้ดเดียวกับ UAT @ <code>e1fc420b</code>) · '
          'URL <b>live.takra.ai</b> · Hub <b>hub.takra.ai</b> · เดินตามลำดับ A → J ได้เลย เพราะของที่สร้างในโฟลว์ก่อนถูกใช้ในโฟลว์ถัดไป<br>'
          '🛡️ <b>กติกา prod:</b> ใช้บัญชี + workspace ของทีม QA เท่านั้น ห้ามแตะ workspace/สินค้า/สคริปต์ของลูกค้า · บัญชี TikTok ต้องเป็นบัญชีของทีม QA (ไลฟ์บน prod ออกอากาศจริงสู่สาธารณะ — ไลฟ์ให้สั้นที่สุดแล้ว "บังคับปิดไลฟ์") · '
          'AI ช่วยร่าง / AI ตอบคอมเมนต์ / ชั่วโมงอวาตาร์ใช้โควตาจริงของแพ็กเกจ · ห้ามปิดผู้ให้บริการหรือแก้ค่าระบบเพื่อทำกรณีผิดพลาด (เทสที่ UAT) · ตั้งชื่อของที่สร้างขึ้นต้นด้วย "QA-PROD" แล้วลบ/เก็บถาวรหลังจบรอบ<br>'
          '🧑 <b>อวาตาร์:</b> บน prod มีอวาตาร์พื้นเขียวตัวเดียวคือ "Graham (พื้นหลังเขียว)" — ใช้ตัวนี้ตามกติกาจัดฉากเดิม<br>'
          '📎 <b>ที่มาของเคส:</b> คัดเคส P0 จากชุด regression ตามเมนู (<code>reg_ai_bymenu_oct_cases.py</code>) — เนื้อเคสเหมือนชุดหลัก แปลงเฉพาะ URL และคำว่า UAT → production · '
          'เคสที่บน UAT รอบ 5–9 ต.ค. ยัง FAIL/BLOCKED มีหมายเหตุ ⚠️ ใน Precondition · ผลรอบนี้บันทึกแยกจากรายงาน UAT'),
    footer='Production smoke · TAKRA AI (Live) · live.takra.ai',
)
