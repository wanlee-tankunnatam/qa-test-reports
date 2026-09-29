// spec TI-288: what the ชวนซื้อ tile SHOWS, given the engine's smoothed rate.
//
// The engine already fixed the DATA (quality_signals.py: an exponential-decay intensity instead of
// a hard 60 s window). This fixes the DISPLAY, which is a separate problem measured on the same
// live: rendering the raw rate with one decimal made the number visibly slide ~21 times a minute,
// and plain integer rounding put the reported 2→1→2 flip-flop back at every rounding boundary
// (measured 4-5 occurrences per run vs 10-16 for the shipped 60 s window).
//
// The rule is ASYMMETRIC, because the two directions do not carry the same evidence:
//   • UP   — only new purchase-prompt comments can raise the rate, so a rise is DATA. Repaint on
//            plain rounding, i.e. as soon as the rate belongs to a higher integer.
//   • DOWN — the rate falls purely because comments age. Nothing happened; the clock moved. So
//            require a wide margin (CTA_FALL) before repainting, which is what removes the
//            residual flip-flop (measured: 0-2 occurrences per run, display changes 0.6-1.9/min).
//   • ZERO — a measured 0 is data, not an absence (spec-ti-280, m2-3.5), and it is also what the
//            modal's `ctaZero` reason keys off. It repaints immediately, with no deadband.
//
// Review round 1 caught both directions of getting this wrong, and both were user-visible:
//   1. A symmetric rise margin of 0.6 could not react to the FIRST prompt after a quiet spell. One
//      fresh prompt is worth ~0.67/min at the default τ, but by the time it is labelled and polled
//      (flush ≈4 s + enrichment tick + poll) the engine reports 0.6 — and `0.6 > 0.6` is false, so
//      the tile stayed on 0 for exactly the event it is named after.
//   2. Deadbanding the way down to zero pinned the tile at 1 forever: `floor(value + 1.5)` is ≥ 1
//      for any value, and from 1 the gap to 0 is 1.0, which never exceeds CTA_FALL. A live that
//      went quiet showed "1 /min · จากคนดู" for hours while the modal one click away said
//      "ยังไม่มีคอมเมนต์ถามซื้อ" — a self-contradiction on the same card.
//
// Lives in lib/ (not in the component) for the reason healthFactorCopy.js documents: CI runs
// `node --test` over src/renderer/src/{lib,stores} and src/main/lib ONLY — a .jsx test is not a
// gate. The component owns just the previous-value ref; every decision is here, and tested.
//
// IDEMPOTENT BY CONSTRUCTION: after a step the result satisfies both guards, so calling it again
// with the same rate returns the same integer. That matters because the card re-renders on every
// comment/track update, far more often than the 1.5 s poll — without idempotency the tile would
// walk down faster on a busy live than on a quiet one, for no reason the host could see.

/** Fall reluctantly: aging alone must not repaint the tile until the gap is this wide. */
export const CTA_FALL = 1.5

const finite = (n) => typeof n === 'number' && Number.isFinite(n)

/**
 * The integer to render on the CTA tile.
 *
 * @param prev   the integer currently shown (null on first measurement / after unavailability)
 * @param value  `ctaPerMin` from the engine poll — a finite rate, or null/undefined when the signal
 *               is unavailable (LHM_INTENT off, poll silent, live not started)
 * @returns integer to show, or null when there is nothing to show (caller renders "—")
 *
 * A non-finite or negative `value` returns null rather than rendering: the real engine cannot emit
 * those, but a foreign listener squatting on :8765 can (TI-327), and "—" is the honest answer to
 * garbage. `prev` is likewise validated so a corrupted ref cannot pin the display.
 */
export function steppedCtaDisplay(prev, value) {
  if (!finite(value) || value < 0) return null
  if (value === 0) return 0
  const up = Math.round(value)
  if (!finite(prev)) return up
  if (up > prev) return up
  if (prev - value > CTA_FALL) return Math.max(0, Math.floor(value + CTA_FALL))
  return prev
}
