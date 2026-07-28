#!/usr/bin/env python3
"""กู้แถวหัวข้อ epic/feature (epicrow + featrow) ของรายงาน mvp1-2 ที่หายจากการถูกปุ่มเซฟทับ

canonical = commit 73cd186 (เวอร์ชันแยกไฟล์ Windows/mac — section ครบ 24 epic / 43 feat)
วิธี: ถอดแถว section เดิมที่อยู่ในขอบเขต canonical ออก แล้วแทรกชุด canonical กลับ
ตามตำแหน่งเคสจริงของไฟล์ปลายทาง (เฉพาะกลุ่มที่มีเคสอยู่ในไฟล์นั้น)
หมวดที่มาทีหลัง (e23 · e24 · e26 · epic17/fullflow ของ E2E redesign) คงของปัจจุบันไว้
"""
import re
import subprocess
import sys

CANON_COMMIT = '73cd186'
CANON_PATH = 'projects/takra-rerun/2026/07/reports/takra-rerun-mvp1-2-ui-test-cases-table-windows.html'
KEEP_EPICS = {'e23', 'e24', 'e26', '17'}          # ของใหม่/ของที่ redesign แล้ว — ไม่แตะ
KEEP_FEATS = {'qa-keyword-reply', 'session-analytics', 'war-room', 'fullflow'}


def parse_rows(src):
    """คืน list ของ (kind, key, html, cids_after) ตามลำดับไฟล์"""
    parts = re.split(r'(?=<tr class=")', src)
    rows = []
    for b in parts:
        me = re.search(r'^<tr class="epicrow[^"]*"[^>]*data-epic="([^"]*)"', b)
        mf = re.search(r'^<tr class="featrow[^"]*" data-featkey="([^"]+)"', b)
        mc = re.search(r'^<tr class="trow[^"]*"', b)
        cid = re.search(r'<td class="cid">([^<]*)</td>', b)
        if me:
            rows.append(['EPIC', me.group(1), b, []])
        elif mf:
            rows.append(['FEAT', mf.group(1), b, []])
        elif mc and cid and rows:
            rows[-1][3].append(cid.group(1).strip())
        elif mc and cid:
            rows.append(['HEAD', '', '', [cid.group(1).strip()]])
    return rows


def row_html(b):
    # ตัดให้จบที่ </tr> แรก (block จาก split อาจพ่วงบรรทัดว่าง/คอมเมนต์ตามหลัง)
    m = re.search(r'^.*?</tr>\n?', b, re.S)
    return m.group(0) if m else b


def restore(path):
    canon_src = subprocess.run(['git', 'show', f'{CANON_COMMIT}:{CANON_PATH}'],
                               capture_output=True, text=True).stdout
    canon = parse_rows(canon_src)

    # สร้างแผน: ต่อ featrow canonical → (epic_html ถ้าเป็น feat แรกของ epic, feat_html, first-cids)
    plan = []          # (epic_key, epic_html|None, feat_key, feat_html, cids)
    cur_epic = (None, None)
    emitted_epic = set()
    for kind, key, b, cids in canon:
        if kind == 'EPIC':
            cur_epic = (key, row_html(b))
        elif kind == 'FEAT':
            ek, eh = cur_epic
            plan.append((ek, eh if ek not in emitted_epic else None, key, row_html(b), cids))
            emitted_epic.add(ek)

    canon_feat_keys = {p[2] for p in plan}
    canon_epic_keys = {p[0] for p in plan}

    s = open(path, encoding='utf-8').read()
    # 1) ถอด section เดิมในขอบเขต canonical (คงชุด KEEP ไว้)
    def strip_row(m):
        b = m.group(0)
        me = re.search(r'data-epic="([^"]*)"', b)
        mf = re.search(r'data-featkey="([^"]+)"', b)
        if me and me.group(1) in canon_epic_keys and me.group(1) not in KEEP_EPICS:
            return ''
        if mf and mf.group(1) not in KEEP_FEATS and (mf.group(1) in canon_feat_keys or True):
            # featrow ที่ไม่ใช่ชุด KEEP — ถอดทั้งหมดในขอบเขต mvp1-2 (จะถูกแทรกกลับจาก canonical)
            return ''
        return b
    s = re.sub(r'<tr class="(?:epicrow|featrow)[^"]*"[^>]*>.*?</tr>\n?', strip_row, s, flags=re.S)

    # 2) หา cid แรกของแต่ละกลุ่มที่มีอยู่จริงในไฟล์นี้ แล้วแทรก section ก่อน trow ของ cid นั้น
    present = set(re.findall(r'<td class="cid">([^<]*)</td>', s))
    inserted_epics = set()
    n_epic = n_feat = 0
    for ek, eh, fk, fh, cids in plan:
        if ek in KEEP_EPICS or fk in KEEP_FEATS:
            continue          # ชุดที่คงของปัจจุบันไว้ — ห้ามแทรกซ้ำ
        first = next((c for c in cids if c in present), None)
        if not first:
            continue
        i = s.find(f'<td class="cid">{first}</td>')
        j = s.rfind('<tr class="trow', 0, i)
        ins = ''
        if eh and ek not in inserted_epics:
            ins += eh
            inserted_epics.add(ek)
            n_epic += 1
        ins += fh
        n_feat += 1
        s = s[:j] + ins + s[j:]

    open(path, 'w', encoding='utf-8').write(s)
    ep = len(re.findall(r'class="epicrow"', s))
    ft = len(re.findall(r'class="featrow"', s))
    print(f'{path.split("/")[-1]}: แทรก epic {n_epic} · feat {n_feat} → รวมในไฟล์ epic {ep} · feat {ft}')


for p in sys.argv[1:]:
    restore(p)
