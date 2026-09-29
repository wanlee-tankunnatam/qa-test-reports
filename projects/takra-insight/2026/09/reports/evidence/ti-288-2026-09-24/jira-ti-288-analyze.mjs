// throwaway (QA · TI-288) — offline analysis of a poller capture. Reads only the jsonl; touches nothing else.
// usage: node jira-ti-288-analyze.mjs <capture.jsonl> [--json out.json]
import { readFileSync, writeFileSync } from 'node:fs'
import { steppedCtaDisplay } from './ctaDisplay.mjs'

const f = process.argv[2]
const jout = process.argv.includes('--json') ? process.argv[process.argv.indexOf('--json') + 1] : null
const recs = readFileSync(f, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l))
const qs = recs.filter((r) => r.kind === 'qs' && r.status === 200 && r.available === true && Number.isFinite(r.rate))
const bad = recs.filter((r) => r.kind === 'qs').length - qs.length
const health = recs.filter((r) => r.kind === 'health')
const TAU = 90_000
const out = { file: f, samples: qs.length, unusableSamples: bad }
if (qs.length < 5) { console.log(JSON.stringify({ ...out, verdict: 'NO DATA (need ≥5 usable samples)' }, null, 2)); process.exit(0) }

const T = qs.map((r) => r.ts), R = qs.map((r) => r.rate), C = qs.map((r) => r.count)
out.durationMin = +((T.at(-1) - T[0]) / 60000).toFixed(2)
out.gaps = { maxSampleGapS: +(Math.max(...T.slice(1).map((t, i) => t - T[i])) / 1000).toFixed(1) }
out.health = { intentAlwaysTrue: health.length ? health.every((h) => h.intent === true) : null, intentModelAlwaysTrue: health.length ? health.every((h) => h.intent_model === true) : null }
out.rate = { min: Math.min(...R), max: Math.max(...R), zeroSamples: R.filter((v) => v === 0).length }

// ── new-data events = count increments (count = eligible rows in the 5τ horizon)
const arrivals = []           // {ts, k}
for (let i = 1; i < C.length; i++) if (C[i] > C[i - 1]) arrivals.push({ ts: T[i], k: C[i] - C[i - 1] })
out.newDataEvents = arrivals.length
out.newRowsSeen = arrivals.reduce((a, b) => a + b.k, 0)
const dataBetween = (a, b) => arrivals.some((x) => x.ts > a && x.ts <= b)

// ── AC1/AC2 (engine): no rise without new data; aging step ≤ exp slope + rounding slack
let riseNoData = 0, cliff = 0
for (let i = 1; i < R.length; i++) {
  const dt = T[i] - T[i - 1]
  const newData = C[i] > C[i - 1]
  if (!newData && R[i] > R[i - 1] + 0.05) riseNoData++
  if (!newData) { const bound = R[i - 1] * (1 - Math.exp(-dt / TAU)) + 0.101; if (R[i - 1] - R[i] > bound + 1e-9) cliff++ }
}
out.engine = { riseWithoutNewData: riseNoData, agingCliffs: cliff }

// ── the reported symptom (AC8): a DROP with no new data that returns to the same value within 45 s
function flips(series) {
  let drops = 0, flip = 0, changes = 0
  for (let i = 1; i < series.length; i++) {
    if (series[i] !== series[i - 1]) changes++
    if (series[i] < series[i - 1]) {
      const noDataBefore = !dataBetween(T[i] - 5000, T[i])
      if (!noDataBefore) continue
      drops++
      for (let j = i + 1; j < series.length && T[j] - T[i] <= 45_000; j++) if (series[j] >= series[i - 1]) { flip++; break }
    }
  }
  const min = (T.at(-1) - T[0]) / 60000
  return { changes, changesPerMin: +(changes / min).toFixed(2), selfDrops: drops, dropThenReturnWithin45s: flip }
}
let tile = null; const tileSim = R.map((v) => { tile = steppedCtaDisplay(tile, v) ?? tile; return tile })
out.tileSim_shippedRule = flips(tileSim)
out.rawRoundedControl = flips(R.map((v) => Math.round(v)))
// control: the pre-fix hard 60 s window, rebuilt from the observed arrivals (APPROXIMATE — arrival = the sample where count rose,
// i.e. label-visible time, a few s after the comment itself)
const oldRate = T.map((t) => arrivals.filter((a) => a.ts > t - 60_000 && a.ts <= t).reduce((s, a) => s + a.k, 0))
out.oldWindow60sControl_approx = flips(oldRate)

// ── what the window actually RENDERED (only when the capture came from jira-ti-288-live.mjs, which reads the tile text)
const uiRaw = qs.map((r) => (Number.isFinite(r.uiTile) ? r.uiTile : null))
if (uiRaw.some((v) => v !== null)) {
  let carry = null; const ui = uiRaw.map((v) => { if (v !== null) carry = v; return carry })
  const aligned = ui.map((v, i) => [v, i]).filter(([v]) => v !== null)
  // the renderer polls every ~1.5 s and re-renders on its own clock → accept a match with the rule's value at any of the last 5 samples
  let match = 0; const miss = []
  for (const [v, i] of aligned) { const win = tileSim.slice(Math.max(0, i - 5), i + 1); if (win.includes(v)) match++; else if (miss.length < 8) miss.push({ tS: +((T[i] - T[0]) / 1000).toFixed(0), ui: v, rule: tileSim[i], engineRate: R[i] }) }
  const seq = []; for (const v of ui) if (v !== null && seq.at(-1) !== v) seq.push(v)
  const uiFlips = flips(ui.map((v) => (v === null ? -1 : v)))
  out.uiTile = { samplesWithTile: aligned.length, matchesShippedRule: `${match}/${aligned.length}`, mismatches: miss, valueSequence: seq.slice(0, 60), ...uiFlips, uiCommentsMax: Math.max(0, ...qs.map((r) => r.uiComments || 0)) }
}

// ── verdict on what THIS capture can prove
const flipRisk = out.tileSim_shippedRule.dropThenReturnWithin45s + (out.uiTile ? out.uiTile.dropThenReturnWithin45s : 0)
const enough = out.newRowsSeen >= 5
out.verdict = !enough ? 'INCONCLUSIVE — too few price_ask arrivals in this capture to exercise the bug (need ≥5, ideally a chatty live)'
  : (riseNoData === 0 && cliff === 0 && flipRisk === 0) ? 'PASS on this capture (no rise without data · no cliffs · 0 drop→return flips on the shipped tile rule)'
  : 'FAIL/REVIEW — see engine/tileSim fields'
console.log(JSON.stringify(out, null, 2))
if (jout) writeFileSync(jout, JSON.stringify(out, null, 2))
