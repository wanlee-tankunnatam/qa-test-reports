# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: multi-session-flag.spec.js >> an engine on the other side of the flag is refused — and STAYS refused past a watchdog tick
- Location: e2e/multi-session-flag.spec.js:116:1

# Error details

```
Error: expect(received).toBe(expected) // Object.is equality

Expected: "engine-flag-mismatch"
Received: "port-foreign"

Call Log:
- Timeout 30000ms exceeded while waiting on the predicate
```

# Test source

```ts
  57  |         const r = await fetch(`${base}/health`, { signal: AbortSignal.timeout(3000) });
  58  |         const h = await r.json();
  59  |         const own = await window.liveHost?.backendState?.();
  60  |         // `ok` alone is not enough: it is also true for an ADOPTED engine, which is exactly the
  61  |         // leftover-process case that would let this test pass without the app spawning anything
  62  |         // — and without the spawn-env normalization ever being exercised.
  63  |         if (typeof h.multi_session === 'boolean' && own?.ok && own.adopted === false) return h.multi_session;
  64  |       } catch { /* not up yet */ }
  65  |       if (Date.now() > deadline) return 'engine-never-answered';
  66  |       await new Promise((r) => setTimeout(r, 1000));
  67  |     }
  68  |   }, { ms: timeoutMs, base: ENGINE_BASE });
  69  | }
  70  | 
  71  | /** The engine port is fixed per run (ENGINE_PORT), so a leftover engine poisons the next launch. Wait it out. */
  72  | async function waitForFreePort(timeoutMs = 30_000) {
  73  |   const { createConnection } = await import('node:net');
  74  |   const deadline = Date.now() + timeoutMs;
  75  |   for (;;) {
  76  |     const busy = await new Promise((resolve) => {
  77  |       const s = createConnection({ port: ENGINE_PORT, host: '127.0.0.1' })
  78  |         .on('connect', () => { s.destroy(); resolve(true); })
  79  |         .on('error', () => resolve(false));
  80  |     });
  81  |     if (!busy) return true;
  82  |     if (Date.now() > deadline) return false;
  83  |     await new Promise((r) => setTimeout(r, 500));
  84  |   }
  85  | }
  86  | 
  87  | test.beforeEach(async () => {
  88  |   // A leftover engine silently changes what these tests measure, so make it a hard failure
  89  |   // rather than letting the next launch adopt someone else's process.
  90  |   expect(await waitForFreePort(), `:${ENGINE_PORT} still held by a leftover engine`).toBe(true);
  91  | });
  92  | 
  93  | test('default (nothing set): main AND the engine are both multi-session', async () => {
  94  |   test.setTimeout(120_000);
  95  |   const { app, window } = await launchApp({ multiSession: 'unset' });
  96  |   try {
  97  |     expect(await mainFlag(window)).toBe(true);
  98  |     expect(await engineFlag(window)).toBe(true);
  99  |   } finally {
  100 |     await closeApp(app);
  101 |   }
  102 | });
  103 | 
  104 | test('LHM_MULTI_SESSION=0: main AND the engine are both off — the off-switch is real on both sides', async () => {
  105 |   test.setTimeout(120_000);
  106 |   const { app, window } = await launchApp({ multiSession: false });
  107 |   try {
  108 |     // Pre-resolver this was `true`: main read "0" as truthy and ran full multi-session.
  109 |     expect(await mainFlag(window)).toBe(false);
  110 |     expect(await engineFlag(window)).toBe(false);
  111 |   } finally {
  112 |     await closeApp(app);
  113 |   }
  114 | });
  115 | 
  116 | test('an engine on the other side of the flag is refused — and STAYS refused past a watchdog tick', async () => {
  117 |   test.setTimeout(180_000);
  118 |   // The unpackaged app pins userData to <appData>/takra-insight-dev on every platform, but the
  119 |   // venv layout differs; keep this to the platform the venv is built for rather than failing
  120 |   // elsewhere for a reason that has nothing to do with the flag.
  121 |   test.skip(process.platform === 'win32', 'venv path is posix-only in this spec');
  122 |   // Stand up an engine with the flag OFF, the way a stale `py:dev` or a pre-flip build leaves one.
  123 |   const engine = spawn(join(APPS_DESKTOP, '.venv/bin/python'), [join(APPS_DESKTOP, 'server.py')], {
  124 |     cwd: APPS_DESKTOP,
  125 |     stdio: 'ignore',
  126 |     env: {
  127 |       ...process.env,
  128 |       PYTHONUNBUFFERED: '1',
  129 |       LHM_MULTI_SESSION: '0',
  130 |       // Same data dir the unpackaged app uses, so it classifies as `ours` — which is the whole
  131 |       // point: identity matches, only the flag differs.
  132 |       LHM_DATA_DIR: join(appDataDir(), 'takra-insight-dev'),
  133 |     },
  134 |   });
  135 |   // spawn() reports ENOENT asynchronously; an unhandled 'error' would kill the whole Playwright
  136 |   // worker instead of failing this test (a fresh worktree has no .venv — see apps/desktop/CLAUDE.md).
  137 |   let spawnError = null;
  138 |   engine.on('error', (e) => { spawnError = e; });
  139 |   try {
  140 |     // Wait for it to actually own the port before the app looks. 127.0.0.1, not localhost:
  141 |     // server.py binds v4 only, and a localhost→::1 resolution would fail every iteration.
  142 |     let up = false;
  143 |     for (let i = 0; i < 60 && !spawnError; i++) {
  144 |       up = await fetch(`${ENGINE_BASE}/health`).then((r) => r.ok).catch(() => false);
  145 |       if (up) break;
  146 |       await new Promise((r) => setTimeout(r, 500));
  147 |     }
  148 |     // Otherwise the app spawns its OWN (agreeing) engine and the failure reads as
  149 |     // "expected a refusal, got ok" — a misattributed red.
  150 |     expect(spawnError, `test engine failed to spawn: ${spawnError?.message}`).toBe(null);
  151 |     expect(up, `test engine never bound :${ENGINE_PORT} — nothing to refuse`).toBe(true);
  152 |     const { app, window } = await launchApp({ multiSession: true }); // app ON, engine OFF
  153 |     try {
  154 |       // Poll rather than sample once: launchApp only awaits domcontentloaded, so the first
  155 |       // backend:state push may not have landed yet.
  156 |       await expect.poll(async () => (await backendState(window))?.reason, { timeout: 30_000 })
> 157 |         .toBe('engine-flag-mismatch');
      |          ^ Error: expect(received).toBe(expected) // Object.is equality
  158 |       // The bug this pins: reduceWatchdog short-circuits on `ours` and used to report healthy on
  159 |       // the next tick, clearing the banner and driving the mismatched engine for the whole run.
  160 |       // > WATCHDOG_INTERVAL_MS (5 s) + PROBE_CAP_WATCHDOG_MS (2 s), with margin, so at least
  161 |       // one full tick provably ran between the two reads.
  162 |       await window.waitForTimeout(12_000);
  163 |       const after = await backendState(window);
  164 |       expect(after?.reason, 'the watchdog cleared the refusal').toBe('engine-flag-mismatch');
  165 |       expect(after?.ok).toBe(false);
  166 |     } finally {
  167 |       await closeApp(app);
  168 |     }
  169 |   } finally {
  170 |     engine.kill('SIGKILL');
  171 |     await waitForFreePort();
  172 |   }
  173 | });
  174 | 
  175 | test('closing the mismatched engine recovers on its own — no restart, no button', async () => {
  176 |   test.setTimeout(240_000);
  177 |   test.skip(process.platform === 'win32', 'venv path is posix-only in this spec');
  178 |   // The claim this pins: "closing the stale one is enough". It was FALSE before the fix — a
  179 |   // startup refusal returns before spawning, so the watchdog was never armed, its reducer
  180 |   // answered `none` to every probe, and nothing cleared the latch once the offending engine was
  181 |   // gone. The app sat refused forever until the user pressed Try again.
  182 |   const engine = spawn(join(APPS_DESKTOP, '.venv/bin/python'), [join(APPS_DESKTOP, 'server.py')], {
  183 |     cwd: APPS_DESKTOP,
  184 |     stdio: 'ignore',
  185 |     env: { ...process.env, PYTHONUNBUFFERED: '1', LHM_MULTI_SESSION: '0', LHM_DATA_DIR: join(appDataDir(), 'takra-insight-dev') },
  186 |   });
  187 |   let spawnError = null;
  188 |   engine.on('error', (e) => { spawnError = e; });
  189 |   let app;
  190 |   try {
  191 |     let up = false;
  192 |     for (let i = 0; i < 60 && !spawnError; i++) {
  193 |       up = await fetch(`${ENGINE_BASE}/health`).then((r) => r.ok).catch(() => false);
  194 |       if (up) break;
  195 |       await new Promise((r) => setTimeout(r, 500));
  196 |     }
  197 |     expect(spawnError, `test engine failed to spawn: ${spawnError?.message}`).toBe(null);
  198 |     expect(up, `test engine never bound :${ENGINE_PORT}`).toBe(true);
  199 | 
  200 |     ({ app } = await launchApp({ multiSession: true }));
  201 |     const window = await app.firstWindow();
  202 |     await expect.poll(async () => (await backendState(window))?.reason, { timeout: 30_000 })
  203 |       .toBe('engine-flag-mismatch');
  204 | 
  205 |     // Do exactly what the banner tells the user to do — and nothing else.
  206 |     engine.kill('SIGKILL');
  207 | 
  208 |     // The app must notice on its own, spawn its own engine, and clear the banner. Generous:
  209 |     // one watchdog tick to see the port free, then a cold engine start.
  210 |     await expect.poll(async () => await backendState(window), { timeout: 120_000 })
  211 |       .toEqual(expect.objectContaining({ ok: true, reason: null }));
  212 |     expect(await mainFlag(window)).toBe(true);
  213 |   } finally {
  214 |     if (app) await closeApp(app);
  215 |     engine.kill('SIGKILL');
  216 |     await waitForFreePort();
  217 |   }
  218 | });
  219 | 
```