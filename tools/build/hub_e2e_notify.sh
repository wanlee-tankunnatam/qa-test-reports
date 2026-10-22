#!/usr/bin/env bash
# รัน e2e ของ takra-hub (Playwright ยิง UAT) → รายงาน HTML ต่อรอบ → push สรุป + ลิงก์เข้ากลุ่ม LINE "Bot Hub"
#
# ใช้:
#   tools/build/hub_e2e_notify.sh [--tier smoke|regression] [--results <json>] [--no-push] [--no-line] [--no-pull]
#   --tier smoke      = project smoke (ไม่ต้อง login · ไม่ใช้รหัสอะไรเลย)
#   --tier regression = @regression|@fullloop − "เส้นเงินเต็มวง" (G-WS-01: ห้ามสร้าง order/ทีมจริงบน UAT)
#   --results = ข้ามการรัน ใช้ results.json ที่มีอยู่ (ไว้ทดสอบตัวรายงาน/แจ้งเตือน)
#   --no-push = ไม่ commit/push repo รายงาน · --no-line = ไม่ส่ง LINE (dry run)
#
# ต่างจากตัว insight: hub ยิง UAT ตรง ⇒ ไม่มี build / ไม่ล้าง MAIN_VITE_* / ไม่แยกโปรไฟล์
# สิ่งที่คงไว้จากบทเรียน insight: pull เฉพาะ checkout สะอาด · workers=1 · กันรันซ้อน · เฝ้าโควตา LINE
set -euo pipefail

REPORTS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HUB="/Users/ice/Documents/rf/takra-hub"
PAGES_BASE="https://wanlee-tankunnatam.github.io/qa-test-reports"

TIER=smoke; RESULTS=""; DO_PUSH=1; DO_LINE=1; DO_PULL=1
while [ $# -gt 0 ]; do case "$1" in
  --tier) TIER="$2"; shift 2;;
  --results) RESULTS="$2"; shift 2;;
  --no-push) DO_PUSH=0; shift;;
  --no-line) DO_LINE=0; shift;;
  --no-pull) DO_PULL=0; shift;;
  *) echo "unknown arg: $1" >&2; exit 2;;
esac; done

# ── 0. กันรันซ้อน (กฎ QA: ห้ามสองรันใช้ UAT พร้อมกัน) + pull เฉพาะ checkout สะอาด ──
if [ -z "$RESULTS" ] && pgrep -f "playwright test" >/dev/null 2>&1; then
  echo "มี playwright รันอยู่แล้วบนเครื่องนี้ — กันชน UAT ตามกฎ QA ⇒ ยกเลิกรอบนี้" >&2; exit 1
fi
if [ "$DO_PULL" = 1 ] && [ -z "$RESULTS" ]; then
  if [ -z "$(git -C "$HUB" status --porcelain)" ]; then
    LOCK_BEFORE=$(md5 -q "$HUB/pnpm-lock.yaml" 2>/dev/null || true)
    echo "== git pull ($(git -C "$HUB" branch --show-current)) =="
    git -C "$HUB" pull --ff-only || echo "⚠️ pull ไม่ได้ (non-ff/ออฟไลน์) — รันบนโค้ดที่มี" >&2
    LOCK_AFTER=$(md5 -q "$HUB/pnpm-lock.yaml" 2>/dev/null || true)
    if [ "$LOCK_BEFORE" != "$LOCK_AFTER" ]; then
      echo "== lockfile เปลี่ยน → pnpm install =="
      (cd "$HUB" && pnpm install --frozen-lockfile >/dev/null)
    fi
  else
    echo "⚠️ checkout ไม่สะอาด — ข้าม pull, รันบนโค้ดที่มี (เลี่ยงทับงานค้างของ session อื่น)" >&2
  fi
fi

BRANCH=$(git -C "$HUB" branch --show-current)
NOTE="UAT · uat-hub.takra.ai จริง"

# ── 1. รันเทส (เว้นแต่ส่ง --results มา) — ยิง UAT ตรง ไม่ต้อง boot อะไร ─────────
if [ -z "$RESULTS" ]; then
  RESULTS="$(mktemp -d)/results.json"
  set +e
  if [ "$TIER" = smoke ]; then
    NOTE="UAT · ชุด smoke ไม่ต้อง login"
    (cd "$HUB" && E2E_SKIP_AUTH=1 PLAYWRIGHT_JSON_OUTPUT_NAME="$RESULTS" \
        pnpm --filter web exec playwright test --project=smoke --reporter=list,json)
  else
    # regression: ต้องมีรหัสบัญชีครบใน root .env (global-setup login เอง) · ตัดเส้นเงินเต็มวง (G-WS-01)
    (cd "$HUB" && PLAYWRIGHT_JSON_OUTPUT_NAME="$RESULTS" \
        pnpm --filter web exec playwright test \
          --grep "@regression|@fullloop" --grep-invert "เส้นเงินเต็มวง" \
          --workers=1 --reporter=list,json)
  fi
  set -e
  [ -s "$RESULTS" ] || { echo "ไม่มี results.json — รันล้มก่อนถึง reporter (เช็ค .env/VPN/UAT)" >&2; exit 1; }
fi

# ── 2. สร้างรายงาน HTML ──────────────────────────────────────────────────────
OUT=$(python3 "$REPORTS_ROOT/tools/build/hub_e2e_run_report.py" \
        --results "$RESULTS" --tier "$TIER" --branch "$BRANCH" --note "$NOTE")
REL="${OUT#"$REPORTS_ROOT"/}"
URL="$PAGES_BASE/$REL"
echo "report: $OUT"

# ── 3. commit + push ให้ลิงก์ Pages ใช้ได้ ───────────────────────────────────
if [ "$DO_PUSH" = 1 ]; then
  git -C "$REPORTS_ROOT" add "$REL"
  git -C "$REPORTS_ROOT" commit -q -m "report(hub): e2e @$TIER $(date +%d/%m' '%H:%M) อัตโนมัติ" -- "$REL"
  git -C "$REPORTS_ROOT" push -q
  echo "pushed: $URL"
fi

# ── 4. สรุป + ส่ง LINE (กลุ่ม Bot Hub เท่านั้น — ห้ามกลุ่มอื่น) ─────────────────
# คำสั่งผู้ใช้ 22 ต.ค. 2026: ทุกผลการรันต้องบอกสาเหตุตกเป็นภาษาคน + เหตุผล skip (ฉบับเต็มอยู่ในรายงาน HTML)
SUMMARY=$(python3 - "$RESULTS" <<'EOF'
import json, sys
from collections import Counter
HINTS = [
    ("Error reading storage state", "ไม่มี login บัญชีนี้ (.env)"),
    ("504", "UAT ตอบ 504 ชั่วคราว"),
    ("strict mode violation", "หน้าเจอของซ้ำ/เปลี่ยน"),
    ("page.goto: Timeout", "เปิดหน้าไม่ขึ้น (UAT ช้า)"),
    ("element(s) not found", "UI เปลี่ยน — หาของเดิมไม่เจอ"),
    ("Timeout", "รอจนหมดเวลา"),
    ("timeout", "รอจนหมดเวลา"),
    ("expect(", "ค่าบนหน้าไม่ตรงที่เทสคาด (บัคจริง/มีตั๋ว)"),
]
def hint(err):
    return next((h for k, h in HINTS if k in err), "ดูในรายงาน")
SKIP_HINTS = [
    (("TKH-230", "trial เปิดอยู่", "ทดลองใช้ฟรี"), "trial ปิดชั่วคราว (TKH-230)"),
    (("ยังไม่ build", "รอ Story", "ยังไม่ถูกเคาะ"), "ฟีเจอร์ยังสร้างไม่เสร็จ"),
    (("ยังไม่มีบัญชี", "E2E_USER", "ไม่ได้ตั้ง", "CONSENT"), "ยังไม่ได้ตั้งบัญชีทดสอบใน .env"),
    (("ลบไม่ได้", "คืนไม่ได้", "ย้อนกลับ", "ทีมจริง", "ลูกค้าจริง", "กินที่นั่ง", "ขยะบัญชี",
      "บัญชีจริง", "สั่งซื้อจริง", "ใช้แล้วทิ้ง", "ให้ลูกค้าเห็น", "ลบเองไม่ได้"), "กันข้อมูลจริงบน UAT พัง (รอ TKH-285)"),
    (("อีเมล", "code ของจริง", "mailhog"), "ต้องอ่านอีเมลจริง — สคริปต์ทำไม่ได้"),
    (("manual", "visual", "ด้วยตา", "skeleton"), "ต้องดูด้วยตา (manual)"),
    (("ไม่มี", "ยังไม่มี", "ว่าง", "fixture", "ไม่พบ", "ไม่เต็ม", "ไม่ถึงเงื่อนไข", "0 แถว",
      "เสี้ยววินาที", "not_configured"), "UAT ไม่มีข้อมูล/fixture ให้ตรวจ"),
]
def skip_hint(raw):
    return next((h for ks, h in SKIP_HINTS if any(k in raw for k in ks)), raw[:55])
d = json.load(open(sys.argv[1]))
s = d.get("stats", {})
fails, skips = [], Counter()
def walk(suites):
    for su in suites:
        for sp in su.get("specs", []):
            for t in sp.get("tests", []):
                st = t.get("status")
                if st in ("unexpected", "flaky"):
                    mark = "❌" if st == "unexpected" else "⚠️"
                    title = sp["title"].split(" @")[0]
                    err = ((t.get("results") or [{}])[-1].get("error") or {}).get("message") or ""
                    fails.append(f"{mark} {title[:60]}\n   → {hint(err)}")
                elif st == "skipped":
                    ann = next((a.get("description") for a in t.get("annotations", [])
                                if a.get("type") in ("skip", "fixme") and a.get("description")), None)
                    skips[skip_hint(ann) if ann else "ไม่ได้รัน (ตัวก่อนหน้าในชุด serial ตก)"] += 1
        walk(su.get("suites", []))
walk(d.get("suites", []))
m, sec = divmod(int(s.get("duration", 0) / 1000), 60)
nf = s.get("unexpected", 0)
print("✅ GATE: ผ่าน — ไม่มีเคสตก" if nf == 0 else f"⛔ GATE: ไม่ผ่าน — ตก {nf} เคส")
print(f"✅ ผ่าน {s.get('expected',0)} · ❌ ตก {nf} · ⚠️ flaky {s.get('flaky',0)} · ⏭ ข้าม {s.get('skipped',0)} · ⏱ {m} นาที {sec} วิ")
for f in fails[:8]:
    print(f)
if len(fails) > 8:
    print(f"…และอีก {len(fails)-8} เคส (ดูในรายงาน)")
if skips:
    print(f"⏭ ข้ามเพราะ (ตัวหลัก):")
    for reason, c in skips.most_common(4):
        print(f"· ×{c} {reason}")
    rest = sum(skips.values()) - sum(c for _, c in skips.most_common(4))
    if rest:
        print(f"· อีก {rest} เคส — เหตุผลครบทุกตัวอยู่ในรายงาน")
EOF
)

# เครื่อง QA: ค่า LINE อยู่ใน root .env ของ hub (E2E_HUB_LINE_*) · CI: inject เป็น env ตรง ๆ
if [ "$DO_LINE" = 1 ] && [ -f "$HUB/.env" ]; then
  while IFS= read -r line; do export "$line"; done \
    < <(grep "^E2E_HUB_LINE" "$HUB/.env" || true)
fi
if [ "$DO_LINE" = 1 ] && { [ -z "${E2E_HUB_LINE_TOKEN:-}" ] || [ -z "${E2E_HUB_LINE_GROUP_ID:-}" ]; }; then
  echo "⚠️ ไม่มี E2E_HUB_LINE_TOKEN/GROUP_ID (ทั้งใน .env และ environment) — ข้ามการส่ง LINE" >&2
  DO_LINE=0
fi

if [ "$DO_LINE" = 1 ]; then
  # เฝ้าโควตา push (แพลนฟรี 300/เดือน — Bot Test ใช้ร่วมกับกลุ่ม Bot Insight) — เกิน 80% เตือนในข้อความ
  QUOTA_LINE=""
  USED=$(curl -s https://api.line.me/v2/bot/message/quota/consumption \
           -H "Authorization: Bearer $E2E_HUB_LINE_TOKEN" | grep -oE '[0-9]+' | head -1 || echo "")
  LIMIT=$(curl -s https://api.line.me/v2/bot/message/quota \
           -H "Authorization: Bearer $E2E_HUB_LINE_TOKEN" | grep -oE '"value":[0-9]+' | grep -oE '[0-9]+' || echo "")
  if [ -n "$USED" ] && [ -n "$LIMIT" ] && [ "$USED" -ge $((LIMIT * 80 / 100)) ]; then
    QUOTA_LINE="
⚠️ โควตา LINE เดือนนี้ใกล้เต็ม: $USED/$LIMIT — พิจารณาแจ้งเฉพาะ FAIL หรืออัปแพลน"
  fi
  TEXT="🧪 ผลรัน e2e @$TIER — takra-hub
$SUMMARY
env: $NOTE
branch: $BRANCH
📄 รายงาน: $URL$QUOTA_LINE"
  CODE=$(python3 - "$E2E_HUB_LINE_TOKEN" "$E2E_HUB_LINE_GROUP_ID" "$TEXT" <<'EOF'
import sys, json, urllib.request
tok, gid, text = sys.argv[1], sys.argv[2], sys.argv[3]
req = urllib.request.Request("https://api.line.me/v2/bot/message/push",
    data=json.dumps({"to": gid, "messages": [{"type": "text", "text": text}]}).encode(),
    headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
print(urllib.request.urlopen(req).status)
EOF
)
  echo "LINE push: HTTP $CODE"
fi
