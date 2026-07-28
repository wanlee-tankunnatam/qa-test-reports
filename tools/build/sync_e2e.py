#!/usr/bin/env python3
"""Sync เนื้อหาเคส Full E2E Flow จาก e2e_cases.py ลงรายงานที่มี epic นี้อยู่แล้ว

ต่างจาก add_e2e.py ตรงที่ตัวนั้น "เพิ่ม" epic ให้รายงานที่ยังไม่มี (เจอแล้วข้าม)
ตัวนี้ "แทนที่" เนื้อหาเคสเดิมตาม TC id — โดย
  · คง data-uid (tc-NNNN) เดิมของแต่ละเคสไว้ → ผลทดสอบใน store-data ไม่หลุด
  · คงหมายเลข epic (data-feat) เดิมไว้ → ตัวกรอง/ตัวนับรอบ ๆ ไม่ต้องแก้
  · แตะเฉพาะบล็อก trow+detail ของเคส E2E — ส่วนอื่นของไฟล์ไม่ขยับ

ใช้:  python3 tools/build/sync_e2e.py [--check] [key...]
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from add_e2e import case_html, file_style   # noqa: E402
from e2e_cases import REPORTS               # noqa: E402


def sync(key: str, spec: dict, check: bool) -> str:
    # รายงานหนึ่ง key อาจมีหลายไฟล์ (เช่น แยกรุ่น mac/windows) — ใช้ 'paths' ถ้ามี
    lines = []
    for p in spec.get('paths', [spec['path']]):
        lines.append(sync_file(key, spec, p, check))
    return '\n'.join(lines)


def sync_file(key: str, spec: dict, relpath: str, check: bool) -> str:
    path = ROOT / relpath
    name = pathlib.Path(relpath).name
    if not path.exists():
        return f'  {key:14} ✗ ไม่พบไฟล์ {relpath}'
    src = path.read_text(encoding='utf-8')
    if spec['feat_key'] not in src:
        return f'  {key:14} {name}: ⏭  ยังไม่มี epic E2E (ใช้ add_e2e.py ก่อน)'

    st = file_style(src)
    done, missing = [], []
    for c in spec['cases']:
        cid = re.escape(c['id'])
        # บล็อกเดิม: trow ของเคสนี้ + detail จนถึงท้ายการ์ด (</div></td></tr> ตัวแรกหลัง detail)
        # class อาจเป็น "trow hide" ได้ ถ้าไฟล์ถูกเซฟตอนตัวกรองเปิดอยู่
        pat = re.compile(
            r'<tr class="trow[^"]*"[^>]*>\s*<td><span class="tog">▸</span></td>\s*'
            r'<td class="cid">' + cid + r'</td>.*?</div></td></tr>\n?',
            re.S)
        m = pat.search(src)
        if not m:
            missing.append(c['id'])
            continue
        old = m.group(0)
        uid = int(re.search(r'data-uid="tc-(\d+)"', old).group(1))
        epic_no = int(re.search(r'data-feat="epic(\d+)"', old).group(1))
        src = src[:m.start()] + case_html(c, uid, epic_no, st) + src[m.end():]
        done.append(f'{c["id"]}→tc-{uid}')

    if missing:
        return f'  {key:14} {name}: ✗ หาเคสไม่เจอ: {missing}'
    if not check:
        path.write_text(src, encoding='utf-8')
    return (f'  {key:14} {name}: {"(ลองดู)" if check else "เขียนแล้ว"} '
            f'{len(done)} เคส: {" · ".join(done)}')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('keys', nargs='*', default=[])
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    keys = args.keys or list(REPORTS)
    for k in keys:
        if k not in REPORTS:
            print(f'  {k:14} ✗ ไม่รู้จัก (มี: {", ".join(REPORTS)})')
            return 1
        print(sync(k, REPORTS[k], args.check))
    return 0


if __name__ == '__main__':
    sys.exit(main())
