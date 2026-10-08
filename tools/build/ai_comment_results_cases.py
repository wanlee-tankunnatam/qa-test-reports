#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 (takra-ai) — ทดสอบ "ผลของ AI" ไม่ผ่านหน้าจอ · จัดเป็นรายงานหน้าตาเดียวกับรายงาน regression

ต้นฉบับ: tools/build/ai-comment-results-sources/2026-10-08.html (หน้าผลทดสอบที่ QA ทำมา · ชุด A/B · ตารางทุกข้อ + ปัญหาที่เจอ)
โมดูลนี้อ่านตารางจากต้นฉบับ → EPICS (ชุด A/B) · feats (กลุ่มตามรหัสข้อ) · 1 แถว = 1 ข้อ
ผลที่ตัดสินไว้ในต้นฉบับ (ผ่าน/ไม่ผ่าน/ก้ำกึ่ง + คำที่ AI พูด) ถูก seed ลง store-data ครั้งแรกเท่านั้น (SEED_STORE) —
หลังจากนั้นเป็นข้อมูลของรายงาน (auto-save) build ซ้ำไม่ทับ
build: python3 tools/build/build_hub_report.py aicomment
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
META = dict(
    out_rel='projects/takra-ai/2026/10/reports/takra-ai-ai-comment-reply-results-2026-10-08-test-cases-table.html',
    title='ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 — ทดสอบผลของ AI (ไม่ผ่านหน้าจอ)',
    emoji='🤖', uid_start=14001,
    download='takra-ai-ai-comment-reply-results-2026-10-08.html',
    back=PAGES + '?project=ai',
    sub=(f'8 ต.ค. 2569 · AI จริงบน UAT · ข้อมูลสินค้าจริงจาก workspace QA · ใช้โค้ดตอบคอมเมนต์ตัวจริง ไม่ได้ไลฟ์ · '
         f'ชุด A {_N.get("aiA", 0)} ข้อ + ชุด B {_N.get("aiB", 0)} ข้อ = {sum(_N.values())} ข้อ · ผลตัดสินจากการอ่านคำตอบเทียบ ควร/ห้าม'),
    groups_label='ชุด A (1 สคริปต์ · BP Coffee) · ชุด B (2 สคริปต์ · รองเท้า HP8009 + HP8075)',
    note=('🤖 <b>ทดสอบผลของ AI ตอบคอมเมนต์ (ไม่ผ่านหน้าจอ)</b> — ส่งคอมเมนต์เข้าโค้ดตอบคอมเมนต์ตัวจริงบน UAT ด้วยข้อมูลสินค้าจริง แล้วอ่านคำที่ AI พูดเทียบ "ควร / ห้าม" · '
          'สถานะ: ✅ ผ่าน = <b>PASS</b> · ❌ ไม่ผ่าน = <b>FAIL</b> · ⚠️ ก้ำกึ่ง (ไม่ผิดชัด แต่ควรดูเอง/ข้อมูลสินค้าขาด) = <b>HOLD</b> · คำที่ AI พูดอยู่ในช่อง Actual'
          '<br>⚠️ สวิตช์ AI ตอบคอมเมนต์ของ workspace QA บน UAT ปิดอยู่ ถ้าไลฟ์จริงตอนนี้จะไม่มีคำตอบเลย'
          + ''.join(f'<br><br><b>{_SETS[k]["chip"]} — {_html.escape(" · ".join(_SET_INFO.get(k, [])[:2]))}</b>'
                    + (f' · ข้ามเพราะต้องไลฟ์จริง: {_html.escape(_skip[i].strip())}' if i < len(_skip) else '')
                    + '<br>ปัญหาที่เจอในชุดนี้:' + _issues_html(k) for i, k in enumerate(('A', 'B')))
          + '📎 ต้นฉบับ: <code>tools/build/ai-comment-results-sources/2026-10-08.html</code>'),
    footer='ผลทดสอบ AI ตอบคอมเมนต์ 8 ต.ค. 2569 · takra-ai · ไม่ผ่านหน้าจอ',
)
