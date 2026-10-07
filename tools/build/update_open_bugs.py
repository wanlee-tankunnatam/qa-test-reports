#!/usr/bin/env python3
"""อัปเดตหน้า timeline/open-bugs.html จาก Jira อัตโนมัติ (launchd 09:00 / 13:00 ทุกวัน)

กติกา:
- ดึงบั๊กที่ยังไม่ปิด (issuetype = Bug, statusCategory != Done) ของทุกโปรเจกต์ในหน้า
- แถวเดิม: คง "รอบ" + "Dev" ที่จัดมือไว้ อัปเดตเฉพาะ ระดับ/ชื่อ/สถานะ จาก Jira
- ใบที่ปิดแล้ว/หายจาก Jira → เอาออก
- ใบใหม่/ใบที่ยังไม่มีรอบ → ใส่รอบส่งถัดไปที่ใกล้ที่สุด (รอบที่มีอยู่แล้วในหน้า ที่วันยังไม่ถึง) ให้อัตโนมัติ
  · Dev = ชื่อเล่นในวงเล็บของ assignee (ไม่มีคนรับถ้าว่าง) · ถ้าไม่มีรอบอนาคตเหลือ → "ยังไม่มีรอบ"
- TAKRA: รอบ = ป้ายวันที่ในตั๋ว Jira เสมอ (ป้ายล่าสุดถ้ามีหลายอัน) · ไม่มีป้าย → "ยังไม่มีรอบ" ไม่ดึงเข้ารอบเอง
- แก้เฉพาะ ROWS + บรรทัด "ข้อมูล ณ" แล้ว commit+push ถ้ามีการเปลี่ยน
auth: ~/.config/jira-auth ผ่าน ~/.claude/scripts/jira.py (ห้าม print token)
"""
import json, pathlib, re, subprocess, sys, datetime, importlib.util

REPO = pathlib.Path(__file__).resolve().parents[2]
PAGE = REPO / 'timeline' / 'open-bugs.html'
KEYS = ['TAKRA', 'TI', 'TAK', 'TKRD', 'TF', 'TKH']
LABEL_ROUND_KEYS = {'TAKRA'}  # โปรเจกต์ที่รอบในหน้า = ป้ายวันที่ใน Jira
MON = dict(JAN=1, FEB=2, MAR=3, APR=4, MAY=5, JUN=6, JUL=7, AUG=8, SEP=9, OCT=10, NOV=11, DEC=12)
ROUND_LABEL = re.compile(r'^(\d{1,2})-([A-Z]{3})$')
NO_ROUND = 'ยังไม่มีรอบ'
TH_MON = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.']

spec = importlib.util.spec_from_file_location('j', pathlib.Path.home() / '.claude/scripts/jira.py')
j = importlib.util.module_from_spec(spec); spec.loader.exec_module(j)


def fetch_open_bugs(key):
    issues, token = {}, None
    while True:
        # ห้ามกรองด้วย statusCategory — TF ตั้งหมวดกลับด้าน ("Done" อยู่หมวด In Progress,
        # "Ready to Test" อยู่หมวด Done) → ดึงทั้งหมดแล้วกรองด้วยชื่อสถานะเอง
        body = {'jql': f'project = {key} AND issuetype = Bug ORDER BY key ASC',
                'maxResults': 100, 'fields': ['summary', 'status', 'priority', 'assignee', 'labels']}
        if token:
            body['nextPageToken'] = token
        s, r = j.call('POST', '/rest/api/3/search/jql', body)
        if s != 200:
            raise RuntimeError(f'{key}: Jira HTTP {s} {str(r)[:200]}')
        for i in r.get('issues', []):
            f = i['fields']
            # ปิดจริง = ชื่อสถานะเหล่านี้ (สำรวจครบทุกโปรเจกต์ 30 ก.ย.)
            if f['status']['name'].upper() in ('DONE', 'CLOSED', 'CANCEL', 'CANCELLED'):
                continue
            name = (f.get('assignee') or {}).get('displayName') or ''
            m = re.search(r'\(([^)]+)\)\s*$', name)
            # แต่ละโปรเจกต์สะกดสถานะไม่เหมือนกัน — รวมให้เป็นชิปเดียวในหน้า
            canon = {'IN REVIEW': 'IN REVIEW', 'READY TO TEST': 'READY TO TEST',
                     'TO DO': 'To Do', 'IN PROGRESS': 'In Progress', 'TESTING': 'TESTING',
                     'NEED ADVISE': 'Need Advise'}
            status = canon.get(f['status']['name'].upper(), f['status']['name'])
            rounds = sorted((x for x in f.get('labels') or []
                             if (lm := ROUND_LABEL.match(x)) and lm.group(2) in MON),
                            key=lambda x: (MON[ROUND_LABEL.match(x).group(2)], int(ROUND_LABEL.match(x).group(1))))
            issues[i['key']] = dict(
                round=rounds[-1] if rounds else NO_ROUND,
                prio=(f.get('priority') or {}).get('name') or 'Medium',
                title=f.get('summary') or '',
                status=status,
                dev=(m.group(1) if m else name).strip() or 'ไม่มีคนรับ')
        token = r.get('nextPageToken')
        if not token:
            return issues


def main():
    html = PAGE.read_text(encoding='utf-8')
    m = re.search(r'const ROWS = \[\n(.*?)\n\];', html, re.S)
    assert m, 'ไม่พบ const ROWS ใน open-bugs.html'
    rows = [json.loads(line.rstrip(',')) for line in m.group(1).splitlines() if line.strip()]

    jira = {}
    for key in KEYS:
        jira.update(fetch_open_bugs(key))
    if not jira:
        raise RuntimeError('Jira คืนบั๊กเปิด 0 ใบทุกโปรเจกต์ — ผิดปกติ ไม่เขียนทับ')

    known = {r[2] for r in rows}
    out, changed, removed = [], [], []
    for r in rows:
        info = jira.get(r[2])
        if not info:
            removed.append(r[2]); continue
        rnd = info['round'] if r[2].split('-')[0] in LABEL_ROUND_KEYS else r[0]
        new = [rnd, r[1], r[2], info['prio'], info['title'], info['status']]
        if new != r[:6]:
            changed.append(r[2])
        out.append(new)
    added = [k for k in sorted(jira, key=lambda k: (k.split('-')[0], int(k.split('-')[1]))) if k not in known]
    for k in added:
        info = jira[k]
        out.append([info['round'] if k.split('-')[0] in LABEL_ROUND_KEYS else NO_ROUND, info['dev'], k, info['prio'], info['title'], info['status']])

    # ใบที่ไม่มีรอบกำกับ → ดึงเข้ารอบส่งถัดไปที่ใกล้ที่สุด (จากรอบที่มีอยู่แล้วในหน้า)
    today = datetime.date.today()

    def round_date(r):
        m2 = re.match(r'^(\d{1,2})-([A-Z]{3})$', r)
        return datetime.date(today.year, MON[m2.group(2)], int(m2.group(1))) if m2 and m2.group(2) in MON else None

    future = sorted((d, r) for r in {r[0] for r in out} if (d := round_date(r)) and d > today)
    next_round = future[0][1] if future else None
    pulled = []
    if next_round:
        for r in out:
            if r[0] == NO_ROUND and r[2].split('-')[0] not in LABEL_ROUND_KEYS:
                r[0] = next_round; pulled.append(r[2])

    if not (changed or added or removed or pulled):
        print(f'{datetime.datetime.now():%F %H:%M} ไม่มีอะไรเปลี่ยน (ข้าม ไม่ commit)'); return

    lines = [json.dumps(r, ensure_ascii=False).replace('</', '<\\/') + ',' for r in out]
    html = html[:m.start()] + 'const ROWS = [\n' + '\n'.join(lines) + '\n];' + html[m.end():]

    now = datetime.datetime.now()
    stamp = f'ข้อมูล ณ {now.day} {TH_MON[now.month - 1]} {now.year} {now:%H:%M} น. (อัปเดตอัตโนมัติ 09:00 / 13:00)'
    html = re.sub(r'ข้อมูล ณ [^<]*', stamp, html, count=1)
    PAGE.write_text(html, encoding='utf-8')

    def git(*args, ok=True):
        p = subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True)
        if ok and p.returncode != 0:
            raise RuntimeError(f'git {" ".join(args)}: {p.stderr.strip()[:300]}')
        return p

    if not git('diff', '--quiet', '--', 'timeline/open-bugs.html', ok=False).returncode:
        print(f'{now:%F %H:%M} ไม่มีอะไรเปลี่ยน'); return
    summary = ' · '.join(x for x in [
        f'อัปเดต {len(changed)}' if changed else '',
        f'เพิ่ม {len(added)} ({", ".join(added[:6])}{"…" if len(added) > 6 else ""})' if added else '',
        f'ดึงเข้ารอบ {next_round} {len(pulled)} ใบ ({", ".join(pulled[:6])}{"…" if len(pulled) > 6 else ""})' if pulled else '',
        f'ปิดแล้วเอาออก {len(removed)} ({", ".join(removed[:6])}{"…" if len(removed) > 6 else ""})' if removed else ''] if x) or 'refresh เวลา'
    git('add', 'timeline/open-bugs.html')
    git('commit', '-m', f'chore(open-bugs): อัปเดตจาก Jira {now:%d/%m %H:%M} — {summary}')
    git('pull', '--rebase', '--autostash')
    git('push')
    print(f'{now:%F %H:%M} push แล้ว — {summary}')


if __name__ == '__main__':
    main()
