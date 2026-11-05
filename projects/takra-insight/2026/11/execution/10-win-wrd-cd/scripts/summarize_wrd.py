"""Summarise a wrd-run.mjs results.json into the facts a report cell needs.

Keeps the reading honest by printing what was measured (probe status, banner, verdict, first-seen
labels) rather than a conclusion, so the cell text is written from evidence.

usage: python -I -X utf8 summarize_wrd.py <out-dir>
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

d = sys.argv[1]
res = json.load(open(os.path.join(d, "results.json"), encoding="utf-8"))

print(f"platform          : {res.get('platform')}")
print(f"flv               : {os.path.basename(res.get('flv', ''))}  ({res.get('totalS')} s)")
print(f"started at        : {res.get('startedAt')}")
print(f"finished at       : {res.get('finishedAt')}")
print(f"telegram tap      : {res.get('tap')}")
print(f"audio consent     : {res.get('audioConsentText')}")
if res.get("_error"):
    print(f"ERROR             : {res['_error']}")

sweep = res.get("probeSweep") or []
if sweep:
    print("\nprobe sweep before any press:")
    for p in sweep:
        print(f"   @{p.get('handle'):24} status={p.get('status')}  {p.get('title', '')}")

print(f"\nattempts: {len(res.get('attempts') or [])}")
for a in res.get("attempts") or []:
    pb = a.get("probeBeforePress") or {}
    print(f"   {a.get('kind')}")
    print(f"      cta offered        : {a.get('ctaOffered')}")
    print(f"      probe before press : status={pb.get('status')} at {pb.get('at')}")
    print(f"      pressed at         : {a.get('pressedAt')}")
    print(f"      refusal banner     : {a.get('refusalBannerShown')}")
    print(f"      started            : {a.get('started')}")
    print(f"      VERDICT            : {a.get('verdict')}")
    if a.get("fail"):
        print(f"      fail               : {a['fail']}")

live = res.get("live")
print(f"\nrecorded live     : {live}")

fs = res.get("firstSeen") or {}
if fs:
    print("\nrisk labels first seen on the live page:")
    for k, v in fs.items():
        print(f"   {k:34} +{v.get('atS')}s   ({v.get('at')})")
else:
    print("\nrisk labels first seen on the live page: NONE")

if res.get("transcriptLabels") is not None:
    print(f"\ntranscript labels : {res.get('transcriptLabels')}")
    print(f"transcript reasons: {res.get('transcriptReasons')}")
tips = res.get("titleTooltips") or []
if tips:
    print(f"tooltips captured : {len(tips)}")
    for t in tips[:10]:
        print(f"   [{t.get('text')}] -> {t.get('title')}")

tg = res.get("telegramCalls") or []
print(f"\ntelegram calls    : {len(tg)}")
for c in tg:
    body = (c.get("body") or "")[:400]
    print(f"   {c.get('method')} http={c.get('status')}  {body}")

print(f"\nstream pulls      : {len(res.get('streams') or [])}")
for s in res.get("streams") or []:
    print(f"   {s.get('connectedAt')}  {s.get('url')}")
