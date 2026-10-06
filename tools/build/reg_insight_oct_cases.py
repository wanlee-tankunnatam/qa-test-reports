#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-insight · คู่ OS รายงานเดียว (os_cols=True)

3 ก้อน (~70 เคส):
  1. Live Readiness ทั้งชุด 33 เคส — import EPICS จาก insight_live_readiness_cases.py ตรง ๆ (เนื้อหาไม่แก้)
  2. จุดที่เคย FAIL ของ Dashboard / Reports / Membership (กลุ่มนี้ถูกตัดออก — roles/permission) (กลุ่ม 'rifail') — อ่าน store-data
     จากรายงานที่เผยแพร่ projects/takra-insight/2026/09/reports/takra-insight-mvp2-{dashboard,reports,membership}-ui-test-cases-table.html
     · รูป store key ที่พบจริง: key เป็น `tc-N` เฉย ๆ (ไม่มี suffix -mac/-win) — Mac เก็บใน store[uid].st
       และ Windows เก็บใน store[uid].stw (ตามกลไก os_cols ของ build_hub_report.py)
     · เอาเคสที่ st=='fail' หรือ stw=='fail' → ดึงเคสเต็มจากโมดูลต้นทาง insight_mvp2_{dashboard,reports,membership}_cases.py
       ตาม id (เนื้อหาไม่แก้ · เติมบรรทัด "ผลรอบก่อน: …" ต่อท้าย src เพราะ harness ไม่ render ฟิลด์ note ต่อเคส)
     · id ระหว่างโมดูลไม่ชนกัน (TC-LR-* / TC-DASH-* / TC-RPT-* / TC-BYOK-*) จึงไม่ต้องเติม prefix
  3. BYOK smoke (กลุ่ม 'ribyok') — เฉพาะ P0 จาก insight_mvp2_byok_cases.py (เนื้อหาไม่แก้)

ผล fail รอบก่อน (สแนปช็อตตอน generate โมดูลนี้ · 2026-09-29):
  Dashboard 10 · Reports 3 · Membership 13 — ดู FAIL_PREV ด้านล่าง

build: python3 tools/build/build_hub_report.py reginsight"""
import insight_live_readiness_cases as _lr
import insight_mvp2_dashboard_cases as _dash
import insight_mvp2_reports_cases as _rpt
import insight_mvp2_membership_cases as _mem
import insight_mvp2_byok_cases as _byok
import insight_reg_oct_new_cases as _new

# KINDS รวมจากทุกโมดูลที่ใช้ (dashboard เป็น superset: มี validation เพิ่มจาก LR)
KINDS = dict(_lr.KINDS)
KINDS.update(_dash.KINDS)
KINDS.update(_rpt.KINDS)
KINDS.update(_mem.KINDS)
KINDS.update(_byok.KINDS)
for _k, _v in _new.KINDS.items():
    KINDS.setdefault(_k, _v)

# ── ก้อน 2 · ผล FAIL รอบก่อนจาก store-data ของรายงานที่เผยแพร่ (st=Mac · stw=Windows) ──
FAIL_PREV = {
    # dashboard (uid 2401–)
    'TC-DASH-A.3': ('fail', 'pass'),
    'TC-DASH-A.4': ('fail', 'pass'),
    'TC-DASH-A.5': ('fail', 'pass'),
    'TC-DASH-B.3': ('pass', 'fail'),
    'TC-DASH-D.2': ('fail', 'pass'),
    'TC-DASH-E.2': ('fail', 'pass'),
    'TC-DASH-E.4': ('fail', 'block'),
    'TC-DASH-F.1': ('fail', 'pass'),
    'TC-DASH-G.1': ('fail', 'pass'),
    'TC-DASH-H.1': ('fail', 'fail'),
    # reports (uid 2501–)
    'TC-RPT-B.8': ('fail', 'fail'),
    'TC-RPT-C.4': ('fail', 'block'),
    'TC-RPT-C.6': ('fail', 'fail'),
    # membership (uid 2601–)
    'TC-MEM-C.3': ('fail', 'block'),
    'TC-MEM-C.4': ('fail', 'block'),
    'TC-MEM-D.2': ('fail', 'pass'),
    'TC-MEM-D.4': ('fail', 'pass'),
    'TC-MEM-D.5': ('fail', 'pass'),
    'TC-MEM-D.6': ('fail', 'pass'),
    'TC-MEM-E.2': ('fail', 'block'),
    'TC-MEM-G.1': ('fail', 'block'),
    'TC-MEM-G.2': ('fail', 'block'),
    'TC-MEM-G.3': ('fail', 'block'),
    'TC-MEM-G.4': ('fail', 'block'),
    'TC-MEM-G.5': ('fail', 'block'),
    'TC-MEM-G.6': ('fail', 'block'),
}

_ST_TH = {'pass': 'PASS', 'fail': 'FAIL', 'block': 'BLOCKED', 'hold': 'HOLD', 'skip': 'SKIP'}


def _fail_cases(mod, label):
    """ดึงเคสเต็มจากโมดูลต้นทางตาม id ที่ fail — คงเนื้อหาเดิม เติมผลรอบก่อนต่อท้าย src"""
    out = []
    for e in mod.EPICS:
        for f in e['feats']:
            for c in f['cases']:
                prev = FAIL_PREV.get(c['id'])
                if not prev:
                    continue
                mac, win = prev
                tag = f'ผลรอบก่อน: FAIL — 🍎 Mac={_ST_TH[mac]} · 🪟 Win={_ST_TH[win]} (รายงาน {label} · 2026/09)'
                out.append(dict(c, src=c['src'] + ' · ' + tag))
    return out


_f_dash = _fail_cases(_dash, 'Dashboard')
_f_rpt = _fail_cases(_rpt, 'Reports')
_f_mem = _fail_cases(_mem, 'Membership')
assert len(_f_dash) + len(_f_rpt) + len(_f_mem) == len(FAIL_PREV), \
    (len(_f_dash), len(_f_rpt), len(_f_mem), len(FAIL_PREV))

_RIFAIL = dict(key='rifail', chip='❌ RI·FAIL', emoji='❌',
               title='จุดที่เคย FAIL รอบก่อน — Dashboard · Reports · Membership (re-test)',
               feats=[
                   dict(featkey='rifail-dash', title='Dashboard (Epic 5) — เคย FAIL', cases=_f_dash),
                   dict(featkey='rifail-rpt', title='Reports (Epic 7) — เคย FAIL', cases=_f_rpt),
                   dict(featkey='rifail-mem', title='Membership (Epic 9) — เคย FAIL', cases=_f_mem),
               ])

# ── ก้อน 3 · BYOK smoke = เฉพาะ P0 (รวมทุกกลุ่มเดิมเป็น epic เดียว 'ribyok') ──
_byok_feats = []
for _e in _byok.EPICS:
    _cs = [c for _f in _e['feats'] for c in _f['cases'] if c['prio'] == 'P0']
    if _cs:
        _byok_feats.append(dict(featkey='riby-' + _e['key'], title=_e['chip'], cases=_cs))
_RIBYOK = dict(key='ribyok', chip='🔑 RI·BYOK smoke', emoji='🔑',
               title='BYOK smoke — AI Provider (Epic 4) เฉพาะ P0', feats=_byok_feats)

# ── EPICS = LR ทั้งชุด (ไม่แก้) + rifail + ribyok ──
EPICS = list(_lr.EPICS) + [_RIFAIL, _RIBYOK]

# ── ตัดเรื่อง roles/permission ออกจากรอบ Insight (สั่ง 2026-09-29) ──
# Membership ทั้งกลุ่ม (บทบาทจาก Hub · เมนูตามบทบาท · ถูกเอาออกจากทีม) + DASH role gate 2 เคส
# หมายเหตุ: dev ยกเลิก role gate ของเมนูแดชบอร์ดแล้ว (Story 6.3 rework) — สอดคล้องกับการตัดชุดนี้
EXCLUDE_ROLES = {'TC-DASH-A.3', 'TC-DASH-A.4'}
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (
        dict(_f0, cases=[c for c in _f0['cases'] if c['id'] not in EXCLUDE_ROLES and not c['id'].startswith('TC-MEM')])
        for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]

# ── ก้อน 4 · UI/ฟีเจอร์ใหม่หลัง 29 ก.ย. (เพิ่ม 6 ต.ค.) — ต่อท้ายเสมอ uid เคสเดิม (tc-14501–14553) จึงไม่เลื่อน ──
EPICS.append(_new.EPIC)

META = dict(
    out_rel='projects/takra-insight/2026/10/reports/takra-insight-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Insight — Regression Test Cases (คู่ 🪟/🍎)',
    emoji='📊', uid_start=14501, os_cols=True,
    download='takra-insight-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=insight',
    # sub / groups_label / note ตั้งท้ายไฟล์ — นับจากเคสที่อยู่ในรายงานจริง
    sub='', groups_label='', note='',
    footer='Regression 5–9 ต.ค. 2569 · takra-insight (คู่ Mac/Windows)',
)


# ── รอบนี้เอาแค่ P0 + P1 (ตัด P2 ออก — สั่ง 2026-09-29) ──
EPICS = [e2 for e2 in (
    dict(_e0, feats=[f2 for f2 in (dict(_f0, cases=[c for c in _f0['cases'] if c['prio'] in ('P0', 'P1')]) for _f0 in _e0['feats']) if f2['cases']])
    for _e0 in EPICS) if e2['feats']]

# ── ตัวเลขบนหัวรายงาน นับจากเคสที่อยู่ในรายงานจริง (หลังตัด roles + P2) ──
def _n(key):
    return sum(len(f['cases']) for e in EPICS if e['key'] == key for f in e['feats'])


def _nf(featkey):
    return sum(len(f['cases']) for e in EPICS for f in e['feats'] if f['featkey'] == featkey)


_n_lr = sum(_n(e['key']) for e in _lr.EPICS)
_n_fail, _n_byok, _n_new = _n('rifail'), _n('ribyok'), _n('rinew')
_n_all = sum(len(f['cases']) for e in EPICS for f in e['feats'])
META['sub'] = ('รอบ Regression <b>🪟 พ 7 ต.ค.</b> · <b>🍎 ศ 9 ต.ค. 2569</b> — สโคปเดียวกันทั้ง 2 OS · '
               f'Live Readiness รอบยืนยัน {_n_lr} + จุดที่เคย FAIL {_n_fail} + BYOK smoke (P0) {_n_byok} + '
               f'🆕 UI/ฟีเจอร์ใหม่ {_n_new} = {_n_all} เคส · บันทึกผลแยกคอลัมน์ 🍎 Mac / 🪟 Windows')
META['groups_label'] = 'LR 8 มิติ + ❌ RI·FAIL + 🔑 RI·BYOK + 🆕 RI·ใหม่ ต.ค.'
META['note'] = (
    '🧪 <b>รอบ Regression 5–9 ต.ค. 2569</b> — <b>🪟 Windows พ 7 ต.ค. · 🍎 Mac ศ 9 ต.ค.</b> สโคปเดียวกันทั้งสองวัน '
    '(Live Readiness ใช้ไลฟ์จริง<b>รอบเดียว</b> ดูจอสอง OS คู่กัน) · บันทึกผลแยกคอลัมน์ Mac/Windows ในหน้านี้'
    f'<br>📦 <b>4 ก้อน:</b> ① Live Readiness ทั้งชุด {_n_lr} เคส (D1–D8 · จาก <code>insight_live_readiness_cases.py</code> ไม่แก้เนื้อหา) · '
    f'② <b>❌ RI·FAIL</b> จุดที่เคย FAIL รอบก่อน {_n_fail} เคส (Dashboard {_nf("rifail-dash")} · Reports {_nf("rifail-rpt")} — '
    'Membership ตัดออกเพราะเป็นเรื่อง roles · ผลรอบก่อนเขียนกำกับท้าย Expected ของแต่ละเคส) · '
    f'③ <b>🔑 RI·BYOK smoke</b> {_n_byok} เคส (เฉพาะ P0 จาก <code>insight_mvp2_byok_cases.py</code>) · '
    f'④ <b>🆕 RI·ใหม่ ต.ค.</b> {_n_new} เคส — UI/ฟีเจอร์ที่ขึ้น UAT หลัง 29 ก.ย. ถึง 5 ต.ค. (origin/uat 7c26b9fe · '
    'จาก <code>insight_reg_oct_new_cases.py</code> · เพิ่ม 6 ต.ค. ต่อท้ายรายงาน ผลเทสเดิมไม่เลื่อน)'
    '<br>🆔 id เคสคงของเดิมจากชุดต้นทาง (TC-LR-* / TC-DASH-* / TC-RPT-* / TC-BYOK-* — ไม่ชนกัน จึงไม่เติม prefix) · เคสใหม่ใช้ TC-OCT-*'
    '<br>📎 แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>')
