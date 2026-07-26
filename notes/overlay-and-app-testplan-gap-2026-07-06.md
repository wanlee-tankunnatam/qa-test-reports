# Test Plan Gap Analysis — takra-rerun (as of 2026-07-06)

**เทียบ:** test plan เดิม `takra-rerun-app-test-cases-table.html` (2026-07-02 17:30, อ้าง ticket สูงสุด TAK-150)
**กับ:** code ปัจจุบัน HEAD `d3a2e3c` (2026-07-06) — ~25 commits หลัง test plan

**สรุปสั้น:** ไม่ต้องเขียนใหม่ทั้งไฟล์ — โครง 17 หมวดคงเดิม ~60%. ต้อง **แก้ 6 หมวดเดิม + เพิ่ม 2 หมวดใหม่ + ทวนเคสเดิมที่ behavior เปลี่ยน**

---

## A. หมวดเดิม — ต้องเพิ่ม/แก้เคส

### 🎨 Overlay (เดิม 6 เคส) — กระทบมากสุด
| ticket | เคสที่ต้องทำ | +/แก้ |
|---|---|---|
| TAK-166 | อัปโหลดรูปที่ account A → ปรากฏในคลังของ account B (workspace-shared) | + |
| TAK-166 | quota นับรวม workspace (image + video + 3D-model ใช้ budget เดียว) | + |
| TAK-169 | ลบรูปที่ layer กำลังอ้างอยู่ → block, 409 `IMAGE_IN_USE` + รายชื่อ account | + |
| TAK-169 | ลบรูปที่ไม่มี layer อ้าง → สำเร็จ | + |
| TAK-168 | คลิก card/chip → layer ถูกเลือก (highlight) | + |
| TAK-168 | ลาก chip บน preview → ตำแหน่งเปลี่ยน | + |
| TAK-168 | resize grip มุม (box) / grip scale fontSize (text) | + |
| TAK-168 | ลูกศร nudge ตำแหน่ง (shift = step ใหญ่) | + |
| TAK-168 | aspect refit ตาม dimension จริงของคลิป | + |
| TAK-165/167/175/133/140 | guide zones (ไม่บังสินค้า/ตะกร้า), clamp (ลากไม่หลุดเฟรม), reorder z-order, baseline text | + |

### 💰 GMV (เดิม 4)
| TAK-153 | แสดง GMV 2 ทศนิยม ตรง TikTok Seller Center | แก้ |
| TAK-153 | parse จาก segments[0] เท่านั้น + tolerant string counts | + |

### 💬 Chat (เดิม 5)
| TAK-154 | chat แสดง emote เป็นรูป | + |
| TAK-154 | ไม่มีรูป emote → แสดง raw code (ไม่ใช่ unicode-glyph fallback) | + |

### 🛒 ปักตะกร้า (เดิม 6)
| TAK-186 | select-all toggle | + |
| TAK-186 | row thumbnails | + |
| TAK-186 | default import = unselected | แก้ |

### 👤 บัญชีไลฟ์ (เดิม 10)
| TAK-185 | เตือนก่อนออกหน้า account detail เมื่อมี unsaved changes | + |
| TAK-187 | อัปโหลดวิดีโอ in-place จาก wizard step "เลือกวิดีโอ" | + |
| TAK-188 | banner lapsed/none → link ไป Takra Hub | + |
| TAK-137 | แสดง display name/@username แทน host | ทวน |
| TAK-139 | edit-account dialog ตรงกับ TikTok login flow | ทวน |

### ⚙️ ตั้งค่า / 📡 Live Settings / UI
| TAK-189 | Logs tab, AUTO 2-col + H/M/S, wizard order, delete redirect, ไลฟ์ layout | + |
| TAK-173 | EmptyState unify + card/tab constants + heading normalize | ทวน UI |
| TAK-146 | empty-state copy ตรง context ของแต่ละหน้า | ทวน |

---

## B. หมวดใหม่ — ยังไม่มีใน test plan เลย

### 📲 Telegram Guided Onboarding (Epic 10) — ใหม่ทั้งหมด
> เดิมมีเทสต์ Telegram config (Story 5.4 / expert form) แต่ flow onboarding แบบ guided ยังไม่ครอบ
| TAK-180/181 (10.1) | guided bot wizard — create-new / retrieve-existing token | + |
| TAK-182 (10.2) | auto chat_id discovery + manual fallback | + |
| TAK-184 (10.3) | change bot / change chat / relink — no-drop, test-gated | + |
| TAK-106 | แยกข้อความ Telegram "test" ออกจาก "link" | + |

### 🛍️ Shop Console Fallback (TAK-178) — grep เดิม 0 เคส
| AC1 | desktop bridge + session live/provisioning → ปุ่ม "จัดการใน TikTok Shop" ข้าง "หยุดไลฟ์" | + |
| AC2 | web (no bridge) หรือ session non-live/terminal → ปุ่มหายไป | + |
| AC3 | คลิก → popup เปิด live-product dashboard เป็น account นั้น + desync toast | + |
| AC4 | ≥2 account live คนละ session → popup แยก partition, cookie ไม่ปน | + |
| AC5 | popup เปิดอยู่ คลิกซ้ำ → focus หน้าต่างเดิม ไม่เปิดซ้ำ | + |
| AC6 | popup เปิดอยู่ → oracle listener ยังทำงาน (ไม่มี webRequest, webPreferences hardened) | + |

---

## C. หมวดที่ไม่กระทบ (คงเดิม)
🔐 Auth · 🔑 Login · 🔌 Proxy · 🔊 Audio · 🔄 Full Flow · ↩️ Reply · ⚡ Edge Cases

---

## ประเมินงาน
- **เพิ่มใหม่ ~25 เคส** (overlay 10, GMV 2, chat 2, basket 3, accounts 3, UI 1, telegram 4, shop 6)
- **ทวน/แก้เคสเดิม ~6 เคส** (TAK-133/137/139/140/146/173)
- **โครง 7 หมวดไม่แตะ**
- ⚠️ หมายเหตุ: overlay + telegram + shop-console หลายเคสเป็น e2e ที่ต้อง **live-verify จริง** (ffmpeg re-encode / desktop bridge) — ยังไม่เคยรัน live end-to-end
