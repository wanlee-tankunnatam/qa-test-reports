#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 (takra-ai) — ทดสอบ "ผลของ AI" ไม่ผ่านหน้าจอ · จัดเป็นรายงานหน้าตาเดียวกับรายงาน regression

ต้นฉบับ: tools/build/ai-comment-results-sources/2026-10-08.html (หน้าผลทดสอบที่ QA ทำมา · ชุด A/B · ตารางทุกข้อ + ปัญหาที่เจอ)
โมดูลนี้อ่านตารางจากต้นฉบับ → EPICS (ชุด A/B) · feats (กลุ่มตามรหัสข้อ) · 1 แถว = 1 ข้อ
ผลที่ตัดสินไว้ในต้นฉบับ (ผ่าน/ไม่ผ่าน/ก้ำกึ่ง + คำที่ AI พูด) ถูก seed ลง store-data ครั้งแรกเท่านั้น (SEED_STORE) —
หลังจากนั้นเป็นข้อมูลของรายงาน (auto-save) build ซ้ำไม่ทับ
build: python3 tools/build/build_hub_report.py aicommenta  (ชุด A · 1 สคริปต์) / aicommentb (ชุด B · 2 สคริปต์)
"""
import html as _html
import json
import pathlib
import re

SRC = pathlib.Path(__file__).resolve().parent / 'ai-comment-results-sources' / '2026-10-08.html'
PAGES = 'https://wanlee-tankunnatam.github.io/qa-test-reports/'

KINDS = {  # ใช้ key ชุดเดิมของ build (สี/คลาส) แต่ตั้งป้ายเป็นของรายงานนี้
    'happy': ('คอมเมนต์ปกติ', 'คำถาม/คอมเมนต์ทั่วไปของผู้ชม'),
    'negative': ('คอมเมนต์พิเศษ ⚑', 'สะกดเลี่ยงคำเสี่ยง · ภาษาอื่น · ภาษาผสม · ลองเจาะคำสั่ง ฯลฯ (มีป้าย ⚑ ในต้นฉบับ)'),
}

_SETS = {
    'A': dict(key='aiA', chip='☕ ชุด A', emoji='☕'),
    'B': dict(key='aiB', chip='👟 ชุด B', emoji='👟'),
}
_VMAP = {'pass': 'pass', 'fail': 'fail', 'warn': 'hold'}          # ก้ำกึ่ง → HOLD (รอตัดสิน/ควรดูเอง)
_VTXT = {'pass': '✅ ผ่าน', 'fail': '❌ ไม่ผ่าน', 'warn': '⚠️ ก้ำกึ่ง'}


def _txt(frag):
    """HTML ชิ้นเล็ก → ข้อความล้วน (เก็บช่องว่างระหว่างแท็ก)"""
    frag = re.sub(r'<br\s*/?>', '\n', frag)
    frag = re.sub(r'</(div|li|p)>', '\n', frag)
    t = _html.unescape(re.sub(r'<[^>]+>', ' ', frag))
    return '\n'.join(' '.join(l.split()) for l in t.split('\n') if l.strip())


def _cell(row, cls):
    m = re.search(rf'<td class="{cls}">([\s\S]*?)</td>', row)
    return m.group(1) if m else ''


def _group_of(cid):
    """A-C1-4 → C1 · A-GB-24-pre → GB · P1-8 → P1 · G-69 → G · X-7 → X"""
    s = re.sub(r'^[AB]-', '', cid)
    return re.match(r'[A-Z]+\d*', s).group(0)


_src = SRC.read_text(encoding='utf-8')
EPICS, SEED_STORE, ISSUES = [], {}, {}
_SET_INFO = {}
for _m in re.finditer(r'<section class="panel" data-s="([AB])">([\s\S]*?)(?=<section class="panel"|<script)', _src):
    _k, _body = _m.group(1), _m.group(2)
    _cards = re.search(r'<div class="card">([\s\S]*?)</div>\s*<h2>', _body)
    _head = _txt(_cards.group(1)).split('\n') if _cards else []
    _SET_INFO[_k] = _head
    # ปัญหาที่เจอในชุดนี้
    ISSUES[_k] = []
    for _iss in re.finditer(r'<section class="issue"><h3><span class="n">\d+</span>([\s\S]*?)</h3><p>([\s\S]*?)</p>([\s\S]*?)</section>', _body):
        _ids = re.findall(r'<a href="#([^"]+)">', _iss.group(3))
        ISSUES[_k].append((_txt(_iss.group(1)), _txt(_iss.group(2)), _ids))
    _feats = {}
    for _r in re.finditer(r'<tr id="([^"]+)"[^>]*data-v="([^"]+)"[^>]*>([\s\S]*?)</tr>', _body):
        cid, v, row = _r.group(1), _r.group(2), _r.group(3)
        cm_raw = _cell(row, 'cm')
        note = re.search(r'<div class="note">([\s\S]*?)</div>', cm_raw)
        comment = _txt(re.sub(r'<div class="note">[\s\S]*?</div>', '', cm_raw))
        flag = _txt(note.group(1)) if note else ''
        said = _txt(_cell(row, 'said'))
        vd = _cell(row, 'vd')
        _w = re.search(r'<div class="why">([\s\S]*?)</div>', vd)
        why = _txt(_w.group(1)) if _w else ''
        stc = _txt(_cell(row, 'st'))
        exp = _cell(row, 'exp')
        should = re.search(r'<b class="okc">ควร</b>([\s\S]*?)</div>', exp)
        nope = re.search(r'<b class="badc">ห้าม</b>([\s\S]*?)</div>', exp)
        expected = []
        if should:
            expected.append('ควร: ' + _txt(should.group(1)))
        if nope:
            expected.append('ห้าม: ' + _txt(nope.group(1)))
        grp = _group_of(cid)
        title = f'ผู้ชมพิมพ์ "{comment}"' + (f' · {flag}' if flag else '')
        case = dict(
            id=cid, title=title, prio='P1', level='ui', kind='negative' if flag else 'happy', ui=True,
            pre=['รันกับ AI จริงบน UAT · ข้อมูลสินค้าจริงจาก workspace QA · ใช้โค้ดตอบคอมเมนต์ตัวจริง (ไม่ผ่านหน้าจอ · ไม่ได้ไลฟ์)'],
            steps=['ส่งคอมเมนต์ผู้ชมตาม Test Data เข้าโค้ดตอบคอมเมนต์ตัวจริงของชุดนี้',
                   'อ่านประโยคที่ AI พูดออกอากาศ และสถานะในระบบ แล้วเทียบกับ "ควร / ห้าม"'],
            data=[f'คอมเมนต์: "{comment}"'] + ([flag] if flag else []),
            expected=expected or ['ตอบตามข้อมูลสินค้า ไม่แต่งข้อมูลเอง'],
            src=f'ที่มา: ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 · ชุด {_k} · กลุ่ม {grp}',
            note=None,
        )
        _feats.setdefault(grp, []).append(case)
        actual = (f'AI พูด: {said}' if said else 'AI พูด: —') + f'\nสถานะในระบบ: {stc}' + f'\nผล: {_VTXT[v]}' + (f' — {why}' if why else '')
        SEED_STORE[cid] = {'st': _VMAP[v], 'actual': actual}
    s = _SETS[_k]
    sub = _head[0] if _head else ''
    EPICS.append(dict(key=s['key'], chip=s['chip'], emoji=s['emoji'],
                      title=f'ชุด {_k} · {sub}',
                      feats=[dict(featkey=f'{s["key"]}-{g.lower()}', title=f'ชุด {_k} · กลุ่ม {g} ({len(cs)} ข้อ)', cases=cs)
                             for g, cs in _feats.items()]))

_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), 'duplicate ids'
_N = {e['key']: sum(len(f['cases']) for f in e['feats']) for e in EPICS}


def _issues_html(k):
    li = ''.join(f'<li><b>{_html.escape(t)}</b> — {_html.escape(d)}'
                 + (f' <span style="opacity:.75">({", ".join(_html.escape(i) for i in ids)})</span>' if ids else '') + '</li>'
                 for t, d, ids in ISSUES.get(k, []))
    return f'<ol style="margin:4px 0 8px 18px;padding:0">{li}</ol>' if li else ''


# ── ชุด B เพิ่ม: สินค้ามากกว่า 1 ตัว (MP) — ทดสอบ 8 ต.ค. 2569 ตามคำขอ QA ──
# หลัก: ถามรายละเอียดเมื่อมีสินค้ามากกว่า 1 ตัว คำตอบต้องกำกับชื่อสินค้า (หรือถามกลับว่าตัวไหน) และไม่เอาข้อมูลของอีกตัวมาตอบ
# ต้นฉบับ: ai-comment-results-sources/2026-10-08-multi-product.json (เคส + ผลดิบจาก probe บนโค้ด origin/uat 6e072387)
_MP = json.loads((SRC.parent / '2026-10-08-multi-product.json').read_text(encoding='utf-8'))
_MP_ON = {'H': 'รองเท้าแตะหัวโต', 'M': 'แมรี่เจน HP8075'}
_FAQCOL = 'ตอบจาก FAQ "มีสีอะไรบ้าง" ของแมรี่เจน (ไม่ผ่าน AI) เพราะคำถามมีคำว่า "อะไรบ้าง"'
_MP_VERDICT = {  # id → (pass|fail|hold, เหตุผล)
    'MP-1-H': ('fail', 'ถามไซซ์ แต่ได้รายการสีของแมรี่เจน ไม่กำกับชื่อ — ' + _FAQCOL),
    'MP-2-H': ('fail', 'กำลังพูดถึงหัวโต แต่ได้สีของแมรี่เจนโดยไม่กำกับชื่อ (หัวโตไม่มีข้อมูลสี) — ' + _FAQCOL),
    'MP-3-H': ('pass', 'กำกับชื่อ "รุ่นรองเท้าหัวโตนี้" และตอบ 3.5 ซม. ตรงข้อมูล'),
    'MP-4-H': ('pass', 'กำกับชื่อ "รองเท้าหัวโต" ตอบกันน้ำตรงข้อมูล'),
    'MP-5-H': ('pass', 'กำกับชื่อ "รุ่นหัวโตนี้" บอกว่ายังไม่มีข้อมูลกันลื่น ไม่ยืมเคลมของแมรี่เจน'),
    'MP-6-H': ('fail', 'ตารางไซซ์ของหัวโตมี 24 ซม. = 39 แต่ด่านไซซ์ตัด ผู้ชมได้ยิน "ส่วนนี้ยังไม่มีข้อมูลนะคะ" (ไม่กำกับชื่อ + ลงท้ายคะ)'),
    'MP-7-H': ('pass', 'ตอบ EVA ตรงข้อมูล — ทั้งสองรุ่นเป็น EVA เหมือนกัน ไม่กำกับชื่อก็ไม่ทำให้เข้าใจผิด'),
    'MP-8-H': ('pass', 'ไม่บอกราคา ชวนดูตะกร้า และกำกับชื่อ "รุ่นหัวโต"'),
    'MP-9-H': ('fail', 'ระบุ "แมรี่เจน" ในคำถามแล้ว ถามไซซ์ แต่ได้รายการสี — ' + _FAQCOL),
    'MP-10-H': ('fail', 'ถาม "รองเท้าหัวโต" มีสีอะไร แต่ได้สีของแมรี่เจน = ข้อมูลผิดสินค้า — ' + _FAQCOL),
    'MP-11-H': ('pass', 'ทวนชื่อ HP8075 ในคำถาม บอกว่ายังไม่มีข้อมูลกันน้ำ ไม่ยืมเคลมกันน้ำของหัวโต'),
    'MP-12-H': ('fail', 'เทียบสองรุ่นถูกและกำกับชื่อครบ แต่มีคำขยะ "เครดิตฟรี" หลุดท้ายประโยค'),
    'MP-13-H': ('pass', 'เทียบถูก หัวโต 3.5 ซม. > แมรี่เจน 3 ซม. พร้อมชื่อรุ่น'),
    'MP-14-H': ('pass', 'บอกว่ามี 2 แบบ พร้อมชื่อ หัวโต + แมรี่เจน HP8075'),
    'MP-15-H': ('pass', '"คู่นี้" = หัวโต — กำกับชื่อ ตอบไซซ์ 36-40 (ไม่มี 41) ตรง SKU'),
    'MP-1-M': ('fail', 'ถามไซซ์ แต่ได้รายการสี ไม่กำกับชื่อ — ' + _FAQCOL),
    'MP-2-M': ('hold', 'ข้อมูลสีถูกกับแมรี่เจนที่กำลังพูดถึง แต่ไม่กำกับชื่อสินค้า (FAQ ตอบเป็นรายการล้วน)'),
    'MP-3-M': ('pass', 'กำกับชื่อ "รุ่น HP8075" ตอบพื้นหนา 3 เซน ตรงข้อมูล'),
    'MP-4-M': ('pass', 'กำกับชื่อ "รุ่น HP8075" บอกว่ายังไม่มีข้อมูลกันน้ำ ไม่ยืมของหัวโต'),
    'MP-5-M': ('pass', 'กำกับชื่อ "แมรี่เจนคู่นี้" ตอบกันลื่นตรง Claims'),
    'MP-6-M': ('fail', 'ด่านไซซ์ตัด ผู้ชมได้ยิน "ส่วนนี้ยังไม่มีข้อมูลนะคะ" ไม่กำกับชื่อ — ควรบอกว่าแมรี่เจนไม่มีตารางไซซ์ (ตารางมีเฉพาะหัวโต)'),
    'MP-7-M': ('pass', 'กำกับชื่อ "แมรี่เจนคู่นี้" ตอบ EVA ตรงข้อมูล'),
    'MP-8-M': ('pass', 'ไม่บอกราคา ชวนดูตะกร้า กำกับชื่อ "รุ่นแมรี่เจน HP8075"'),
    'MP-9-M': ('fail', 'ระบุ "แมรี่เจน" แล้ว ถามไซซ์ แต่ได้รายการสี — ' + _FAQCOL),
    'MP-10-M': ('fail', 'ถาม "รองเท้าหัวโต" มีสีอะไร แต่ได้สีของแมรี่เจน = ข้อมูลผิดสินค้า — ' + _FAQCOL),
    'MP-11-M': ('pass', 'บอกว่า HP8075 ยังไม่มีข้อมูลกันน้ำ ไม่เดา'),
    'MP-12-M': ('fail', 'ถามว่าสองคู่ต่างกันยังไง แต่พูดแค่หัวโต ไม่พูดถึงแมรี่เจนเลย (เทียบไม่ครบ)'),
    'MP-13-M': ('pass', 'เทียบถูก หัวโต 3.5 > HP8075 3 เซน พร้อมชื่อรุ่น'),
    'MP-14-M': ('pass', 'บอกว่ามี 2 แบบ พร้อมชื่อทั้งสองรุ่น'),
    'MP-15-M': ('pass', '"คู่นี้" = HP8075 — กำกับชื่อ ตอบ 36-41 ตามข้อมูลข้อความ (ข้อมูลขัดกับ SKU 36-40 — ต้องแก้ข้อมูลสินค้า)'),
}
_MP_RES = {r['id']: r for r in _MP['results']}
_mp_feats = {}
for _c in _MP['cases']:
    cid = _c['id']; st_ = cid.rsplit('-', 1)[1]
    r = _MP_RES[cid]; v, why = _MP_VERDICT[cid]
    said = r['spoken'] or (r.get('heardInstead') or '—')
    route = 'FAQ ของร้าน (ไม่ผ่าน AI)' if r['route'] == 'faq/policy' else ('AI' if r['spoken'] else f'AI → ระบบตัด ({r.get("failReason")}) → พูดประโยคแทน')
    case = dict(
        id=cid, title=f'ผู้ชมพิมพ์ "{_c["q"]}" · ขณะพูดสคริปต์{_MP_ON[st_]}', prio='P1', level='ui',
        kind='happy', ui=True,
        pre=['รันกับ AI จริงบน UAT (โค้ด origin/uat 6e072387 · 8 ต.ค. 2569 20:22) · ใช้โค้ดตอบคอมเมนต์ตัวจริง ไม่ผ่านหน้าจอ',
             'รอบไลฟ์มีสินค้า 2 ตัว: รองเท้าแตะหัวโต + แมรี่เจน HP8075 (ข้อมูลสินค้าจริงจากคลังสินค้า UAT)',
             f'ขณะอวาตาร์กำลังพูดสคริปต์ของ{_MP_ON[st_]}'],
        steps=[f'ส่งคอมเมนต์ผู้ชมตาม Test Data ขณะอวาตาร์พูดสคริปต์ของ{_MP_ON[st_]}',
               'อ่านประโยคที่อวาตาร์พูด แล้วดูว่ากำกับชื่อสินค้าหรือไม่ และใช้ข้อมูลของสินค้าตัวไหนตอบ'],
        data=[f'คอมเมนต์: "{_c["q"]}"'],
        expected=['ควร: ' + _c['ok'], 'ห้าม: ' + _c['bad']],
        src='ที่มา: ทดสอบเพิ่ม 8 ต.ค. 2569 — หลัก QA: ถามข้อมูลเมื่อมีสินค้ามากกว่า 1 ตัว คำตอบต้องกำกับชื่อสินค้า และไม่เอาข้อมูลอีกตัวมาตอบ',
        note=None)
    _mp_feats.setdefault(st_, []).append(case)
    SEED_STORE[cid] = {'st': v, 'actual': f'AI พูด: {said}\nเส้นทาง: {route}\nผล: {_VTXT["warn" if v == "hold" else v]} — {why}'}
EPICS.append(dict(key='aiBmp', chip='🔀 ชุด B · หลายสินค้า', emoji='🔀',
                  title='ชุด B เพิ่ม · สินค้ามากกว่า 1 ตัว — ถามโดยไม่ระบุสินค้า / ระบุสินค้า / เทียบ (ทดสอบ 8 ต.ค. 2569)',
                  feats=[dict(featkey=f'aiBmp-{k.lower()}', title=f'ขณะพูดสคริปต์{_MP_ON[k]} ({len(v)} ข้อ)', cases=v)
                         for k, v in _mp_feats.items()]))
_ids = [c['id'] for e in EPICS for f in e['feats'] for c in f['cases']]
assert len(_ids) == len(set(_ids)), 'duplicate ids'
_N = {e['key']: sum(len(f['cases']) for f in e['feats']) for e in EPICS}

_skip = re.findall(r'ข้ามเพราะต้องไลฟ์จริง:\s*([^<]+)', _src)
# uid ตรึงตามลำดับข้อในต้นฉบับ (ชุด A ต่อด้วยชุด B) = ค่าเดิมของรายงานรวม (tc-14001…) — แยกไฟล์แล้วผลเทสไม่หลุด
UID_MAP = {cid: 14001 + n for n, cid in enumerate(_ids)}  # ลำดับต้นฉบับ A แล้ว B แล้ว MP (ต่อท้าย = 14150…) — uid เดิมไม่เลื่อน
_ALL_EPICS = EPICS
_FILES = {  # 1 ไฟล์ต่อ 1 ชุด (แยก 8 ต.ค. 2569 ตามคำขอ)
    'a': dict(set='A', slug='1script', name='1 สคริปต์ · 1 สินค้า (BP Coffee)'),
    'b': dict(set='B', slug='2scripts', name='2 สคริปต์ · 2 สินค้า (รองเท้า HP8009 + HP8075)'),
}


def out_rel(key):
    return f'projects/takra-ai/2026/10/reports/takra-ai-ai-comment-reply-results-2026-10-08-{_FILES[key]["slug"]}-test-cases-table.html'


def _meta(key):
    f = _FILES[key]
    k = f['set']
    i = ('A', 'B').index(k)
    n = _N[_SETS[k]['key']]
    return dict(
        out_rel=out_rel(key),
        title=f'ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 — {f["name"]} · ทดสอบผลของ AI (ไม่ผ่านหน้าจอ)',
        emoji=_SETS[k]['emoji'], uid_start=14001,
        download=f'takra-ai-ai-comment-reply-results-2026-10-08-{f["slug"]}.html',
        back=PAGES + '?project=ai',
        sub=(f'8 ต.ค. 2569 · AI จริงบน UAT · ข้อมูลสินค้าจริงจาก workspace QA · ใช้โค้ดตอบคอมเมนต์ตัวจริง ไม่ได้ไลฟ์ · '
             f'ชุด {k} · {_html.escape(_SET_INFO.get(k, [""])[0])} · {n} ข้อ · ผลตัดสินจากการอ่านคำตอบเทียบ ควร/ห้าม'),
        groups_label=f'ชุด {k} · {f["name"]}',
        note=_summary_html(key),
        footer=f'ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 · ชุด {k} · takra-ai · ไม่ผ่านหน้าจอ',
    )


# ── สรุปผลการทดสอบ (อยู่ในกล่องหมายเหตุด้านบนของรายงานแต่ละชุด · ไม่ทำไฟล์สรุปแยก — สั่ง 8 ต.ค. 2569) ──
# ตัวเลขเป็นผล ณ 8 ต.ค. 2569 หลังปรับผล 2 รอบ · ผลสดดูที่แถบ "สรุปผล" ของหน้า (คำนวณจาก store-data)
_TB = 'style="border-collapse:collapse;margin:6px 0 10px;font-size:12.5px;width:100%"'
_TH = 'style="text-align:left;padding:4px 8px;border-bottom:1px solid #d6dbe4;white-space:nowrap"'
_TD = 'style="padding:4px 8px;border-bottom:1px solid #eef1f5;vertical-align:top"'


def _tbl(head, rows):
    h = ''.join(f'<th {_TH}>{x}</th>' for x in head)
    r = ''.join('<tr>' + ''.join(f'<td {_TD}>{x}</td>' for x in row) + '</tr>' for row in rows)
    return f'<table {_TB}><thead><tr>{h}</tr></thead><tbody>{r}</tbody></table>'


_SUM = {
    'A': dict(
        res=('75', '69', '4', '2', '92.0%', 'A-GB-22 · 23 · 26 · 27 (ต้องไลฟ์จริง)'),
        fail=[('🔴 สูง', 'ระบบตัดคำตอบที่มีในข้อมูล', 'AI ตอบ 30 ซองถูก แต่ด่านขนาดดื่มตัดทิ้ง ผู้ชมได้ยิน "ยังไม่มีข้อมูล" ทั้งที่ FAQ "ในหนึ่งแพ็กมีกี่ซอง" ตอบไว้ 30 ซอง', 'A-C1-4'),
              ('🔴 สูง', 'ตัวอักษรขยะหลุดออกอากาศ', 'อักษรจีน "亚洲国产" · "&lt;&gt;" ต่อท้ายประโยค', 'A-NC-2 · A-GB-3'),
              ('🔴 สูง', 'FAQ ตอบผิดคำถาม', 'ถาม 3 เรื่อง (ชงยังไง · ส่งฟรีไหม · มีน้ำตาลไหม) ตอบจาก FAQ แค่เรื่องน้ำตาล', 'A-GB-19')],
        bug=[('🟠 กลาง', 'ประโยคที่ระบบพูดแทนลงท้าย "ค่ะ" เสมอ แม้ Graham ใช้ ผม/ครับ (เนื้อหาถูก จึงลง PASS)', 'A-C1-8 · A-C1-12 · A-GB-46 · A-GB-6 · A-GB-7 · A-GB-8 · A-GB-9 · A-GB-16 · A-GB-28 · A-GB-29')],
        hold=[('A-GB-11', 'ไม่แต่งข่าว แต่ถามกลับว่าอยากฟังข่าวด้านไหน แทนที่จะโยงกลับสินค้า'),
              ('A-GB-33', 'ลงท้ายครับถูก แต่ชมเองว่ากาแฟ "ลำขนาด สดชื่น" ซึ่งไม่มีในข้อมูล')],
        adj=['รอบ 1 · FAIL → PASS 10 ข้อ — เนื้อหาตรงข้อมูล พลาดแค่คำลงท้าย "ค่ะ" ของประโยคระบบ (A-GB-8 ต้องยืนยันว่าบทไม่มีโปร ถ้ามีให้กลับเป็น FAIL)',
             'รอบ 2 · A-C1-4 PASS → FAIL — FAQ กาแฟบอก 30 ซอง แต่ผู้ชมได้ยิน "ยังไม่มีข้อมูล"'],
        data=[('BP COFFEE (กาแฟ)', 'ฉบับร่าง · 3/4', '0 SKU (ไม่มีราคา) · ไม่มีวิธีชง รสชาติ คาเฟอีน ปริมาณดื่มต่อวัน · เลข อย. 90-1-06065-6-0005 มีแค่บนรูปซอง ไม่มีในข้อมูลตัวอักษร')],
    ),
    'B': dict(
        res=('74', '58', '13', '3', '78.4%', 'X-10 · G-56 · G-94 · G-95 · G-96 (ต้องไลฟ์จริง)'),
        fail=[('🔴 สูง', 'FAQ ตอบผิดคำถาม', 'คำถามที่มี "อะไรบ้าง" ได้ FAQ "มีสีอะไรบ้าง" ของแมรี่เจน → "กล้วย / ดำ / ซากุระ / โอวัลติน" แม้ถามไซซ์/ข่าว หรือรองเท้าหัวโตอยู่บนจอ — ทั้งที่แมรี่เจนมี FAQ "ขนาดสินค้า" อยู่แล้ว', 'P1-8 · P4-4 · X-7 · G-54 · G-69 · G-91-pre'),
              ('🔴 สูง', 'ระบบตัดคำตอบที่มีในข้อมูล', 'ตาราง FAQ "ขนาดสินค้า" ของรองเท้าหัวโตมี 24 ซม. = ไซซ์ 39 และ 37 = 23 ซม. แต่ด่านไซซ์ตัด ผู้ชมได้ยิน "ยังไม่มีข้อมูล"', 'P1-15 · G-132'),
              ('🔴 สูง', 'ตัวอักษรขยะหลุดออกอากาศ', 'อักษรคุชราต "રસ" "વરસાદ" · คำแปลก "เครดิตฟรี" ต่อท้ายประโยค', 'P1-9 · G-109 · G-122'),
              ('🟠 กลาง', 'ถามไซซ์ภาษาลาว/เขมร คำตอบถูกโดนตัดเป็นราคา', 'AI ตอบ "36 ถึง 40 ค่ะ" ถูก แต่ด่านราคามองเลขเป็นราคา ผู้ชมได้ยินให้ไปดูตะกร้าแทน', 'G-125 · G-127')],
        bug=[('🟢 ต่ำ', 'อวาตาร์ชายใช้กับสคริปต์เสียงหญิงได้โดยไม่เตือน — สคริปต์ตั้ง "เพศผู้พูด" หญิง Graham จึงพูด หนู/ค่ะ และยอมเปลี่ยนคำลงท้ายตามที่ผู้ชมสั่ง (ทำตามค่าที่ตั้ง จึงลง PASS)', 'G-2 · G-43 · G-114 · G-117 · G-120')],
        hold=[('P1-1', 'แนะนำการใช้งานเอง — ข้อมูลมีจุดเด่น "เหมาะสมกับทุกๆ สถานที่" ใกล้เคียง แต่ AI ไม่ได้อ้างตรง ๆ'),
              ('G-23', 'ระบบตัดเรื่องโปรแล้วชวนดูตะกร้า — ต้องเช็กว่าบทมีโปรหรือไม่'),
              ('G-61', 'เลี่ยงไม่บอกว่าเป็น AI ("ขอเป็นคนจริงในใจ") — ควรกำหนดนโยบายเปิดเผยว่าเป็น AI')],
        adj=['รอบ 1 · FAIL → PASS 6 ข้อ — G-2 · G-43 · G-114 · G-117 · G-120 (สคริปต์ตั้งเพศผู้พูดหญิง AI ทำตามค่าที่ตั้ง) · P4-3 (ข้อมูล "2 รุ่น" ไม่พอ)',
             'รอบ 2 · G-128 · G-131 FAIL → PASS (ตาราง FAQ 38 = 23.5 ซม. AI ตอบตรง ไม่ได้แต่ง) · X-2 HOLD → PASS (ชื่อสินค้าไม่มีรหัส HP8009 จริง) · P1-15 PASS → FAIL · G-132 HOLD → FAIL (ข้อมูลมีในตาราง แต่ระบบตัด)'],
        data=[('Hello Polo รองเท้าแตะหัวโต (HP8009)', 'เปิดใช้ · 3/4', 'FAQ มี 1 ข้อ (ตารางไซซ์) · ชื่อสินค้าไม่มีรหัส HP8009 · ไม่มีข้อมูลสี · ตารางไซซ์ยาวถึง 45 แต่ SKU ขาย 36-40 · เลือกหมวดไว้ครบ 12 หมวด'),
              ('Hello Polo แมรี่เจน HP8075', 'ฉบับร่าง · 4/4', '<b>ไซซ์ขัดกันเอง</b> — จุดเด่น/Claims/FAQ บอก 36–41 แต่ SKU บอก 36-40 · ยังเป็นฉบับร่าง · เลือกหมวดไว้ครบ 12 หมวด (ชุดคำเสี่ยงรวม 183 คำ รวมคำของอาหาร/อาหารเสริม)'),
              ('สคริปต์รองเท้าทั้งสอง', '—', 'ตั้ง "เพศผู้พูด" เป็นหญิง ทั้งที่ใช้อวาตาร์ Graham (ชาย)')],
    ),
}


_SHORT = {
    'A': dict(res='75 ข้อ · ✅ ผ่าน 69 · ❌ ไม่ผ่าน 4 · ⚠️ HOLD 2 · <b>92.0%</b> · ข้าม 4 (ต้องไลฟ์จริง)',
              fail=['ระบบตัดคำตอบที่มีในข้อมูล — FAQ บอก 30 ซอง แต่ผู้ชมได้ยิน "ยังไม่มีข้อมูล" (A-C1-4)',
                    'ตัวอักษรขยะหลุดออกอากาศ (A-NC-2 · A-GB-3)',
                    'FAQ ตอบผิดคำถาม — ถาม 3 เรื่อง ตอบแค่เรื่องเดียว (A-GB-19)'],
              bug='ประโยคระบบลงท้าย "ค่ะ" ตายตัว แม้อวาตาร์ชาย (10 ข้อ · ลง PASS เพราะเนื้อหาถูก)',
              data='กาแฟยังเป็นฉบับร่าง · 0 SKU · ไม่มีวิธีชง/คาเฟอีน · เลข อย. มีแค่บนรูป'),
    'B': dict(res='ชุดหลัก 74 ข้อ · ✅ 58 · ❌ 13 · ⚠️ HOLD 3 · <b>78.4%</b> · ข้าม 5 (ต้องไลฟ์จริง)'
                  '<br>🔀 <b>เพิ่ม: สินค้ามากกว่า 1 ตัว (MP)</b> 30 ข้อ · ✅ 18 · ❌ 11 · ⚠️ HOLD 1 · <b>60.0%</b> — '
                  'เส้นทาง AI กำกับชื่อสินค้าและเลือกตัวที่กำลังพูดถึงได้ถูก · เส้นทาง FAQ ไม่กำกับชื่อและไม่ดูว่าสินค้าตัวไหน: '
                  'ทุกคำถามที่มี "อะไรบ้าง" (8/8) ได้รายการสีของแมรี่เจน แม้ถาม "แมรี่เจนมีไซซ์" หรือ "รองเท้าหัวโตมีสี"',
              fail=['FAQ ตอบผิดคำถาม/ผิดสินค้า — ถามไซซ์แต่ได้รายการสี · ถามสีหัวโตแต่ได้สีแมรี่เจน (ชุดหลัก 6 · MP 6)',
                    'ระบบตัดคำตอบที่มีในข้อมูล — ตารางไซซ์มีใน FAQ แต่ผู้ชมได้ยิน "ยังไม่มีข้อมูล" (P1-15 · G-132 · MP-6-H · MP-6-M)',
                    'เทียบสองรุ่นไม่ครบ — ถามต่างกันยังไง พูดแค่รุ่นเดียว (MP-12-M)',
                    'ตัวอักษรขยะหลุดออกอากาศ (P1-9 · G-109 · G-122 · MP-12-H)',
                    'ถามไซซ์ภาษาลาว/เขมร คำตอบถูกโดนตัดเป็นราคา (G-125 · G-127)'],
              bug='สคริปต์ตั้งเพศผู้พูดหญิง Graham จึงพูด หนู/ค่ะ โดยไม่มีการเตือน (5 ข้อ · ลง PASS เพราะทำตามค่าที่ตั้ง)',
              data='แมรี่เจนไซซ์ขัดกัน (36–41 กับ SKU 36-40) · รองเท้าเลือกหมวดครบ 12 หมวด · หัวโตไม่มีรหัส HP8009'),
}


def _summary_html(key):
    k = _FILES[key]['set']
    d = _SHORT[k]
    other = 'b' if key == 'a' else 'a'
    return ('📋 <b>สรุปผล ชุด ' + k + ' · ' + _FILES[key]['name'] + '</b> — ' + d['res']
            + '<br>❌ <b>ปัญหาที่ยัง FAIL:</b><ul style="margin:2px 0 4px 18px;padding:0">'
            + ''.join(f'<li>{x}</li>' for x in d['fail']) + '</ul>'
            + '🐞 <b>บั๊กแม้ PASS:</b> ' + d['bug']
            + '<br>📦 <b>ข้อมูลสินค้าที่ต้องแก้:</b> ' + d['data']
            + '<br>✅ <b>QA:</b> 🟡 ยังไม่พร้อมใช้กับลูกค้า — แก้ปัญหาข้างบน + ข้อมูลสินค้า แล้วรันซ้ำ'
            + '<br><span style="opacity:.75">เกณฑ์: ข้อมูลไม่พอแต่ AI ไม่แต่ง = PASS · ข้อมูลมีแต่ผู้ชมได้คำตอบผิด = FAIL · คำที่ AI พูดและเหตุผลอยู่ในช่อง Actual · '
            + f'อีกชุด: <a href="{PAGES}{out_rel(other)}">{_FILES[other]["name"]}</a></span>')


META = None


def select(key):
    """build_hub_report.py เรียก select('a'|'b') ก่อนอ่าน EPICS/META — 1 ไฟล์ต่อ 1 ชุด"""
    global EPICS, META
    k = _FILES[key]['set']
    EPICS = [e for e in _ALL_EPICS if e['key'] in ({'aiA'} if k == 'A' else {'aiB', 'aiBmp'})]
    META = _meta(key)
