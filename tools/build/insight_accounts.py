"""บัญชีทดสอบของรายงาน TAKRA Insight (env UAT) — ไม่เก็บรหัสผ่าน

ผู้ใช้กำหนด 23 ก.ย. 2569: ทุกเคสใช้บัญชีเดียวกัน แล้ว "สลับบทบาท" เอาเองก่อนเริ่มทดสอบ
(บทบาทผูกกับพื้นที่ทำงาน/ทีม — บัญชีเดียวเป็นได้ทั้งเจ้าของ · ผู้จัดการแบรนด์ · โฮสต์ ตามทีมที่เลือกอยู่)

ใช้:  from insight_accounts import apply_accounts   แล้วเรียก apply_accounts(EPICS) ท้ายไฟล์ cases
ผลที่ได้ต่อเคส
  • Test Data มีบรรทัด  บัญชีที่ใช้ (UAT): <อีเมล> · บทบาท "…"
  • เคสที่ต้องใช้บทบาทเฉพาะ จะมี step สลับพื้นที่ทำงาน/บทบาท แทรกหลัง step เข้าสู่ระบบ
"""
import re

ENV = 'UAT'
ACCT = 'wanleeta.official@gmail.com'

# บทบาทในแอป (คำจริงจาก i18n/th.js) → คีย์ที่ใช้จับในบท step
ROLE_PATTERNS = [
    ('ผู้จัดการแบรนด์', r'บัญชี BM\b|ผู้จัดการแบรนด์'),
    ('โฮสต์',           r'บัญชี HOST\b|บัญชีโฮสต์|เป็น "โฮสต์"|บทบาท "โฮสต์"'),
    ('เจ้าของ',         r'บัญชี OWNER\b|บัญชีเจ้าของ|เป็น "เจ้าของ"|บทบาท "เจ้าของ"|ที่เป็น "เจ้าของ"'),
]

SWITCH = ('ก่อนเริ่มทดสอบ ให้สลับบทบาทของบัญชีนี้ก่อน: กดรูปโปรไฟล์มุมล่างซ้าย ("โปรไฟล์และบัญชี") '
          'ดูส่วน "พื้นที่ทำงาน" แล้วกดชื่อทีมที่บัญชีนี้มีบทบาท "{role}" '
          '(ถ้าทีมที่ใช้อยู่เป็นบทบาทนี้อยู่แล้ว ข้ามขั้นนี้)')


# ── เคสที่ตกลงว่า "ไม่ทดสอบ" เพราะต้องสมัคร/เชิญบัญชีใหม่ทุกครั้ง (ผู้ใช้กำหนด 23 ก.ย. 2569) ──
NO_TEST = {
    'TC-RPT-A.1', 'TC-MEM-C.3', 'TC-MEM-C.4',
    'TC-MEM-E.1', 'TC-MEM-E.2', 'TC-MEM-E.3', 'TC-MEM-E.4', 'TC-MEM-E.5',
}
NO_TEST_FLAG = '🚫 ไม่ทดสอบในรอบนี้ — เคสนี้ต้องสมัคร/เชิญบัญชีใหม่ทุกครั้งที่เทสซ้ำ'


def role_of(case):
    """บทบาทที่เคสต้องใช้ — ดูจาก step แรก (ขั้นเข้าสู่ระบบ) ก่อน แล้วค่อยดู Precondition"""
    steps = case.get('steps') or []
    for txt in ([steps[0]] if steps else []) + [' '.join(steps[1:] + (case.get('pre') or []))]:
        for role, pat in ROLE_PATTERNS:
            if re.search(pat, txt):
                return role
    return None


def apply_accounts(EPICS):
    for ep in EPICS:
        for feat in ep['feats']:
            for c in feat['cases']:
                role = role_of(c)
                line = f'บัญชีที่ใช้ ({ENV}): {ACCT}' + (f' · บทบาท "{role}"' if role else '')
                data = list(c.get('data') or [])
                if not any(ACCT in d for d in data):
                    data.insert(0, line)
                c['data'] = data
                if c['id'] in NO_TEST:
                    c['flag'] = NO_TEST_FLAG
                steps = list(c.get('steps') or [])
                if role and steps and not any('สลับบทบาท' in s for s in steps):
                    steps.insert(1, SWITCH.format(role=role))
                    c['steps'] = steps
    return EPICS
