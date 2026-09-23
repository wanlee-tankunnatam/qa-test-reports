#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build takra-ai MVP-1 (happy path) + MVP-2 (full-category) UI manual test case report.
Inputs: mvp1 report HTML (cards copied verbatim, filtered to happy path) + mvp2_epic*.json + mvp2_e2e.json
Output: new self-contained HTML using the same harness as takra-ai-mvp2-ui-test-cases-table.html
"""
import re, html, json, os, sys
from collections import Counter, OrderedDict

SCR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takra-ai-mvp1-2-sources")
REPO = '/Users/ice/Documents/other/qa-test-reports'
TPL = f'{REPO}/projects/takra-ai/2026/07/reports/takra-ai-mvp2-ui-test-cases-table.html'
MVP1 = f'{REPO}/projects/takra-ai/2026/07/reports/takra-ai-mvp1-ui-test-cases-table.html'
OUT_REL = 'projects/takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html'
OUT = f'{REPO}/{OUT_REL}'

TYPES = OrderedDict([
    ('happy', ('Happy Path', '✅', 'Flow ปกติ')),
    ('negative', ('Negative', '⛔', 'ข้อมูลผิด / Action ผิด')),
    ('boundary', ('Boundary / Edge', '🧩', 'Min / Max / ก่อนขอบ / ตรงขอบ / เกินขอบ')),
    ('validation', ('Validation', '🧪', 'Format · Required · Character · Length')),
    ('error', ('Exception / Error', '💥', 'API fail · Network fail · Server error · Timeout')),
    ('permission', ('Permission', '🔐', 'Role ไหนทำได้ / ทำไม่ได้')),
    ('data', ('Data', '🗂️', 'Empty · Null · Duplicate · Existing · Non-existing')),
])
# legacy → new (in case a source JSON still uses the old 8-type taxonomy)
LEGACY = {'edge': ('boundary', 'Edge'), 'empty': ('data', 'Empty'), 'duplicate': ('data', 'Duplicate')}


def norm_type(c):
    t = c.get('type')
    if t in LEGACY:
        t, sub = LEGACY[t]
        c['type'] = t
        c.setdefault('sub', sub)
    if t == 'happy' and not c.get('sub'):
        c['sub'] = 'Flow ปกติ'
    return c

# ---------- MVP-1 (happy path, carried over) ----------
MVP1_EXCL = {'TC-L1.4', 'TC-L1.5', 'TC-L1.8', 'TC-EN.1', 'TC-SA.2', 'TC-A2.4', 'TC-V2.4', 'TC-R2.2', 'TC-SC.4',
             'TC-SB.3', 'TC-SA3.2', 'TC-SA3.3', 'TC-RC.2', 'TC-PF.3', 'TC-HC.1', 'TC-RA.2', 'TC-PD.2'}
MVP1_EPIC_INFO = {
    '1': ('🚪', 'เข้าระบบ & รากฐาน Workspace', 'Epic 1 · FR1-6 · FR3a'),
    '2': ('📦', 'คลังของ Workspace — Avatar/Voice · สินค้า · คำเสี่ยง · สคริปต์', 'Epic 2 · FR7-13 · FR46 · FR67-72'),
    '3': ('🎬', 'สร้างไลฟ์ใน Studio', 'Epic 3 · FR14-33 · free-form single-canvas'),
    '4': ('📡', 'ออกอากาศ (Avatar Live · Phone-as-Camera)', 'Epic 4 · FR34-39'),
    '5': ('💬', 'แจ้งเตือน operator & Risk-block fallback', 'Epic 5 · FR44-45 · UI เท่านั้น'),
    '6': ('✨', 'AI ช่วยเขียน Script', 'Epic 6 · FR29-31 · value-add'),
    '7': ('🔄', 'Full E2E Flow — วิ่งครบลูปตั้งแต่ต้นจนจบ', 'E2E · ข้าม Epic 1-6'),
}
# steps that started mid-way in the source report → prepend entry step (steps-to-reproduce rule)
MVP1_STEP_FIX = {
    'TC-R2.6': 'เปิดเบราว์เซอร์ไปที่ https://uat-live.takra.ai แล้วเข้าสู่ระบบด้วยบัญชี Owner จากนั้นไปที่เมนู "คำเสี่ยง"',
    'TC-CT.1': 'เปิดเบราว์เซอร์ไปที่ https://uat-live.takra.ai แล้วเข้าสู่ระบบด้วยบัญชี Owner จากนั้นไปที่เมนู "ไลฟ์ของฉัน" แล้วเปิดไลฟ์ที่กำลังออกอากาศเข้าห้องคุมไลฟ์',
}


def load_mvp1():
    s = open(MVP1, encoding='utf-8').read()
    featlabels = {}
    for m in re.finditer(r'<tr class="featrow" data-featkey="([^"]+)"><td colspan="7">(.*?)</td></tr>', s):
        featlabels[m.group(1)] = m.group(2)
    parts = s.split('<tr class="trow')[1:]
    cases = []
    for p in parts:
        head = p[:p.find('>')]
        feat = re.search(r'data-feat="([^"]+)"', head).group(1)
        lvl = re.search(r'data-level="([^"]+)"', head).group(1)
        prio = re.search(r'data-prio="([^"]+)"', head).group(1)
        cid = re.search(r'<td class="cid">([^<]+)</td>', p).group(1)
        if re.search(r'\.E\d', cid):
            continue
        if cid in MVP1_EXCL:
            continue
        card_start = p.find('<div class="card">')
        card_end = p.find('<div class="sec"><h4>Status</h4>')
        card = p[card_start:card_end]
        title = re.search(r'<div class="h-title">(.*?)</div>', card, flags=re.S).group(1).strip()
        title = re.sub(r'^\[MVP1\]\s*', '', title)
        meta = re.search(r'<div class="h-prio">(.*?)</div>', card, flags=re.S).group(1).strip()
        fk = re.search(r'· (?:UI|E2E) · ([^ ]+) · Epic', meta)
        featkey = fk.group(1) if fk else 'fullflow'
        if cid in MVP1_STEP_FIX:
            card = card.replace('<h4>Test Steps</h4><ol><li>', '<h4>Test Steps</h4><ol><li>' + html.escape(MVP1_STEP_FIX[cid], quote=False) + '</li><li>', 1)
        epic = feat.replace('epic', '')
        cases.append(dict(id=cid, title=title, feat=epic, featkey=featkey, prio=prio, level=lvl, meta=meta, card=card))
    return cases, featlabels


# ---------- MVP-2 (authored JSON) ----------
MVP2_ORDER = [10, 15, 14, 9, 8, 12, 16, 99]
MVP2_EMOJI = {8: '📜', 9: '🖥️', 10: '🧑‍🎤', 12: '💳', 14: '📡', 15: '🎬', 16: '⚙️', 99: '🔄'}


def load_mvp2():
    epics = {}
    for n in MVP2_ORDER:
        fn = f'{SCR}/mvp2_e2e.json' if n == 99 else f'{SCR}/mvp2_epic{n}.json'
        if not os.path.exists(fn):
            print('WARN missing', fn)
            continue
        d = json.load(open(fn, encoding='utf-8'))
        epics[n] = d
    return epics


def esc(x):
    return html.escape(str(x), quote=False)


def li(items):
    return ''.join('<li>' + esc(i) + '</li>' for i in items)


def card_mvp2(c, featlabel, epic_n):
    tlabel, temoji, _d = TYPES.get(c['type'], (c['type'], '', ''))
    lvl = 'E2E' if c.get('level') == 'e2e' else 'UI'
    meta = f"Priority: <b>{esc(c['prio'])}</b> · {lvl} · {esc(featlabel)} · Epic {epic_n}"
    if c.get('story'):
        meta += f" · Story {esc(c['story'])}"
    meta += f" · ประเภท: <b>{temoji} {tlabel}</b>" + (f" › {esc(c['sub'])}" if c.get('sub') else '') + " · MVP-2"
    out = ['<div class="card">',
           f'  <div class="h-title">{esc(c["title"])}</div>',
           f'  <div class="h-prio">{meta}</div>']
    if c.get('ui_status') == 'not-in-ui' or c.get('ui_note'):
        note = c.get('ui_note') or 'ไม่พบใน UI (as of 2026-08-19) — เขียนจากสเปก'
        out.append(f'  <div class="note-box" style="margin:0 0 10px">⚠️ <b>สถานะ UI:</b> {esc(note)}</div>')
    out.append('  <div class="sec"><h4>Precondition</h4><ul>' + li(c.get('precondition') or ['—']) + '</ul></div>')
    out.append('  <div class="sec"><h4>Test Steps</h4><ol>' + li(c['steps']) + '</ol></div>')
    out.append('  <div class="sec"><h4>Test Data</h4><ul>' + li(c.get('test_data') or ['—']) + '</ul></div>')
    out.append('  <div class="grid">')
    out.append('    <div class="sec"><h4>Expected Result</h4><ul>' + li(c['expected']) + '</ul></div>')
    out.append('    <div class="sec"><h4>Actual Result</h4><textarea class="actualbox" rows="4" placeholder="— บันทึกผลตอนทดสอบ —"></textarea></div>')
    out.append('  </div>')
    return '\n'.join(out) + '\n'


def status_jira(uid):
    return f'''  <div class="sec"><h4>Status</h4><div class="statusrow">
    <span class="opt pass" data-uid="{uid}" data-st="pass">PASS</span>
    <span class="opt fail" data-uid="{uid}" data-st="fail">FAIL</span>
    <span class="opt hold" data-uid="{uid}" data-st="hold">HOLD</span>
    <span class="opt block" data-uid="{uid}" data-st="block">BLOCKED</span>
    <span class="opt skip" data-uid="{uid}" data-st="skip">SKIP</span>
  </div></div>
  <div class="sec jira-sec"><h4>🐞 Jira / Bug (ใส่ได้หลายลิงก์)</h4>
    <div class="jira-list" data-uid="{uid}"></div>
    <div class="jira-add"><input type="text" class="jira-input" data-uid="{uid}" placeholder="วางลิงก์ Jira หรือพิมพ์ TAK-123 แล้ว Enter"><button class="btn jira-btn" data-uid="{uid}">+ เพิ่มลิงก์</button></div>
  </div>
</div></td></tr>
'''


def trow(uid, cid, title, level, prio, mvp, featv, typ, ui_status, sub=''):
    lvlcls = 'lvl-e2e' if level == 'e2e' else 'lvl-ui'
    lvltxt = 'E2E' if level == 'e2e' else 'UI'
    tlabel, temoji, _d = TYPES.get(typ, (typ, '', ''))
    subtxt = f' › {esc(sub)}' if sub and typ != 'happy' else ''
    badge = f'<span class="ty ty-{typ}" title="{tlabel}">{temoji} {tlabel}{subtxt}</span>'
    if ui_status == 'not-in-ui':
        badge += ' <span class="edge-badge" title="ยังไม่พบหน้าจอนี้ใน UI (เขียนจากสเปก)">ไม่พบใน UI</span>'
    return (f'<tr class="trow" data-mvp="{mvp}" data-feat="{featv}" data-type="{typ}" data-level="{level}" data-prio="{prio}" onclick="tg(this)">\n'
            f'  <td><span class="tog">▸</span></td><td class="cid">{esc(cid)}</td>\n'
            f'  <td class="ctitle">{esc(title)} {badge}</td>\n'
            f'  <td class="lvl"><span class="lv {lvlcls}">{lvltxt}</span></td>\n'
            f'  <td><span class="prio {prio.lower()}">{prio}</span></td>\n'
            f'  <td class="status" data-uid="{uid}"><span class="stb pending">รอเทส</span></td>\n'
            f'  <td class="jira-cell" data-uid="{uid}"></td>\n'
            f'</tr>\n<tr class="detail"><td colspan="7">')


def owner_select(featkey):
    return (f'<span class="epic-owner-wrap">👤 <select class="feat-owner" data-featkey="{featkey}">'
            f'<option value="">— ผู้รับผิดชอบ —</option><option>Wanlee T (Ice)</option><option>Kachain B (Moss)</option></select></span>')


def type_counts_html(cnt):
    bits = []
    for k, (lab, em, _d) in TYPES.items():
        if cnt.get(k):
            bits.append(f'<span class="ty ty-{k}" style="margin-left:4px">{em} {cnt[k]}</span>')
    return ''.join(bits)


UID_MAP = f'{SCR}/uid_map.json'


def load_uid_map():
    try:
        return json.load(open(UID_MAP, encoding='utf-8'))
    except FileNotFoundError:
        return {}


def existing_store():
    """Carry saved results over from the current published file (never reset testers' work)."""
    try:
        cur = open(OUT, encoding='utf-8').read()
    except FileNotFoundError:
        return {}
    m = re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', cur)
    try:
        return json.loads((m.group(1) or '{}').strip() or '{}') if m else {}
    except Exception:
        return {}


def main():
    tpl = open(TPL, encoding='utf-8').read()
    uid_map = load_uid_map()
    next_uid = [max(uid_map.values()) + 1 if uid_map else 1]

    def uid_for(mvp, cid):
        k = f'{mvp}:{cid}'
        if k not in uid_map:
            uid_map[k] = next_uid[0]
            next_uid[0] += 1
        return f'tc-{uid_map[k]}'

    mvp1_cases, mvp1_featlabels = load_mvp1()
    mvp2 = load_mvp2()

    rows = []
    uid_n = 0
    stats = Counter()
    type_cnt = Counter()
    prio_cnt = Counter()
    epic_chip = []  # (value, label, count)
    mvp_cnt = Counter()
    mvp2_epic_type = {}
    not_in_ui = 0

    # ===== MVP-1 =====
    rows.append('<tr class="mvprow" data-mvp="mvp1"><td colspan="7">🟦 MVP-1 — Happy Path (regression · ต่อยอดจากรายงาน MVP-1 UI · เฉพาะเคส flow หลักที่ผ่านตามสเปก) <span class="rp" id="mvp1-count"></span></td></tr>')
    by_epic = OrderedDict()
    for c in mvp1_cases:
        by_epic.setdefault(c['feat'], OrderedDict()).setdefault(c['featkey'], []).append(c)
    for ep, feats in by_epic.items():
        emoji, name, ref = MVP1_EPIC_INFO[ep]
        n_ep = sum(len(v) for v in feats.values())
        featv = f'm1e{ep}'
        epic_chip.append((featv, f'{emoji} MVP1·E{ep}', n_ep))
        label = f'{emoji} MVP-1 · ขั้นที่ {ep} · {name} ({ref})' if ep != '7' else f'{emoji} MVP-1 · {name}'
        rows.append(f'<tr class="epicrow" data-epic="{featv}"><td colspan="7">{esc(label)} <span class="rp">({n_ep} เคส · happy path)</span></td></tr>')
        for fk, cases in feats.items():
            fl = mvp1_featlabels.get(fk, '')
            # strip counts/owner from source label, keep "📁 key"
            lab = f'📁 {fk}' if fk != 'fullflow' else '📁 fullflow — เข้าระบบ → เตรียมคลัง → สร้างไลฟ์ใน Studio → เตรียมพร้อม → ออกอากาศ → จบ · และ variation'
            lv = 'lvl-e2e">🔄' if fk == 'fullflow' else 'lvl-ui">🌐'
            rows.append(f'<tr class="featrow" data-featkey="m1-{fk}"><td colspan="7">{lab} <span class="rp"><span class="lv {lv} {len(cases)}</span></span> {owner_select("m1-" + fk)}</td></tr>')
            for c in cases:
                uid_n += 1
                uid = uid_for('mvp1', c['id'])
                rows.append(trow(uid, c['id'], c['title'], c['level'], c['prio'], 'mvp1', featv, 'happy', 'in-ui'))
                card = c['card']
                card = card.replace('<div class="h-title">[MVP1] ', '<div class="h-title">', 1)
                card = re.sub(r'(<div class="h-prio">)(.*?)(</div>)', lambda m: m.group(1) + m.group(2) + ' · ประเภท: <b>✅ Happy Path</b> · MVP-1' + m.group(3), card, count=1, flags=re.S)
                rows.append(card + status_jira(uid))
                type_cnt['happy'] += 1
                prio_cnt[c['prio']] += 1
                mvp_cnt['mvp1'] += 1
                stats['mvp1'] += 1

    # ===== MVP-2 =====
    rows.append('<tr class="mvprow" data-mvp="mvp2"><td colspan="7">🟪 MVP-2 — ครบ 7 ประเภท: Happy Path · Negative · Boundary/Edge · Validation · Exception/Error · Permission · Data (Epic 8–16 · ออกแบบจาก epics-mvp2.md + test-artifacts/mvp-2 + UI จริง) <span class="rp" id="mvp2-count"></span></td></tr>')
    step = 0
    for n in MVP2_ORDER:
        if n not in mvp2:
            continue
        d = mvp2[n]
        step += 1
        featv = f'm2e{n}'
        n_ep = sum(len(f['cases']) for f in d['features'])
        for f in d['features']:
            for c in f['cases']:
                norm_type(c)
        tc = Counter(c['type'] for f in d['features'] for c in f['cases'])
        mvp2_epic_type[n] = tc
        emoji = MVP2_EMOJI.get(n, '•')
        epic_chip.append((featv, f'{emoji} MVP2·E{n}' if n != 99 else '🔄 MVP2·E2E', n_ep))
        if n == 99:
            label = f'{emoji} MVP-2 · {d["epic_title"]} ({d.get("epic_ref", "")})'
        else:
            label = f'{emoji} MVP-2 · ขั้นที่ {step} · {d["epic_title"]} ({d.get("epic_ref", "")})'
        rows.append(f'<tr class="epicrow" data-epic="{featv}"><td colspan="7">{esc(label)} <span class="rp">({n_ep} เคส {type_counts_html(tc)})</span></td></tr>')
        for f in d['features']:
            fc = Counter(c['type'] for c in f['cases'])
            fstat = f.get('ui_status', 'in-ui')
            fbadge = ''
            if fstat == 'not-in-ui':
                fbadge = ' <span class="edge-badge">ไม่พบใน UI — เขียนจากสเปก</span>'
            elif fstat == 'partial':
                fbadge = ' <span class="edge-badge">UI มีบางส่วน</span>'
            is_e2e = all(c.get('level') == 'e2e' for c in f['cases'])
            lv = 'lvl-e2e">🔄' if is_e2e else 'lvl-ui">🌐'
            fk = f"m2-{f['key']}"
            rows.append(f'<tr class="featrow" data-featkey="{fk}"><td colspan="7">📁 {esc(f["key"])} — {esc(f["label"])}{fbadge} <span class="rp"><span class="lv {lv} {len(f["cases"])}</span> {type_counts_html(fc)}</span> {owner_select(fk)}</td></tr>')
            # ensure ordering by type
            order = {k: i for i, k in enumerate(TYPES)}
            cases = sorted(f['cases'], key=lambda c: order.get(c['type'], 99))
            for c in cases:
                uid_n += 1
                uid = uid_for('mvp2', c['id'])
                lvl = c.get('level', 'ui')
                us = c.get('ui_status') or fstat
                if us == 'partial':
                    us = 'in-ui'
                if us == 'not-in-ui':
                    not_in_ui += 1
                rows.append(trow(uid, c['id'], c['title'], lvl, c['prio'], 'mvp2', featv, c['type'], us, c.get('sub', '')))
                rows.append(card_mvp2(c, f['key'], n if n != 99 else '8-16') + status_jira(uid))
                type_cnt[c['type']] += 1
                prio_cnt[c['prio']] += 1
                mvp_cnt['mvp2'] += 1

    total = uid_n
    body_rows = '\n'.join(rows)

    # ---------- assemble from template ----------
    out = tpl
    # title / header
    out = out.replace('<title>[MVP2] TAKRA AI — MVP-2 UI Manual Test Cases</title>',
                      '<title>[MVP1+2] TAKRA AI — MVP-1 Happy Path + MVP-2 Full-Category UI Manual Test Cases</title>')
    # CSS additions
    css_add = '''
/* MVP banner row + type badges (MVP1+2 report) */
tr.mvprow td{background:linear-gradient(90deg,#0f172a,#334155);color:#fff;font-weight:800;font-size:14px;padding:12px 14px;letter-spacing:.2px}
tr.mvprow .rp{font-weight:400;font-size:11.5px;opacity:.8;margin-left:8px}
tr.mvprow.hide{display:none!important}
.ty{display:inline-block;margin-left:6px;padding:1px 7px;border-radius:999px;font-size:9.5px;font-weight:700;border:1px solid;vertical-align:middle;white-space:nowrap;background:#fff}
.ty-happy{color:#15803d;border-color:#86efac;background:#f0fdf4}
.ty-negative{color:#b91c1c;border-color:#fca5a5;background:#fef2f2}
.ty-boundary{color:#7c3aed;border-color:#c4b5fd;background:#f5f3ff}
.ty-validation{color:#0e7490;border-color:#67e8f9;background:#ecfeff}
.ty-error{color:#c2410c;border-color:#fdba74;background:#fff7ed}
.ty-data{color:#a16207;border-color:#fde047;background:#fefce8}
.ty-permission{color:#1d4ed8;border-color:#93c5fd;background:#eff6ff}
.fchip .ty{margin-left:0;font-size:9px;padding:0 5px}
tr.featrow .ty{margin-left:3px}
</style>'''
    out = out.replace('</style>', css_add, 1)
    # store-data → carry over saved results from the currently published file (keyed by stable uid)
    store_json = json.dumps(existing_store(), ensure_ascii=False, indent=2)
    out = re.sub(r'(<script id="store-data"[^>]*>)[\s\S]*?(</script>)', lambda m: m.group(1) + '\n' + store_json + '\n' + m.group(2), out, count=1)
    # header block
    hdr_old = re.search(r'<header class="top">[\s\S]*?</header>', out).group(0)
    p0, p1, p2 = prio_cnt.get('P0', 0), prio_cnt.get('P1', 0), prio_cnt.get('P2', 0)
    mvp2_ui = sum(1 for n, d in mvp2.items() if n != 99 for f in d['features'] for c in f['cases'])
    mvp2_e2e = sum(len(f['cases']) for f in mvp2.get(99, {'features': []})['features'])
    hdr_new = f'''<header class="top">
  <h1>🤖 [MVP1+2] TAKRA AI — MVP-1 Happy Path + MVP-2 Full-Category UI Manual Test Cases</h1>
  <div class="sub">เทส UI อย่างเดียว (Manual) · MVP-1 = happy path regression · MVP-2 = ครบ 7 ประเภท (Happy Path · Negative · Boundary/Edge · Validation · Exception/Error · Permission · Data) · Target: <b>https://uat-live.takra.ai/</b></div>
  <div class="meta">
    <span class="pill">รวม {total} เคส</span>
    <span class="pill">MVP-1 happy {mvp_cnt['mvp1']}</span>
    <span class="pill">MVP-2 {mvp_cnt['mvp2']} (UI {mvp2_ui} + E2E {mvp2_e2e})</span>
    <span class="pill">P0 {p0} · P1 {p1} · P2 {p2}</span>
    <span class="pill">สร้าง 2026-08-19</span>
  </div>
</header>'''
    out = out.replace(hdr_old, hdr_new, 1)

    # note boxes: keep the target note, add scope note after it
    tcount_bits = ' · '.join(f'{TYPES[k][1]} {TYPES[k][0]} <b>{type_cnt.get(k,0)}</b>' for k in TYPES)
    mvp2_type_only = Counter()
    for n, d in mvp2.items():
        for f in d['features']:
            for c in f['cases']:
                mvp2_type_only[c['type']] += 1
    tcount2 = ' · '.join(f'{TYPES[k][1]} {TYPES[k][0]} <b>{mvp2_type_only.get(k,0)}</b>' for k in TYPES)
    typedefs = ' · '.join(f'<b>{TYPES[k][1]} {TYPES[k][0]}</b> = {esc(TYPES[k][2])}' for k in TYPES)
    scope_note = f'''
  <div class="note-box" style="background:#eef2ff;border-color:#c7d2fe;color:#3730a3">📚 <b>ขอบเขตรายงานนี้</b> ·
    <b>MVP-1 (Happy Path)</b> = เคส flow หลัก {mvp_cnt['mvp1']} เคส ยกมาจากรายงาน <a href="https://wanlee-tankunnatam.github.io/qa-test-reports/projects/takra-ai/2026/07/reports/takra-ai-mvp1-ui-test-cases-table.html" target="_blank" rel="noopener">MVP-1 UI</a> (ตัดเคส edge/negative/validation ออก · ID เดิม · อ้าง <code>epics.md</code>) ·
    <b>MVP-2</b> = {mvp_cnt['mvp2']} เคส ออกแบบใหม่จาก <code>_bmad-output/planning-artifacts/epics-mvp2.md</code> + <code>_bmad-output/test-artifacts/mvp-2/</code> (test-plan · gaps · case/mvp2-*) + UI จริงใน <code>apps/web/src</code> (as of 2026-08-19) ·
    ประเภท MVP-2: {tcount2} ·<br>📖 <b>นิยาม:</b> {typedefs} ·
    ⚠️ <b>Epic 11 (Ops/Support)</b> ย้ายไป TAKRA Hub แล้ว (2026-08-10) — ไม่มีเคสในรายงานนี้ · <b>Epic 13</b> (Tool-calling) = backend-only ไม่มีหน้าจอ ·
    เคสที่ติดป้าย <span class="edge-badge">ไม่พบใน UI</span> ({not_in_ui} เคส) = หน้าจอนั้นยังไม่พบในโค้ด UI ณ วันสร้าง เขียนจากสเปก → ถ้า UI ยังไม่มาให้ลงผล BLOCKED</div>
'''
    target_note_end = out.find('</div>', out.find('<div class="note-box">🌐')) + len('</div>')
    out = out[:target_note_end] + scope_note + out[target_note_end:]

    # summary pending count
    out = out.replace('<span class="cnt pending">รอเทส <b id="sum-pending">206</b></span>', f'<span class="cnt pending">รอเทส <b id="sum-pending">{total}</b></span>')
    out = out.replace('0% ทดสอบแล้ว (0/206)', f'0% ทดสอบแล้ว (0/{total})')

    # filters block: rebuild Epic row + add MVP row + type row
    filt_old = re.search(r'<div class="filters">[\s\S]*?\n  </div>\n\n  <div class="tablewrap">', out).group(0)
    epic_chips = '\n'.join(f'      <button class="fchip" data-f="feat" data-v="{v}">{esc(l)} ({n})</button>' for v, l, n in epic_chip)
    type_chips = '\n'.join(f'      <button class="fchip" data-f="type" data-v="{k}" title="{esc(TYPES[k][2])}"><span class="ty ty-{k}">{TYPES[k][1]} {TYPES[k][0]}</span> ({type_cnt.get(k,0)})</button>' for k in TYPES)
    filt_new = f'''<div class="filters">
    <div class="row"><label>MVP</label>
      <button class="fchip" data-f="mvp" data-v="mvp1">🟦 MVP-1 Happy Path ({mvp_cnt['mvp1']})</button>
      <button class="fchip" data-f="mvp" data-v="mvp2">🟪 MVP-2 ครบทุกประเภท ({mvp_cnt['mvp2']})</button>
      <button class="clearbtn" data-clear="mvp">✕</button>
    </div>
    <div class="row"><label>Epic</label>
{epic_chips}
      <button class="clearbtn" data-clear="feat">✕</button>
    </div>
    <div class="row"><label>ประเภท</label>
{type_chips}
      <button class="clearbtn" data-clear="type">✕</button>
    </div>
    <div class="row"><label>Level</label>
      <button class="fchip" data-f="level" data-v="ui">🌐 UI</button>
      <button class="fchip" data-f="level" data-v="e2e">🔄 E2E</button>
      <button class="clearbtn" data-clear="level">✕</button>
    </div>
    <div class="row"><label>Priority</label>
      <button class="fchip" data-f="prio" data-v="P0">P0</button>
      <button class="fchip" data-f="prio" data-v="P1">P1</button>
      <button class="fchip" data-f="prio" data-v="P2">P2</button>
      <button class="clearbtn" data-clear="prio">✕</button>
    </div>
    <div class="row"><label>สถานะ</label>
      <button class="fchip" data-f="status" data-v="pass">✅ PASS</button>
      <button class="fchip" data-f="status" data-v="fail">❌ FAIL</button>
      <button class="fchip" data-f="status" data-v="hold">⏸ HOLD</button>
      <button class="fchip" data-f="status" data-v="block">🚫 BLOCKED</button>
      <button class="fchip" data-f="status" data-v="skip">⏭ SKIP</button>
      <button class="fchip" data-f="status" data-v="pending">⏳ รอเทส</button>
      <button class="clearbtn" data-clear="status">✕</button>
    </div>
  </div>

  <div class="tablewrap">'''
    out = out.replace(filt_old, filt_new, 1)

    # table body
    tb_start = out.find('<tbody>') + len('<tbody>')
    tb_end = out.rfind('</tbody>')
    out = out[:tb_start] + '\n\n' + body_rows + '\n\n' + out[tb_end:]

    # footer
    out = re.sub(r'<footer>.*?</footer>', f'<footer>[MVP1+2] TAKRA AI — MVP-1 Happy Path + MVP-2 Full-Category UI Manual Test Cases · {total} TCs · UI only · UAT https://uat-live.takra.ai/ · สร้าง 2026-08-19</footer>', out, count=1)

    # JS: filters (add mvp + type), mvprow hide, GH_PATH, download name, remove TC-AD.1 hack
    # JS: GitHub contents API omits `content` for files > 1MB → auto-save used to fall back to
    # serialising the LOCAL DOM (a stale tab could revert the whole report structure). Fix:
    # fetch the blob via the git/blobs API, and never fall back to the local DOM.
    js_fetch_old = out[out.find('  async function fetchRemote() {'):out.find('  // Merge statuses that exist on the remote copy')]
    js_fetch_new = '''  async function fetchRemote() {
    var r = await fetch(
      API + '?ref=' + GH_BRANCH + '&t=' + Date.now(),
      { cache: 'no-store', headers: { Authorization: 'token ' + token, Accept: 'application/vnd.github+json' } }
    );
    if (!r.ok) {
      if (r.status === 401) { localStorage.removeItem('gh_pat'); }
      throw new Error('ดึงไฟล์ไม่ได้ (HTTP ' + r.status + ') — ตรวจ token หรือ branch');
    }
    var j = await r.json();
    // Files > 1MB: the contents API returns content "" (encoding "none") → read the blob instead.
    if ((!j.content || !j.content.length) && j.sha) {
      var b = await fetch(
        'https://api.github.com/repos/' + GH_OWNER + '/' + GH_REPO + '/git/blobs/' + j.sha + '?t=' + Date.now(),
        { cache: 'no-store', headers: { Authorization: 'token ' + token, Accept: 'application/vnd.github+json' } }
      );
      if (!b.ok) throw new Error('ดึงเนื้อไฟล์ (blob) ไม่ได้ (HTTP ' + b.status + ')');
      var bj = await b.json();
      j.content = bj.content; j.encoding = bj.encoding;
    }
    return j;
  }

'''
    assert js_fetch_old.strip().startswith('async function fetchRemote()')
    out = out.replace(js_fetch_old, js_fetch_new, 1)
    out = out.replace(
        "      if (!/<script id=\"store-data\"[^>]*>[\\s\\S]*?<\\/script>/.test(remoteHtml)) return buildEncoded();",
        "      if (!/<script id=\"store-data\"[^>]*>[\\s\\S]*?<\\/script>/.test(remoteHtml)) throw new Error('ไฟล์บน GitHub ไม่มี store-data — ไม่บันทึกเพื่อกันทับโครงสร้าง');")
    out = out.replace(
        "    } catch (_) {\n      return buildEncoded();   // fallback: serialize local DOM\n    }",
        "    } catch (e) {\n      throw new Error('ประกอบไฟล์จาก GitHub ไม่ได้ (' + (e && e.message) + ') — ไม่บันทึกเพื่อกันทับโครงสร้าง');\n    }")
    # pullLatest (token path) has the same >1MB problem → reuse blob fallback
    out = out.replace(
        "      html = decodeURIComponent(escape(atob(((await r.json()).content || '').replace(/\\s/g, ''))));",
        "      var pj = await r.json();\n      if ((!pj.content || !pj.content.length) && pj.sha) {\n        var pb = await fetch('https://api.github.com/repos/' + GH_OWNER + '/' + GH_REPO + '/git/blobs/' + pj.sha + '?t=' + Date.now(), { cache: 'no-store', headers: { Authorization: 'token ' + token, Accept: 'application/vnd.github+json' } });\n        if (!pb.ok) throw new Error('HTTP ' + pb.status + ' (blob)');\n        pj = await pb.json();\n      }\n      html = decodeURIComponent(escape(atob((pj.content || '').replace(/\\s/g, ''))));")

    out = out.replace("var filters = { feat: new Set(), level: new Set(), prio: new Set(), status: new Set() };",
                      "var filters = { mvp: new Set(), feat: new Set(), type: new Set(), level: new Set(), prio: new Set(), status: new Set() };")
    out = out.replace("    if (filters.feat.size  && !filters.feat.has(row.dataset.feat))   ok = false;",
                      "    if (filters.mvp.size   && !filters.mvp.has(row.dataset.mvp))     ok = false;\n"
                      "    if (filters.feat.size  && !filters.feat.has(row.dataset.feat))   ok = false;\n"
                      "    if (filters.type.size  && !filters.type.has(row.dataset.type))   ok = false;")
    out = out.replace("  recount();\n}\n\nfunction recount() {",
                      "  document.querySelectorAll('tr.mvprow').forEach(function(mr) {\n"
                      "    var n = mr.nextElementSibling, any = false;\n"
                      "    while (n && !n.classList.contains('mvprow')) {\n"
                      "      if (n.classList.contains('trow') && !n.classList.contains('hide')) { any = true; break; }\n"
                      "      n = n.nextElementSibling;\n"
                      "    }\n"
                      "    mr.classList.toggle('hide', !any);\n"
                      "  });\n"
                      "  recount();\n}\n\nfunction recount() {")
    out = out.replace("var GH_PATH   = 'projects/takra-ai/2026/07/reports/takra-ai-mvp2-ui-test-cases-table.html';",
                      f"var GH_PATH   = '{OUT_REL}';")
    out = out.replace("a.download = 'takra-ai-mvp2-ui-test-cases.html';", "a.download = 'takra-ai-mvp1-happy-mvp2-full-ui-test-cases.html';")
    out = re.sub(r"// Set TC-AD\.1 default to BLOCKED\n\(function\(\) \{[\s\S]*?\}\)\(\);\n", "", out, count=1)
    # per-MVP counts in banner rows (static)
    out = out.replace('<span class="rp" id="mvp1-count"></span>', f'<span class="rp">({mvp_cnt["mvp1"]} เคส)</span>')
    out = out.replace('<span class="rp" id="mvp2-count"></span>', f'<span class="rp">({mvp_cnt["mvp2"]} เคส · {tcount2})</span>')

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(out)
    json.dump(uid_map, open(UID_MAP, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('uid map', len(uid_map), 'max', max(uid_map.values()))
    print('WROTE', OUT, len(out), 'bytes')
    print('total', total, 'mvp1', mvp_cnt['mvp1'], 'mvp2', mvp_cnt['mvp2'], 'not_in_ui', not_in_ui)
    print('types', dict(type_cnt))
    print('prio', dict(prio_cnt))
    for n, tc in mvp2_epic_type.items():
        print('epic', n, dict(tc))


if __name__ == '__main__':
    main()
