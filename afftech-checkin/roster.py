"""Roster = 30 people from the registration CSV + walk-ins from extras.json (baked into the page)."""
import csv, json, re, pathlib

SRC = "/Users/ice/Downloads/registrations-afftech-2-out-of-the-cave-2026-09-05.csv"

def digits(s):
    d = re.sub(r"\D", "", s or "")
    if d.startswith("66") and len(d) == 11: d = "0" + d[2:]
    return d
def fmt(d): return f"{d[:3]}-{d[3:6]}-{d[6:]}" if len(d) == 10 else d
def split_note(s):
    m = re.search(r"\s*\(\s*([^)]*?)\s*\)\s*", s or "")
    if not m: return (s or "").strip(), ""
    return (s[:m.start()] + s[m.end():]).strip(), m.group(1).strip()

def build_roster(extras_path):
    with open(SRC, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    net = [r for r in rows if (r.get("กิจกรรมเสริม") or "") == "Exclusive Networking Night" and r.get("สถานะชำระเงิน") == "paid"]
    people, order = {}, []
    for r in net:
        rid = r["รหัสลงทะเบียน"]
        first, n1 = split_note(r["ชื่อ"]); last, n3 = split_note(r["นามสกุล"]); nick, n2 = split_note(r["ชื่อเล่น"])
        d = digits(r["เบอร์โทร"])
        m = re.match(r"ออเดอร์ (REG-\w+) \(\d+ ใบ\) — ผู้ซื้อ:", r["หมายเหตุ"] or "")
        people[rid] = dict(id=rid, nick=nick, first=first, last=last, phone=fmt(d) if d else "", phoneRaw=d,
                           tag=n1 or n2 or n3, companionOf=m.group(1) if m else "", mainCheckin=(r["เช็คอิน"] == "เช็คอินแล้ว"))
        order.append(rid)
    final = []
    for rid in order:
        p = people[rid]
        if p["companionOf"]: continue
        final.append(p)
        for c in (people[x] for x in order if people[x]["companionOf"] == rid):
            c["buyerNick"] = p["nick"] or p["first"]; c["buyerPhone"] = p["phone"]; c["buyerPhoneRaw"] = p["phoneRaw"]
            final.append(c)
    assert len(final) == 30, len(final)

    # walk-ins added at the door, kept in extras.json so they survive any browser
    seed = {}
    ep = pathlib.Path(extras_path)
    extras = json.loads(ep.read_text(encoding="utf-8")) if ep.exists() else []
    for i, e in enumerate(extras, 1):
        d = digits(e.get("phone", ""))
        pid = e.get("id") or f"X-{i:02d}"
        final.append(dict(id=pid, nick=(e.get("nick") or "").strip(), first=(e.get("first") or "").strip(), last=(e.get("last") or "").strip(),
                          phone=fmt(d) if d else "", phoneRaw=d, tag=(e.get("tag") or "").strip(), reg=(e.get("reg") or "").strip(),
                          companionOf="", mainCheckin=True))
        if e.get("checkedIn"):
            seed[pid] = {"at": e.get("at") or "2026-09-05T12:00:00.000Z"}
    for i, p in enumerate(final, 1): p["n"] = i
    return final, seed
