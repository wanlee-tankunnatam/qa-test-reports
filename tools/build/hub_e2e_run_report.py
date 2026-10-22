#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""สร้างรายงาน HTML ต่อรอบรัน e2e (Playwright) ของ takra-hub จาก results.json

ต่างจากรายงาน manual (ui-test-cases-table): สถานะมาจาก runner แล้ว จึงเป็นหน้า read-only
ไม่มีปุ่มกรอกผล/localStorage — โทนสี/โครงหน้าใช้ชุดเดียวกับรายงานเดิมใน repo นี้

ใช้:
  python3 tools/build/hub_e2e_run_report.py \
      --results /path/smoke-results.json --tier smoke \
      --branch feature/x --note "unconfigured · โปรไฟล์แยก" \
      [--out projects/takra-hub/2026/10/reports/xxx.html]
พิมพ์ path ไฟล์ที่เขียนออก stdout บรรทัดเดียว (ให้ wrapper เอาไปทำลิงก์ต่อ)
"""
import argparse, html, json, os, re, sys
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAGES_BASE = "https://wanlee-tankunnatam.github.io/qa-test-reports"

ANSI = re.compile(r"\x1b\[[0-9;]*m")
STATUS_MAP = {"expected": "pass", "unexpected": "fail", "flaky": "flaky", "skipped": "skip"}
STATUS_TH = {"pass": "PASS", "fail": "FAIL", "flaky": "FLAKY", "skip": "SKIP"}

# ชื่อฟีเจอร์ภาษาคนต่อโฟลเดอร์ spec (แบบเดียวกับรายงาน insight) — ของใหม่ที่ไม่อยู่ในนี้ fallback เป็นชื่อโฟลเดอร์
FEATURE_NAMES = {
    "admin-dashboard": "แดชบอร์ดแอดมิน",
    "admin-package": "แพ็กเกจ (ฝั่งแอดมิน)",
    "admin-subscription": "subscription (ฝั่งแอดมิน)",
    "affiliate": "ผู้แนะนำ (affiliate)",
    "auth-harness": "ด่านตรวจ session บัญชีเทส",
    "authz-log": "บันทึกสิทธิ์ (authz log)",
    "billing-vat": "ภาษีและค่าธรรมเนียม (VAT)",
    "catalog": "หน้ารวมแพ็กเกจ",
    "checkout-payment": "ชำระเงิน/แนบสลิป",
    "consent-gate": "ด่านยอมรับเอกสาร (consent)",
    "cs-console": "คอนโซล CS",
    "cs-console-ux": "คอนโซล CS — UX",
    "downloads": "หน้าดาวน์โหลดแอป",
    "finance-reconcile": "กระทบยอดการเงิน",
    "free-trial": "ทดลองใช้ฟรี",
    "invite-flow": "เชิญสมาชิกเข้าทีม",
    "legal-admin": "เอกสารกฎหมาย (แอดมิน)",
    "legal-pages": "หน้าเอกสารกฎหมาย",
    "login-bff": "เข้าสู่ระบบ",
    "my-subscriptions": "บริการของฉัน",
    "password-reset-bff": "รีเซ็ตรหัสผ่าน",
    "profile-workspaces": "โปรไฟล์และทีม",
    "promotion-admin": "โค้ดส่วนลด (แอดมิน)",
    "promotion-checkout": "โค้ดส่วนลดตอนชำระเงิน",
    "promotion-report": "รายงานโค้ดส่วนลด",
    "register-bff": "สมัครสมาชิก",
    "smoke": "สโมคพื้นฐาน (ไม่ต้อง login)",
    "staff": "บัญชีพนักงาน",
    "trial-switch": "สวิตช์ปิด/เปิด trial",
    "verify-email": "ยืนยันอีเมล",
    "workspace-members": "สมาชิกทีม",
}


def feature_name(fname):
    # hub spec = "{feature}/{aspect}.spec.ts" หรือไฟล์เดี่ยวเช่น "auth-harness.spec.ts"
    parts = fname.split("/")
    key = parts[0] if len(parts) > 1 else os.path.basename(fname).split(".spec")[0]
    name = FEATURE_NAMES.get(key, key)
    aspect = os.path.basename(fname).split(".spec")[0]
    if len(parts) > 1 and aspect not in ("ui", "harness"):
        name += f" ({aspect})"
    return name


# คำสั่งผู้ใช้ 22 ต.ค. 2026: ทุกผลการรันต้องบอก "ทำไมตก" เป็นภาษาคน และ "ทำไม skip" ทุกตัว
FAIL_HINTS = [
    ("Error reading storage state", "ไม่มีไฟล์ login ของบัญชีนี้ — ยังไม่ได้ตั้งรหัสผ่านใน .env (ตั้งใจให้ล้มดัง ๆ ไม่ข้ามเงียบ)"),
    ("504", "UAT ตอบ 504 Gateway time-out — เซิร์ฟเวอร์สะดุดชั่วคราว ไม่ใช่บัคของหน้า ลองรันใหม่"),
    ("strict mode violation", "เจอ element ชื่อเดียวกันหลายตัวบนหน้า — เนื้อหา/โครงหน้าบน UAT มีของซ้ำหรือเปลี่ยนไป"),
    ("page.goto: Timeout", "เปิดหน้าไม่สำเร็จในเวลาที่กำหนด — UAT ช้าหรือหน้าโหลดไม่ขึ้น"),
    ("element(s) not found", "หา element ที่เทสคาดไว้ไม่เจอ — UI บน UAT อาจเปลี่ยนไปจากตอนเขียนเทส (ต้อง re-anchor เทส)"),
    ("Timeout", "รอ element/ข้อมูลจนหมดเวลา — หน้าอาจเปลี่ยน หรือข้อมูลที่คาดไว้ไม่มีบน UAT"),
    ("timeout", "รอจนหมดเวลา — หน้าโหลดช้าหรือขั้นตอนก่อนหน้าไปไม่ถึงจุดที่จะตรวจ"),
    ("expect(", "ค่าที่วัดได้จริงบนหน้า ไม่ตรงเกณฑ์ที่เทสตั้งไว้ — เป็นพฤติกรรมผิดจริงหรือบัคที่มีตั๋วอยู่ (ดู error)"),
]
DID_NOT_RUN = "ไม่ได้รัน — เทสก่อนหน้าในชุดเดียวกัน (serial) ตก ตัวที่เหลือจึงถูกข้ามอัตโนมัติ"

# แปลงเหตุผล skip (ข้อความเทคนิคจากในสเปค) เป็นภาษาคน — เรียงจากเฉพาะเจาะจงไปกว้าง
SKIP_HINTS = [
    (("TKH-230", "trial เปิดอยู่", "ทดลองใช้ฟรี"),
     "ฟีเจอร์ทดลองใช้ฟรีถูกปิดชั่วคราว (TKH-230) — ไม่มีอะไรให้ตรวจจนกว่าจะเปิดกลับ"),
    (("ยังไม่ build", "รอ Story", "ยังไม่ถูกเคาะ"),
     "ฟีเจอร์นี้ dev ยังสร้างไม่เสร็จ — รอ Story ปิดก่อนแล้วค่อยถอด skip"),
    (("ยังไม่มีบัญชี", "E2E_USER", "ไม่ได้ตั้ง", "CONSENT"),
     "ยังไม่ได้ตั้งบัญชีทดสอบ/รหัสผ่านใน .env — เตรียมบัญชีแล้วจะรันได้ทันที"),
    (("ลบไม่ได้", "คืนไม่ได้", "ย้อนกลับ", "ยกเลิกแล้วคืนไม่ได้", "ทีมจริง", "ลูกค้าจริง", "กินที่นั่ง",
      "Zitadel ซึ่งลบเองไม่ได้", "ขยะบัญชี", "บัญชีจริง", "สั่งซื้อจริง", "ใช้แล้วทิ้ง", "ให้ลูกค้าเห็น"),
     "ถ้ารันจริงจะไปสร้าง/แก้ข้อมูลจริงบน UAT แบบย้อนคืนไม่ได้ — รอสภาพแวดล้อมทดสอบแยก (TKH-285) หรือทดสอบชั้น api"),
    (("อีเมล", "code ของจริง", "mailhog"),
     "ต้องอ่านอีเมลจริงถึงจะได้ลิงก์/โค้ดยืนยัน ซึ่งสคริปต์อ่านไม่ได้ — เหมาะทดสอบชั้น api"),
    (("manual", "visual", "ด้วยตา", "skeleton"),
     "ต้องดูด้วยตา (manual) — จังหวะ/ภาพที่ต้องตรวจ สคริปต์จับไม่เสถียร"),
    (("ไม่มี", "ยังไม่มี", "ว่าง", "fixture", "ไม่พบ", "ไม่เต็ม", "ไม่ถึงเงื่อนไข", "0 แถว", "เสี้ยววินาที", "not_configured"),
     "UAT ยังไม่มีข้อมูล/สภาพที่เคสนี้ต้องใช้ — ต้องให้ทีมเตรียม fixture ก่อน"),
]


def fail_hint(err):
    for needle, hint in FAIL_HINTS:
        if needle in err:
            return hint
    return "ดูรายละเอียดใน error ด้านล่าง"


def skip_hint(raw):
    for needles, hint in SKIP_HINTS:
        if any(k in raw for k in needles):
            return hint
    return raw  # แปลไม่ออก → โชว์ข้อความเดิม (ส่วนใหญ่เขียนเป็นไทยอยู่แล้ว)


def skip_reason(t):
    for a in t.get("annotations", []):
        if a.get("type") in ("skip", "fixme") and a.get("description"):
            return a["description"]
    # skip โดยไม่มี annotation = Playwright ข้ามให้เองหลังตัวก่อนหน้าในชุด serial ตก
    return DID_NOT_RUN


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
                        "why": (fail_hint(err) if st in ("fail", "flaky")
                                else skip_hint(skip_reason(t)) if st == "skip" else ""),
                        "whyraw": skip_reason(t) if st == "skip" else "",
                    })
            walk(su.get("suites", []))
    walk(data.get("suites", []))
    return data.get("stats", {}), rows


def explain_error(err):
    """แปล error ของ Playwright เป็นประโยคภาษาคน — คืน (หัวเรื่อง, คำอธิบาย) · ยกมาจากรายงาน insight"""
    if not err:
        return None
    lines = [l for l in err.splitlines() if l.strip()]
    first = lines[0] if lines else ""
    loc = (re.search(r"Locator:\s*(.+)", err) or [None, None])[1]
    exp = (re.search(r"Expected[^:\n]*:\s*(.+)", err) or [None, None])[1]
    rec = (re.search(r"Received[^:\n]*:\s*(.+)", err) or [None, None])[1]
    tmo = (re.search(r"Timeout:\s*(\d+)ms", err) or [None, None])[1]
    wait = f" (รอครบ {int(tmo)//1000} วิแล้ว)" if tmo else ""
    not_found = "element(s) not found" in err

    # spec เขียนข้อความ assert เป็นไทยเอง → ใช้ประโยคนั้นนำได้เลย
    custom = re.sub(r"^Error:\s*", "", first)
    headline = custom if re.search(r"[ก-๙]", custom) else None

    if "Error reading storage state" in err:
        body = "ไม่มีไฟล์ login ของบัญชีนี้ — ยังไม่ได้ตั้งรหัสผ่านใน .env (ตั้งใจให้ล้มดัง ๆ ไม่ข้ามเงียบ)"
    elif "504" in err:
        body = "UAT ตอบ 504 Gateway time-out — เซิร์ฟเวอร์สะดุดชั่วคราว ไม่ใช่บัคของหน้า ลองรันใหม่"
    elif "strict mode violation" in err:
        body = f"เทสหา {loc or 'element'} ตัวเดียว แต่บนหน้ามีหลายตัว — เนื้อหา/โครงหน้าบน UAT มีของซ้ำหรือเปลี่ยนไป"
    elif "Test timeout" in err:
        body = "เทสรันเกินเวลาที่กำหนด — มักเกิดจากหน้า/ปุ่มที่รออยู่ไม่โผล่ขึ้นมาเลย ทำให้เทสค้างรอจนหมดเวลา"
    elif "toBeVisible" in err and not_found:
        body = f"เทสมองหา {loc or 'element'} บนหน้าจอ แต่หาไม่เจอเลย{wait} — มักเกิดจาก UI เปลี่ยน (ข้อความ/ชื่อปุ่มไม่ตรงกับที่เทสหา) หรือหน้าที่คาดไว้ไม่ได้เปิดขึ้น"
    elif "toBeVisible" in err:
        body = f"{loc or 'element'} มีอยู่ในหน้า แต่ไม่แสดงผล (ถูกซ่อน/ยังไม่ render){wait}"
    elif not_found:
        body = f"เทสจะตรวจค่า{(' ของ ' + loc) if loc else ''} แต่หา element นั้นไม่เจอเลย{wait} — มักเกิดจาก UI เปลี่ยนคำ/โครงสร้าง ไม่ตรงกับที่เทสเขียนไว้"
    elif "toHaveCount" in err:
        body = f"จำนวนรายการไม่ตรงที่คาด: ต้องการ {exp or '?'} แต่เจอ {rec or '?'}" + (f" (ตัวที่นับ: {loc})" if loc else "")
    elif exp and rec:
        body = f"ค่าที่ได้ไม่ตรงที่คาด: คาด {exp.strip()} แต่ได้จริง {rec.strip()}" + (f" (จุดที่ตรวจ: {loc})" if loc else "")
    else:
        body = custom
    return (headline, body)


def fmt_dur(ms):
    s = ms / 1000
    return f"{int(s // 60)} นาที {int(s % 60)} วิ" if s >= 60 else f"{s:.1f} วิ"


def build_html(stats, rows, tier, branch, note, run_at):
    n = {k: sum(1 for r in rows if r["status"] == k) for k in ("pass", "fail", "flaky", "skip")}
    total = len(rows)
    ran = total - n["skip"]
    pct = round(100 * n["pass"] / ran) if ran else 0
    files = sorted({r["file"] for r in rows})

    def anchor(fname):
        return "feat-" + re.sub(r"[^A-Za-z0-9._~-]", "-", fname.replace("/", "-").split(".spec")[0])

    # ── แถบสรุปต่อฟีเจอร์ (กดแล้วกรอง+กระโดดไปกลุ่มนั้น) — แบบเดียวกับรายงาน insight ──
    feat_rows = []
    for fname in files:
        frows = [r for r in rows if r["file"] == fname]
        c = {k: sum(1 for r in frows if r["status"] == k) for k in ("pass", "fail", "flaky", "skip")}
        cls = "fail" if c["fail"] else ("flaky" if c["flaky"] else "pass")
        feat_rows.append(
            f'<tr class="fsrow" data-file="{html.escape(fname)}" data-anchor="{anchor(fname)}">'
            f'<td><a href="#{anchor(fname)}">{html.escape(feature_name(fname))}</a>'
            f'<span class="fsfile">{html.escape(fname)}</span></td>'
            f'<td class="num ok">{c["pass"]}</td><td class="num {"bad" if c["fail"] else ""}">{c["fail"]}</td>'
            f'<td class="num">{c["flaky"]}</td><td class="num">{c["skip"]}</td>'
            f'<td><span class="stb {cls}">{"FAIL" if c["fail"] else ("FLAKY" if c["flaky"] else "PASS")}</span></td></tr>')
    feat_summary = ('<div class="featsum"><table class="fs">'
                    '<thead><tr><th>ฟีเจอร์</th><th>ผ่าน</th><th>ตก</th><th>flaky</th><th>ข้าม</th><th>สรุป</th></tr></thead>'
                    f'<tbody>{"".join(feat_rows)}</tbody></table></div>')

    body_rows = []
    uid = 0
    for fname in files:
        frows = [r for r in rows if r["file"] == fname]
        fp = sum(1 for r in frows if r["status"] == "pass")
        body_rows.append(
            f'<tr class="featrow" id="{anchor(fname)}" data-file="{html.escape(fname)}"><td colspan="5">{html.escape(feature_name(fname))}'
            f'<span class="rp">ผ่าน {fp}/{len(frows)} · {html.escape(fname)}</span></td></tr>')
        for r in frows:
            uid += 1
            st = r["status"]
            tags = " ".join(f'<span class="lv lvl-ui">{html.escape(t)}</span>' for t in r["tags"])
            # เหตุผลเต็มของ skip แตกเป็นข้อ ๆ ตามตัวคั่น "·" (คำสั่งผู้ใช้: อย่าปล่อยเป็นบรรทัดยาวติดกัน)
            raw_segments = [p.strip() for p in re.split(r"\s*·\s*", r["whyraw"] or "") if p.strip()]
            skip_detail = st == "skip" and raw_segments and r["whyraw"] != r["why"]
            has_detail = (bool(r["err"]) and st in ("fail", "flaky")) or skip_detail
            tog = '<span class="tog">▶</span>' if has_detail else '<span class="tog"></span>'
            body_rows.append(
                f'<tr class="trow" data-uid="{uid}" data-st="{st}" data-file="{html.escape(fname)}">'
                f'<td>{tog}</td>'
                f'<td class="ctitle">{html.escape(r["title"])}'
                + (f'<div class="why">{"⏭" if st == "skip" else "💬"} {html.escape(r["why"])}</div>' if r["why"] else '')
                + f'</td>'
                f'<td class="lvl">{tags}</td>'
                f'<td class="status"><span class="stb {st}">{STATUS_TH[st]}</span></td>'
                f'<td class="cid">{fmt_dur(r["dur"]) if st != "skip" else "—"}</td></tr>')
            if bool(r["err"]) and st in ("fail", "flaky"):
                ex = explain_error(r["err"])
                ex_html = ""
                if ex:
                    headline, body_txt = ex
                    ex_html = ('<div class="sec"><h4>ทำไมไม่ผ่าน (ภาษาคน)</h4>'
                               + (f'<p class="exhead">{html.escape(headline)}</p>' if headline else "")
                               + f'<p class="exbody">{html.escape(body_txt)}</p></div>')
                body_rows.append(
                    f'<tr class="detail" data-uid="{uid}" data-st="{st}" data-file="{html.escape(fname)}"><td colspan="5">'
                    f'<div class="card">{ex_html}<div class="sec"><h4>Error (ดิบ)</h4>'
                    f'<pre class="errpre">{html.escape(r["err"][:3000])}</pre></div></div></td></tr>')
            elif skip_detail:
                items = "".join(f'<li>{html.escape(p)}</li>' for p in raw_segments)
                body_rows.append(
                    f'<tr class="detail" data-uid="{uid}" data-st="{st}" data-file="{html.escape(fname)}"><td colspan="5">'
                    f'<div class="card"><div class="sec"><h4>เหตุผลที่ SKIP (จากใน spec)</h4>'
                    f'<ul class="exlist">{items}</ul></div></div></td></tr>')

    # กล่องสรุป "ข้ามเพราะอะไร" — จัดกลุ่มเหตุผล skip เรียงจากเยอะไปน้อย
    skip_counts = {}
    for r in rows:
        if r["status"] == "skip":
            skip_counts[r["why"]] = skip_counts.get(r["why"], 0) + 1
    # ผลตัดสิน gate ของรอบรันนี้ (คำสั่งผู้ใช้ 22 ต.ค. 2026) — เกณฑ์: FAIL ต้องเป็น 0 ถึงจะผ่าน
    if n["fail"] == 0:
        gate_cls, gate_txt = "pass", ("✅ GATE: ผ่าน — ไม่มีเคสตก"
            + (f"<small>มี flaky {n['flaky']} เคส — ผ่านแบบมีเงื่อนไข ควรจับตา</small>" if n["flaky"] else ""))
    else:
        gate_cls, gate_txt = "fail", (f"⛔ GATE: ไม่ผ่าน — ตก {n['fail']} เคส"
            "<small>ต้องตก 0 หรือทุกตัวมีตั๋ว/เหตุกำกับและ QA เซ็นรับ — ดูสาเหตุรายตัวในตาราง</small>")
    gate_box = f'<div class="gatebox {gate_cls}">{gate_txt}</div>'

    skip_box = ""
    if skip_counts:
        items = "".join(
            f'<li><b>×{c}</b> — ' + "<br>· ".join(
                html.escape(p.strip()) for p in re.split(r"\s*·\s*", reason) if p.strip()) + '</li>'
            for reason, c in sorted(skip_counts.items(), key=lambda kv: -kv[1]))
        skip_box = (f'<details class="skipbox"><summary>⏭ เหตุผลที่ข้าม {n["skip"]} เคส '
                    f'({len(skip_counts)} สาเหตุ — กดเพื่อดู)</summary><ul>{items}</ul></details>')

    file_chips = "".join(
        f'<button class="fchip" data-f="file" data-v="{html.escape(f)}">{html.escape(os.path.basename(f))}</button>'
        for f in files)

    return f"""<!DOCTYPE html>
<html lang="th"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[E2E @{tier}] TAKRA Hub — ผลรันอัตโนมัติ {run_at:%d %b %Y %H:%M}</title>
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
.why{{font-weight:400;font-size:11.5px;color:#92400e;margin-top:2px}}
tr.trow[data-st="skip"] .why{{color:#6b7280}}
.whyraw{{color:#9ca3af;font-size:10.5px}}
.exlist{{margin:0;padding-left:18px;font-size:12.5px;color:#4b5563}}
.exlist li{{margin:3px 0}}
.exhead{{margin:0 0 4px;font-weight:700;font-size:13px}}
.exbody{{margin:0;font-size:13px;border-left:3px solid var(--hold);padding:4px 12px;color:var(--txt)}}
.featsum{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:6px 10px;margin:0 0 14px;overflow-x:auto}}
table.fs{{border-collapse:collapse;width:100%;min-width:560px;font-size:12.5px}}
table.fs th{{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.4px;text-align:left;padding:6px 10px;border-bottom:2px solid var(--line)}}
table.fs td{{padding:5px 10px;border-bottom:1px solid var(--line)}}
table.fs tr:last-child td{{border-bottom:none}}
tr.fsrow{{cursor:pointer}}tr.fsrow:hover td{{background:#f7f9fc}}
tr.fsrow.active td{{background:rgba(37,99,235,.14)}}
td.num{{text-align:right;font-variant-numeric:tabular-nums;width:52px}}
td.num.ok{{color:var(--pass);font-weight:700}}td.num.bad{{color:var(--fail);font-weight:700}}
.fsfile{{display:block;font-family:monospace;font-size:10px;color:var(--muted)}}
.gatebox{{border-radius:12px;padding:14px 20px;margin:0 0 14px;font-size:24px;font-weight:900;text-align:center;border:3px solid;letter-spacing:.3px}}
.gatebox.pass{{background:#f0fdf4;border-color:var(--pass);color:#15803d}}
.gatebox.fail{{background:#fef2f2;border-color:var(--fail);color:#b91c1c}}
.gatebox small{{display:block;font-size:13px;font-weight:600;color:#6b7280;margin-top:4px}}
.whyfull{{margin:0;font-size:12.5px;background:#fffbeb;border:1px solid #fde68a;border-radius:7px;padding:8px 12px;color:#92400e}}
.skipbox{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:8px 14px;margin:0 0 14px;font-size:12px}}
.skipbox summary{{cursor:pointer;font-weight:700;color:#374151}}
.skipbox ul{{margin:8px 0 4px;padding-left:18px}}
.skipbox li{{margin:3px 0;color:#4b5563}}
footer{{color:var(--muted);font-size:12px;text-align:center;padding:20px}}
</style>
</head>
<body>
<a id="hub-back-btn" href="{PAGES_BASE}/?project=hub" title="กลับไปหน้ารวมรายงาน (Hub)" style="position:fixed;top:12px;right:14px;z-index:99999;display:inline-flex;align-items:center;gap:7px;padding:10px 18px;border-radius:999px;background:#fff;color:#1e3a8a;font-size:14px;font-weight:800;text-decoration:none;box-shadow:0 4px 16px rgba(0,0,0,.35);border:2px solid #1e3a8a;font-family:'Segoe UI','Sarabun',system-ui,sans-serif">🏠 รายงานทั้งหมด</a>
<header class="top{' hasfail' if n['fail'] else ''}">
  <h1>🤖 [E2E @{tier}] TAKRA Hub — ผลรันอัตโนมัติ</h1>
  <div class="sub">Playwright web e2e (ยิง UAT) · รันเมื่อ {run_at:%a %d %b %Y %H:%M} · generate อัตโนมัติจาก results.json (read-only)</div>
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
  {gate_box}
  {feat_summary}
  {'<div class="note-box">⚠️ มีเคส FAIL — ใต้ชื่อเคสมีคำอธิบายสั้น ๆ ว่าทำไมตก · กดที่แถวเพื่อดูคำอธิบาย + error เต็ม</div>' if n['fail'] else ''}
  {skip_box}
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
<footer>generate โดย tools/build/hub_e2e_run_report.py · QA takra-hub</footer>
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
function gotoFeature(file,anchorId){{
  const off=F.file===file;
  F.file=off?null:file;
  document.querySelectorAll('tr.fsrow').forEach(x=>x.classList.toggle('active',!off&&x.dataset.file===file));
  apply();
  if(!off){{const row=document.getElementById(anchorId);
    if(row)row.scrollIntoView({{behavior:'smooth',block:'start'}});}}
}}
document.querySelectorAll('tr.fsrow').forEach(tr=>tr.addEventListener('click',e=>{{
  e.preventDefault(); gotoFeature(tr.dataset.file,tr.dataset.anchor);
}}));
if(location.hash.startsWith('#feat-')){{
  const row=document.getElementById(location.hash.slice(1));
  if(row)gotoFeature(row.dataset.file,row.id);
}}
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
        ROOT, "projects", "takra-hub", f"{run_at:%Y}", f"{run_at:%m}", "reports",
        f"takra-hub-e2e-{a.tier}-{run_at:%Y%m%d-%H%M}.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(stats, rows, a.tier, a.branch, a.note, run_at))
    print(out)


if __name__ == "__main__":
    main()
