#!/usr/bin/env bash
# รัน desktop e2e ของ takra-insight → สร้างรายงาน HTML ต่อรอบ → push สรุป + ลิงก์เข้ากลุ่ม LINE "Bot Insight"
#
# ใช้:
#   tools/build/insight_e2e_notify.sh [--tier smoke|regression] [--results <json>] [--no-push] [--no-line]
#   --results = ข้ามการรัน ใช้ results.json ที่มีอยู่ (ไว้ทดสอบตัวรายงาน/แจ้งเตือน)
#   --no-push = ไม่ commit/push repo รายงาน (ลิงก์ Pages จะยังไม่ขึ้น)
#   --no-line = ไม่ส่ง LINE (dry run)
#
# สูตรรันมาจากบทเรียน 2026-10-22: ต้อง (1) npm run build ก่อนเสมอ (2) blank MAIN_VITE_* ทุกตัว
# ใน .env.development (main อ่าน process.env ตอน runtime → ถ้าไม่ล้าง แอปวิ่ง cloud consent แล้ว
# UI spec ตายยกแผง) (3) โปรไฟล์สดผ่าน CFFIXED_USER_HOME+HOME (โปรไฟล์ dev ที่แชร์มี login ค้าง)
# (4) exclude e2e/ti318 แบบเดียวกับ CI (.github/workflows/desktop-e2e.yml)
set -euo pipefail

REPORTS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
INSIGHT="/Users/ice/Documents/rf/takra-insight/apps/desktop/desktop"
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

# ── 0. อัปเดตโค้ดเป็นล่าสุดก่อนรันเสมอ (ปิดได้ด้วย --no-pull) ────────────────
# pull เฉพาะเมื่อ checkout สะอาด — จะได้ไม่ทับงานค้างของคน/session อื่นบนเครื่อง
# หมายเหตุ: ถ้า pull แล้วมีของใหม่ฝั่ง engine/model bundle และจะเทสเคสที่ใช้ engine จริง
# ต้องลบ+โหลด model ใหม่ตาม Model Install Rule ใน CLAUDE.md ก่อน (tier smoke/uat
# ปัจจุบันเป็น stub/hub ล้วน ไม่แตะ model จึงไม่ทำอัตโนมัติที่นี่)
if [ "$DO_PULL" = 1 ] && [ -z "$RESULTS" ]; then
  if [ -z "$(git -C "$INSIGHT" status --porcelain)" ]; then
    LOCK_BEFORE=$(md5 -q "$INSIGHT/package-lock.json" 2>/dev/null || true)
    echo "== git pull ($(git -C "$INSIGHT" branch --show-current)) =="
    git -C "$INSIGHT" pull --ff-only || echo "⚠️ pull ไม่ได้ (non-ff/ออฟไลน์) — รันบนโค้ดที่มี" >&2
    LOCK_AFTER=$(md5 -q "$INSIGHT/package-lock.json" 2>/dev/null || true)
    if [ "$LOCK_BEFORE" != "$LOCK_AFTER" ]; then
      echo "== lockfile เปลี่ยน → npm ci =="
      (cd "$INSIGHT" && npm ci >/dev/null)
    fi
  else
    echo "⚠️ checkout ไม่สะอาด — ข้าม pull, รันบนโค้ดที่มี (เลี่ยงทับงานค้างของ session อื่น)" >&2
  fi
fi

BRANCH=$(git -C "$INSIGHT" branch --show-current)
# ป้าย env ยึดตาม tier เสมอ (ไม่ขึ้นกับว่ารันเองหรือส่ง --results มา) — กันรายงาน UAT ติดป้าย local
if [ "$TIER" = uat ]; then
  NOTE="UAT · uat-hub.takra.ai จริง"
else
  NOTE="unconfigured · โปรไฟล์แยก (เทียบเท่า CI)"
fi

# ── 1. รันเทส (เว้นแต่ส่ง --results มา) ──────────────────────────────────────
# tier "uat" = suite e2e/uat (playwright.uat.config.js) — สูตรกลับด้านกับ local:
# build:uat (bake uat-hub จริง) · ไม่ล้าง MAIN_VITE_* · ไม่แยกโปรไฟล์ · ต้อง
# `node e2e/uat/login-capture.cjs` (login มือ) มาก่อน และพอร์ต 8765 ต้องว่าง
# (ปิดแอป installed ก่อน) — รายละเอียด: e2e/uat/README.md
if [ "$TIER" = uat ] && [ -z "$RESULTS" ]; then
  if lsof -nP -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "พอร์ต 8765 ไม่ว่าง — ปิดแอป Takra Insight ที่เปิดอยู่ก่อน (e2e/uat/README.md)" >&2; exit 1
  fi
  RESULTS="$(mktemp -d)/results.json"
  NOTE="UAT · uat-hub.takra.ai จริง"
  echo "== npm run build:uat =="
  (cd "$INSIGHT" && npm run build:uat >/dev/null)
  set +e
  (cd "$INSIGHT" && PLAYWRIGHT_JSON_OUTPUT_NAME="$RESULTS" \
      npx playwright test --config playwright.uat.config.js --reporter=list,json)
  set -e
  [ -s "$RESULTS" ] || { echo "ไม่มี results.json — รันล้มก่อนถึง reporter" >&2; exit 1; }
elif [ -z "$RESULTS" ]; then
  RESULTS="$(mktemp -d)/results.json"
  echo "== npm run build =="
  (cd "$INSIGHT" && npm run build >/dev/null)
  PROFILE=$(mktemp -d /tmp/ins-e2e-profile.XXXXXX)
  # blank MAIN_VITE_* ทุก key ที่มีจริงในไฟล์ จะเพิ่ม key ใหม่ในอนาคตก็โดนล้างเอง
  BLANKS=()
  while IFS= read -r k; do BLANKS+=("$k="); done \
    < <(grep -oE '^MAIN_VITE_[A-Z_]+' "$INSIGHT/.env.development" | sort -u)
  echo "== playwright @$TIER (โปรไฟล์ $PROFILE) =="
  set +e
  (cd "$INSIGHT" && env "${BLANKS[@]}" \
      CFFIXED_USER_HOME="$PROFILE" HOME="$PROFILE" \
      PLAYWRIGHT_JSON_OUTPUT_NAME="$RESULTS" \
      npx playwright test --grep "@$TIER" --reporter=list,json 'e2e/(?!ti318)')
  set -e
  rm -rf "$PROFILE"
  [ -s "$RESULTS" ] || { echo "ไม่มี results.json — รันล้มก่อนถึง reporter" >&2; exit 1; }
fi

# ── 2. สร้างรายงาน HTML ──────────────────────────────────────────────────────
OUT=$(python3 "$REPORTS_ROOT/tools/build/insight_e2e_run_report.py" \
        --results "$RESULTS" --tier "$TIER" --branch "$BRANCH" --note "$NOTE")
REL="${OUT#"$REPORTS_ROOT"/}"
URL="$PAGES_BASE/$REL"
echo "report: $OUT"

# ── 3. commit + push ให้ลิงก์ Pages ใช้ได้ ───────────────────────────────────
if [ "$DO_PUSH" = 1 ]; then
  git -C "$REPORTS_ROOT" add "$REL"
  git -C "$REPORTS_ROOT" commit -q -m "report(insight): e2e @$TIER $(date +%d/%m' '%H:%M) อัตโนมัติ" -- "$REL"
  git -C "$REPORTS_ROOT" push -q
  echo "pushed: $URL"
fi

# ── 4. สรุป + ส่ง LINE ───────────────────────────────────────────────────────
SUMMARY=$(python3 - "$RESULTS" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
s = d.get("stats", {})
fails = []
def walk(suites):
    for su in suites:
        for sp in su.get("specs", []):
            for t in sp.get("tests", []):
                if t.get("status") in ("unexpected", "flaky"):
                    mark = "❌" if t["status"] == "unexpected" else "⚠️"
                    title = sp["title"].split(" @")[0]
                    fails.append(f"{mark} {title[:70]}")
        walk(su.get("suites", []))
walk(d.get("suites", []))
m, sec = divmod(int(s.get("duration", 0) / 1000), 60)
fail = s.get("unexpected", 0); flaky = s.get("flaky", 0)
if fail:
    print(f"🔴 GATE ไม่ผ่าน — ตก {fail} เคส")
elif flaky:
    print(f"🟡 GATE ผ่านแบบมีเงื่อนไข — flaky {flaky} เคส ควรจับตา")
else:
    print("🟢 GATE ผ่าน")
print(f"✅ ผ่าน {s.get('expected',0)} · ❌ ตก {fail} · ⚠️ flaky {flaky} · ⏭ ข้าม {s.get('skipped',0)} · ⏱ {m} นาที {sec} วิ")
for f in fails[:8]:
    print(f)
if len(fails) > 8:
    print(f"…และอีก {len(fails)-8} เคส (ดูในรายงาน)")
EOF
)

# เครื่อง QA: ค่า LINE อยู่ใน .env.development · CI: inject มาเป็น env ตรงๆ (GitHub Secrets) ไม่มีไฟล์นี้
if [ "$DO_LINE" = 1 ] && [ -f "$INSIGHT/.env.development" ]; then
  while IFS= read -r line; do export "$line"; done \
    < <(grep "^E2E_INS_LINE" "$INSIGHT/.env.development")
fi
if [ "$DO_LINE" = 1 ] && { [ -z "${E2E_INS_LINE_TOKEN:-}" ] || [ -z "${E2E_INS_LINE_GROUP_ID:-}" ]; }; then
  echo "⚠️ ไม่มี E2E_INS_LINE_TOKEN/GROUP_ID (ทั้งในไฟล์ env และ environment) — ข้ามการส่ง LINE" >&2
  DO_LINE=0
fi

if [ "$DO_LINE" = 1 ]; then
  # เฝ้าโควตา push (แพลนฟรี 300/เดือน) — เกิน 80% เตือนในข้อความเลย จะได้เห็นก่อนโดนตัด
  QUOTA_LINE=""
  USED=$(curl -s https://api.line.me/v2/bot/message/quota/consumption \
           -H "Authorization: Bearer $E2E_INS_LINE_TOKEN" | grep -oE '[0-9]+' | head -1 || echo "")
  LIMIT=$(curl -s https://api.line.me/v2/bot/message/quota \
           -H "Authorization: Bearer $E2E_INS_LINE_TOKEN" | grep -oE '"value":[0-9]+' | grep -oE '[0-9]+' || echo "")
  if [ -n "$USED" ] && [ -n "$LIMIT" ] && [ "$USED" -ge $((LIMIT * 80 / 100)) ]; then
    QUOTA_LINE="
⚠️ โควตา LINE เดือนนี้ใกล้เต็ม: $USED/$LIMIT — พิจารณาแจ้งเฉพาะ FAIL หรืออัปแพลน"
  fi
  TEXT="🧪 ผลรัน e2e @$TIER — takra-insight
$SUMMARY
env: $NOTE
branch: $BRANCH
📄 รายงาน: $URL$QUOTA_LINE"
  CODE=$(python3 - "$E2E_INS_LINE_TOKEN" "$E2E_INS_LINE_GROUP_ID" "$TEXT" <<'EOF'
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
