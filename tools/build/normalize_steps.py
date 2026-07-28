#!/usr/bin/env python3
"""ปรับ Test Steps ทุกเคสให้เป็นแบบ Steps to Reproduce — เริ่มจากเปิดแอป → ล็อกอิน → ไปที่เมนู

หลักการ:
  · step ชุดเปิด (เปิดแอป · ล็อกอิน · นำทาง) อยู่ใน Test Steps เสมอ ไม่ฝากไว้ใน Precondition
  · Precondition เหลือเฉพาะของที่ต้องเตรียม (บัญชี/ไฟล์/ข้อมูล/สภาพแวดล้อม)
  · step แรกเดิมที่เป็น login ล้วนถูกแทนด้วยชุดเปิดมาตรฐาน · prefix "เข้าสู่ระบบ แล้ว…" ถูกตัดเหลือส่วนนำทาง
  · เคสที่ไม่มี step นำทางเลย เติมเส้นทางเมนูตามหมวด (NAV ด้านล่าง)

ไม่แตะ: เคสหลายเครื่อง (มี "เครื่องที่ 2"/"อีกเครื่อง" — ลำดับ login ต่อเครื่องเป็นสาระของเคส)
        · war-room (เป็นเว็บ central เขียนถูกแล้ว) · fullflow (โครง Run sheet/Phase)
        · เคสที่ step ทดสอบการเปิดแอป/ล็อกอินเอง (sign-in) ได้เฉพาะ step เปิดแอป

ใช้:  python3 tools/build/normalize_steps.py <report.html> --os "Windows" [--check]
"""
import argparse
import pathlib
import re
import sys

# ── เส้นทางเมนูตามหมวด (ตรวจกับ UI จริงใน web/src แล้ว) ใช้เมื่อเคสไม่มี step นำทาง ──
# เมนูข้าง: บัญชีไลฟ์ · คลังวิดีโอ · สรุปไลฟ์ย้อนหลัง · ระบบ & ตั้งค่า (แท็บ ระบบ/Workspace/Telegram/Logs)
# แท็บในหน้าบัญชี (ปุ่ม ⚙️ ตั้งค่าบัญชี): ไลฟ์ · วิดีโอ · โอเวอร์เลย์ · ตะกร้าสินค้า · ตารางปัก · AUTO · ถามตอบ · พร็อกซี
ACC = ['ไปที่เมนู "บัญชีไลฟ์"', 'เลือกบัญชีไลฟ์ที่ต้องการ']
def _tab(name):
    return ACC + [f'เปิดแท็บ "{name}"']
NAV = {
    'account-crud':          ['ไปที่เมนู "บัญชีไลฟ์"'],
    'create-room':           ['ไปที่เมนู "บัญชีไลฟ์"'],
    'auto-mode':             _tab('AUTO'),
    'telegram':              ['ไปที่เมนู "ระบบ & ตั้งค่า"', 'เปิดแท็บ "Telegram"'],
    'playlist-crud':         ['ไปที่เมนู "คลังวิดีโอ"', 'สลับไปแท็บ "เพลย์ลิสต์"'],
    'overlay-brand':         _tab('โอเวอร์เลย์'),
    'overlay-per-clip':      _tab('โอเวอร์เลย์'),
    'pin-timeline':          _tab('ตารางปัก'),
    'pin-countdown':         _tab('ตารางปัก'),
    'playlist-bind':         _tab('วิดีโอ'),   # ช่อง เพลย์ลิสต์ที่ออกอากาศ อยู่บนแท็บ วิดีโอ (VideoTab)
    'pin-match-confirm':     ['ไปที่เมนู "บัญชีไลฟ์"'],
    'single-active-lock':    ['ไปที่เมนู "บัญชีไลฟ์"'],
    'authority-availability': ['ไปที่เมนู "บัญชีไลฟ์"'],
    'pin-auto-live':         ['ไปที่เมนู "บัญชีไลฟ์"'],
    'playlist-rotation':     ['ไปที่เมนู "บัญชีไลฟ์"'],
    'auto-chat-reply':       _tab('AUTO'),
    'qa-keyword-reply':      _tab('ถามตอบ'),
    'proxy':                 _tab('พร็อกซี'),
    'cloud-files':           ['ไปที่เมนู "คลังวิดีโอ"'],
    'error-card':            ['ไปที่เมนู "บัญชีไลฟ์"'],
    'session-analytics':     ['ไปที่เมนู "สรุปไลฟ์ย้อนหลัง"'],
    'desktop-local':         None,
    'version-update':        None,
}
# ชุด step เปิดที่เวอร์ชันก่อนเคยฉีดไว้ — ถอนออกก่อนเมื่อรันซ้ำ (idempotent)
_ACC_OLD = 'ไปที่เมนู "บัญชีไลฟ์" แล้วเปิดบัญชีที่ต้องการ (ปุ่ม ⚙️ ตั้งค่าบัญชี)'
OLD_INJECTED = {
    _ACC_OLD,
    _ACC_OLD + ' แล้วเปิดแท็บ "AUTO"', _ACC_OLD + ' แล้วเปิดแท็บ "โอเวอร์เลย์"',
    _ACC_OLD + ' แล้วเปิดแท็บ "ตารางปัก"', _ACC_OLD + ' แล้วเปิดแท็บ "ไลฟ์"',
    _ACC_OLD + ' แล้วเปิดแท็บ "ถามตอบ"',
    'ไปที่เมนู "ระบบ & ตั้งค่า" แล้วเปิดแท็บ "Telegram"',
    'ไปที่เมนู "คลังวิดีโอ" แล้วสลับไปแท็บ "เพลย์ลิสต์"',
}
LOGIN_STEP = 'ล็อกอินด้วยบัญชี UAT ที่มีแพ็กเกจใช้งานอยู่'
# step นำทางที่มี " แล้ว" ต่อ action → แตกเป็นคนละ step (ตามตัวอย่าง Steps to Reproduce)
NAV_START = re.compile(r'^(ไปที่|เปิดเมนู|เปิดแท็บ|สลับไป|เปิดหน้า|กดเมนู)')
NAV_SPLIT = re.compile(r'(?<=") (?:แล้ว)?(?=(?:กด|เปิด|สลับไป|เลือก|ไปที่|เข้า|ดู|อ่าน|จด))')
CHECK_LEAD = re.compile(r'^(ดู|อ่าน|ตรวจ|สังเกต|เทียบ|เฝ้าดู|นับ|ฟัง)')
# หมายเหตุ: โหมดปัจจุบันแตะเฉพาะ Test Steps — Precondition ไม่แก้แล้ว (คำสั่งทีม 2026-07-28)


def _split_nav(step):
    st = step.strip()
    if not NAV_START.match(st):
        return [st]
    return [x.strip() for x in NAV_SPLIT.split(st) if x.strip()]


# แก้ชื่อเมนู/หน้าที่เคสเก่าอ้างแต่ไม่มีจริงใน UI (ตรวจกับ nav-config + AccountDetailPage แล้ว)
BODY_FIXES = [
    ('เมนู "ห้องคุมไลฟ์"', 'เมนู "บัญชีไลฟ์"'),          # ไม่มีเมนูนี้ — ห้องคุมไลฟ์เข้าจากการ์ดบัญชี
    ('ไปที่ หน้าหลัก (บัญชีไลฟ์)', 'ไปที่เมนู "บัญชีไลฟ์"'),
    ('เมนู "ถามตอบ"', 'แท็บ "ถามตอบ"'),                  # ถามตอบเป็นแท็บในหน้าบัญชี
    ('ไปที่เมนูตั้งค่า → แท็บ "บอท Telegram"', 'ไปที่เมนู "ระบบ & ตั้งค่า" แล้วเปิดแท็บ "Telegram"'),
    ('ไปที่เมนูตั้งค่า → แท็บ "ระบบ"', 'ไปที่เมนู "ระบบ & ตั้งค่า" แล้วเปิดแท็บ "ระบบ"'),
    ('ไปที่เมนูตั้งค่า → "บันทึกการทำงาน" (Audit)', 'ไปที่เมนู "ระบบ & ตั้งค่า" แล้วเปิดแท็บ "Logs" (บันทึกการทำงาน)'),
    ('ไปที่เมนูตั้งค่า/เกี่ยวกับแอป', 'ไปที่เมนู "ระบบ & ตั้งค่า" แล้วเปิดแท็บ "ระบบ"'),
    ('ไปที่เมนูตั้งค่า', 'ไปที่เมนู "ระบบ & ตั้งค่า"'),
    ('ไปที่เมนู "คลังวิดีโอ" แล้วกด "สร้างเพลย์ลิสต์ใหม่"',
     'ไปที่เมนู "คลังวิดีโอ" แล้วสลับไปแท็บ "เพลย์ลิสต์" แล้วกด "สร้างเพลย์ลิสต์ใหม่"'),
]
SKIP_FEATS = {'war-room', 'fullflow', 'device-portability'}
SIGNIN_FEATS = {None, 'sign-in'}          # เคสที่การล็อกอินคือสิ่งที่เทส

# step แรกที่เป็น login ล้วน → แทนด้วยชุดเปิดมาตรฐาน
PURE_LOGIN = re.compile(
    r'^(เข้าสู่ระบบด้วยบัญชีทดสอบ|เข้าสู่ระบบบนแอปเดสก์ท็อป|เข้าแอปหลังล็อกอิน|เข้าสู่ระบบ)$')
# prefix login นำหน้า step นำทาง → ตัดเหลือส่วนนำทาง
LOGIN_PREFIX = re.compile(
    r'^เข้าสู่ระบบ(ด้วยบัญชีทดสอบ|ด้วยบัญชี UAT)? แล้ว')
# สัญญาณว่า step เป็นการนำทาง/มีบริบทหน้าแล้ว
HAS_NAV = re.compile(r'เมนู|แท็บ|หน้า|เปิดบัญชี|คลิกเข้าไป|ไปที่|เปิดการตั้งค่า|ที่การ์ด')
MULTI = re.compile(r'เครื่องที่ 2|อีกเครื่อง|ทั้งสองเครื่อง|ทั้ง 2 เครื่อง|เครื่อง A|เครื่อง B')
# Precondition ที่เป็น state เปิดแอป/ล็อกอิน (ไม่ใช่ของที่ต้องเตรียม)
PRE_BOILER = re.compile(
    r'^(เปิดแอป Takra Rerun บนเครื่อง แล้วล็อกอินด้วยบัญชี UAT ที่มีแพ็กเกจใช้งานอยู่'
    r'|เปิดแอป Takra Rerun และล็อกอินด้วยบัญชี UAT แล้ว'
    r'|ล็อกอินเข้าแอปแล้ว|ล็อกอินเข้าแอป|เข้าสู่ระบบแล้ว'
    r'|เปิดแอป Takra Rerun บนเครื่อง|เปิดเมนู "?คลังวิดีโอ"?|เปิดเมนู "?บัญชีไลฟ์"?'
    r'|เปิดเมนู "คลังวิดีโอ" แล้วเลื่อนลงมาที่ส่วน "เพลย์ลิสต์.*)$')
PRE_UAT = 'มีบัญชี UAT ที่มีแพ็กเกจใช้งานอยู่'


# หมวดจาก prefix ของ TC id — ใช้แทน featrow ของไฟล์ซึ่งเพี้ยนตำแหน่ง (ตรวจแล้ว)
CID_FEAT = [
    ('TC-E2E', 'fullflow'), ('TC-WR', 'war-room'), ('TC-HH6', 'device-portability'),
    ('TC-HH', 'cloud-files'), ('TC-Z7b', 'pin-countdown'), ('TC-Z7c', 'pin-match-confirm'),
    ('TC-O5b', 'pin-timeline'), ('TC-Z1', 'playlist-crud'), ('TC-Z2', 'playlist-crud'),
    ('TC-Z3', 'playlist-bind'), ('TC-Z8', 'playlist-crud'), ('TC-Z4', 'playlist-rotation'),
    ('TC-BB', 'overlay-brand'), ('TC-MC', 'pin-match-confirm'),
    ('TC-R1', 'proxy'), ('TC-R2', 'proxy'),
    ('TC-FF', 'single-active-lock'), ('TC-AU', 'authority-availability'),
    ('TC-PIN', 'pin-auto-live'), ('TC-AA', 'playlist-rotation'), ('TC-X', 'playlist-rotation'),
    ('TC-Q4', 'auto-chat-reply'), ('TC-Q6', 'qa-keyword-reply'),
    ('TC-JJ', 'error-card'), ('TC-DD', 'version-update'),
    ('TC-SA', 'session-analytics'), ('TC-WS2', 'session-analytics'), ('TC-M4', 'cloud-files'),
    ('M1-A', 'sign-in'), ('M1-B', 'account-crud'), ('M1-C', 'cloud-files'),
    ('M1-D', 'create-room'), ('M1-G', 'desktop-local'),
    # M1-E/M1-F คร่อมสองหมวด (auto/telegram · audit/version) — ใช้ featrow เดิมซึ่งถูกอยู่แล้ว
]


def cid_feat(cid, fallback):
    for p, k in CID_FEAT:
        if cid.startswith(p):
            return k
    return fallback


def _fix(x):
    for old, new in BODY_FIXES:
        x = x.replace(old, new)
    return x


def normalize_case(featkey, cid, steps, pres, os_label):
    """คืน (steps ใหม่, pres ใหม่, เหตุผลถ้าข้าม)"""
    featkey = cid_feat(cid, featkey)
    if featkey in SKIP_FEATS or cid.startswith('TC-E2E'):
        return None, None, 'โครงพิเศษ — ข้าม'
    if any(MULTI.search(x) for x in steps):
        return None, None, 'หลายเครื่อง — ข้าม (รีวิวมือ)'

    s1 = f'เปิด TAKRA Rerun ({os_label})'
    body = list(steps)
    # ถอนชุดเปิดที่เวอร์ชันก่อนฉีดไว้ (รันซ้ำได้)
    while body and (body[0].strip() in OLD_INJECTED
                    or body[0].strip() == s1 or body[0].strip() == LOGIN_STEP):
        body.pop(0)
    if featkey in SIGNIN_FEATS:
        opening = [s1]
        # การล็อกอินคือตัวเทส — ตัดเฉพาะ step เปิดแอปที่ซ้ำ
        if body and re.match(r'^เปิดแอป(เดสก์ท็อป)?( Takra Rerun)?(จากไอคอน)?$', body[0].strip()):
            body.pop(0)
        body = [_fix(x) for x in body]
    else:
        opening = [s1, LOGIN_STEP]
        # ตัด step login ล้วนที่นำหน้า (ซ้ำกับชุดเปิด)
        while body and PURE_LOGIN.match(body[0].strip()):
            body.pop(0)
        # ตัด prefix "เข้าสู่ระบบ แล้ว…" ของ step ถัดมา
        if body:
            body[0] = LOGIN_PREFIX.sub('', body[0].strip()) or body[0]
        # แก้ชื่อเมนูที่ไม่มีจริงใน UI
        body = [_fix(x) for x in body]
        # ไม่มี step นำทางเลย → เติมเส้นทางเมนูของหมวด (step ละบรรทัด)
        nav = NAV.get(featkey)
        head = ' '.join(body[:2])
        already = nav and [x.strip() for x in body[:len(nav)]] == nav
        if nav and not already and not HAS_NAV.search(head):
            opening.extend(nav)
        elif body and body[0].strip().startswith('เปิดบัญชีไลฟ์'):
            # body นำทางเข้าบัญชีเองแต่ข้ามขั้นเมนู — เติมเมนูให้ครบเส้นทาง
            opening.append('ไปที่เมนู "บัญชีไลฟ์"')
    # แตก step นำทางที่รวบหลาย action ให้เป็นคนละบรรทัด
    body = [y for x in body for y in _split_nav(x)]
    # ปิดท้ายด้วยการตรวจผล ถ้า step สุดท้ายยังเป็น action
    if body and not CHECK_LEAD.match(body[-1].strip()):
        body.append('ตรวจสอบผลลัพธ์')

    # ขอบเขตปัจจุบัน: แตะเฉพาะ Test Steps — Precondition คืนของเดิมเสมอ
    return opening + body, list(pres), None


def run(path, os_label, check):
    src = path.read_text(encoding='utf-8')
    parts = re.split(r'(?=<tr class=")', src)
    featkey, cid = None, None
    changed, skipped = [], []
    for i, b in enumerate(parts):
        m = re.search(r'class="featrow" data-featkey="([^"]+)"', b)
        if m:
            featkey = m.group(1)
            continue
        if b.startswith('<tr class="trow'):
            c = re.search(r'<td class="cid">([^<]*)</td>', b)
            cid = c.group(1).strip() if c else None
            continue
        if not b.startswith('<tr class="detail') or not cid:
            continue
        st = re.search(r'(<h4>Test Steps</h4><ol>)(.*?)(</ol>)', b, re.S)
        pre = re.search(r'(<h4>Precondition</h4><ul>)(.*?)(</ul>)', b, re.S)
        if not st or not pre:
            continue
        steps = re.findall(r'<li>(.*?)</li>', st.group(2), re.S)
        pres = re.findall(r'<li>(.*?)</li>', pre.group(2), re.S)
        if not steps:
            continue
        new_steps, new_pres, why = normalize_case(featkey, cid, steps, pres, os_label)
        if why:
            skipped.append((cid, why))
            cid = None
            continue
        nb = b.replace(st.group(0), st.group(1) + ''.join(f'<li>{x}</li>' for x in new_steps) + st.group(3))
        nb = nb.replace(pre.group(0), pre.group(1) + ''.join(f'<li>{x}</li>' for x in new_pres) + pre.group(3))
        if nb != b:
            parts[i] = nb
            changed.append(cid)
        cid = None
    if not check:
        path.write_text(''.join(parts), encoding='utf-8')
    return changed, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report')
    ap.add_argument('--os', default='Windows')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    p = pathlib.Path(a.report)
    changed, skipped = run(p, a.os, a.check)
    tag = '(ลองดู)' if a.check else 'เขียนแล้ว'
    print(f'{p.name}: {tag} ปรับ {len(changed)} เคส · ข้าม {len(skipped)}')
    import collections
    for why, n in collections.Counter(w for _, w in skipped).items():
        print(f'  ข้าม {n:3} — {why}: {", ".join(c for c, w in skipped if w == why)[:150]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
