#!/usr/bin/env python3
"""สร้างปฏิทินทดสอบ (แบบชีต) ของ TAKRA AI · Live ลง timeline/index.html
แหล่งข้อมูล = หัวข้องานที่ BA/dev กำหนด (ไม่ใช่ test case):
  - Epic/Story + ประเภท [BE]/[FS]/[FE]  ← _bmad-output/planning-artifacts/epics.md + epics-mvp2.md
  - สถานะ DEV ราย story                 ← _bmad-output/implementation-artifacts/sprint-status.yaml
QA เป็นคนกำหนด "วันเทส" (SCHEDULE ด้านล่าง) · dev/BA ไม่ได้กำหนดวันในเอกสาร จึงเว้น "กำหนด DEV" ให้กรอกเอง
รัน: python3 tools/build/build_timeline_calendar.py   (แทนที่ระหว่าง <!-- CAL:START --> … <!-- CAL:END -->)
"""
import re, html, pathlib, collections

AI = pathlib.Path('/Users/ice/Documents/rf/takra-ai')
OUT = pathlib.Path(__file__).resolve().parents[2] / 'timeline' / 'index.html'
REPORT = 'https://wanlee-tankunnatam.github.io/qa-test-reports/projects/takra-ai/2026/08/reports/takra-ai-mvp1-happy-mvp2-full-ui-test-cases-table.html'
JIRA_BOARD = 'https://kitdi.atlassian.net/jira/software/projects/TAKRA/boards/1593/timeline'

# ---------- ตารางวันเทส (QA กำหนด · ทำงาน จ–ศ · ~1 epic/วัน) ----------
EPIC_INFO = {
  1: ('MVP-1', 'เข้าระบบ & รากฐาน Workspace'),
  2: ('MVP-1', 'คลังของ Workspace — Avatar/Voice · สินค้า · คำเสี่ยง · สคริปต์'),
  3: ('MVP-1', 'Live Studio — สร้างไลฟ์'),
  4: ('MVP-1', 'ออกอากาศ Avatar Live (Phone-as-Camera)'),
  5: ('MVP-1', 'คอมเมนต์ · ตอบอัตโนมัติ · Risk Filter · Live Console · Recap'),
  6: ('MVP-1', 'AI ช่วยเขียน Script'),
  7: ('MVP-1', 'Production Readiness & Pilot (Infra — ไม่มี UI)'),
  8: ('MVP-2', 'AIEventLog — audit trail ของ AI'),
  9: ('MVP-2', 'Live Monitoring & Post-Live Recap'),
  10: ('MVP-2', 'คลัง Avatar & Voice self-service'),
  11: ('MVP-2', 'Internal Ops & Support — ⛔ ย้ายไป TAKRA Hub (2026-08-10)'),
  12: ('MVP-2', 'Billing — มิเตอร์ · แจ้งเตือน · cap'),
  13: ('MVP-2', 'Tool-Calling Auto-Reply (Engine align)'),
  15: ('MVP-2', 'Studio & Live-Creation riders'),
  16: ('MVP-2', 'Settings & Account IA + Usage unify'),
  19: ('MVP-2', 'Multi-Platform RTMP core (แยกจาก Epic 14 · 2026-08-24)'),
}
# epic → รายการวันที่จะเทส (เรียง story ไล่ไปตามวัน)
SCHEDULE = {
  1: ['2026-09-16'], 2: ['2026-09-16'], 3: ['2026-09-17'], 4: ['2026-09-18'], 5: ['2026-09-18'], 6: ['2026-09-18'],
  8: ['2026-09-21'], 9: ['2026-09-22', '2026-09-23'], 10: ['2026-09-24', '2026-09-25'],
  12: ['2026-09-28'], 15: ['2026-09-29'], 16: ['2026-09-30'], 13: ['2026-10-01'],
  19: ['2026-10-05', '2026-10-06'],
}
WEEKS = [
  ('สัปดาห์ที่ 1 · 14–18 ก.ย.', 'MVP-1 regression ทั้ง 6 epic (14–15 ก.ย. ไปทำ Trendora)', '2026-09-14', '2026-09-18'),
  ('สัปดาห์ที่ 2 · 21–25 ก.ย.', 'MVP-2 backbone — AIEventLog · Live Console/Recap · Avatar/Voice', '2026-09-21', '2026-09-25'),
  ('สัปดาห์ที่ 3 · 28 ก.ย.–2 ต.ค.', 'MVP-2 — Billing · Studio riders · Settings · Tool-calling (2 ต.ค. กันไว้ retest)', '2026-09-28', '2026-10-02'),
  ('สัปดาห์ที่ 4 · 5–9 ต.ค.', 'MVP-2 — RTMP · Full E2E (7 ต.ค.) · retest รวบยอด (8 ต.ค.) · สรุป + DoD (9 ต.ค.)', '2026-10-05', '2026-10-09'),
]
EXTRA_ROWS = [  # (date, topic, detail, remark)
  ('2026-10-02', 'Retest บั๊ก MVP-2 ที่ dev ปิดในสัปดาห์', 'ทุก story ที่สถานะ QA = ไม่ผ่าน แล้ว dev แจ้งปิด', 'อัปเดต Jira ให้ตรง'),
  ('2026-10-07', 'Full E2E MVP-2', 'วิ่งครบลูปข้าม Epic 8–16 · Studio → ไลฟ์ → Console → Recap → แจ้งเตือน', 'ห้ามสลับบัญชีกลางทาง'),
  ('2026-10-08', 'Retest รวบยอด', 'ทุกเคส ไม่ผ่าน / บล็อก / พัก ที่ dev ปิดแล้ว', ''),
  ('2026-10-09', 'สรุปผล + DoD MVP-2', 'อัปเดต QA Summary · เช็ค DoD MVP-2 · รายงานหัวหน้า', ''),
]
TH_MON = {'09': 'ก.ย.', '10': 'ต.ค.'}
def thd(d): return d[8:10].lstrip('0') + ' ' + TH_MON[d[5:7]]

# ---------- อ่านหัวข้อ story จาก epics ----------
def read_titles():
    t = {}
    for f in ('epics.md', 'epics-mvp2.md'):
        for line in (AI / '_bmad-output/planning-artifacts' / f).read_text(encoding='utf-8').splitlines():
            m = re.match(r'^### Story (\d+)\.(\d+[a-z]?(?:-\d)?): \[([^\]]+)\] (.*)$', line)
            if not m: continue
            ep, st, typ, title = m.groups()
            title = re.sub(r'\s*\*\(.*?\)\*\s*', ' ', title)          # *(annotation)*
            title = re.sub(r'\s*🆕.*$', '', title)
            title = re.sub(r'\*\*(.*?)\*\*', r'\1', title)
            title = re.sub(r'~~(.*?)~~', r'\1', title)
            title = re.sub(r'`', '', title).strip()
            keys = re.findall(r'TAKRA-\d+', line)
            t[(int(ep), st)] = (typ, title, keys)
    return t

def read_status():
    st = collections.OrderedDict()
    for line in (AI / '_bmad-output/implementation-artifacts/sprint-status.yaml').read_text(encoding='utf-8').splitlines():
        m = re.match(r'^  (\d+)-(\d+[a-z]?(?:-\d)?)-([\w\-]+?): *([\w\-]+)', line)
        if not m: continue
        ep, sn, slug, val = m.groups()
        if slug == 'retrospective': continue
        st.setdefault((int(ep), sn), []).append((slug, val))
    return st

RANK = {'blocked': 0, 'backlog': 1, 'ready-for-dev': 2, 'in-progress': 3, 'review': 4, 'ready-for-review': 4, 'done': 5}
DEV_LABEL = {'blocked': ('blocked', 'ติดบล็อก'), 'backlog': ('plan', 'วางแผน'), 'ready-for-dev': ('plan', 'วางแผน'),
             'in-progress': ('wip', 'กำลังทำ'), 'review': ('review', 'รอรีวิว'), 'ready-for-review': ('review', 'รอรีวิว'), 'done': ('done', 'เสร็จแล้ว')}
QA_OPTS = [('wait', 'รอทดสอบ'), ('pend', 'รอดำเนินการ'), ('wip', 'กำลังทดสอบ'), ('done', 'เสร็จแล้ว'), ('fail', 'ไม่ผ่าน'), ('block', 'บล็อก'), ('na', 'ไม่มี UI')]
DEV_OPTS = [('plan', 'วางแผน'), ('wip', 'กำลังทำ'), ('review', 'รอรีวิว'), ('done', 'เสร็จแล้ว'), ('blocked', 'ติดบล็อก')]

def sel(kind, opts, val, rid):
    o = ''.join('<option value="%s"%s>%s</option>' % (v, ' selected' if v == val else '', l) for v, l in opts)
    return '<select class="st %s" data-k="%s" data-rid="%s" data-v="%s">%s</select>' % (kind, kind, rid, val, o)

def story_sort(k):
    m = re.match(r'(\d+)([a-z]?)(?:-(\d))?', k[1]); return (k[0], int(m.group(1)), m.group(2), int(m.group(3) or 0))

def main():
    titles, status = read_titles(), read_status()
    epics = collections.OrderedDict()
    for k in sorted(status, key=story_sort): epics.setdefault(k[0], []).append(k)
    rows = []
    # เรียงตามวันเทส: epic ที่มีวัน → ตามวัน · epic ไม่มีวัน (7, 11) ไว้ท้าย
    order = sorted(epics, key=lambda e: (SCHEDULE.get(e, ['9999'])[0], e))
    n_story = n_ui = 0
    for ep in order:
        mvp, name = EPIC_INFO.get(ep, ('?', ''))
        keys = epics[ep]; days = SCHEDULE.get(ep, [])
        # นับสถานะ
        cnt = collections.Counter()
        items = []
        for i, k in enumerate(keys):
            ents = status[k]
            worst = min(ents, key=lambda e: RANK.get(e[1], 9))[1]
            typ, title, jira = titles.get(k, ('', '', []))
            if not title:
                slug = ents[0][0]; title = slug.replace('-', ' ')
                typ = 'BE' if slug.endswith('-be') else ('FE' if slug.endswith('-fe') or slug.startswith('fe-') else typ or '?')
            parts = re.split(r'[/+]', typ)
            ui = any(t in ('FS', 'FE', 'Ops') for t in parts)   # เทส UI ได้เฉพาะ story ที่มีฝั่งหน้าจอ
            cnt[worst] += 1
            due = ''
            if days and ui:
                due = days[min(len(days) - 1, (i * len(days)) // max(1, len(keys)))]
            dcls, dlab = DEV_LABEL.get(worst, ('plan', worst))
            if not ui: qa = 'na'
            elif worst == 'done': qa = 'wait'
            elif worst in ('review', 'ready-for-review'): qa = 'pend'
            elif worst == 'blocked': qa = 'block'
            else: qa = 'pend'
            sub = ' · '.join('%s=%s' % (s.rsplit('-', 1)[-1] if s.endswith(('-be', '-fe')) else 'story', v) for s, v in ents) if len(ents) > 1 else ''
            items.append((k, typ, title, jira, dcls, qa, due, sub, ui))
            n_story += 1; n_ui += ui
        done = cnt['done']; total = len(keys)
        ep_due = thd(days[-1]) if days else '—'
        ep_dev = 'done' if done == total else ('wip' if cnt['done'] or cnt['review'] or cnt['in-progress'] else 'plan')
        rows.append('<tr class="grp" data-grp="e%d"><td colspan="2"><b>%s · Epic %d — %s</b> <span class="epc">dev เสร็จ %d/%d story</span></td>'
                    '<td class="c-st"><span class="pill dev-%s">%s</span></td><td class="c-d"></td><td class="c-st"></td><td class="c-d"><b>%s</b></td><td></td><td class="c-rem">%s</td></tr>'
                    % (ep, mvp, ep, html.escape(name), done, total, ep_dev, {'done': 'เสร็จแล้ว', 'wip': 'กำลังทำ', 'plan': 'วางแผน'}[ep_dev], ep_due,
                       'ไม่มี UI ให้เทส — ดูผลจาก CI/ops' if ep == 7 else ('takra-ai ไม่ทำ' if ep == 11 else '')))
        for k, typ, title, jira, dcls, qa, due, sub, ui in items:
            rid = 's%d-%s' % k
            jl = ' '.join('<a class="jk" href="https://kitdi.atlassian.net/browse/%s" target="_blank" rel="noopener">%s</a>' % (j, j) for j in jira)
            topic = '<span class="sid">%d.%s</span> <span class="typ">[%s]</span>' % (k[0], k[1], html.escape(typ))
            rows.append('<tr data-rid="%s" data-title="ตะกร้าไลฟ์ takra ai ปฏิทิน epic %d story %s %s"%s>'
                        '<td class="c-topic">%s</td><td class="c-detail">%s %s</td><td class="c-st">%s</td><td class="c-d"><input type="text" class="txt" data-rid="%s" data-k="ddev" placeholder="—"></td>'
                        '<td class="c-st">%s</td><td class="c-d">%s</td><td class="c-act"><input type="date" data-rid="%s" data-k="act"></td><td class="c-rem">%s</td></tr>'
                        % (rid, k[0], k[1], html.escape(title.lower()), (' data-href="%s"' % REPORT) if ui else '',
                           topic, html.escape(title), jl, sel('dev', DEV_OPTS, dcls, rid), rid, sel('qa', QA_OPTS, qa, rid),
                           thd(due) if due else '<span class="muted">—</span>', rid, html.escape(sub) if sub else ('ไม่มี UI · เทสผ่าน integration/E2E ของ dev' if not ui and ep not in (7, 11) else '')))
        # แถวเสริม (E2E/retest/สรุป) — วางตามวัน
    # แถวเสริมท้ายตาราง
    rows.append('<tr class="grp" data-grp="x"><td colspan="2"><b>ปิดรอบ MVP-2</b></td><td></td><td></td><td></td><td class="c-d"><b>9 ต.ค.</b></td><td></td><td></td></tr>')
    for i, (d, topic, detail, rem) in enumerate(EXTRA_ROWS):
        rid = 'x%d' % i
        rows.append('<tr data-rid="%s" data-title="ตะกร้าไลฟ์ takra ai ปฏิทิน %s" data-href="%s"><td class="c-topic"><b>%s</b></td><td class="c-detail">%s</td><td class="c-st"></td><td class="c-d"></td>'
                    '<td class="c-st">%s</td><td class="c-d">%s</td><td class="c-act"><input type="date" data-rid="%s" data-k="act"></td><td class="c-rem">%s</td></tr>'
                    % (rid, topic.lower(), REPORT, topic, detail, sel('qa', QA_OPTS, 'wait', rid), thd(d), rid, rem))

    weeks = ''.join('<tr class="wk"><td class="c-wkn"><b>%s</b></td><td colspan="2">%s</td><td class="c-d">%s</td><td class="c-d">%s</td></tr>' % (t, g, thd(a), thd(b)) for t, g, a, b in WEEKS)
    block = f'''<!-- CAL:START (generated by tools/build/build_timeline_calendar.py — อย่าแก้ตรงนี้ด้วยมือ) -->
        <div class="jira">หัวข้อ = Epic/Story ที่ BA/dev กำหนด (epics.md · epics-mvp2.md) · สถานะ DEV = sprint-status.yaml ของ dev (อัปเดตล่าสุด 2026-09-10) · {n_story} story ({n_ui} story มี UI) · วันเทส = QA วาง ~1 epic/วัน · แผนตัวจริงบน Jira: <a href="{JIRA_BOARD}" target="_blank" rel="noopener">📋 TAKRA board timeline ↗</a></div>
        <div class="legend"><span class="lg dev-done">DEV เสร็จแล้ว</span><span class="lg dev-review">DEV รอรีวิว</span><span class="lg dev-plan">DEV วางแผน</span><span class="lg dev-blocked">DEV ติดบล็อก</span><span class="lg qa-wait">QA รอทดสอบ</span><span class="lg qa-pend">QA รอดำเนินการ (รอ dev)</span><span class="lg qa-na">ไม่มี UI</span><span class="lg">สถานะ · กำหนด DEV · Action Date แก้ในหน้าได้ — จำในเบราว์เซอร์เครื่องนี้เท่านั้น</span></div>
        <div class="tblwrap wkwrap"><table class="tbl weeks"><thead><tr><th>สัปดาห์</th><th colspan="2">โฟกัส</th><th>เริ่ม</th><th>Duedate</th></tr></thead><tbody>{weeks}</tbody></table></div>
        <div class="tblwrap"><table class="tbl sheet"><thead><tr><th>หัวข้อ (Story)</th><th>รายละเอียด</th><th>สถานะ DEV</th><th>กำหนด DEV</th><th>สถานะ QA</th><th>วันเทส (Duedate)</th><th>Action Date</th><th>Remark</th></tr></thead><tbody>
{chr(10).join(rows)}
</tbody></table></div>
        <!-- CAL:END -->'''
    h = OUT.read_text(encoding='utf-8')
    h2, n = re.subn(r'<!-- CAL:START.*?<!-- CAL:END -->', lambda m: block, h, flags=re.S)
    assert n == 1, 'ไม่พบ marker CAL:START/END ใน timeline/index.html'
    OUT.write_text(h2, encoding='utf-8')
    print('ok epics=%d stories=%d ui=%d' % (len(epics), n_story, n_ui))

if __name__ == '__main__':
    main()
