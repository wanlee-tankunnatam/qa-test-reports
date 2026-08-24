#!/usr/bin/env python3
"""สร้างรายงาน UI manual test case ของ TAKRA Hub จาก tools/build/hub_cases.py

harness (CSS + JS ปุ่ม ☁️ เซฟ/ตัวกรอง/Jira/owner) ลอกจากรายงาน takra-rerun MVP-2 เพื่อให้หน้าตา/พฤติกรรมเหมือนกัน
แล้วแพตช์เฉพาะ GH_PATH · ชื่อไฟล์ดาวน์โหลด · ตัวกรอง "ประเภท" (kind)

ใช้:  python3 tools/build/build_hub_report.py [mvp1|mvp2|mvp2rbac]   # เขียนไฟล์ (default mvp1)
      python3 tools/build/build_hub_report.py mvp2 --check            # แค่ตรวจ/นับ ไม่เขียน
ข้อมูลเคส: mvp1 = hub_cases.py · mvp2 = hub_mvp2_cases.py · mvp2rbac = hub_mvp2_rbac_cases.py (Epic 1 RBAC/ABAC + Aff Account)
      (แต่ละไฟล์มี META บอก path/ชื่อ/uid เริ่ม)
สถานะผลเทสเดิมในไฟล์ปลายทาง (<script id="store-data">) จะถูกคงไว้ถ้ามีอยู่แล้ว
"""
import html
import importlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
MODULES = {'mvp1': 'hub_cases', 'mvp2': 'hub_mvp2_cases', 'mvp2rbac': 'hub_mvp2_rbac_cases',
           'aitickets': 'ai_tickets_cases'}
_which = next((a for a in sys.argv[1:] if a in MODULES), 'mvp1')
_mod = importlib.import_module(MODULES[_which])
EPICS, KINDS, META = _mod.EPICS, _mod.KINDS, _mod.META

TEMPLATE = ROOT / 'projects/takra-rerun/2026/07/reports/takra-rerun-mvp2-ui-test-cases-table.html'
OUT_REL = META['out_rel']
OUT = ROOT / OUT_REL
UID_START = META['uid_start']
TITLE = META['title']
# ปุ่ม "รายงานทั้งหมด" — ตั้งต่อรายงานได้ผ่าน META['back'] (ค่าเริ่มต้น = hub)
BACK = META.get('back', 'https://wanlee-tankunnatam.github.io/qa-test-reports/?project=hub')

OWNER_SEL = ('<span class="epic-owner-wrap">👤 <select class="feat-owner" data-featkey="{fk}">'
             '<option value="">— ผู้รับผิดชอบ —</option><option>Wanlee T (Ice)</option><option>Kachain B (Moss)</option></select></span>')
PRIO_CLS = {'P0': 'p0', 'P1': 'p1', 'P2': 'p2'}
KIND_CLS = {'happy': 'kd-happy', 'negative': 'kd-neg', 'boundary': 'kd-bnd', 'validation': 'kd-val',
            'exception': 'kd-exc', 'permission': 'kd-perm', 'data': 'kd-data'}

EXTRA_CSS = """
/* ประเภทเคส (kind) */
.kd{display:inline-block;margin-left:6px;padding:0 6px;border-radius:4px;font-size:9.5px;font-weight:700;vertical-align:middle;border:1px solid;white-space:nowrap}
.kd-happy{color:#15803d;background:#f0fdf4;border-color:#bbf7d0}
.kd-neg{color:#b91c1c;background:#fef2f2;border-color:#fecaca}
.kd-bnd{color:#b45309;background:#fffbeb;border-color:#fde68a}
.kd-val{color:#6d28d9;background:#f5f3ff;border-color:#ddd6fe}
.kd-exc{color:#be123c;background:#fff1f2;border-color:#fecdd3}
.kd-perm{color:#0f766e;background:#f0fdfa;border-color:#99f6e4}
.kd-data{color:#1d4ed8;background:#eff6ff;border-color:#bfdbfe}
.chk{margin-top:4px;padding:6px 8px;border-left:3px solid #16a34a;background:rgba(22,163,74,.07)}
.noui{display:inline-block;margin-left:6px;padding:0 6px;border-radius:4px;font-size:9.5px;font-weight:700;vertical-align:middle;color:#991b1b;background:#fee2e2;border:1px solid #fca5a5;white-space:nowrap}
"""

def esc(s: str) -> str:
    return html.escape(s, quote=False)

def ul(items):
    return '<ul>' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ul>'

def ol(items, start=None):
    a = f' start="{start}"' if start and start > 1 else ''
    return f'<ol{a}>' + ''.join(f'<li>{esc(x)}</li>' for x in items) + '</ol>'

def kind_tag(kind):
    return f'<span class="kd {KIND_CLS[kind]}">{KINDS[kind][0]}</span>'

def status_block(uid):
    return f'''  <div class="sec"><h4>Status</h4><div class="statusrow">
    <span class="opt pass" data-uid="{uid}" data-st="pass">PASS</span>
    <span class="opt fail" data-uid="{uid}" data-st="fail">FAIL</span>
    <span class="opt hold" data-uid="{uid}" data-st="hold">HOLD</span>
    <span class="opt block" data-uid="{uid}" data-st="block">BLOCKED</span>
    <span class="opt skip" data-uid="{uid}" data-st="skip">SKIP</span>
  </div></div>
  <div class="sec jira-sec"><h4>🐞 Jira / Bug (ใส่ได้หลายลิงก์)</h4>
    <div class="jira-list" data-uid="{uid}"></div>
    <div class="jira-add"><input type="text" class="jira-input" data-uid="{uid}" placeholder="วางลิงก์ Jira หรือพิมพ์ TKH-123 แล้ว Enter"><button class="btn jira-btn" data-uid="{uid}">+ เพิ่มลิงก์</button></div>
  </div>
'''

def case_html(c, uid, epic_key, epic_title_short):
    u = f'tc-{uid}'
    lvl = c.get('level', 'ui')
    lv_html = ('<span class="lv lvl-e2e">E2E</span>' if lvl == 'e2e' else '<span class="lv lvl-ui">UI</span>')
    kind = c['kind']
    in_ui = c.get('ui', True)
    noui = '' if in_ui else ' <span class="noui">⛔ ไม่พบใน UI</span>'
    head = f'''<tr class="trow" data-feat="{epic_key}" data-level="{lvl}" data-prio="{c['prio']}" data-kind="{kind}" data-ui="{'yes' if in_ui else 'no'}" onclick="tg(this)">
  <td><span class="tog">▸</span></td><td class="cid">{esc(c['id'])}</td>
  <td class="ctitle">{esc(c['title'])} {kind_tag(kind)}{noui}</td>
  <td class="lvl">{lv_html}</td>
  <td><span class="prio {PRIO_CLS[c['prio']]}">{c['prio']}</span></td>
  <td class="status" data-uid="{u}"><span class="stb pending">รอเทส</span></td>
  <td class="jira-cell" data-uid="{u}"></td>
</tr>
'''
    hprio = (f'Priority: <b>{c["prio"]}</b> · {"E2E" if lvl == "e2e" else "UI"} · ประเภท: <b>{KINDS[kind][0]}</b> '
             f'<span class="hint">({esc(KINDS[kind][1])})</span> · {esc(epic_title_short)}')
    body = [f'<tr class="detail"><td colspan="7"><div class="card">',
            f'  <div class="h-title">{esc(c["title"])}</div>',
            f'  <div class="h-prio">{hprio}</div>']
    e2e = c.get('e2e')
    if e2e:
        body.append(f'  <div class="sec"><h4>📄 อ้างอิงเอกสาร</h4><div class="hint" style="font-size:12px">{esc(e2e["summary"])}</div></div>')
        body.append(f'  <div class="sec"><h4>⏱ Run sheet</h4><div class="hint" style="font-size:12px">{esc(e2e["runsheet"])}</div></div>')
    if not in_ui:
        body.append('  <div class="sec"><div class="hint" style="padding:6px 8px;border-left:3px solid #dc2626;background:rgba(220,38,38,.06)">⛔ <b>ไม่พบใน UI</b> ณ origin/develop 2026-08-19 (commit 27da4c0) — เคสเขียนตาม AC ในสเปกไว้ล่วงหน้า ชื่อปุ่ม/ข้อความอ้างจากเอกสาร อาจต่างจากของจริงเมื่อ build · ถ้ายังไม่มีหน้าจอให้บันทึกเป็น <b>BLOCKED</b> แล้วกลับมาปรับคำเมื่อ dev ส่งมอบ</div></div>')
    if c['pre']:
        body.append(f'  <div class="sec"><h4>Precondition</h4>{ul(c["pre"])}</div>')
    if c['data']:
        body.append(f'  <div class="sec"><h4>Test Data</h4>{ul(c["data"])}</div>')
    if e2e:
        for ph in e2e['phases']:
            body.append(f'  <div class="sec"><h4>Test Steps — {esc(ph["title"])}</h4>{ol(ph["steps"], ph.get("start"))}'
                        f'<div class="hint chk">✅ <b>เช็คพอยต์:</b> {esc(ph["check"])}</div></div>')
        body.append('  <div class="sec"><h4>🧭 กติกาเมื่อพังกลางทาง</h4><ul>'
                    '<li>เฟสไหนไม่ผ่านเช็คพอยต์ ให้บันทึกใน Actual ว่า <b>FAIL@เฟสนั้น</b> พร้อม TC รายขั้นที่เกี่ยว แล้วเปิดบั๊กที่เคสรายขั้น ไม่ใช่ที่เคสนี้</li>'
                    '<li>ถ้าเฟสถัดไปยังเดินต่อได้ ให้เดินให้จบลูปแล้วบันทึกทุกจุดที่พัง — อย่าหยุดกลางทางถ้าไม่จำเป็น</li>'
                    '<li>ถ้าถูกบล็อกจนไปต่อไม่ได้ ให้จบเคสเป็น FAIL และระบุเฟสที่ค้างไว้ใน Actual</li></ul></div>')
    else:
        body.append(f'  <div class="sec"><h4>Test Steps</h4>{ol(c["steps"])}</div>')
    exp = ul(c['expected']) + f'<div class="hint" style="margin-top:6px">{esc(c["src"])}</div>'
    body.append('  <div class="grid">')
    body.append(f'    <div class="sec"><h4>Expected Result</h4>{exp}</div>')
    body.append('    <div class="sec"><h4>Actual Result</h4><textarea class="actualbox" rows="4" placeholder="— บันทึกผลตอนทดสอบ —"></textarea></div>')
    body.append('  </div>')
    body.append(status_block(u))
    body.append('</div></td></tr>\n')
    return head + '\n'.join(body)

def build():
    src = TEMPLATE.read_text(encoding='utf-8')
    css_end = src.index('</style>\n</head>')
    css = src[:css_end]
    css = css.replace('<title>[MVP2] TAKRA Rerun — MVP-2 UI Manual Test Cases</title>', f'<title>{TITLE}</title>')
    js_start = src.index('<script>\n// ── Load store from embedded JSON ──')
    js = src[js_start:]
    js = js.replace("var GH_PATH   = 'projects/takra-rerun/2026/07/reports/takra-rerun-mvp2-ui-test-cases-table.html';",
                    f"var GH_PATH   = '{OUT_REL}';")
    js = js.replace("a.download = 'takra-ai-mvp2-ui-test-cases.html';", f"a.download = '{META['download']}';")
    # ตัวกรองประเภท (kind)
    js = js.replace("var filters = { feat: new Set(), level: new Set(), prio: new Set(), status: new Set() };",
                    "var filters = { feat: new Set(), level: new Set(), prio: new Set(), status: new Set(), kind: new Set(), ui: new Set() };")
    js = js.replace("    if (filters.prio.size  && !filters.prio.has(row.dataset.prio))   ok = false;",
                    "    if (filters.prio.size  && !filters.prio.has(row.dataset.prio))   ok = false;\n"
                    "    if (filters.kind.size  && !filters.kind.has(row.dataset.kind))   ok = false;\n"
                    "    if (filters.ui.size    && !filters.ui.has(row.dataset.ui))       ok = false;")
    for needle in ("var GH_PATH   = '" + OUT_REL, META['download'], "kind: new Set()", "filters.kind.has", "filters.ui.has"):
        assert needle in js, f'patch failed: {needle}'

    # เก็บ store-data เดิมถ้ามีไฟล์อยู่แล้ว
    store = '{}'
    if OUT.exists():
        m = re.search(r'<script id="store-data"[^>]*>([\s\S]*?)</script>', OUT.read_text(encoding='utf-8'))
        if m and m.group(1).strip():
            store = m.group(1).strip()
            json.loads(store)

    # ── body ──
    uid = UID_START
    rows = []
    counts = {'P0': 0, 'P1': 0, 'P2': 0}
    kind_counts = {k: 0 for k in KINDS}
    chips = []
    total = 0
    e2e_n = 0
    noui_n = 0
    for e in EPICS:
        n = sum(len(f['cases']) for f in e['feats'])
        chips.append(f'<button class="fchip" data-f="feat" data-v="{e["key"]}">{e["chip"]} ({n})</button>')
        rows.append(f'\n<!-- {e["key"]} -->\n<tr class="epicrow" data-epic="{e["key"]}"><td colspan="7">{e["emoji"]} {esc(e["title"])} <span class="rp">({n} เคส)</span></td></tr>')
        short = e['title'].split(' · ')[0] + ' · ' + e['title'].split(' · ')[1] if ' · ' in e['title'] else e['title']
        for f in e['feats']:
            n_ui = sum(1 for c in f['cases'] if c.get('level', 'ui') != 'e2e')
            n_e2e = len(f['cases']) - n_ui
            lvs = (f'<span class="lv lvl-ui">🌐 {n_ui}</span>' if n_ui else '') + (f' <span class="lv lvl-e2e">🔄 {n_e2e}</span>' if n_e2e else '')
            rows.append(f'<tr class="featrow" data-featkey="{f["featkey"]}"><td colspan="7">📁 {esc(f["title"])} <span class="rp">{lvs}</span> {OWNER_SEL.format(fk=f["featkey"])}</td></tr>')
            for c in f['cases']:
                rows.append(case_html(c, uid, e['key'], short))
                uid += 1
                total += 1
                counts[c['prio']] += 1
                kind_counts[c['kind']] += 1
                if not c.get('ui', True):
                    noui_n += 1
                if c.get('level') == 'e2e':
                    e2e_n += 1
    ui_n = total - e2e_n
    kind_chips = ''.join(f'<button class="fchip" data-f="kind" data-v="{k}" title="{esc(v[1])}">{v[0]} ({kind_counts[k]})</button>' for k, v in KINDS.items())

    ui_row = ''
    if noui_n:
        ui_row = (f'''    <div class="row"><label>สถานะ UI</label>
      <button class="fchip" data-f="ui" data-v="yes">✅ พร้อมเทส ({total - noui_n})</button>
      <button class="fchip" data-f="ui" data-v="no">⛔ ไม่พบใน UI ({noui_n})</button>
      <button class="clearbtn" data-clear="ui">✕</button>
    </div>
''')
    noui_pill = f'<span class="pill">⛔ ไม่พบใน UI {noui_n} · พร้อมเทส {total - noui_n}</span>' if noui_n else ''
    header = f'''
<header class="top">
  <h1>{META['emoji']} {TITLE}</h1>
  <div class="sub">{META['sub']}</div>
  <div class="meta">
    <span class="pill">{ui_n} เคส + E2E {e2e_n} = {total}</span>
    <span class="pill">{META['groups_label']}</span>
    <span class="pill">UI + E2E · manual</span>{noui_pill}
    <span class="pill">P0 {counts['P0']} · P1 {counts['P1']} · P2 {counts['P2']}</span>
    <span class="pill">ประเภท: Happy {kind_counts['happy']} · Negative {kind_counts['negative']} · Boundary {kind_counts['boundary']} · Validation {kind_counts['validation']} · Exception {kind_counts['exception']} · Permission {kind_counts['permission']} · Data {kind_counts['data']}</span>
  </div>
</header>

<div class="wrap">

  <div class="note-box">{META["note"]}</div>

  <div class="runsum">
    <h3>📊 สรุปผล Manual Test</h3>
    <div class="sumchips">
      <span class="cnt pass">PASS <b id="sum-pass">0</b></span>
      <span class="cnt fail">FAIL <b id="sum-fail">0</b></span>
      <span class="cnt hold">HOLD <b id="sum-hold">0</b></span>
      <span class="cnt block">BLOCKED <b id="sum-block">0</b></span>
      <span class="cnt skip">SKIP <b id="sum-skip">0</b></span>
      <span class="cnt pending">รอเทส <b id="sum-pending">{total}</b></span>
    </div>
    <div class="progress"><div id="sumbar" class="progressbar" style="width:0%"></div></div>
    <div class="hint" id="sumpct" style="margin-top:5px">0% ทดสอบแล้ว (0/{total})</div>
  </div>

  <div class="toolbar">
    <button class="btn" onclick="toggleAll(true)">▸ กางทั้งหมด</button>
    <button class="btn" onclick="toggleAll(false)">▾ ยุบทั้งหมด</button>
    <span class="hint">💡 คลิกแถว → ดู Steps / Expected (UI only)</span>
    <span style="margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <span id="save-status" class="hint" style="white-space: nowrap; color: var(--muted);">✓ ตรงกับ GitHub</span>
      <label class="hint" style="display:flex;gap:4px;align-items:center;white-space:nowrap;cursor:pointer" title="บันทึกขึ้น GitHub อัตโนมัติหลังหยุดแก้ ~5 วินาที"><input type="checkbox" id="chk-autosave" checked=""> auto-save</label>
      <button class="btn" id="btn-token" title="ใส่/เปลี่ยน GitHub token (ถ้าเซฟไม่ขึ้น/token เสีย กดอันนี้)">🔑 Token</button>
      <button class="btn" id="btn-refresh" title="ดึงผลล่าสุดจาก GitHub มา merge (ไม่ต้อง reload)">🔄 ดึงล่าสุด</button>
      <button class="btn primary" id="btn-publish" style="">☁️ บันทึกขึ้น GitHub</button>
      <button class="btn" id="btn-save-file" title="ดาวน์โหลด HTML ไว้ใช้ offline">💾 ดาวน์โหลด</button>
      <button class="btn" style="color:var(--fail)" id="btn-reset">🗑 ล้างผล</button>
    </span>
  </div>

  <div class="filters">
    <div class="row"><label>กลุ่ม</label>
      {''.join(chips)}
      <button class="clearbtn" data-clear="feat">✕</button>
    </div>
    <div class="row"><label>ประเภท</label>
      {kind_chips}
      <button class="clearbtn" data-clear="kind">✕</button>
    </div>
{ui_row}    <div class="row"><label>Priority</label>
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

  <div class="tablewrap">
  <table class="tc" id="main-table">
    <thead><tr><th style="width:22px"></th><th style="width:130px">TC ID</th><th>Test Case</th><th style="width:74px">Level</th><th style="width:55px">Pri</th><th style="width:80px">Status</th><th style="width:120px">Jira</th></tr></thead>
    <tbody>
'''
    footer = f'''
</tbody>
  </table>
  </div>

</div>
<footer>{TITLE} · {ui_n} UI + {e2e_n} E2E = {total} TCs · {META['footer']}</footer>

'''
    out = (css + EXTRA_CSS + '</style>\n</head>\n<body>\n'
           f'<a id="hub-back-btn" href="{BACK}" title="กลับไปหน้ารวมรายงาน (Hub)" style="position:fixed;top:12px;right:14px;z-index:99999;display:inline-flex;align-items:center;gap:7px;padding:10px 18px;border-radius:999px;background:#ffffff;color:#1e3a8a;font-size:14px;font-weight:800;text-decoration:none;box-shadow:0 4px 16px rgba(0,0,0,.35);border:2px solid #1e3a8a;font-family:\'Segoe UI\',\'Sarabun\',system-ui,sans-serif">🏠 รายงานทั้งหมด</a>\n\n\n'
           f'<script id="store-data" type="application/json">\n{store}\n</script>\n'
           + header + '\n'.join(rows) + footer + js)
    return out, dict(total=total, ui=ui_n, e2e=e2e_n, noui=noui_n, prio=counts, kind=kind_counts)

if __name__ == '__main__':
    html_out, stats = build()
    print(json.dumps(stats, ensure_ascii=False))
    if '--check' in sys.argv:
        sys.exit(0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_out, encoding='utf-8')
    print('wrote', OUT.relative_to(ROOT), len(html_out), 'bytes')
