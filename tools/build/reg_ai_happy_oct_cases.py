#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-ai (Live) · รายการที่ 1: MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4) + avatar/voice self-service 10 เคส (เพิ่ม 5 ต.ค.)

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

_DATA = json.loads((SRC / 'regai1.json').read_text(encoding='utf-8'))
EPICS = _DATA['epics']
# uid ตรึงต่อเคส (ตั้ง 5 ต.ค. ตอนแทรกเคส avatar/voice self-service) — เพิ่มเคสกลางไฟล์ได้โดยผลเทสเดิมไม่เลื่อน
# เคสใหม่: build จะพิมพ์ uid ที่แจกให้ → เพิ่มลง uid_map ใน regai1.json ด้วย
UID_MAP = _DATA.get('uid_map', {})

META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression MVP-1 Happy Path',
    emoji='🎥', uid_start=13001,
    download='takra-ai-regression-oct0509-happy-ui-test-cases-table.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=ai',
    sub='รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · MVP-1 happy path ทั้งเส้น 141 เคส (UI 137 + E2E 4) + avatar/voice self-service 10 เคส (เพิ่ม 5 ต.ค.) · ขั้นที่ 1 เข้าระบบ → ขั้นที่ 6 AI + Full E2E · Target: <b>UAT</b> https://uat-live.takra.ai',
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

# ── รวมรายการที่ 2 (จุดเคย FAIL + ใบงาน ก.ย. + tool-calling) เข้ารายงานนี้ — สั่ง 2026-10-06 ให้เหลือลิงก์เดียว ──
# ต่อท้ายเสมอ · uid ของก้อนนี้ตรึงไว้ที่ค่าเดิมจากรายงาน fail-features (tc-13501–13665) ใน uid_map ของ regai1.json
# id ในก้อน "เคย FAIL" ที่ซ้ำกับเคส happy ด้านบน (23 เคส) เติม "-RF" (re-test FAIL) ให้ id/uid ไม่ชนกันในรายงานเดียว
import reg_ai_failfeat_oct_cases as _ff

for _k, _v in _ff.KINDS.items():
    KINDS.setdefault(_k, _v)
_HAPPY_IDS = {c['id'] for e in EPICS for f in e['feats'] for c in f['cases']}
_N_HAPPY = len(_HAPPY_IDS)
for _e in _ff.EPICS:
    EPICS.append(dict(_e, feats=[dict(_f, cases=[dict(_c, id=_c['id'] + '-RF') if _c['id'] in _HAPPY_IDS else _c
                                                 for _c in _f['cases']]) for _f in _e['feats']]))
_N_FF = sum(len(f['cases']) for e in _ff.EPICS for f in e['feats'])

# ── ก้อนที่ 3: 🆕 UI/ฟีเจอร์ที่เปลี่ยน/เพิ่มบน UAT (ตรวจ 6 ต.ค.) — ต่อท้ายเสมอ · ไม่แก้เคสเดิม ──
# uid ตรึงใน uid_map ของ regai1.json ตั้งแต่ tc-13666 · เคสเดิมที่ถูกแทนยังอยู่ครบ (ลง SKIP ที่เคสเดิมถ้าทำบน UI ไม่ได้แล้ว)
import ai_reg_oct_new_cases as _new

for _k, _v in _new.KINDS.items():
    KINDS.setdefault(_k, _v)
EPICS.append(_new.EPIC)
_N_NEW = sum(len(f['cases']) for f in _new.EPIC['feats'])
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), 'duplicate ids หลังรวม'
assert all(i in UID_MAP for i in _ids), f'uid ยังไม่ตรึง: {[i for i in _ids if i not in UID_MAP]}'

# ── เอาเคสเดิมออก (สั่ง 2026-10-06): ① เคสที่ UI เปลี่ยนแล้วมีเคส 🆕 TC-OCT-* แทน ② เคส "-RF" ที่ซ้ำกับเคสหลักในขั้นที่ 1–6 ──
# เอาออกเฉพาะเคสที่ "ยังไม่มีผลบันทึก" ใน store-data ของรายงาน (สถานะ/Actual/Jira) — เคสที่มีผลแล้วคงไว้ ไม่ให้ข้อมูลที่บันทึกหายจากจอ
# uid ยังตรึงใน uid_map เหมือนเดิม (ไม่แจกซ้ำ) · เช็กกับ store ทุกครั้งที่ build จึงกันกรณีมีคนบันทึกผลระหว่างนี้
import pathlib as _pl, re as _re

_OUT = _pl.Path(__file__).resolve().parents[2] / META['out_rel']
_m = _re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', _OUT.read_text(encoding='utf-8')) if _OUT.exists() else None
_STORE = json.loads(_m.group(1).strip() or '{}') if _m else {}
_has_data = lambda i: bool(_STORE.get(f'tc-{UID_MAP[i]}'))
# ③ (สั่ง 2026-10-06) กลุ่ม "จุดที่เคย FAIL ในรายงาน MVP1+2" ทั้งกลุ่ม — เคส MVP-1 ซ้ำ/ถูกแทนหมดแล้ว · ที่เหลือคือ Epic 14 RTMP (ยังไม่ขึ้น UAT)
#   + Epic 15 เป้า/ร่าง (มีเคส 🆕 กลุ่ม M ครอบ) — ใส่ Epic 14 กลับได้ตอน TAKRA-783 merge (uid ยังตรึง)
_FAIL_IDS = {c['id'] for e in EPICS if e['key'] == 'rgfail' for f in e['feats'] for c in f['cases']}
_RETIRE_WANT = {i for i in _ids if not i.startswith('TC-OCT-') and (i in _new.REPLACED or i.endswith('-RF') or i in _FAIL_IDS)}
RETIRED = sorted(i for i in _RETIRE_WANT if not _has_data(i))
KEPT_WITH_DATA = sorted(_RETIRE_WANT - set(RETIRED))   # อยากเอาออกแต่มีผลบันทึกแล้ว → คงไว้
_retired = set(RETIRED)
EPICS = [e2 for e2 in (dict(_e, feats=[f2 for f2 in (dict(_f, cases=[c for c in _f['cases'] if c['id'] not in _retired])
                                                    for _f in _e['feats']) if f2['cases']]) for _e in EPICS) if e2['feats']]
_cnt = lambda keys: sum(len(f['cases']) for e in EPICS if e['key'] in keys for f in e['feats'])
_N_HAPPY = _cnt({'rg1', 'rg2', 'rg3', 'rg4', 'rg5', 'rg6', 'rge2e'})
_N_NEW = _cnt({'ranew'})
_N_FF = sum(len(f['cases']) for e in EPICS for f in e['feats']) - _N_HAPPY - _N_NEW
print(f'retired {len(RETIRED)} เคส (ไม่มีผลบันทึก) · คงไว้เพราะมีผลแล้ว {len(KEPT_WITH_DATA)} เคส')

META.update(
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression (Happy Path + ฟีเจอร์ ก.ย. + อัปเดต UAT 6 ต.ค.)',
    sub=('รอบ Regression <b>จ 5 – ศ 9 ต.ค. 2569</b> · รายงานเดียวรวมทุกเคสของ takra-ai (Live) · '
         f'MVP-1 happy path + avatar/voice self-service {_N_HAPPY} เคส + ใบงาน TAKRA-1223–1230 · '
         f'tool-calling auto-reply {_N_FF} เคส + 🆕 อัปเดตตาม UAT 6 ต.ค. {_N_NEW} เคส = {_N_HAPPY + _N_FF + _N_NEW} เคส · '
         'Target: <b>UAT</b> https://uat-live.takra.ai'),
    groups_label='ขั้นที่ 1–6 + Full E2E · ใบงาน 1223–1230 · tool-calling (ARS · SRF · RPL · RSK · COM · RCP) · 🆕 อัปเดต UAT 6 ต.ค.',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — takra-ai (Live) <b>รายงานเดียว</b> (รวม 6 ต.ค.): '
          f'① <b>MVP-1 happy path ทั้งเส้น</b> + avatar/voice self-service ({_N_HAPPY} เคส) เดินตามขั้นที่ 1 → ขั้นที่ 6 แล้วปิดท้ายด้วย Full E2E · '
          f'② <b>ฟีเจอร์ ก.ย.</b> ({_N_FF} เคส · เดิมอยู่รายงาน fail-features) — ใบงาน TAKRA-1223–1230 และ tool-calling รันทั้งชุด '
          '(กลุ่ม "จุดที่เคย FAIL ในรายงาน MVP1+2" เอาออกแล้ว 6 ต.ค. — เคส MVP-1 ซ้ำกับขั้นที่ 1–6/มีเคส 🆕 แทน · Epic 14 RTMP ยังไม่ขึ้น UAT) · '
          f'③ <b>🆕 อัปเดตตาม UAT 6 ต.ค.</b> ({_N_NEW} เคส · ต่อท้าย) — ตรวจโค้ดทั้งโปรเจกต์ (origin/uat 5e79e582 = develop) ทุกหน้าเทียบทุกเคส: UI/ฟีเจอร์ที่เปลี่ยน → เคสแทน · ฟีเจอร์ที่ยังไม่มีเคส → เคสใหม่ (เฉพาะ P0/P1) '
          'เขียนเป็นเคสใหม่ <b>ไม่แก้เคสเดิม</b> · ที่มาของแต่ละเคสบอกว่า "แทนเคสเดิม" ตัวไหน'
          f'<br>🧹 <b>เอาเคสเดิมออกแล้ว {len(RETIRED)} เคส</b> (6 ต.ค.): เคสที่ UI เปลี่ยนแล้วมีเคส 🆕 แทน + เคส <code>-RF</code> ที่ซ้ำกับเคสหลักในขั้นที่ 1–6 '
          f'— เอาออกเฉพาะเคสที่ยังไม่มีผลบันทึก · อีก {len(KEPT_WITH_DATA)} เคสที่ถูกแทนแต่มีผลบันทึกแล้วคงไว้ (ดูผลเดิมได้ · รอบนี้ให้เทสที่เคส 🆕 แทน)'
          '<br>📎 เคสคัดจาก: รายงานรวม MVP1+2 (<code>regai1.json</code> · <code>regai2_fails.json</code>) · '
          '<code>ai_tickets_1223_cases.py</code> · <code>ai_autoreply_cases.py</code> · แผนรวม: '
          '<a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    noui_note=_ff.META['noui_note'], noui_badge=_ff.META['noui_badge'],
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · Happy Path + ฟีเจอร์ ก.ย. + อัปเดต UAT 6 ต.ค.',
)
