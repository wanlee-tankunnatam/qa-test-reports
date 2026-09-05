"""Build index.html: roster from the registration CSV + template.html, shared state in state.json via the GitHub API."""
import csv, json, re, pathlib

HERE = pathlib.Path(__file__).parent
SRC = "/Users/ice/Downloads/registrations-afftech-2-out-of-the-cave-2026-09-05.csv"
GH = {"owner": "wanlee-tankunnatam", "repo": "qa-test-reports", "branch": "master", "path": "afftech-checkin/state.json"}

# ---------- roster from CSV (embedded in the page, never modified at runtime) ----------
with open(SRC, encoding="utf-8-sig") as fh:
    rows = list(csv.DictReader(fh))
net = [r for r in rows if (r.get("กิจกรรมเสริม") or "") == "Exclusive Networking Night" and r.get("สถานะชำระเงิน") == "paid"]
def digits(s):
    d = re.sub(r"\D", "", s or "")
    if d.startswith("66") and len(d) == 11: d = "0" + d[2:]
    return d
def fmt(d): return f"{d[:3]}-{d[3:6]}-{d[6:]}" if len(d) == 10 else d
def split_note(s):
    m = re.search(r"\s*\(\s*([^)]*?)\s*\)\s*", s or "")
    if not m: return (s or "").strip(), ""
    return (s[:m.start()] + s[m.end():]).strip(), m.group(1).strip()
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
for i, p in enumerate(final, 1): p["n"] = i
assert len(final) == 30, len(final)

# ---------- transform template ----------
s = (HERE / "template.html").read_text(encoding="utf-8")
def rep(old, new):
    global s
    assert s.count(old) == 1, ("not unique/found", old[:80])
    s = s.replace(old, new)

# token setup panel under the progress bar
rep("""    <div class="bar" aria-hidden="true"><i id="bar"></i></div>
  </header>""", """    <div class="bar" aria-hidden="true"><i id="bar"></i></div>
    <div class="ghsetup" id="ghSetup" hidden>
      <p>ใส่ GitHub token ครั้งเดียวต่อเครื่อง เพื่อให้การติ๊ก/เพิ่ม/แก้ บันทึกขึ้น state.json ให้ทุกคนเห็น (ถ้าได้ลิงก์ที่มี #token= มาแล้ว หน้านี้จะจำให้เอง)</p>
      <div class="ghrow">
        <input id="ghToken" type="password" placeholder="github_pat_…" autocomplete="off" aria-label="GitHub token">
        <button class="btn primary" id="ghSave" type="button">บันทึก token</button>
      </div>
    </div>
  </header>""")
rep("""  .bar > i { display: block; height: 100%; width: 0; background: var(--accent); border-radius: 3px; transition: width .35s ease; }""",
    """  .bar > i { display: block; height: 100%; width: 0; background: var(--accent); border-radius: 3px; transition: width .35s ease; }
  .ghsetup { margin-top: 12px; padding: 12px; border: 1px dashed var(--accent); border-radius: 12px; background: var(--accent-soft); }
  .ghsetup p { margin: 0 0 8px; font-size: 13px; color: var(--text); }
  .ghrow { display: flex; gap: 8px; }
  .ghrow input { flex: 1; min-width: 0; font: inherit; font-size: 15px; padding: 9px 12px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); color: var(--text); }
  .ghrow input:focus { outline: 0; border-color: var(--accent); }
  .ghsetup[hidden] { display: none; }""")

start = s.index("  loadLocal();\n  render();\n\n  (async () => {")
end = s.index("  })();\n</script>") + len("  })();\n")
s = s[:start] + """  // ---------- shared state = state.json in the GitHub repo (read/write through the GitHub API) ----------
  const GH = __GH__;
  const GH_API = `https://api.github.com/repos/${GH.owner}/${GH.repo}/contents/${GH.path}`;
  const TOKEN_KEY = "afftech2-gh-token";
  let token = "", etag = null, version = -1;
  const EMPTY = () => ({ version: 0, [COLL]: {}, [COLL_EXTRA]: {}, [COLL_EDITS]: {}, [COLL_REMOVED]: {} });
  saveLocal = function () {};            // no per-device copy: GitHub is the only source of truth

  function loadToken() {
    const m = location.hash.match(/[#&]token=([^&]+)/);
    if (m) {
      try { localStorage.setItem(TOKEN_KEY, decodeURIComponent(m[1])); } catch {}
      history.replaceState(null, "", location.pathname + location.search);
    }
    try { token = localStorage.getItem(TOKEN_KEY) || ""; } catch { token = ""; }
    $("ghSetup").hidden = !!token;
  }
  const b64decode = str => new TextDecoder().decode(Uint8Array.from(atob(str.replace(/\\s/g, "")), c => c.charCodeAt(0)));
  function b64encode(str) { let bin = ""; new TextEncoder().encode(str).forEach(b => { bin += String.fromCharCode(b); }); return btoa(bin); }
  function ghHeaders(extra) {
    const h = Object.assign({ "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" }, extra || {});
    if (token) h["Authorization"] = "Bearer " + token;
    return h;
  }
  async function ghGet(useEtag) {
    const r = await fetch(`${GH_API}?ref=${GH.branch}`, { headers: ghHeaders(useEtag && etag ? { "If-None-Match": etag } : {}), cache: "no-store" });
    if (r.status === 304) return null;
    if (r.status === 401 || r.status === 403) { const e = new Error("auth " + r.status); e.code = r.status; throw e; }
    if (r.status === 404) return { json: EMPTY(), sha: null, etag: null };
    if (!r.ok) throw new Error("GET " + r.status);
    const j = await r.json();
    let data; try { data = JSON.parse(b64decode(j.content)); } catch { data = EMPTY(); }
    return { json: data, sha: j.sha, etag: r.headers.get("ETag") };
  }
  function applyRemote(data) {
    const v = data.version || 0;
    if (version >= 0 && v === version) return;
    version = v;
    const ci = data[COLL] || {}; const next = {};
    Object.keys(ci).forEach(id => { const b = ci[id] || {}; if (b.in) next[id] = { at: b.at || new Date().toISOString() }; });
    state = next;
    extras = Object.entries(data[COLL_EXTRA] || {}).map(([id, e]) => Object.assign({ id }, e || {}));
    overrides = Object.assign({}, data[COLL_EDITS] || {});
    removed = {}; Object.keys(data[COLL_REMOVED] || {}).forEach(id => { removed[id] = true; });
    rebuild(); render();
  }
  async function commitOps(ops) {
    if (!token) { $("ghSetup").hidden = false; toast("ใส่ GitHub token ก่อน ถึงจะบันทึกให้ทุกคนเห็นได้"); throw new Error("no token"); }
    for (let attempt = 0; attempt < 6; attempt++) {
      const cur = await ghGet(false);
      const data = cur.json;
      ops.forEach(o => { const c = data[o.coll] || (data[o.coll] = {}); if (o.op === "set") c[o.id] = o.data; else delete c[o.id]; });
      data.version = (data.version || 0) + 1;
      data.updatedAt = new Date().toISOString();
      const body = { message: "checkin: " + ops.map(o => o.op + " " + o.id).join(", "), content: b64encode(JSON.stringify(data, null, 2)), branch: GH.branch };
      if (cur.sha) body.sha = cur.sha;
      const r = await fetch(GH_API, { method: "PUT", headers: ghHeaders({ "Content-Type": "application/json" }), body: JSON.stringify(body) });
      if (r.status === 409 || r.status === 422) { await new Promise(res => setTimeout(res, 300 + Math.random() * 900)); continue; }
      if (r.status === 401 || r.status === 403) { $("ghSetup").hidden = false; toast("token ใช้ไม่ได้หรือหมดอายุ ใส่ใหม่"); throw new Error("auth " + r.status); }
      if (!r.ok) { toast("บันทึกขึ้น GitHub ไม่สำเร็จ (" + r.status + ")"); throw new Error("PUT " + r.status); }
      etag = null;
      applyRemote(data);
      return;
    }
    toast("มีคนบันทึกพร้อมกันหลายครั้ง ลองกดใหม่อีกที");
    throw new Error("conflict");
  }
  db = { collection: name => ({ doc: id => ({
    set: data => commitOps([{ op: "set", coll: name, id, data }]),
    delete: () => commitOps([{ op: "delete", coll: name, id }]),
  }) }) };
  async function pollLoop() {
    for (;;) {
      try {
        const got = await ghGet(true);
        if (got) { etag = got.etag; applyRemote(got.json); }
        setSync("shared", token ? "ซิงค์ผ่าน GitHub · ทุกคนเห็นชุดเดียวกัน" : "อ่านอย่างเดียว · ใส่ token เพื่อบันทึก");
      } catch (e) {
        if (e.code === 401) { $("ghSetup").hidden = false; setSync("local", "token ใช้ไม่ได้ · ใส่ใหม่"); }
        else if (e.code === 403) setSync("local", token ? "GitHub ปฏิเสธ (สิทธิ์/จำนวนครั้ง)" : "อ่านเกินโควตา · ใส่ token");
        else setSync("local", "ต่อ GitHub ไม่ได้ · กำลังลองใหม่");
      }
      await new Promise(res => setTimeout(res, 4000));
    }
  }
  $("ghSave").addEventListener("click", () => {
    const v = $("ghToken").value.trim();
    if (!v) return;
    try { localStorage.setItem(TOKEN_KEY, v); } catch {}
    token = v; $("ghToken").value = ""; $("ghSetup").hidden = true; etag = null;
    toast("บันทึก token แล้ว");
  });

  loadToken();
  rebuild();
  render();
  pollLoop();
""" + s[end:]
assert "window.claude" not in s
s = s.replace("__GH__", json.dumps(GH))
assert s.count("__DATA__") == 1
s = s.replace("__DATA__", json.dumps(final, ensure_ascii=False))

# ---------- standalone document ----------
s = s.replace("<title>AFFTECH #2 Networking Night</title>\n", "", 1)
html = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark">
<title>AFFTECH #2 Networking Night</title>
<style>[hidden]{display:none!important} img{max-width:100%}</style>
""" + s + "\n</body>\n</html>\n"
html = html.replace("</style>\n\n<div class=\"wrap\">", "</style>\n</head>\n<body>\n\n<div class=\"wrap\">", 1)
assert html.count("</head>") == 1 and "<body>" in html
(HERE / "index.html").write_text(html, encoding="utf-8")
print("built index.html —", len(final), "people")
