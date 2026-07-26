#!/usr/bin/env python3
"""สร้างไฟล์ redirect ให้ URL เก่าทุกอันชี้มาที่ตำแหน่งใหม่

ลิงก์ที่เคยแชร์ใน Jira/แชตต้องใช้ได้ต่อ ตัว redirect ต้องวางไว้ที่ path เดิมเป๊ะ ๆ
(GitHub Pages ไม่มี server-side redirect) จึงใช้ meta refresh + canonical

ใช้:  python3 tools/make-redirects.py [--check]
      --check = ตรวจอย่างเดียว ไม่เขียนไฟล์

เวลาย้าย/เปลี่ยนชื่อไฟล์รอบใหม่: เติม path เก่า→ใหม่ใน MOVES แล้วรันซ้ำ
"""
import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://wanlee-tankunnatam.github.io/qa-test-reports/'

# ชื่อไฟล์เดิม → ตำแหน่งใหม่ (ชื่อไฟล์เดิมไม่ซ้ำกัน ใช้เป็นคีย์ได้)
MOVES = {
    # ── takra-ai ────────────────────────────────────────────────────────────
    'takra-ai-mvp1-test-cases-table.html':
        'projects/takra-ai/2026/06/reports/takra-ai-mvp1-full-test-cases-table.html',
    'takra-ai-mvp1-ui-test-cases-table.html':
        'projects/takra-ai/2026/07/reports/takra-ai-mvp1-ui-test-cases-table.html',
    'takra-ai-mvp2-ui-test-cases-table.html':
        'projects/takra-ai/2026/07/reports/takra-ai-mvp2-ui-test-cases-table.html',
    'live-mvp-1-qa-closeout-full.html':
        'projects/takra-ai/2026/07/summary/takra-ai-mvp1-qa-summary.html',
    'live-mvp-2-qa-closeout-full.html':
        'projects/takra-ai/2026/07/summary/takra-ai-mvp2-qa-summary.html',
    'live-mvp-1-qa-dod-checklist.html':
        'projects/takra-ai/dod/mvp1/takra-ai-mvp1-qa-dod-checklist.html',
    'live-mvp-2-qa-dod-checklist.html':
        'projects/takra-ai/dod/mvp2/takra-ai-mvp2-qa-dod-checklist.html',

    # ── takra-insight ───────────────────────────────────────────────────────
    'takra-inside-mvp-0.5-ui-test-cases-table.html':       # ชื่อเดิมสะกดผิด
        'projects/takra-insight/2026/06/reports/takra-insight-mvp0.5-ui-test-cases-table.html',
    'takra-insight-mvp0.5-1-ui-test-cases-table-mac.html':
        'projects/takra-insight/2026/07/reports/takra-insight-mvp0.5-1-ui-test-cases-table-mac.html',
    'takra-insight-mvp0.5-1-ui-test-cases-table-windows.html':
        'projects/takra-insight/2026/07/reports/takra-insight-mvp0.5-1-ui-test-cases-table-windows.html',
    'takra-insight-mvp0.5-1-ui-test-cases-table-mac_old.html':
        'projects/takra-insight/archive/takra-insight-mvp0.5-1-ui-test-cases-table-mac-old.html',
    'takra-insight-mvp0.5-1-ui-test-cases-table-windows_old.html':
        'projects/takra-insight/archive/takra-insight-mvp0.5-1-ui-test-cases-table-windows-old.html',
    'takra-insight-mvp1-ui-test-cases-table.html':
        'projects/takra-insight/2026/07/reports/takra-insight-mvp1-ui-test-cases-table.html',
    'takra-insight-mvp2-ui-test-cases-table.html':
        'projects/takra-insight/2026/07/reports/takra-insight-mvp2-ui-test-cases-table.html',
    'insight-mvp-0.5-qa-closeout-full.html':
        'projects/takra-insight/2026/07/summary/takra-insight-mvp0.5-qa-summary.html',
    'insight-mvp-1-qa-summary.html':
        'projects/takra-insight/2026/07/summary/takra-insight-mvp1-qa-summary.html',
    'insight-mvp-1-qa-dod-checklist.html':
        'projects/takra-insight/dod/mvp1/takra-insight-mvp1-qa-dod-checklist.html',

    # ── takra-rerun ─────────────────────────────────────────────────────────
    'takra-rerun-mvp1-2-ui-test-cases-table.html':
        'projects/takra-rerun/2026/07/reports/takra-rerun-mvp1-2-ui-test-cases-table.html',
    'takra-rerun-mvp1-test-cases-table.html':
        'projects/takra-rerun/2026/07/reports/takra-rerun-mvp1-e2e-test-cases-table.html',
    'takra-rerun-mvp2-test-cases-table.html':
        'projects/takra-rerun/2026/07/reports/takra-rerun-mvp2-ui-test-cases-table.html',
    'rerun-mvp-1-qa-closeout-full.html':
        'projects/takra-rerun/2026/07/summary/takra-rerun-mvp1-qa-summary.html',
    'rerun-mvp-2-qa-closeout-full.html':
        'projects/takra-rerun/2026/07/summary/takra-rerun-mvp2-qa-summary.html',
}

# commit ที่เก็บโครงสร้างเก่าไว้ — ใช้ดึงรายชื่อ path เดิมทั้งหมด จะได้ไม่ตกหล่น
OLD_REF = 'eca44fe'


def old_paths() -> list:
    out = subprocess.run(['git', 'ls-tree', '-r', '--name-only', OLD_REF],
                         cwd=ROOT, capture_output=True, text=True, check=True)
    keep = []
    for p in out.stdout.splitlines():
        parts = p.split('/')
        if not p.endswith('.html'):
            continue
        if parts[0] in ('reports', 'summary', 'dod') and len(parts) == 2:
            keep.append(p)                                  # ราก (ก่อน reorg รอบแรก)
        elif len(parts) == 4 and parts[0] == 'projects' and parts[2] in ('reports', 'summary', 'dod'):
            keep.append(p)                                  # projects/<proj>/<type>/ (รอบที่ live อยู่)
    return sorted(keep)


def stub(target: str) -> str:
    url = BASE + target
    return (
        '<!doctype html><meta charset="utf-8"><title>ย้ายแล้ว — QA Report</title>\n'
        f'<link rel="canonical" href="{url}">\n'
        f'<meta http-equiv="refresh" content="0; url={url}">\n'
        '<p style="font-family:sans-serif">รายงานนี้ย้ายไป '
        f'<a href="{url}">ตำแหน่งใหม่</a> · กำลังพาไป…</p>\n'
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    paths, missing_map, missing_target, wrote = old_paths(), [], [], 0
    for old in paths:
        name = old.rsplit('/', 1)[-1]
        target = MOVES.get(name)
        if not target:
            missing_map.append(old)
            continue
        if not (ROOT / target).is_file():
            missing_target.append(f'{old} -> {target}')
            continue
        if (ROOT / old).is_file() and 'refresh' not in (ROOT / old).read_text(encoding='utf-8')[:400]:
            print(f"  ✗ ข้าม {old} — มีไฟล์จริงอยู่ ไม่ใช่ redirect")
            continue
        if args.check:
            continue
        dst = ROOT / old
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(stub(target), encoding='utf-8')
        wrote += 1

    print(f"  path เก่าทั้งหมด {len(paths)}  ·  เขียน redirect {wrote}")
    for label, items in (('ไม่มีใน MOVES', missing_map), ('ปลายทางไม่มีจริง', missing_target)):
        if items:
            print(f"  ✗ {label} {len(items)} รายการ:")
            for i in items:
                print(f"      {i}")
    return 1 if (missing_map or missing_target) else 0


if __name__ == '__main__':
    sys.exit(main())
