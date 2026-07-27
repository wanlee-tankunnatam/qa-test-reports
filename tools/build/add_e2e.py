#!/usr/bin/env python3
"""เพิ่ม epic "Full E2E Flow" (เคสวิ่งครบลูปตั้งแต่ต้นจนจบ) ลงในรายงาน

เคสถูกร้อยจาก "ขั้นที่ 1 → N" ที่แต่ละรายงานมีอยู่แล้ว — ไม่ได้แต่งพฤติกรรมใหม่
แต่ละขั้นอ้าง TC เดิมในไฟล์กำกับไว้ เพื่อให้ตามกลับไปดูเคสละเอียดได้

ใช้:  python3 tools/build/add_e2e.py [--check] [key...]
      --check = แสดงสิ่งที่จะเปลี่ยน ไม่เขียนไฟล์
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from e2e_cases import REPORTS          # noqa: E402  (ข้อมูลเคสอยู่ไฟล์ข้าง ๆ)

PRIO_CLS = {'P0': 'p0', 'P1': 'p1', 'P2': 'p2'}


# ── อ่านรูปแบบเฉพาะไฟล์ เพื่อให้แถวใหม่หน้าตาเหมือนแถวเดิมเป๊ะ ─────────────────
def file_style(src: str) -> dict:
    owner = re.search(r'(<span class="epic-owner-wrap">[\s\S]*?</select></span>)', src)
    jira_ph = re.search(r'class="jira-input"[^>]*placeholder="([^"]*)"', src)
    epics = [int(m) for m in re.findall(r'data-epic="(\d+)"', src)]
    feats = [int(m) for m in re.findall(r'data-feat="epic(\d+)"', src)]
    uids = [int(m) for m in re.findall(r'data-uid="tc-(\d+)"', src)]
    return {
        'owner': owner.group(1) if owner else '',
        'jira_ph': jira_ph.group(1) if jira_ph else 'วางลิงก์ Jira แล้ว Enter',
        'next_epic': max(epics + feats or [0]) + 1,
        'next_uid': max(uids) + 1,
        'has_jira': 'jira-sec' in src,
    }


# ── สร้าง HTML ของเคสหนึ่งเคส ────────────────────────────────────────────────
def case_html(c: dict, uid: int, epic_no: int, st: dict) -> str:
    u = f'tc-{uid}'
    pc = PRIO_CLS[c['prio']]

    steps, n = [], 1
    for head, items in c['phases']:
        lis = ''.join(f'<li>{s}</li>' for s in items)
        start = f' start="{n}"' if n > 1 else ''
        steps.append(f'    <div class="sec"><h4>Test Steps — {head}</h4><ol{start}>{lis}</ol></div>')
        n += len(items)

    pre = ''.join(f'<li>{p}</li>' for p in c['pre'])
    exp = ''.join(f'<li>{e}</li>' for e in c['expected'])
    opts = '\n'.join(
        f'      <span class="opt {k}" data-uid="{u}" data-st="{k}">{lbl}</span>'
        for k, lbl in (('pass', 'PASS'), ('fail', 'FAIL'), ('hold', 'HOLD'),
                       ('block', 'BLOCKED'), ('skip', 'SKIP')))
    jira_sec = (
        f'\n    <div class="sec jira-sec"><h4>🐞 Jira / Bug (ใส่ได้หลายลิงก์)</h4>\n'
        f'      <div class="jira-list" data-uid="{u}"></div>\n'
        f'      <div class="jira-add"><input type="text" class="jira-input" data-uid="{u}" '
        f'placeholder="{st["jira_ph"]}"><button class="btn jira-btn" data-uid="{u}">+ เพิ่มลิงก์</button></div>\n'
        f'    </div>') if st['has_jira'] else ''

    return f'''<tr class="trow" data-feat="epic{epic_no}" data-level="e2e" data-prio="{c['prio']}" onclick="tg(this)">
  <td><span class="tog">▸</span></td><td class="cid">{c['id']}</td>
  <td class="ctitle">{c['title']}</td>
  <td class="lvl"><span class="lv lvl-e2e">E2E</span></td>
  <td><span class="prio {pc}">{c['prio']}</span></td>
  <td class="status" data-uid="{u}"><span class="stb pending">รอเทส</span></td>
  <td class="jira-cell" data-uid="{u}"></td>
</tr>
<tr class="detail"><td colspan="7"><div class="card">
    <div class="h-title">{c['title']}</div>
    <div class="h-prio">Priority: <b>{c['prio']}</b> · E2E · {c['scope']}</div>
    <div class="sec"><h4>📄 อ้างอิงเอกสาร</h4><div class="hint" style="font-size:12px">{c['ref']}</div></div>
    <div class="sec"><h4>Precondition</h4><ul>{pre}</ul></div>
{chr(10).join(steps)}
    <div class="grid">
      <div class="sec"><h4>Expected Result</h4><ul>{exp}</ul></div>
      <div class="sec"><h4>Actual Result</h4><textarea class="actualbox" rows="4" placeholder="— บันทึกผลตอนทดสอบ —"></textarea></div>
    </div>
    <div class="sec"><h4>Status</h4><div class="statusrow">
{opts}
    </div></div>{jira_sec}
</div></td></tr>
'''


def block_html(spec: dict, st: dict) -> tuple:
    """คืน (html ของทั้ง epic, จำนวนเคส, uid ที่ใช้)"""
    e = st['next_epic']
    uid = st['next_uid']
    rows, used = [], []
    for c in spec['cases']:
        rows.append(case_html(c, uid, e, st))
        used.append(uid)
        uid += 1
    n = len(spec['cases'])
    head = (
        f'\n<!-- ═══════════════════════════════════════════════ Full E2E Flow ═══ -->\n'
        f'<tr class="epicrow" data-epic="{e}"><td colspan="7">{spec["epic_title"]} '
        f'<span class="rp">({n} เคส)</span></td></tr>\n'
        f'<tr class="featrow" data-featkey="{spec["feat_key"]}"><td colspan="7">📁 {spec["feat_key"]} — '
        f'{spec["feat_desc"]} <span class="rp"><span class="lv lvl-e2e">🔄 {n}</span></span> '
        f'{st["owner"]}</td></tr>\n\n')
    return head + '\n'.join(rows), n, used, e


# ── แก้ตัวเลข/ชิป ที่อยู่รอบ ๆ ให้สอดคล้อง ────────────────────────────────────
def retouch(src: str, spec: dict, n: int, epic_no: int) -> str:
    # 1) chip ตัวกรอง Epic — เติมอันใหม่ก่อนปุ่มล้างของแถว Epic
    # 1) chip ตัวกรอง — ต่อท้าย chip ของ feat ตัวสุดท้าย
    #    (บางไฟล์แยกเป็นหลายแถว เช่น MVP-1 / MVP-2 จึงเกาะ chip ไม่ใช่เกาะ label)
    chips = list(re.finditer(r'<button class="fchip" data-f="feat"[^>]*>[^<]*</button>', src))
    if not chips:
        raise SystemExit('  ✗ หา chip ตัวกรอง feat ไม่เจอ — โครง .filters ไม่ตรงที่คาด')
    at = chips[-1].end()
    src = (src[:at] + f'\n      <button class="fchip" data-f="feat" data-v="epic{epic_no}">'
           f'🔄 E2E ({n})</button>' + src[at:])

    # 2) pill จำนวนเคสรวม  "… = 219"  →  "… = 219 + E2E 4 = 223"
    def bump(m):
        total = int(m.group(2))
        return f'{m.group(1)}{total} + E2E {n} = {total + n}'
    src = re.sub(r'(<span class="pill">[^<]*?= )(\d+)(?=</span>)', bump, src, count=1)

    # 3) pill "UI only …"  →  บอกว่ามี E2E ด้วย
    src = re.sub(r'(<span class="pill">)(UI only)(</span>)', r'\g<1>UI + E2E\g<3>', src, count=1)
    src = re.sub(r'(<span class="pill">)(UI only · manual)(</span>)', r'\g<1>UI + E2E · manual\g<3>', src, count=1)

    # 4) footer "… · 219 TCs · …" — ยึด "จำนวนแถวจริง" ไม่ใช่บวกจากเลขเดิม
    #    (บางไฟล์เลขใน footer กับใน pill ไม่ตรงกันมาแต่เดิม)
    real = len(set(re.findall(r'<td class="status" data-uid="(tc-\d+)"', src)))
    src = re.sub(r'(<footer>[\s\S]*?)(\d+) TCs', lambda m: f'{m.group(1)}{real} TCs', src, count=1)
    return src


def apply(key: str, spec: dict, check: bool) -> str:
    path = ROOT / spec['path']
    src = path.read_text(encoding='utf-8')
    if spec['feat_key'] in src:
        return f'  {key:14} ⏭  มี epic E2E อยู่แล้ว ข้าม'

    st = file_style(src)
    html, n, uids, epic_no = block_html(spec, st)
    out = src.replace('</tbody>', html + '\n</tbody>', 1)
    if out == src:
        return f'  {key:14} ✗ หา </tbody> ไม่เจอ'
    out = retouch(out, spec, n, epic_no)

    if not check:
        path.write_text(out, encoding='utf-8')
    return (f'  {key:14} {"(ลองดู)" if check else "เขียนแล้ว"} '
            f'+{n} เคส · uid {uids[0]}–{uids[-1]} · epic{epic_no} · '
            f'{len(out) - len(src):+,} bytes')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('keys', nargs='*')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    keys = a.keys or list(REPORTS)
    for k in keys:
        if k not in REPORTS:
            print(f'  ✗ ไม่รู้จัก key: {k}')
            return 1
        print(apply(k, REPORTS[k], a.check))
    return 0


if __name__ == '__main__':

    sys.exit(main())
