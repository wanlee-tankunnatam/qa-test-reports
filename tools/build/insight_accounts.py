"""บัญชีทดสอบของรายงาน TAKRA Insight (env UAT) — ไม่เก็บรหัสผ่าน

ผู้ใช้สร้างบัญชีจริงแล้ว 23 ก.ย. 2569: แยกบัญชีละบทบาท จึงไม่ต้องสลับบทบาทเองอีก
บัญชีชุดนี้ใช้ทั้งเทสมือและสคริปต์ E2E บน UAT

ใช้:  from insight_accounts import apply_accounts   แล้วเรียก apply_accounts(EPICS) ท้ายไฟล์ cases
ผลที่ได้: ทุกเคสมีบรรทัด "บัญชีที่ใช้ (UAT): <อีเมล> · บทบาท …" ในส่วน Test Data
"""
import re

ENV = 'UAT'

OWNER = 'qa.owner@realfactory.co.th'      # เจ้าของ ทีม A
BM = 'qa.bm@realfactory.co.th'            # ผู้จัดการแบรนด์ ทีม A
HOST_A = 'qa.hosta@realfactory.co.th'     # โฮสต์ ทีม A (ตั้ง key ครบ · มีไลฟ์ + รายงาน)
HOST_B = 'qa.hostb@realfactory.co.th'     # โฮสต์ ทีม A (ยังไม่ตั้ง key จึงไม่มีรายงาน)
MULTI = 'qa.multi@realfactory.co.th'      # เจ้าของทีม B + โฮสต์ทีม A (เคสสลับพื้นที่ทำงาน)

# เรียงตามความจำเพาะ — เจอกฎแรกที่ตรงแล้วหยุด
ACCOUNT_RULES = [
    (MULTI,  'เจ้าของทีม B + โฮสต์ทีม A', r'\bMULTI\b|2 พื้นที่ทำงาน|≥ 2 ทีม|อยู่ 2 ทีม|สลับพื้นที่ทำงาน'),
    (BM,     'ผู้จัดการแบรนด์',            r'บัญชี BM\b|ผู้จัดการแบรนด์'),
    (HOST_A, 'โฮสต์',                     r'บัญชี HOST\b|บัญชีโฮสต์|เป็น "โฮสต์"|บทบาท "โฮสต์"'),
    (OWNER,  'เจ้าของ',                   r'บัญชี OWNER\b|บัญชีเจ้าของ|เป็น "เจ้าของ"|บทบาท "เจ้าของ"|ที่เป็น "เจ้าของ"'),
]
DEFAULT = (OWNER, 'เจ้าของ')

# เคสที่ต้องมีโฮสต์อีกคนที่ยังไม่ตั้ง key ร่วมด้วย — เติมบรรทัดบัญชีประกอบ
SECOND_HOST = r'โฮสต์ B|โฮสต์อีกคน|โฮสต์ที่ยังไม่|ยังไม่เคยบันทึก key|โฮสต์ 2 คน|โฮสต์สองคน'


def account_of(case):
    """(อีเมล, บทบาท) ที่เคสนี้ใช้ล็อกอิน — ดู step แรก (ขั้นเข้าสู่ระบบ) ก่อน แล้วค่อยดูที่เหลือ"""
    steps = case.get('steps') or []
    for txt in ([steps[0]] if steps else []) + [' '.join(steps[1:] + (case.get('pre') or []))]:
        for email, role, pat in ACCOUNT_RULES:
            if re.search(pat, txt):
                return email, role
    return DEFAULT


def apply_accounts(EPICS):
    for ep in EPICS:
        for feat in ep['feats']:
            for c in feat['cases']:
                email, role = account_of(c)
                lines = [f'บัญชีที่ใช้ ({ENV}): {email} · บทบาท "{role}"']
                text = ' '.join(c.get('steps', []) + (c.get('pre') or []) + [c.get('title', '')])
                if re.search(SECOND_HOST, text) and email != HOST_B:
                    lines.append(f'บัญชีประกอบ: {HOST_B} — โฮสต์ที่ยังไม่ตั้ง key '
                                 '(เตรียมไว้เป็นข้อมูลเปรียบเทียบ ไม่ต้องล็อกอิน)')
                data = [d for d in (c.get('data') or []) if 'บัญชีที่ใช้' not in d]
                c['data'] = lines + data
    return EPICS
