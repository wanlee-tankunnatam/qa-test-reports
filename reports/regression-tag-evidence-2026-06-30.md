# Regression/Smoke Tag + Evidence Run — 2026-06-30

Engineer: qa-test-engineer · Env: Colima (macOS arm64) · Docker via Testcontainers
Principle: green never lies — counts below are real test-runner output, not estimates.

## Env (Colima)
```
DOCKER_HOST="unix:///Users/ice/.colima/default/docker.sock"
TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE="/var/run/docker.sock"
TESTCONTAINERS_HOST_OVERRIDE="127.0.0.1"
TESTCONTAINERS_RYUK_DISABLED="true"
```
colima status: running (Virtualization.Framework, docker runtime). `docker ps` OK via colima socket. Docker Server 29.5.2.

---

## TASK A — Tags applied (verified it() name match, not just line number)

### chat-tokens.repository.spec.ts (apps/api/test/chat-tokens/)
PRE-TAG GATE: ran the spec on Colima FIRST to confirm TC-R-3 / TC-R-10 are green
(legacy claimed stale FAIL). Result: 1 suite passed, 12 passed, 0 failed (0.6s).
Both TC-R-3 (UPSERT reconnect) and TC-R-10 (concurrent UPSERT) GREEN -> cleared to tag.

- TC-R-2 (getById RLS cross-tenant)  -> ` @regression @P1`  [was line 104]
- TC-R-3 (UPSERT same row reconnect) -> ` @regression @P1`  [was line 124]
- TC-R-9 (tenant isolation list/getByShop) -> ` @regression @P1` [was line 312]
- TC-R-10 (10 concurrent UPSERT -> 1 row) -> ` @regression @P1` [was line 350]

### audit-log.e2e-spec.ts (apps/api/test/audit/)
- RBAC cs_manager -> 403 (admin-gate) -> ` @regression @P1`  [line 123]
- Admin reads tenant A, newest first; RLS hides B -> ` @regression @P1 @smoke` [line 127]
- append-only: gochat_app cannot UPDATE/DELETE -> ` @regression @P1` [line 187]

### auth-rail.e2e-spec.ts (apps/api/test/auth/)
- valid tenant-A token -> GET /stores ONLY tenant A -> ` @regression @P1 @smoke` [line 109]

### web (apps/web/)
- connections-v3.smoke.spec.ts:71 `Tab A: shop list renders (>= 1 card visible)` -> ` @smoke`
- package.json: added `"test:smoke:web": "playwright test --grep @smoke"`

NOTE: no production/logic code touched. Web diff = test-name text + 1 npm script only.

---

## TASK B — Evidence runs (real counts)

### 1) pnpm --filter @gochat/api test:regression   (22:14 + re-run 22:16)
exit 0 (both runs, stable)
Test Suites: 101 skipped, 6 passed, 6 of 107 total
Tests:       1046 skipped, 99 passed, 1145 total
(skipped = non-@regression tests filtered out by `-t '@regression'` — NOT a Docker skip)
=> 0 failed. Our tagged api cases selected + green.

### 2) pnpm --filter @gochat/api test:smoke   (22:16)
exit 0
Test Suites: 43 skipped, 3 passed, 3 of 46 total
Tests:       452 skipped, 6 passed, 458 total
=> 0 failed. 3 passing suites = followup + auth-rail + audit-log (only e2e files with @smoke).
Our 2 new api smoke cases (auth-rail valid-token, audit Admin-reads) confirmed green.

### 3) pnpm --filter @gochat/web test:smoke:web  (--grep @smoke)  (22:17)
exit 1 — FAILED
1 test selected (connections Tab A shop-list @smoke) -> 1 FAILED, 0 passed.
Reason: getByTestId('shop-list') never visible (timeout 10s, element not found).

Scoping run (full connections-v3.smoke.spec.ts, all 9, no grep):
  3 passed, 6 FAILED (24.0s)
  PASS: tab-nav (#54), header-add-connection (#84), wizard-alias (#98)
  FAIL: shop-list (#71), shop-filters (#124), kebab-detail (#139),
        kebab-disconnect (#167), region-badge (#188), shopcard-logo (#202)
  -> every test depending on shop-list / shop-card render FAILS.

ROOT CAUSE SIGNATURE: preview webServer logged `AggregateError [ECONNREFUSED]` x26.
Build succeeds (914 modules, 351ms). Page shell + "การเชื่อมต่อ (Connections)" heading
render, but the shop list area never populates — the page appears to attempt a real
backend fetch that is refused, despite the spec header claiming mock-first / no API.
This is a REAL regression in the connections shop-list render (hermetic mock path broken),
pre-existing — my changes are text-only (tag) and cannot cause it.

---

## Outcome
- api regression + api smoke: GREEN on Colima (0 fail, not false-skip).
- web smoke (connections shop-list): RED — 6/9 fail, blocker reported (do NOT claim green).
- @smoke tag is applied to a currently-RED web test; per green-never-lies it is NOT a
  passing smoke gate until the connections shop-list render is fixed.

Raw logs: scratchpad reg-verbose.log / smoke-api.log / smoke-web-full.log / smoke-web-line71.log
