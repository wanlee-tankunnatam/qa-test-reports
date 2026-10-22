#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สร้างรายงาน HTML ต่อรอบรัน e2e (Playwright) ของ takra-insight จาก results.json

ต่างจากรายงาน manual (ui-test-cases-table): สถานะมาจาก runner แล้ว จึงเป็นหน้า read-only
ไม่มีปุ่มกรอกผล/localStorage — โทนสี/โครงหน้าใช้ชุดเดียวกับรายงานเดิมใน repo นี้

ใช้:
  python3 tools/build/insight_e2e_run_report.py \
      --results /path/smoke-results.json --tier smoke \
      --branch feature/x --note "unconfigured · โปรไฟล์แยก" \
      [--out projects/takra-insight/2026/10/reports/xxx.html]
พิมพ์ path ไฟล์ที่เขียนออก stdout บรรทัดเดียว (ให้ wrapper เอาไปทำลิงก์ต่อ)
"""
import argparse, html, json, os, re, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAGES_BASE = "https://wanlee-tankunnatam.github.io/qa-test-reports"

ANSI = re.compile(r"\x1b\[[0-9;]*m")
STATUS_MAP = {"expected": "pass", "unexpected": "fail", "flaky": "flaky", "skipped": "skip"}
STATUS_TH = {"pass": "PASS", "fail": "FAIL", "flaky": "FLAKY", "skip": "SKIP"}


def collect(results_path):
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)
    rows = []  # (file, title, tags, status, duration_ms, error)
    def walk(suites):
        for su in suites:
            for sp in su.get("specs", []):
                for t in sp.get("tests", []):
                    st = STATUS_MAP.get(t.get("status"), "fail")
                    res = (t.get("results") or [{}])[-1]
                    err = ANSI.sub("", ((res.get("error") or {}).get("message") or ""))
                    dur = sum(r.get("duration", 0) for r in (t.get("results") or []))
                    title = sp.get("title", "")
                    tags = re.findall(r"@[\w-]+", title) or [
                        t if str(t).startswith("@") else f"@{t}" for t in sp.get("tags", [])]
                    rows.append({
                        "file": sp.get("file") or su.get("file") or su.get("title", ""),
                        "title": re.sub(r"\s*@[\w-]+", "", title).strip(),
                        "tags": tags, "status": st, "dur": dur, "err": err,
                    })
            walk(su.get("suites", []))
    walk(data.get("suites", []))
    return data.get("stats", {}), rows


def fmt_dur(ms):
    s = ms / 1000
    return f"{int(s // 60)} นาที {int(s % 60)} วิ" if s >= 60 else f"{s:.1f} วิ"


def build_html(stats, rows, tier, branch, note, run_at):
    n = {k: sum(1 for r in rows if r["status"] == k) for k in ("pass", "fail", "flaky", "skip")}
    total = len(rows)
    ran = total - n["skip"]
    pct = round(100 * n["pass"] / ran) if ran else 0
    files = sorted({r["file"] for r in rows})

    body_rows = []
    uid = 0
    for fname in files:
        frows = [r for r in rows if r["file"] == fname]
        fp = sum(1 for r in frows if r["status"] == "pass")
        body_rows.append(
            f'<tr class="featrow" data-file="{html.escape(fname)}"><td colspan="5">{html.escape(fname)}'
            f'<span class="rp">ผ่าน {fp}/{len(frows)}</span></td></tr>')
        for r in frows:
            uid += 1
            st = r["status"]
            tags = " ".join(f'<span class="lv lvl-ui">{html.escape(t)}</span>' for t in r["tags"])
            has_err = bool(r["err"]) and st in ("fail", "flaky")
            tog = '<span class="tog">▶</span>' if has_err else '<span class="tog"></span>'
            body_rows.append(
                f'<tr class="trow" data-uid="{uid}" data-st="{st}" data-file="{html.escape(fname)}">'
                f'<td>{tog}</td>'
                f'<td class="ctitle">{html.escape(r["title"])}</td>'
                f'<td class="lvl">{tags}</td>'
                f'<td class="status"><span class="stb {st}">{STATUS_TH[st]}</span></td>'
                f'<td class="cid">{fmt_dur(r["dur"]) if st != "skip" else "—"}</td></tr>')
            if has_err:
                body_rows.append(
                    f'<tr class="detail" data-uid="{uid}" data-st="{st}" data-file="{html.escape(fname)}"><td colspan="5">'
                    f'<div class="card"><div class="sec"><h4>Error</h4>'
                    f'<pre class="errpre">{html.escape(r["err"][:3000])}</pre></div></div></td></tr>')

    file_chips = "".join(
        f'<button class="fchip" data-f="file" data-v="{html.escape(f)}">{html.escape(os.path.basename(f))}</button>'
        for f in files)

    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[E2E @{tier}] TAKRA Insight — ผลรันอัตโนมัติ {run_at:%d %b %Y %H:%M}</title>
<style>
:root{{--bg:#f5f6f8;--card:#fff;--card2:#f0f2f5;--line:#dce0e7;--txt:#1f2430;--muted:#6b7280;--accent:#2563eb;
--pass:#16a34a;--fail:#dc2626;--hold:#d97706;--skip:#9ca3af;--lv-ui:#db2777}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--txt);font-family:"Segoe UI","Sarabun",system-ui,sans-serif;line-height:1.5;font-size:13px}}
a{{color:var(--accent)}}
header.top{{padding:20px 28px 14px;border-bottom:1px solid var(--line);background:linear-gradient(135deg,#166534,#16a34a);color:#fff}}
header.top.hasfail{{background:linear-gradient(135deg,#7f1d1d,#dc2626)}}
header.top h1{{margin:0 0 4px;font-size:20px}}
header.top .sub{{font-size:12.5px;opacity:.88}}
header.top .meta{{margin-top:10px;display:flex;flex-wrap:wrap;gap:8px}}
.pill{{display:inline-block;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:600;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.35);color:#fff}}
.wrap{{padding:16px 22px 80px;max-width:1100px;margin:0 auto}}
.counts{{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}}
.cnt{{font-size:12px;font-weight:700;padding:5px 12px;border-radius:8px;border:1px solid var(--line);background:#fff}}
.cnt b{{font-size:14px}}
.cnt.pass{{color:var(--pass);border-color:#bbf7d0}}.cnt.fail{{color:var(--fail);border-color:#fecaca}}
.cnt.flaky{{color:var(--hold);border-color:#fde68a}}.cnt.skip{{color:var(--skip)}}
.progress{{height:10px;background:var(--card2);border-radius:6px;overflow:hidden;border:1px solid var(--line);margin:0 0 14px}}
.progressbar{{height:100%;background:var(--pass);width:{pct}%}}
.filters{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:0 0 14px}}
.filters .row{{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:3px 0}}
.filters label{{font-size:11px;font-weight:700;color:var(--muted);min-width:60px}}
.fchip{{border:1px solid var(--line);background:#fff;border-radius:999px;padding:3px 11px;font-size:11.5px;cursor:pointer;color:var(--txt)}}
.fchip:hover{{border-color:var(--accent);color:var(--accent)}}
.fchip.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}
.tablewrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:#fff}}
table.tc{{border-collapse:collapse;width:100%;min-width:760px;background:#fff}}
table.tc th,table.tc td{{padding:8px 10px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}
table.tc thead th{{position:sticky;top:0;background:var(--card2);color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.4px;z-index:3;border-bottom:2px solid var(--line)}}
tr.featrow td{{background:#eaf1fb;color:#1d4ed8;font-weight:700;font-size:12px}}
tr.featrow .rp{{font-weight:500;font-size:11px;color:#3b6fc4;margin-left:8px}}
tr.trow{{cursor:pointer}}tr.trow:hover{{background:#f7f9fc}}tr.trow.open{{background:#eef4fe}}
.tog{{display:inline-block;width:14px;color:var(--muted);transition:transform .15s;font-size:11px}}
tr.trow.open .tog{{transform:rotate(90deg);color:var(--accent)}}
.cid{{font-family:monospace;font-size:10px;color:var(--muted);white-space:nowrap}}
.ctitle{{font-weight:600;font-size:12.5px;max-width:520px}}
td.lvl{{white-space:nowrap}}
.lv{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:5px;border:1px solid;background:#fff;display:inline-block;vertical-align:middle;margin-right:3px}}
.lv.lvl-ui{{color:var(--lv-ui);border-color:var(--lv-ui)}}
td.status{{white-space:nowrap}}
.stb{{font-weight:700;font-size:10px;padding:3px 8px;border-radius:5px;display:inline-block}}
.stb.pass{{background:var(--pass);color:#fff}}.stb.fail{{background:var(--fail);color:#fff}}
.stb.flaky{{background:var(--hold);color:#fff}}.stb.skip{{background:var(--skip);color:#fff}}
tr.detail{{display:none}}tr.detail.show{{display:table-row}}
tr.detail>td{{background:#fafbfc;padding:0;border-bottom:2px solid var(--line)}}
.card{{padding:16px 20px}}
.card .sec h4{{margin:0 0 5px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:#374151}}
.errpre{{white-space:pre-wrap;background:#fff;border:1px dashed #fecaca;border-radius:7px;padding:9px 12px;font-size:11.5px;color:#991b1b;margin:0}}
tr.hide{{display:none!important}}
.note-box{{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:8px 12px;font-size:12px;color:#92400e;margin:0 0 12px}}
footer{{color:var(--muted);font-size:12px;text-align:center;padding:20px}}
</style>
</head>
<body>
<a id="hub-back-btn" href="{PAGES_BASE}/?project=insight" title="กลับไปหน้ารวมรายงาน (Hub)" style="position:fixed;top:12px;right:14px;z-index:99999;display:inline-flex;align-items:center;gap:7px;padding:10px 18px;border-radius:999px;background:#fff;color:#1e3a8a;font-size:14px;font-weight:800;text-decoration:none;box-shadow:0 4px 16px rgba(0,0,0,.35);border:2px solid #1e3a8a;font-family:'Segoe UI','Sarabun',system-ui,sans-serif">🏠 รายงานทั้งหมด</a>
<header class="top{' hasfail' if n['fail'] else ''}">
  <h1>🤖 [E2E @{tier}] TAKRA Insight — ผลรันอัตโนมัติ</h1>
  <div class="sub">Playwright desktop e2e · รันเมื่อ {run_at:%a %d %b %Y %H:%M} · generate อัตโนมัติจาก results.json (read-only)</div>
  <div class="meta">
    <span class="pill">branch: {html.escape(branch)}</span>
    <span class="pill">⏱ {fmt_dur(stats.get('duration', 0))}</span>
    <span class="pill">{html.escape(note)}</span>
  </div>
</header>
<div class="wrap">
  <div class="counts">
    <span class="cnt pass">PASS <b>{n['pass']}</b></span>
    <span class="cnt fail">FAIL <b>{n['fail']}</b></span>
    <span class="cnt flaky">FLAKY <b>{n['flaky']}</b></span>
    <span class="cnt skip">SKIP <b>{n['skip']}</b></span>
    <span class="cnt">รวม <b>{total}</b> · ผ่าน {pct}% ของที่รัน</span>
  </div>
  <div class="progress"><div class="progressbar"></div></div>
  {'<div class="note-box">⚠️ มีเคส FAIL — กดที่แถวเพื่อดู error เต็ม</div>' if n['fail'] else ''}
  <div class="filters">
    <div class="row"><label>สถานะ</label>
      <button class="fchip" data-f="st" data-v="pass">✅ PASS</button>
      <button class="fchip" data-f="st" data-v="fail">❌ FAIL</button>
      <button class="fchip" data-f="st" data-v="flaky">⚠️ FLAKY</button>
      <button class="fchip" data-f="st" data-v="skip">⏭ SKIP</button>
    </div>
    <div class="row"><label>ไฟล์</label>{file_chips}</div>
  </div>
  <div class="tablewrap"><table class="tc">
    <thead><tr><th></th><th>Test case</th><th>Tags</th><th>ผล</th><th>เวลา</th></tr></thead>
    <tbody>{''.join(body_rows)}</tbody>
  </table></div>
</div>
<footer>generate โดย tools/build/insight_e2e_run_report.py · QA takra-insight</footer>
<script>
const F={{st:null,file:null}};
function apply(){{
  document.querySelectorAll('tr.trow,tr.detail').forEach(tr=>{{
    const ok=(!F.st||tr.dataset.st===F.st)&&(!F.file||tr.dataset.file===F.file);
    tr.classList.toggle('hide',!ok);
    if(tr.classList.contains('detail')&&!tr.classList.contains('show'))tr.classList.add('hide')===false;
  }});
  document.querySelectorAll('tr.featrow').forEach(fr=>{{
    const any=[...document.querySelectorAll(`tr.trow[data-file="${{CSS.escape(fr.dataset.file)}}"]`)].some(r=>!r.classList.contains('hide'));
    fr.classList.toggle('hide',!any);
  }});
}}
document.querySelectorAll('.fchip').forEach(b=>b.addEventListener('click',()=>{{
  const f=b.dataset.f,v=b.dataset.v,on=b.classList.contains('active');
  document.querySelectorAll(`.fchip[data-f="${{f}}"]`).forEach(x=>x.classList.remove('active'));
  F[f==='st'?'st':'file']=on?null:v;
  if(!on)b.classList.add('active');
  apply();
}}));
document.querySelectorAll('tr.trow').forEach(tr=>tr.addEventListener('click',()=>{{
  const d=document.querySelector(`tr.detail[data-uid="${{tr.dataset.uid}}"]`);
  if(!d)return; tr.classList.toggle('open'); d.classList.toggle('show');
}}));
</script>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--tier", default="smoke")
    ap.add_argument("--branch", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    stats, rows = collect(a.results)
    run_at = datetime.fromisoformat(stats.get("startTime", "").replace("Z", "+00:00")).astimezone() if stats.get("startTime") else datetime.now()
    out = a.out or os.path.join(
        ROOT, "projects", "takra-insight", f"{run_at:%Y}", f"{run_at:%m}", "reports",
        f"takra-insight-e2e-{a.tier}-{run_at:%Y%m%d-%H%M}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(stats, rows, a.tier, a.branch, a.note, run_at))
    print(out)


if __name__ == "__main__":
    main()
