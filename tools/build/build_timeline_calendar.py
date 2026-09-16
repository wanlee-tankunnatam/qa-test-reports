#!/usr/bin/env python3
"""ปฏิทินทดสอบ (แบบชีต) ของทุกโปรเจกต์ → timeline/index.html (ระหว่าง <!-- CAL:START --> … <!-- CAL:END -->)
แหล่งข้อมูล = หัวข้องานที่ BA/dev กำหนด (ไม่ใช่ test case):
  - Epic/Story          ← epics*.md (BMad) · docs/epic/ep-*.md (clip) · prd.md (farm)
  - สถานะ DEV ราย story ← sprint-status.yaml ของ dev (ถ้ามี) · ตารางสถานะในเอกสาร (clip) · ไม่มี = "ไม่ระบุ"
QA กำหนด "กำหนด QA" เอง: takra-ai วางมือ (SCHEDULE_AI) · โปรเจกต์อื่นวางอัตโนมัติ ~1 epic/วันทำงาน เริ่ม AUTO_START (แก้ในหน้าได้ บันทึกขึ้น GitHub)
รัน: python3 tools/build/build_timeline_calendar.py
"""
import re, html, pathlib, collections, subprocess, datetime

OUT = pathlib.Path(__file__).resolve().parents[2] / 'timeline' / 'index.html'
PAGES = 'https://wanlee-tankunnatam.github.io/qa-test-reports/'
JIRA = 'https://kitdi.atlassian.net/browse/'
AUTO_START = '2026-09-21'
TH_MON = ['ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.','ต.ค.','พ.ย.','ธ.ค.']
def thd(d): return str(int(d[8:10])) + ' ' + TH_MON[int(d[5:7]) - 1]

# ---------- takra-ai: วางมือ (คงของเดิม) ----------
AI_EPIC_NAME = {
  1: 'เข้าระบบ & รากฐาน Workspace', 2: 'คลังของ Workspace — Avatar/Voice · สินค้า · คำเสี่ยง · สคริปต์', 3: 'Live Studio — สร้างไลฟ์',
  4: 'ออกอากาศ Avatar Live (Phone-as-Camera)', 5: 'คอมเมนต์ · ตอบอัตโนมัติ · Risk Filter · Live Console · Recap', 6: 'AI ช่วยเขียน Script',
  7: 'Production Readiness & Pilot (Infra — ไม่มี UI)', 8: 'AIEventLog — audit trail ของ AI', 9: 'Live Monitoring & Post-Live Recap',
  10: 'คลัง Avatar & Voice self-service', 11: 'Internal Ops & Support — ⛔ ย้ายไป TAKRA Hub (2026-08-10)', 12: 'Billing — มิเตอร์ · แจ้งเตือน · cap',
  13: 'Tool-Calling Auto-Reply (Engine align)', 15: 'Studio & Live-Creation riders', 16: 'Settings & Account IA + Usage unify',
  19: 'Multi-Platform RTMP core (แยกจาก Epic 14 · 2026-08-24)',
}
SCHEDULE_AI = {
  1: ['2026-09-16'], 2: ['2026-09-16'], 3: ['2026-09-17'], 4: ['2026-09-18'], 5: ['2026-09-18'], 6: ['2026-09-18'],
  8: ['2026-09-21'], 9: ['2026-09-22', '2026-09-23'], 10: ['2026-09-24', '2026-09-25'],
  12: ['2026-09-28'], 15: ['2026-09-29'], 16: ['2026-09-30'], 13: ['2026-10-01'], 19: ['2026-10-05', '2026-10-06'],
}
WEEKS_AI = [
  ('สัปดาห์ที่ 1 · 14–18 ก.ย.', 'MVP-1 regression ทั้ง 6 epic (14–15 ก.ย. ไปทำ Trendora)', '2026-09-14', '2026-09-18'),
  ('สัปดาห์ที่ 2 · 21–25 ก.ย.', 'MVP-2 backbone — AIEventLog · Live Console/Recap · Avatar/Voice', '2026-09-21', '2026-09-25'),
  ('สัปดาห์ที่ 3 · 28 ก.ย.–2 ต.ค.', 'MVP-2 — Billing · Studio riders · Settings · Tool-calling (2 ต.ค. กันไว้ retest)', '2026-09-28', '2026-10-02'),
  ('สัปดาห์ที่ 4 · 5–9 ต.ค.', 'MVP-2 — RTMP · Full E2E (7 ต.ค.) · retest รวบยอด (8 ต.ค.) · สรุป + DoD (9 ต.ค.)', '2026-10-05', '2026-10-09'),
]
EXTRA_AI = [
  ('2026-10-02', 'Retest บั๊ก MVP-2 ที่ dev ปิดในสัปดาห์', 'ทุก story ที่สถานะ QA = ไม่ผ่าน แล้ว dev แจ้งปิด', 'อัปเดต Jira ให้ตรง'),
  ('2026-10-07', 'Full E2E MVP-2', 'วิ่งครบลูปข้าม Epic 8–16 · Studio → ไลฟ์ → Console → Recap → แจ้งเตือน', 'ห้ามสลับบัญชีกลางทาง'),
  ('2026-10-08', 'Retest รวบยอด', 'ทุกเคส ไม่ผ่าน / บล็อก / พัก ที่ dev ปิดแล้ว', ''),
  ('2026-10-09', 'สรุปผล + DoD MVP-2', 'อัปเดต QA Summary · เช็ค DoD MVP-2 · รายงานหัวหน้า', ''),
]

# ---------- ทะเบียนโปรเจกต์ ----------
P = 'projects/'
PROJECTS = [
  dict(id='ai', name='TAKRA AI · Live (ตะกร้าไลฟ์)', emoji='🤖', jira='TAKRA', board='https://kitdi.atlassian.net/jira/software/projects/TAKRA/boards/1593/timeline',
       repo='/Users/ice/Documents/rf/takra-ai', ref=None, kind='bmad', unique_epics=True,
       sources=[('_bmad-output/planning-artifacts/epics.md', 'MVP-1', ''), ('_bmad-output/planning-artifacts/epics-mvp2.md', 'MVP-2', '')],
       sprint='_bmad-output/implementation-artifacts/sprint-status.yaml',
       report=PAGES + P + 'takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html',
       schedule=SCHEDULE_AI, weeks=WEEKS_AI, extra=EXTRA_AI, epic_name=AI_EPIC_NAME),
  dict(id='rerun', name='TAKRA Rerun', emoji='🎬', jira='TAK', board='https://kitdi.atlassian.net/jira/software/projects/TAK/boards/1661/timeline',
       repo='/Users/ice/Documents/rf/takra-rerun', ref='origin/develop', kind='bmad', unique_epics=True,
       sources=[('_bmad-output/planning-artifacts/epics.md', 'MVP-1', ''), ('_bmad-output/planning-artifacts/epics-mvp2.md', 'MVP-2', ''), ('_bmad-output/planning-artifacts/epics-mvp3.md', 'MVP-3', '')],
       sprint='_bmad-output/implementation-artifacts/sprint-status.yaml',
       report=PAGES + '?project=rerun'),
  dict(id='insight', name='TAKRA Insight', emoji='🐘', jira='TI', board='https://kitdi.atlassian.net/jira/software/projects/TI/boards/1660/timeline',
       repo='/Users/ice/Documents/rf/takra-insight', ref='origin/develop', kind='bmad', unique_epics=False,
       sources=[('_bmad-output/planning-artifacts/epics.md', 'MVP-1', ''), ('_bmad-output/planning-artifacts/epics-mvp2.md', 'MVP-2', 'm2')],
       sprint='_bmad-output/implementation-artifacts/sprint-status.yaml',
       report=PAGES + '?project=insight'),
  dict(id='hub', name='TAKRA Hub', emoji='🏢', jira='TKH', board='https://kitdi.atlassian.net/jira/software/projects/TKH/boards/1733/timeline',
       repo='/Users/ice/Documents/rf/takra-hub', ref='origin/develop', kind='bmad', unique_epics=False,
       sources=[('docs/epics.md', 'MVP-1', ''), ('docs/epics-mvp2.md', 'MVP-2', 'm2'), ('docs/epics-mvp3.md', 'MVP-3', 'm3')],
       sprint='_bmad-output/implementation-artifacts/sprint-status.yaml',
       report=PAGES + '?project=hub'),
  dict(id='clip', name='TAKRA Clip', emoji='✂️', jira='ACL', board='https://kitdi.atlassian.net/jira/software/projects/ACL/list',
       repo='/Users/ice/Documents/rf/takra-clip-main', ref=None, kind='clip',
       sources=[('docs/epic/ep-01-service.md', 'EP', ''), ('docs/epic/ep-02-bo.md', 'EP', ''), ('docs/epic/ep-03-front-end-web-app.md', 'EP', ''), ('docs/epic/ep-04-front-end-desktop-app.md', 'EP', ''), ('docs/epic/ep-05-extension.md', 'EP', '')],
       sprint=None, report=PAGES + '?project=clip'),
  dict(id='farm', name='TAKRA Post (takra-farm)', emoji='📱', jira=None, board=None,
       repo='/Users/ice/Documents/rf/takra-farm', ref=None, kind='farm',
       sources=[('docs/prd.md', 'v1', '')], sprint=None, report=PAGES + '?project=farm'),
  dict(id='lipsync', name='TAKRA Lib-Sync', emoji='🎙️', jira='TLS', board=None,
       repo='/Users/ice/Documents/other/takra-lib-sync', ref='origin/uat', kind='bmad', unique_epics=True,
       sources=[('_bmad-output/planning-artifacts/epics.md', 'M1', ''),
                ('_bmad-output/planning-artifacts/backlog/epic-1-foundation.md', 'Backlog', ''), ('_bmad-output/planning-artifacts/backlog/epic-2-cicd.md', 'Backlog', ''),
                ('_bmad-output/planning-artifacts/backlog/epic-3-backend.md', 'Backlog', ''), ('_bmad-output/planning-artifacts/backlog/epic-4-desktop.md', 'Backlog', ''),
                ('_bmad-output/planning-artifacts/backlog/epic-5-customer-ops.md', 'Backlog', ''), ('_bmad-output/planning-artifacts/backlog/epic-6-pilot.md', 'Backlog', '')],
       sprint=None, report=PAGES + '?project=lipsync'),
  dict(id='radar', name='Trendora (takra-radar)', emoji='📡', jira='TKRD', board='https://kitdi.atlassian.net/jira/software/projects/TKRD/',
       repo='/Users/ice/Documents/rf/takra-radar', ref='ac885d7', kind='bmad', unique_epics=True,
       sources=[('_bmad-output/planning-artifacts/epics.md', 'MVP-1', '')],
       sprint='_bmad-output/implementation-artifacts/sprint-status.yaml',
       report=PAGES + P + 'takra-radar/2026/09/reports/takra-radar-mvp1-ui-test-cases-table.html'),
]

def read(pj, path):
    if pj['ref']:
        r = subprocess.run(['git', '-C', pj['repo'], 'show', pj['ref'] + ':' + path], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ''
    p = pathlib.Path(pj['repo']) / path
    return p.read_text(encoding='utf-8') if p.exists() else ''

def clean_title(t):
    t = re.sub(r'\s*\*\(.*?\)\*\s*', ' ', t); t = re.sub(r'\s*🆕.*$', '', t)
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t); t = re.sub(r'~~(.*?)~~', r'\1', t); t = t.replace('`', '')
    return re.sub(r'\s+', ' ', t).strip()

# ---------- parsers → list of epics: dict(key, mvp, num, name, stories=[dict(no, title, typ, jira, slug_hint)]) ----------
def parse_bmad(pj):
    epics, order = {}, []
    for path, mvp, prefix in pj['sources']:
        txt = read(pj, path)
        cur = None
        for line in txt.splitlines():
            m = re.match(r'^#{1,3} Epic ([\w\-]+)[:：—\-]\s*(.*)$', line)
            if m:
                num, name = m.group(1), clean_title(m.group(2))
                key = (mvp, num)
                if key not in epics:
                    epics[key] = dict(key=key, mvp=mvp, num=num, name=name, stories=[], prefix=prefix, order=[]); order.append(key)
                cur = epics[key]; continue
            m = re.match(r'^#{2,3} Story ([\w\-]+)\.(\d+[a-z]?(?:-\d)?)[:：]\s*(.*)$', line)
            if m and cur is not None:
                raw = m.group(3); typ = (re.match(r'\[([^\]]+)\]', raw) or [None, ''])[1]
                title = clean_title(re.sub(r'^\[[^\]]+\]\s*', '', raw))
                jira = re.findall(r'\b(?:%s)-\d+' % (pj['jira'] or 'XXX'), raw)
                sno = m.group(2)
                if any(s['no'] == sno for s in cur['stories']): continue
                cur['stories'].append(dict(no=sno, title=title, typ=typ, jira=jira, dev='unk', ents=[]))
    return [epics[k] for k in order]

def parse_clip(pj):
    out = []
    for path, mvp, _ in pj['sources']:
        txt = read(pj, path)
        m = re.match(r'^# (EP-\d+) · (.*)$', txt.split('\n', 1)[0].strip())
        num, name = (m.group(1), clean_title(m.group(2))) if m else (path, path)
        ep = dict(key=(mvp, num), mvp=mvp, num=num, name=name, stories=[], prefix='', order=[])
        for line in txt.splitlines():
            r = re.match(r'^\|\s*\[?((?:SVC|BO|EXT)-\d+)\]?[^|]*\|\s*(.*?)\s*\|(.*)$', line)
            if not r: continue
            sid, title, rest = r.group(1), clean_title(re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', r.group(2))), r.group(3)
            st = rest.split('|')[-2] if rest.count('|') >= 1 else rest
            dev = 'done' if '🟢' in st else ('wip' if '🟡' in st else 'plan')
            jira = re.findall(r'ACL-\d+', line)
            ep['stories'].append(dict(no=sid, title=title, typ='BE' if sid.startswith('SVC') else 'FS', jira=jira, dev=dev, ents=[]))
        out.append(ep)
    return out

def parse_farm(pj):
    txt = read(pj, pj['sources'][0][0]); out = []; cur = None; last = None
    for line in txt.split('## 5. Epics', 1)[-1].split('## 6.', 1)[0].splitlines():
        m = re.match(r'^### Epic (\d+)\s*[—\-:]\s*(.*)$', line)
        if m:
            cur = dict(key=('v1', m.group(1)), mvp='v1', num=m.group(1), name=clean_title(m.group(2)), stories=[], prefix='', order=[]); out.append(cur); last = None; continue
        m = re.match(r'^- \*\*(\d+\.\d+)\*\*\s*(.*)$', line)
        if m and cur:
            last = dict(no=m.group(1).split('.')[1], title=clean_title(m.group(2)), typ='FS', jira=[], dev='unk', ents=[]); cur['stories'].append(last); continue
        if last and line.startswith('  ') and line.strip(): last['title'] = clean_title(last['title'] + ' ' + line.strip())
    return out

# ---------- สถานะ dev จาก sprint-status ----------
RANK = {'blocked': 0, 'descoped': 0, 'backlog': 1, 'ready-for-dev': 2, 'in-progress': 3, 'review': 4, 'ready-for-review': 4, 'done': 5}
DEVMAP = {'blocked': 'blocked', 'descoped': 'blocked', 'backlog': 'plan', 'ready-for-dev': 'plan', 'in-progress': 'wip', 'review': 'review', 'ready-for-review': 'review', 'done': 'done'}
def apply_sprint(pj, epics):
    if not pj.get('sprint'): return None
    txt = read(pj, pj['sprint'])
    if not txt: return None
    upd = (re.search(r'last_updated:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', txt) or [None, '?'])[1]
    idx = {}
    for ep in epics:
        for s in ep['stories']: idx[(ep['mvp'], ep['num'], s['no'])] = (ep, s)
    by_num = collections.defaultdict(list)
    for (mvp, num, no), v in idx.items(): by_num[(num, no)].append(v)
    for line in txt.splitlines():
        m = re.match(r'^  (?:(m\d)-)?(\d+)-(\d+[a-z]?(?:-\d)?)-([\w\-]+?):\s*([\w\-]+)(.*)$', line)
        if not m: continue
        pre, num, no, slug, val, rest = m.groups()
        if slug == 'retrospective' or slug.startswith('epic'): continue
        mvp = {None: 'MVP-1', 'm2': 'MVP-2', 'm3': 'MVP-3'}.get(pre)
        hit = idx.get((mvp, num, no)) if not pj.get('unique_epics') else None
        if not hit:
            cands = by_num.get((num, no), [])
            hit = cands[0] if cands else None
        if not hit:
            # story มีใน sprint-status แต่ไม่มีหัวข้อในเอกสาร → เพิ่มจาก slug (ถ้า epic ก็ไม่มี → สร้าง epic จาก sprint-status)
            if not any(ep['num'] == num and (pj.get('unique_epics') or ep['mvp'] == mvp) for ep in epics):
                mv = mvp if not pj.get('unique_epics') else (epics[-1]['mvp'] if epics else 'MVP-1')
                nm = (pj.get('epic_name') or {}).get(int(num), 'Epic %s (มีเฉพาะใน sprint-status)' % num)
                epics.append(dict(key=(mv, num), mvp=mv, num=num, name=nm, stories=[], prefix='', order=[]))
            for ep in epics:
                if ep['num'] == num and (pj.get('unique_epics') or ep['mvp'] == mvp):
                    s = dict(no=no, title=slug.replace('-', ' '), typ=('BE' if slug.endswith('-be') else ('FE' if slug.endswith('-fe') or slug.startswith('fe-') else '')), jira=[], dev='unk', ents=[])
                    ep['stories'].append(s); idx[(ep['mvp'], ep['num'], no)] = (ep, s); hit = (ep, s); break
        if not hit: continue
        ep, s = hit
        s['ents'].append((slug, val))
        jira = re.findall(r'\b%s-\d+' % pj['jira'], rest) if pj['jira'] else []
        for j in jira:
            if j not in s['jira']: s['jira'].append(j)
    for ep in epics:
        for s in ep['stories']:
            if s['ents']:
                worst = min(s['ents'], key=lambda e: RANK.get(e[1], 9))[1]
                s['dev'] = DEVMAP.get(worst, 'unk')
    return upd

NON_UI = re.compile(r'\b(backend|scaffold|migration|terraform|deployment|observability|telemetry pipeline|ci matrix|ci gate|ci tier|backfill|schema|monorepo|dockerized|contract tests?|state machine|adapter|ingestion|cron|load test|infra)\b', re.I)
def is_ui(s):
    parts = re.split(r'[/+]', s['typ'] or '')
    if s['typ']:
        return any(t in ('FS', 'FE', 'Ops', 'Desktop', 'UI') for t in parts)
    return not NON_UI.search(s['title'])

def workdays(start, n):
    d = datetime.date.fromisoformat(start); out = []
    while len(out) < n:
        if d.weekday() < 5: out.append(d.isoformat())
        d += datetime.timedelta(days=1)
    return out

QA_OPTS = [('wait', 'รอทดสอบ'), ('pend', 'รอดำเนินการ'), ('wip', 'กำลังทดสอบ'), ('done', 'เสร็จแล้ว'), ('fail', 'ไม่ผ่าน'), ('block', 'บล็อก'), ('na', 'ไม่มี UI')]
DEV_OPTS = [('unk', 'ไม่ระบุ'), ('plan', 'วางแผน'), ('wip', 'กำลังทำ'), ('review', 'รอรีวิว'), ('done', 'เสร็จแล้ว'), ('blocked', 'ติดบล็อก')]
DEV_TXT = dict(DEV_OPTS)
def sel(kind, opts, val, rid):
    o = ''.join('<option value="%s"%s>%s</option>' % (v, ' selected' if v == val else '', l) for v, l in opts)
    return '<select class="st %s" data-k="%s" data-rid="%s" data-v="%s">%s</select>' % (kind, kind, rid, val, o)
def story_sort(no):
    m = re.match(r'(\d+)([a-z]?)(?:-(\d))?', no); return (int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (999, no, 0)
def epic_sort_num(num):
    m = re.search(r'(\d+)', num); return int(m.group(1)) if m else 0

def build_project(pj):
    epics = {'bmad': parse_bmad, 'clip': parse_clip, 'farm': parse_farm}[pj['kind']](pj)
    upd = apply_sprint(pj, epics)
    pid = pj['id']
    for ep in epics:
        ep['stories'].sort(key=lambda s: story_sort(s['no']))
        if pj.get('epic_name') and epic_sort_num(ep['num']) in pj['epic_name']: ep['name'] = pj['epic_name'][epic_sort_num(ep['num'])]
    # ---- กำหนด QA ----
    sched = {}
    if pj.get('schedule'):
        for ep in epics: sched[ep['key']] = pj['schedule'].get(epic_sort_num(ep['num']), [])
    else:
        started = ('done', 'review', 'wip') if upd else ('done', 'review', 'wip', 'unk')   # มี sprint-status → เอาเฉพาะ epic ที่ dev เริ่มแล้ว
        cands = [ep for ep in epics if any(is_ui(s) and s['dev'] in started for s in ep['stories'])]
        days = workdays(AUTO_START, len(cands))
        for ep, d in zip(cands, days): sched[ep['key']] = [d]
        for ep in epics: sched.setdefault(ep['key'], [])
    # ---- rows (เรียงล่าสุดไว้บน) ----
    order = sorted(epics, key=lambda ep: (sched[ep['key']][-1] if sched[ep['key']] else '0000', epic_sort_num(ep['num'])), reverse=True)
    rows = []; n_story = n_ui = 0; n_done_epic = 0
    for ep in order:
        days = sched[ep['key']]; keys = ep['stories']; cnt = collections.Counter(); items = []
        for i, s in enumerate(keys):
            ui = is_ui(s); cnt[s['dev']] += 1
            due = days[min(len(days) - 1, (i * len(days)) // max(1, len(keys)))] if (days and ui) else ''
            if not ui: qa = 'na'
            elif s['dev'] == 'done': qa = 'wait'
            elif s['dev'] == 'blocked': qa = 'block'
            elif s['dev'] in ('review', 'wip', 'plan'): qa = 'pend'
            else: qa = 'wait'
            sub = ' · '.join('%s=%s' % (sl.rsplit('-', 1)[-1] if sl.endswith(('-be', '-fe')) else 'story', v) for sl, v in s['ents']) if len(s['ents']) > 1 else ''
            items.append((s, ui, qa, due, sub)); n_story += 1; n_ui += ui
        items.reverse()
        done, total = cnt['done'], len(keys)
        ep_dev = 'done' if total and done == total else ('wip' if (cnt['done'] or cnt['review'] or cnt['wip']) else ('unk' if cnt['unk'] == total else 'plan'))
        if ep_dev == 'done': n_done_epic += 1
        grp = '%s.e%s' % (pid, ep['num'])
        elabel = ('%s · Epic %s' % (ep['mvp'], ep['num'])) if not str(ep['num']).startswith('EP-') else ep['num']
        tip = html.escape('Epic %s — %s' % (ep['num'], ep['name']), quote=True)
        rows.append('<tr class="grp" data-grp="%s" data-mvp="%s"><td class="c-topic" data-tip="%s"><b>%s</b> <span class="epc">dev เสร็จ %d/%d story</span></td>'
                    '<td class="c-st"><span class="pill dev-%s">%s</span></td><td class="c-d"><input type="date" data-rid="%s" data-k="ddev"></td><td class="c-st"></td>'
                    '<td class="c-d"><input type="date" class="bold" data-rid="%s" data-k="due" value="%s"></td><td></td><td class="c-rem"></td></tr>'
                    % (grp, ep['mvp'], tip, html.escape(elabel), done, total, ep_dev, DEV_TXT.get(ep_dev, ep_dev) if ep_dev != 'unk' else 'ไม่ระบุ', grp, grp, days[-1] if days else ''))
        for s, ui, qa, due, sub in items:
            rid = '%s.s%s-%s' % (pid, ep['num'], s['no'])
            jl = ' '.join('<a class="jk" href="%s%s" target="_blank" rel="noopener">%s</a>' % (JIRA, j, j) for j in s['jira'])
            sid = ('%s.%s' % (ep['num'], s['no'])) if not str(s['no']).startswith(('SVC', 'BO', 'EXT')) else s['no']
            topic = '<span class="sid">%s</span>%s' % (html.escape(sid), (' <span class="typ">[%s]</span>' % html.escape(s['typ'])) if s['typ'] else '')
            stip = html.escape('Story %s · %s' % (sid, s['title']), quote=True)
            rem = html.escape(sub) if sub else ('ไม่มี UI · เทสผ่าน integration/E2E ของ dev' if not ui else '')
            rows.append('<tr data-rid="%s" data-title="%s ปฏิทิน epic %s story %s %s"%s><td class="c-topic" data-tip="%s">%s %s</td>'
                        '<td class="c-st">%s</td><td class="c-d"><input type="date" data-rid="%s" data-k="ddev"></td><td class="c-st">%s</td>'
                        '<td class="c-d"><input type="date" data-rid="%s" data-k="due" value="%s"></td><td class="c-act"><input type="date" data-rid="%s" data-k="act"></td>'
                        '<td class="c-rem"><textarea class="rem" rows="2" data-rid="%s" data-k="rem" placeholder="หมายเหตุ…">%s</textarea></td></tr>'
                        % (rid, html.escape(pj['name'].lower()), ep['num'], sid, html.escape(s['title'].lower()), (' data-href="%s"' % pj['report']) if ui else '',
                           stip, topic, jl, sel('dev', DEV_OPTS, s['dev'], rid), rid, sel('qa', QA_OPTS, qa, rid), rid, due, rid, rid, rem))
    # ---- แถวปิดรอบ (เฉพาะที่กำหนด) ----
    head = []
    if pj.get('extra'):
        head.append('<tr class="grp" data-grp="%s.x"><td class="c-topic"><b>ปิดรอบ</b></td><td class="c-st"></td><td class="c-d"></td><td class="c-st"></td><td class="c-d"><input type="date" class="bold" data-rid="%s.x" data-k="due" value="%s"></td><td></td><td class="c-rem"></td></tr>' % (pid, pid, pj['extra'][-1][0]))
        for i, (d, topic, detail, rem) in reversed(list(enumerate(pj['extra']))):
            rid = '%s.x%d' % (pid, i)
            head.append('<tr data-rid="%s" data-title="%s ปฏิทิน %s" data-href="%s"><td class="c-topic" data-tip="%s"><b>%s</b></td><td class="c-st"></td><td class="c-d"></td>'
                        '<td class="c-st">%s</td><td class="c-d"><input type="date" data-rid="%s" data-k="due" value="%s"></td><td class="c-act"><input type="date" data-rid="%s" data-k="act"></td>'
                        '<td class="c-rem"><textarea class="rem" rows="2" data-rid="%s" data-k="rem" placeholder="หมายเหตุ…">%s</textarea></td></tr>'
                        % (rid, html.escape(pj['name'].lower()), topic.lower(), pj['report'], html.escape(detail, quote=True), topic, sel('qa', QA_OPTS, 'wait', rid), rid, d, rid, rid, html.escape(rem)))
    rows = head + rows
    # ---- ตารางสัปดาห์ ----
    if pj.get('weeks'):
        weeks = list(pj['weeks'])
    else:
        byweek = collections.OrderedDict()
        for ep in epics:
            for d in sched[ep['key']]:
                dd = datetime.date.fromisoformat(d); mon = dd - datetime.timedelta(days=dd.weekday())
                byweek.setdefault(mon, []).append('Epic %s' % ep['num'])
        weeks = []
        for i, (mon, eps) in enumerate(sorted(byweek.items())):
            fri = mon + datetime.timedelta(days=4)
            weeks.append(('สัปดาห์ที่ %d · %s–%s' % (i + 1, thd(mon.isoformat()), thd(fri.isoformat())), ' · '.join(dict.fromkeys(eps)), mon.isoformat(), fri.isoformat()))
    wk = ''.join('<tr class="wk"><td class="c-wkn"><b>%s</b></td><td colspan="2">%s</td><td class="c-d"><input type="date" data-rid="%s.w%d" data-k="start" value="%s"></td><td class="c-d"><input type="date" class="bold" data-rid="%s.w%d" data-k="due" value="%s"></td></tr>'
                 % (t, g, pid, i, a, pid, i, b) for i, (t, g, a, b) in reversed(list(enumerate(weeks))))
    src = ' · '.join(dict.fromkeys(s[0].split('/')[-1] for s in pj['sources']))
    sprint_txt = ('สถานะ DEV = sprint-status.yaml ของ dev (อัปเดตล่าสุด %s)' % upd) if upd else ('สถานะ DEV = ตารางสถานะในเอกสาร epic' if pj['kind'] == 'clip' else 'ไม่มี sprint-status → สถานะ DEV "ไม่ระบุ" (กรอกเองได้)')
    sched_txt = 'กำหนด QA วางมือ' if pj.get('schedule') else ('กำหนด QA วางอัตโนมัติ ~1 epic/วันทำงาน เริ่ม %s (เฉพาะ epic ที่ dev เริ่มแล้ว) — แก้ในหน้าได้' % thd(AUTO_START))
    board = ('<a href="%s" target="_blank" rel="noopener">📋 Jira %s ↗</a>' % (pj['board'], pj['jira'])) if pj.get('board') else 'Jira: ยังไม่พบใน repo'
    ref = (' @ ' + pj['ref']) if pj['ref'] else ''
    block = '''<div class="pj" data-pj="%s" data-name="%s" data-emoji="%s">
        <div class="jira">หัวข้อ = Epic/Story ที่ BA/dev กำหนด (%s%s) · %s · %d epic (dev เสร็จ %d) · %d story (%d มี UI) · %s · %s</div>
        <div class="tblwrap wkwrap"><table class="tbl weeks"><thead><tr><th>สัปดาห์</th><th colspan="2">โฟกัส</th><th>เริ่ม</th><th>กำหนด QA</th></tr></thead><tbody>%s</tbody></table></div>
        <div class="tblwrap"><table class="tbl sheet"><thead><tr><th>หัวข้อ (hover ดูรายละเอียด)</th><th>สถานะ DEV</th><th>กำหนด DEV</th><th>สถานะ QA</th><th>กำหนด QA</th><th>Action Date</th><th>Remark</th></tr></thead><tbody>
%s
</tbody></table></div>
        </div>''' % (pid, html.escape(pj['name'], quote=True), pj['emoji'], html.escape(src), ref, sprint_txt, len(epics), n_done_epic, n_story, n_ui, sched_txt, board, wk, '\n'.join(rows))
    return block, dict(epics=len(epics), stories=n_story, ui=n_ui)

def main():
    blocks, stats = [], []
    for pj in PROJECTS:
        b, st = build_project(pj); blocks.append(b); stats.append((pj['id'], st))
    tabs = ''.join('<button class="pjtab%s" data-pj="%s"><span>%s</span> %s <small>%d</small></button>' % (' on' if pj['id'] == 'ai' else '', pj['id'], pj['emoji'], html.escape(pj['name'].split(' (')[0]), st['epics']) for pj, (_, st) in zip(PROJECTS, stats))
    legend = '''<div class="legend"><span class="lg dev-done">DEV เสร็จแล้ว</span><span class="lg dev-review">DEV รอรีวิว</span><span class="lg dev-plan">DEV วางแผน</span><span class="lg dev-blocked">DEV ติดบล็อก</span><span class="lg qa-wait">QA รอทดสอบ</span><span class="lg qa-pend">QA รอดำเนินการ (รอ dev)</span><span class="lg qa-na">ไม่มี UI</span><span class="lg">สถานะ · กำหนด DEV · กำหนด QA · Action Date · Remark แก้ในหน้าได้ — บันทึกขึ้น GitHub อัตโนมัติเหมือนไฟล์ test case</span></div>'''
    out = '<!-- CAL:START (generated by tools/build/build_timeline_calendar.py — อย่าแก้ตรงนี้ด้วยมือ) -->\n        <div class="pjtabs" id="pjtabs">%s</div>\n        %s\n        %s\n        <!-- CAL:END -->' % (tabs, legend, '\n        '.join(blocks))
    h = OUT.read_text(encoding='utf-8')
    h2, n = re.subn(r'<!-- CAL:START.*?<!-- CAL:END -->', lambda m: out, h, flags=re.S)
    assert n == 1, 'ไม่พบ marker CAL:START/END'
    OUT.write_text(h2, encoding='utf-8')
    for pid, st in stats: print('%-8s epics=%2d stories=%3d ui=%3d' % (pid, st['epics'], st['stories'], st['ui']))

if __name__ == '__main__':
    main()
