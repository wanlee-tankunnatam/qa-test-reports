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
# ตั้งแต่ 6 ต.ค. บันทึกผลที่รายงาน "แยกตามเมนู" (reg_ai_bymenu_oct_cases · uid เดิม) → นับผลจากไฟล์นั้นด้วย
_MENU_OUT = _OUT.parent / 'takra-ai-regression-oct0509-bymenu-ui-test-cases-table.html'
_m2 = _re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', _MENU_OUT.read_text(encoding='utf-8')) if _MENU_OUT.exists() else None
_STORE = {**_STORE, **(json.loads(_m2.group(1).strip() or '{}') if _m2 else {})}
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

# ── จัดฉากก่อนไลฟ์ทุกครั้ง (สั่ง 2026-10-06): ข้อความ "AI Live" อยู่หน้าสุด + สุ่มฉากหลัง ──
# ใส่ตอน build ให้ทุกเคสที่ต้องไลฟ์ (เคสต้นทางไม่แตะ · uid/ผลเทสไม่เปลี่ยน):
#   ① มี step กด "เริ่มไลฟ์" ใน Studio → แทรก step จัดฉากก่อนจุดกด (ตัด step เดิมเป็น 2 ท่อนถ้าประโยคเดียวพาเข้า Studio แล้วกดเลย)
#      (เฉพาะเมื่อกดต่อจนไลฟ์จริง "ไลฟ์เลย"/"เริ่มออกอากาศ" — เคสที่กดแค่ดู "ตรวจก่อนไลฟ์" หรือ "ตั้งเวลา" ไม่แตะ)
#   ② ไม่มี step กดเริ่มไลฟ์ แต่ต้องมีไลฟ์ออกอากาศอยู่ (Precondition / กด "เริ่มออกอากาศ" รอบที่เตรียมไว้) → เติมบรรทัด Precondition
# คำ UI ลอกจาก takra-ai origin/uat (studio.ts · studioPanels.ts · inspector-panel.tsx ปุ่ม "AI Live")
SCENE_SETUP_STEP = (
    'จัดฉากก่อนไลฟ์ (ทำทุกครั้งที่ต้องไลฟ์ · ทุกฉากในไลฟ์): '
    '⓪ อวาตาร์ Graham เท่านั้น — ที่หัวข้อ "ผู้นำเสนอ" ถ้า "อวาตาร์ของไลฟ์นี้" ไม่ใช่ "Graham (พื้นหลังเขียว)" ให้กดแถวนั้น '
    'พิมพ์ "Graham" ในช่องค้นหา เลือก "Graham (พื้นหลังเขียว)" แล้วกด "นำไปใช้" (ห้ามใช้อวาตาร์ตัวอื่นเด็ดขาด) '
    '① สุ่มฉากหลัง — ถ้าฉากยังไม่มีฉากหลัง กด "เพิ่ม Layer" เลือก "รูปภาพ" หรือ "วิดีโอ" ในหมวด "ฉากหลัง / สื่อ" แล้วกด "เพิ่มลงในฉาก" · '
    'ถ้ามีอยู่แล้ว เลือก layer ฉากหลังนั้นแล้วกด "เปลี่ยนรูปภาพ" หรือ "เปลี่ยนวิดีโอ" — ในหน้าต่างคลังสื่อสุ่มเลือกไฟล์ที่ไม่ซ้ำกับรอบก่อน แล้วกด "ใส่ลงในฉาก" (หรือ "เลือก") '
    '② ข้อความ "AI Live" หน้าสุด — ถ้ายังไม่มี กด "เพิ่ม Layer" เลือก "ข้อความ" กด "เพิ่มลงในฉาก" แล้วกดปุ่ม "AI Live" ใต้หัวข้อ "เนื้อหาข้อความ" · '
    'เลือก layer ข้อความนี้แล้วกด "เลื่อนขึ้นหน้า" จนอยู่หน้าสุด ไม่ถูกอวาตาร์หรือ layer อื่นบัง')
SCENE_SETUP_PRE = ('ไลฟ์ที่ใช้ในเคสนี้เริ่มจากฉากที่จัดตามกติกาจัดฉากก่อนไลฟ์: ใช้อวาตาร์ "Graham (พื้นหลังเขียว)" เท่านั้น (ห้ามตัวอื่นเด็ดขาด) · มี layer ข้อความ "AI Live" อยู่หน้าสุด (ไม่ถูกอวาตาร์หรือ layer อื่นบัง) '
                   'และสุ่มฉากหลังใหม่จากคลังสื่อ (ไม่ซ้ำกับรอบก่อน)')
SCENE_GRAHAM_DATA = 'อวาตาร์: "Graham (พื้นหลังเขียว)" เท่านั้น — ห้ามใช้อวาตาร์ตัวอื่นเด็ดขาด'
# เคสที่สโคปต้องใช้อวาตาร์อื่น — ยังติดกติกา Graham แต่บอกให้ลง SKIP ถ้า Graham ใช้กับเคสนี้ไม่ได้
SCENE_GRAHAM_CONFLICT = {
    'TC-OCT-S.8': '⚠️ รอบนี้ใช้อวาตาร์ "Graham (พื้นหลังเขียว)" เท่านั้น — เคสนี้ต้องใช้อวาตาร์ selfhost · ถ้า Graham ไม่ใช่อวาตาร์ selfhost ให้ลง SKIP (ห้ามเปลี่ยนไปใช้อวาตาร์ตัวอื่น)',
}
_PRESS_LIVE = _re.compile(r'(?:ใน Studio\s*)?กด(?:ปุ่ม)?\s*"เริ่มไลฟ์"')
_GO_LIVE = _re.compile(r'(?:กด(?:ปุ่ม)?|→|และ)\s*"(?:ไลฟ์เลย|เริ่มออกอากาศ|เริ่มไลฟ์เลย)"')   # กดจริง ไม่ใช่แค่ "ดูปุ่ม"/"เลือกแท็บ"
_ON_AIR = _re.compile(r'(?<!ไม่มีไลฟ์อื่น)กำลังออกอากาศ|ระหว่างไลฟ์|ระหว่างออกอากาศ|ไลฟ์อยู่|ออกอากาศอยู่|เริ่มออกอากาศแล้ว|กำลังไลฟ์')
_TAIL = _re.compile(r'(?:\s|แล้ว|จากนั้น|และ|·|—|,)+$')


def _graham(c):
    data = [d for d in c.get('data', []) if d != 'อวาตาร์: Graham เท่านั้น']   # แทนบรรทัดเดิมของกติกา 5 ต.ค. ไม่ให้ซ้ำ
    c = dict(c, data=[SCENE_GRAHAM_DATA] + data)
    if c['id'] in SCENE_GRAHAM_CONFLICT:   # ใส่บน Precondition ให้เห็นก่อนเริ่ม (note รายเคสไม่ถูกแสดงในรายงาน)
        c['pre'] = [SCENE_GRAHAM_CONFLICT[c['id']]] + list(c.get('pre', []))
    return c


def _scene_setup(c):
    c2, how = _scene_setup_raw(c)
    return (_graham(c2), how) if how else (c2, how)


def _scene_setup_raw(c):
    steps = list(c['steps'])
    for i, s in enumerate(steps):
        m = _PRESS_LIVE.search(s)
        if not m or not _GO_LIVE.search(' '.join([s[m.start():]] + steps[i + 1:])):
            continue   # กด "เริ่มไลฟ์" แค่เปิดดูตรวจก่อนไลฟ์/ตั้งเวลา ไม่ได้ไลฟ์จริง → ไม่แทรก (เช่น TC-OCT-R.17 ที่ต้องไม่มี "AI Live")
        head = _TAIL.sub('', s[:m.start()])
        if len(head) < 15:   # step ขึ้นต้นด้วยการกดเริ่มไลฟ์ (step ก่อนหน้าพาเข้า Studio แล้ว)
            return dict(c, steps=steps[:i] + [SCENE_SETUP_STEP] + steps[i:]), 'step'
        return dict(c, steps=steps[:i] + [head, SCENE_SETUP_STEP, s[m.start():]] + steps[i + 1:]), 'split'
    if _GO_LIVE.search(' '.join(steps)) or _ON_AIR.search(' '.join(c.get('pre', []))):
        return dict(c, pre=list(c.get('pre', [])) + [SCENE_SETUP_PRE]), 'pre'
    return c, None


# เคสที่ต้องไลฟ์แต่ regex ด้านบนจับไม่ได้ (ตรวจ 6 ต.ค. · สั่งย้ำ "อวาตาร์ Graham · layer "AI Live" เสมอ · สุ่มฉากหลัง เท่านั้น"):
#   เริ่มไลฟ์ด้วยคำอื่น ("เริ่มไลฟ์ใหม่" / ส่งตรงเข้า TikTok / ไลฟ์จริง) · E2E (steps อยู่ใน phases) ·
#   Precondition ต้องมีไลฟ์ที่ออกอากาศจบแล้วซึ่งผู้เทสต้องไลฟ์เอง → เติมบรรทัดกติกาใน Precondition
SCENE_EXTRA_PRE = {
    'T1224.8', 'T1228.5', 'T1229.8', 'TC-RA.4', 'TC-RA.5',
    'T1223.5', 'T1223.6', 'T1223.7', 'T1223.8', 'T1223.9', 'T1223.10', 'T1223.11',
    'TC-E2E.1', 'TC-E2E.2', 'TC-E2E.3', 'TC-E2E.4', 'TC-E2E.5',
    'TC-OCT-M.4', 'TC-OCT-M.6', 'TC-OCT-M.14', 'TC-N2.1', 'TC-N2.2', 'TC-N2.3', 'TC-OCT-U.2', 'TC-OCT-Q.3',
    # 6 ต.ค. รอบ 2 (สั่ง "ทุกไลฟ์ต้องมีอวาตาร์ Graham ทุกเคสที่ต้องไลฟ์จริง"): ต้องมีรอบที่จบแล้ว · อาจไลฟ์จริงเพื่อใช้ชั่วโมงอวาตาร์ · ดูสรุปไลฟ์บน remote
    'TC-OCT-Q.11', 'TC-OCT-G.12', 'T1226.3',
}


def _scene_setup_all(c):
    c2, how = _scene_setup(c)
    if not how and c['id'] in SCENE_EXTRA_PRE:
        return _graham(dict(c, pre=list(c.get('pre', [])) + [SCENE_SETUP_PRE])), 'pre'
    return c2, how


SCENE_SETUP_COUNT = {'step': 0, 'split': 0, 'pre': 0}
for _e in EPICS:
    for _f in _e['feats']:
        _out = []
        for _c in _f['cases']:
            _c2, _how = _scene_setup_all(_c)
            if _how:
                SCENE_SETUP_COUNT[_how] += 1
            _out.append(_c2)
        _f['cases'] = _out
_N_SCENE = sum(SCENE_SETUP_COUNT.values())
print(f'จัดฉากก่อนไลฟ์ {_N_SCENE} เคส · {SCENE_SETUP_COUNT}')

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
          f'<br>🎬 <b>จัดฉากก่อนไลฟ์ทุกครั้ง</b> (6 ต.ค.): ทุกเคสที่ต้องไลฟ์ใช้อวาตาร์ <b>"Graham (พื้นหลังเขียว)" เท่านั้น</b> (ห้ามตัวอื่นเด็ดขาด) · ใส่ layer ข้อความ <b>"AI Live"</b> ไว้หน้าสุด (ไม่ถูกอวาตาร์หรือ layer อื่นบัง) '
          f'และ<b>สุ่มฉากหลัง</b>ใหม่จากคลังสื่อทุกรอบ (ไม่ซ้ำรอบก่อน) — แทรกเป็น step ก่อนกด "เริ่มไลฟ์" {SCENE_SETUP_COUNT["step"] + SCENE_SETUP_COUNT["split"]} เคส · '
          f'เติมใน Precondition ของเคสที่ใช้รอบไลฟ์ที่เตรียมไว้/กำลังออกอากาศ {SCENE_SETUP_COUNT["pre"]} เคส · '
          'เคสที่กด "เริ่มไลฟ์" แค่ดู "ตรวจก่อนไลฟ์" หรือตั้งเวลาไม่ใส่ (TC-OCT-R.17 ต้องไม่มี "AI Live" เพื่อดูข้อเตือน)'
          '<br>📎 เคสคัดจาก: รายงานรวม MVP1+2 (<code>regai1.json</code> · <code>regai2_fails.json</code>) · '
          '<code>ai_tickets_1223_cases.py</code> · <code>ai_autoreply_cases.py</code> · แผนรวม: '
          '<a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    noui_note=_ff.META['noui_note'], noui_badge=_ff.META['noui_badge'],
    footer='Regression 5–9 ต.ค. 2569 · takra-ai (Live) · Happy Path + ฟีเจอร์ ก.ย. + อัปเดต UAT 6 ต.ค.',
)

# ── ย้ายไปบันทึกผลที่รายงาน "แยกตามเมนู/ฟีเจอร์" (สั่ง 2026-10-06) — ไฟล์นี้คงไว้ดูผลเดิม ──
# NOTE_BODY = note เดิม (รายงานแยกตามเมนูดึงไปใช้ต่อ) · ป้ายย้ายใส่เฉพาะไฟล์นี้
NOTE_BODY = META['note']
MOVED_URL = 'https://wanlee-tankunnatam.github.io/qa-test-reports/projects/takra-ai/2026/10/reports/takra-ai-regression-oct0509-bymenu-ui-test-cases-table.html'
META.update(
    title='[REG 5–9 ต.ค.] TAKRA AI · Live — Regression (ไฟล์เดิม · ย้ายไปรายงานแยกตามเมนูแล้ว)',
    note=('<div style="padding:10px 12px;margin-bottom:8px;border:2px solid #dc2626;border-radius:8px;background:#fef2f2;color:#991b1b;font-size:14px">'
          '⚠️ <b>เลิกบันทึกผลที่ไฟล์นี้แล้ว (6 ต.ค. 2569)</b> — เคสชุดเดียวกันทั้งหมดพร้อมผลเทสที่บันทึกไว้ ย้ายไป '
          f'<a href="{MOVED_URL}"><b>รายงานแยกตามเมนู/ฟีเจอร์</b></a> แล้ว · บันทึกผลที่นั่นเท่านั้น</div>' + NOTE_BODY),
)
