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


_skip = re.findall(r'ข้ามเพราะต้องไลฟ์จริง:\s*([^<]+)', _src)
# uid ตรึงตามลำดับข้อในต้นฉบับ (ชุด A ต่อด้วยชุด B) = ค่าเดิมของรายงานรวม (tc-14001…) — แยกไฟล์แล้วผลเทสไม่หลุด
UID_MAP = {cid: 14001 + n for n, cid in enumerate(_ids)}
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


def _summary_html(key):
    k = _FILES[key]['set']
    d = _SUM[k]
    other = 'b' if key == 'a' else 'a'
    r = d['res']
    out = ('📋 <b>สรุปผลการทดสอบ — ชุด ' + k + ' · ' + _FILES[key]['name'] + '</b> (ณ 8 ต.ค. 2569 · ตัดสินเทียบข้อมูลสินค้าจริงบน UAT แล้ว)'
           '<br><span style="opacity:.85">ทดสอบผลของ AI ตอบคอมเมนต์ (ไม่ผ่านหน้าจอ) — ส่งคอมเมนต์เข้าโค้ดตอบคอมเมนต์ตัวจริงบน UAT ด้วย AI จริงและข้อมูลสินค้าจริง แล้วอ่านคำที่ AI พูดเทียบ "ควร / ห้าม" และข้อมูลในคลังสินค้า · '
           'สถานะ: ✅ PASS · ❌ FAIL · ⚠️ HOLD (ก้ำกึ่ง ควรดูเอง) · คำที่ AI พูดและเหตุผลอยู่ในช่อง Actual</span>'
           + _tbl(['ข้อ', '✅ ผ่าน', '❌ ไม่ผ่าน', '⚠️ HOLD', '% ผ่าน', 'ข้าม'], [r])
           + '<b>❌ ปัญหาที่ยัง FAIL</b> — ไม่เกี่ยวกับข้อมูลน้อย ระบบส่งสิ่งที่ผิดไปถึงผู้ชม'
           + _tbl(['ความรุนแรง', 'ปัญหา', 'รายละเอียด', 'รหัสข้อ'], d['fail'])
           + '<b>🐞 บั๊กที่พบแม้ผล PASS</b>' + _tbl(['ความรุนแรง', 'ปัญหา', 'รหัสข้อ'], d['bug'])
           + '<b>⚠️ HOLD — ควรตัดสินร่วมกับ PO/BA</b>' + _tbl(['รหัส', 'เหตุผล'], d['hold'])
           + '<b>⚖️ เกณฑ์ตัดสินและการปรับผล</b> — ข้อมูลไม่พอ และ AI ไม่ได้แต่ง (ตอบตรงว่าไม่มีข้อมูล) = PASS · ข้อมูลมีอยู่ แต่ผู้ชมได้คำตอบผิด/ได้ยินว่าไม่มีข้อมูล/ได้ยินตัวอักษรขยะ = FAIL'
           + '<ul style="margin:4px 0 10px 18px;padding:0">' + ''.join(f'<li>{x}</li>' for x in d['adj']) + '</ul>'
           + '<b>📦 ข้อมูลสินค้าที่ต้องแก้ก่อนรันซ้ำ</b>' + _tbl(['สินค้า', 'สถานะ', 'สิ่งที่ต้องแก้'], d['data'])
           + '<b>✅ QA Recommendation — 🟡 ยังไม่พร้อมเปิดใช้กับลูกค้า</b>'
             '<ul style="margin:4px 0 10px 18px;padding:0">'
             '<li>แจ้ง DEV แก้ความรุนแรงสูง: FAQ ตอบผิดคำถาม · ระบบตัดคำตอบที่มีในข้อมูล (ด่านไซซ์/ด่านขนาดดื่มต้องอ่าน FAQ และตารางไซซ์ด้วย) · ตัวอักษรขยะหลุดออกอากาศ</li>'
             '<li>แจ้ง DEV ความรุนแรงกลาง/ต่ำ: ด่านราคาตัดคำตอบไซซ์ภาษาลาว/เขมร · ประโยคระบบลงท้าย "ค่ะ" ตายตัว · อวาตาร์ชายกับสคริปต์เสียงหญิงไม่มีการเตือน</li>'
             '<li>ให้ PO/BA ตัดสินข้อ HOLD (นโยบายเปิดเผยว่าเป็น AI) และยืนยันโปรในบท</li>'
             '<li>แก้ข้อมูลสินค้าตามตารางข้างบน แล้วรันซ้ำ · เปิดสวิตช์ AI ตอบคอมเมนต์ของ workspace QA บน UAT (ตอนนี้ปิดอยู่) แล้วเทสข้อที่ต้องไลฟ์จริง</li></ul>'
           + f'📎 อีกชุด: <a href="{PAGES}{out_rel(other)}">{_FILES[other]["name"]}</a>'
           + ' · ต้นฉบับ: <code>tools/build/ai-comment-results-sources/2026-10-08.html</code>')
    return out


META = None


def select(key):
    """build_hub_report.py เรียก select('a'|'b') ก่อนอ่าน EPICS/META — 1 ไฟล์ต่อ 1 ชุด"""
    global EPICS, META
    k = _FILES[key]['set']
    EPICS = [e for e in _ALL_EPICS if e['key'] == _SETS[k]['key']]
    META = _meta(key)
