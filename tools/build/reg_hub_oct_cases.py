#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""รอบ Regression 5–9 ต.ค. 2569 — takra-hub · เฉพาะ MVP-2 (ตัด MVP-1 ออก — สั่ง 2026-09-29)
คัดจาก hub_mvp2_cases.py + hub_mvp2_rbac_cases.py: P0+P1 เฉพาะเคสที่ UI มีจริง (ui=True — ก้อน QR/refund/coupon ที่ยังไม่ build ไม่เข้ารอบ)
build: python3 tools/build/build_hub_report.py reghub"""
import hub_mvp2_cases as _m2
import hub_mvp2_rbac_cases as _rbac

KINDS = dict(_rbac.KINDS)
KINDS.update(_m2.KINDS)


def _pick(epics, prefix):
    out = []
    for _e in epics:
        _feats = []
        for _f in _e['feats']:
            _cs = [c for c in _f['cases'] if c['prio'] in ('P0', 'P1') and c.get('ui', True)]
            if _cs:
                _feats.append(dict(_f, featkey=prefix + '-' + _f['featkey'], cases=_cs))
        if _feats:
            out.append(dict(_e, key=prefix + _e['key'], feats=_feats))
    return out


EPICS = _pick(_m2.EPICS, 'rg') + _pick(_rbac.EPICS, 'rgx')

_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), f'duplicate ids: {sorted(set(i for i in _ids if _ids.count(i) > 1))}'

META = dict(
    out_rel='projects/takra-hub/2026/10/reports/takra-hub-regression-oct0509-ui-test-cases-table.html',
    title='[REG 5–9 ต.ค.] TAKRA Hub — Regression MVP-2 Test Cases',
    emoji='🧾', uid_start=15001, download='takra-hub-regression-oct0509-ui-test-cases.html',
    back='https://wanlee-tankunnatam.github.io/qa-test-reports/?project=hub',
    sub='รอบ Regression <b>พ 7 ต.ค. 2569</b> · เฉพาะ MVP-2: RBAC/สิทธิ์พนักงาน · เอกสารกฎหมาย · Affiliate · หน้างาน CS/ทีม — P0+P1 เฉพาะที่ UI มีจริง',
    groups_label='MVP-2 + RBAC/Affiliate',
    note=('🧪 <b>รอบ Regression 5–9 ต.ค. 2569 — เฉพาะ MVP-2 (ตัด MVP-1 ออกตามสั่ง 29 ก.ย.)</b>: คัดจากรายงาน MVP-2 (117 เคส) + RBAC/Aff (82 เคส) — <b>P0+P1 เฉพาะเคสที่ UI มีจริง</b> · '
          'ก้อนที่ยังไม่ build (QR/PromptPay · Payment recovery · Refund · Coupon · Campaign — 63 เคส ⛔ ไม่พบใน UI) <b>ไม่เข้ารอบนี้</b> รอ dev ส่งมอบแล้วค่อยเปิดรอบของมันเอง'
          '<br>⚠️ บัคตีกลับ TKH-50/121/239 re-test เมื่อ dev ปิด · ของใหม่ VAT/ใบเสร็จ/รวมสลิป ตรวจซ้ำตอนเดิน flow ที่เกี่ยว'
          '<br>📎 แก้เคสที่ชุดหลัก (<code>hub_mvp2_cases.py</code> · <code>hub_mvp2_rbac_cases.py</code>) แล้ว build ใหม่ · แผนรวม: <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/timeline/regression-plan.html#plan">regression-plan</a>'),
    footer='Regression 5–9 ต.ค. 2569 · takra-hub (MVP-2)',
)
