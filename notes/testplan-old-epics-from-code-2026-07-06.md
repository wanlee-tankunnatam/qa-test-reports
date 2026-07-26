# Test Plan — Epic เก่า (derive จากโค้ดจริง as-built)

**วันที่:** 2026-07-06 · **HEAD:** `d3a2e3c` · **branch:** develop
**หลักการ:** เคสทั้งหมด derive จาก **โค้ดจริง** ไม่ใช่ AC ใน epics.md (ซึ่งตกยุค) — เพื่อเติม/แก้ test plan เดิม `takra-rerun-app-test-cases-table.html` (07-02)
**ขอบเขต:** เฉพาะส่วน Epic เก่าที่ code เปลี่ยนหลัง 07-02 (Overlay, GMV, Chat, Basket, Accounts, Shop-console). Epic 10 (Telegram onboarding) แยกทำต่างหาก

**รวม ~129 เคส** · Priority: P0 = must, P1 = should, P2 = edge/nice

---

# 🎨 Overlay (TAK-152/165/166/167/168/169/175) — ~50 เคส

## A. Image library — delete guard (TAK-169) / workspace-shared (TAK-166)
| ID | Scenario | Steps → Expected (from code) | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-A1 | ลบรูปที่ layer (บัญชีใดก็ได้ใน ws) ใช้อยู่ | DELETE image → **409** `IMAGE_IN_USE`, msg "รูปนี้กำลังถูกใช้งานในโอเวอร์เลย์ของบัญชีอื่น…", `details.accounts=[{id,name}]`; row/object ไม่ถูกลบ | api | P0 | overlay_image_handler.go:192; overlayimg.go:341-389 |
| OV-A2 | ลบรูปที่ไม่มี layer ใช้ | DELETE → **204**; object ลบก่อน แล้ว row; quota คืน; audit ok | api | P0 | overlayimg.go:356-369 |
| OV-A3 | scan อ้างอิงทั้ง workspace (รูปใช้โดยบัญชี B, ลบผ่าน A) | DELETE ผ่าน A → 409, `accounts` ระบุ **B** | api | P0 | overlayimg.go:333-389 |
| OV-A4 | frame-clock bezel นับเป็น reference | รูปเป็น imageId ของ layer `clock/frame` → DELETE → 409 | api | P1 | overlayimg.go:372-411 |
| OV-A5 | layers JSON เสีย ไม่ปลดล็อกลบผิด | blob เสีย = "no ref" เฉพาะ blob นั้น; ref ที่ valid ยัง 409 (fail-closed) | api | P2 | overlayimg.go:391-411 |
| OV-A6 | ลบรูปข้าม tenant / ลบไปแล้ว | DELETE → **404** `IMAGE_NOT_FOUND` "ไม่พบรูปภาพนี้" | api | P1 | overlayimg.go:342 |
| OV-A7 | imgId ไม่ใช่ UUID | DELETE → **400** `INVALID_REQUEST` "รหัสรูปภาพไม่ถูกต้อง" | api | P1 | overlay_image_handler.go:167 |
| OV-A8 | storage backend ล่มตอนลบ (รูปไม่ถูกใช้) | → **503** `STORAGE_UNAVAILABLE`; row คงไว้ (retry ได้) | api | P2 | overlayimg.go:356 |

## B. Upload / quota (shared กับ videos + 3D models)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-B1 | อัปโหลดรูปสำเร็จ | POST multipart → **201** `{id,filename,mime,sizeBytes,url}` (ไม่มี object_key); size = bytes จริง; audit ok | api | P0 | overlayimg.go:273-295 |
| OV-B2 | ชนิดไฟล์ไม่รองรับ | .txt/.pdf → **400** `INVALID_IMAGE` "รองรับเฉพาะ PNG, JPG, WEBP, GIF" | api | P1 | overlayimg.go:218 |
| OV-B3 | เกิน per-file cap (32MiB) | → **413** `FILE_TOO_LARGE` + `details.limitBytes` (เช็คทั้ง declaredSize + post-stream) | api | P1 | overlayimg.go:223-260 |
| OV-B4 | โควตารวมเต็ม | → **403** `STORAGE_QUOTA_EXCEEDED` + `{usedBytes,limitBytes,remainingBytes}`; object cleanup ไม่ orphan | api | P0 | overlayimg.go:227-271 |
| OV-B5 | quota แชร์ video+image+model | อัปรูปที่พอดีเดี่ยวแต่รวมไม่พอ → 403 (usedBytes = SUM 3 ตาราง) | api | P0 | overlayimg.go:468-484 |
| OV-B6 | quota ≤ 0 = unlimited | ข้ามการเช็ค quota | api | P2 | overlayimg.go:486-494 |
| OV-B7 | non-multipart / ไม่มี file part | → **400** `INVALID_REQUEST` | api | P2 | overlay_image_handler.go:73 |
| OV-B8 | อัปโหลดไปบัญชีนอก ws | → **404** `ACCOUNT_NOT_FOUND` | api | P1 | overlayimg.go:214 |

## C. List / serve scoping
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-C1 | รูปมองเห็นข้ามบัญชีใน ws เดียว | A อัป → GET list ของ B **มี** รูปนั้น (scope by workspace_id, newest first) | api | P0 | overlay_images.sql.go:147 |
| OV-C2 | แยกขาดข้าม ws | รูป ws1 → GET/serve ผ่าน ws2 = ไม่เห็น / 404 | api | P0 | overlay_images.sql.go:34-67 |
| OV-C3 | serve bytes + header | GET → 200, Content-Type = mime, `Cache-Control: private, max-age=300` | api | P1 | overlay_image_handler.go:134 |
| OV-C4 | serve imgId ไม่ใช่ UUID | → 400 `INVALID_REQUEST` | api | P2 | overlay_image_handler.go:139 |
| OV-C5 | materialize go-live cross-account ใน ws | A render overlay อ้างรูปของ B → resolve ได้ (JOIN by workspace_id); นอก ws → skip layer | api | P1 | overlay_images.sql.go:69-94 |

## D. Layers persist + move (live)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-D1 | GET overlay บัญชีไม่มี layer | → 200 `{layers:[]}` | api | P1 | overlay_handler.go:42 |
| OV-D2 | PUT overlay save + echo | → 200 re-read; `layers:null`→`[]`; body >1MiB/invalid → 400 | api | P0 | overlay_handler.go:55-77 |
| OV-D3 | PUT บัญชีนอก ws | → 404 `ACCOUNT_NOT_FOUND` | api | P1 | service.go:116 |
| OV-D4 | move layer สด | POST move `{layerId,x,y}` → 204; px=round(x·w)+OffX; ส่ง zmq `name x`,`name y` (timeout 3s) | api | P1 | move.go:56-76 |
| OV-D5 | move ไม่มี overlay ขยับได้ / layer ไม่รู้จัก | → 404 `OVERLAY_UNAVAILABLE` | api | P1 | move.go:56-66 |
| OV-D6 | move session UUID เสีย / ไม่มี layerId | → 400 `INVALID_REQUEST` | api | P2 | overlay_handler.go:86 |
| OV-D7 | resolve ข้าม dead layer ตอน go-live | layer imageId ว่าง/ materialize fail/hidden → ข้าม, layer อื่นยัง build | api | P1 | service.go:148-193 |

## E. Editor — select / drag / clamp (TAK-165/168)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-E1 | คลิก/ลาก chip → เลือก layer + badge "กำลังแก้ไข" | selectedLayerId set; card `data-selected`; grip โผล่เฉพาะ layer ที่เลือก | ui | P1 | OverlayPanel.tsx:462-570 |
| OV-E2 | ลาก chip ย้ายตำแหน่ง | x,y = start + delta/frame, ปัด 2dp; slider/% ตามสด | ui | P1 | OverlayPanel.tsx:495-507 |
| OV-E3 | **clamp: far-edge อยู่ในเฟรม** | ลากไปมุมล่างขวาเกิน → x∈[0,1-w0], y∈[0,1-h0] (ทั้ง layer ไม่หลุด) | ui | P0 | OverlayPanel.tsx:465-507 |
| OV-E4 | clamp: layer ใหญ่กว่าเฟรม | w0>1/h0>1 → pin ที่ 0 (มุมบนซ้าย) | ui | P2 | OverlayPanel.tsx:500 |
| OV-E5 | arrow-nudge 0.01 / Shift 0.1 | โฟกัส chip + ลูกศร → ±0.01(0.1), clamp [0,1] **ธรรมดา (ไม่ใช่ far-edge)** | ui | P1 | OverlayPanel.tsx:532-544 |
| OV-E6 | position slider clamp 0..1 เท่านั้น | ดัน slider 100% → layer กว้างหลุดเฟรมบางส่วนได้ (ต่างจากลาก) | ui | P2 | OverlayPanel.tsx:1401-1414 |
| OV-E7 | เพิ่ม layer stagger กันซ้อน | เพิ่มซ้ำ → x=y=0.05,0.09,0.13…wrap .40 | ui | P2 | OverlayPanel.tsx:381 |

## F. Editor — resize grips
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-F1 | grip image/clock → resize W&H | drag SE → w/h = clamp [0.05,1] | ui | P0 | OverlayPanel.tsx:474-512 |
| OV-F2 | grip **text → fontSize** (ไม่ใช่ box) | drag ลง=ใหญ่ → fontSize [0.02,0.2] | ui | P0 | OverlayPanel.tsx:480-515 |
| OV-F3 | grip โผล่เฉพาะ layer ที่เลือก | `data-testid=overlay-resize-handle` เฉพาะ selected | ui | P1 | OverlayPanel.tsx:566-584 |
| OV-F4 | frame-clock corner warp quad | toggle ปรับตัวเลข/กรอบ + ลากมุม → warp quad (amber/blue), clamp [-0.3,1.3]; รีเซ็ตมุมคืน IDENT | ui | P1 | OverlayPanel.tsx:487-700 |

## G. Editor — reorder / z-order (TAK-167)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-G1 | list บนสุด = วาดบนสุด | render `layers.map().reverse()`; array back→front | ui | P1 | OverlayPanel.tsx:938 |
| OV-G2 | ▲/▼ สลับเพื่อนบ้าน | ▲=move(+1) หน้า, ▼=move(-1); disabled ที่ปลายสุด | ui | P1 | OverlayPanel.tsx:391-400 |
| OV-G3 | ลาก grip ⠿ จัดลำดับ (DnD) | drop → splice-move; indicator + ghost; no-op ถ้า from===to | ui | P2 | OverlayPanel.tsx:405-1016 |
| OV-G4 | ลำดับ array = z-order ที่ save | reorder + save → array order ส่ง backend ตรง | ui/api | P1 | OverlayPanel.tsx:940 |

## H. Editor — types / defaults / aspect refit (TAK-168)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-H1 | + ข้อความ | layer `{text:'ข้อความ',color:'ffffff',fontSize:0.05}` | ui | P2 | OverlayPanel.tsx:906 |
| OV-H2 | + นาฬิกา (digital LED) | `{w:0.5,h:digitalClockHeight,fontSize:0.92,format:HH:MM:SS,color:ff3b30}` | ui | P2 | OverlayPanel.tsx:912 |
| OV-H3 | + รูปภาพ (ว่าง) เปิด picker | `{imageId:'',w:0.25,h:0.25}`; chip แสดง "เลือกรูป" | ui | P1 | OverlayPanel.tsx:425 |
| OV-H4 | **เลือกรูป → refit H ตาม aspect จริง** | probe natWxH → h=aspectHeight clamp [0.05,1] (frame bezel ไม่ refit) | ui | P1 | OverlayPanel.tsx:1450; aspect.ts:16 |
| OV-H5 | เปลี่ยนแบบนาฬิกา seed default | frame/analog/digital → w/h/quad/format ต่างกัน | ui | P2 | OverlayPanel.tsx:342-373 |
| OV-H6 | digital clock: grip=box / slider=fontSize | ทั้งคู่ปรับได้คนละทาง | ui | P2 | OverlayPanel.tsx:705-746 |

## I. Editor — guide zones / save validation (TAK-175)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-I1 | guide zones เปิด default, toggle ได้ | 3 โซนแดง (บน 8%, ปุ่ม TikTok ขวา 15%×45%, คอมเมนต์ล่าง 24%); pointer-events-none; ไม่ส่ง render | ui | P2 | OverlayPanel.tsx:853-886 |
| OV-I2 | **save block เมื่อ image/frame layer ไม่มีรูป** | บันทึก → toast "มีเลเยอร์ที่ยังไม่ได้เลือกรูป"; ไม่ยิง PUT | ui | P0 | OverlayPanel.tsx:782-795 |
| OV-I3 | save สำเร็จ | PUT → toast "บันทึกโอเวอร์เลย์แล้ว ✓"; onSaved(); กัน double-save | ui | P1 | OverlayPanel.tsx:782-802 |
| OV-I4 | ลบรูปจากคลัง → เคลียร์ imageId ใน layer (คง box) | layer imageId===X → set '' (re-pick ได้; go-live ไม่ render) | ui | P1 | OverlayPanel.tsx:432-436 |
| OV-I5 | seed จาก server ตอนโหลด | draft seeded จาก server (guard data!==seededFrom) | ui | P2 | OverlayPanel.tsx:330 |

## J. Image picker dialog — in-use guard UI (TAK-169)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-J1 | ลบรูปที่ layer บัญชีนี้ใช้ (local) | คลิก X → ไม่ยิง network; toast "ลบไม่ได้ — รูปกำลังถูกใช้งาน" + badge "ใช้อยู่" | ui | P1 | OverlayImagePickerDialog.tsx:64-160 |
| OV-J2 | ลบรูปที่ local ไม่ได้ใช้ | คลิก X → `confirm("ลบ '…' ออกจากคลัง?")` → DELETE → onDeleted | ui | P1 | OverlayImagePickerDialog.tsx:79 |
| OV-J3 | ลบแล้ว backend 409 (บัญชีอื่นใช้) | toast "บัญชีที่ยังใช้รูปนี้: A, B — นำรูปออก…" (จาก err.accounts) | ui | P0 | OverlayImagePickerDialog.tsx:84-101 |
| OV-J4 | ลบได้ 404 = สำเร็จ (idempotent) | 204 หรือ 404 → resolve success, drop จาก cache | api/ui | P2 | use-overlay-images.ts:122 |
| OV-J5 | คลิก thumbnail → เพิ่ม layer + ปิด dialog | onPick(id) → set imageId + refit (image) | ui | P1 | OverlayImagePickerDialog.tsx:144 |
| OV-J6 | upload จาก picker | accept png/jpeg/webp/gif ≤32MB; error → Thai toast | ui | P2 | OverlayImagePickerDialog.tsx:116 |

## K. 3D model / frame bezel
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| OV-K1 | อัป .glb auto-select เมื่อยังไม่มี | success → set modelId (ถ้ายังไม่มี) ไม่งั้น toast ให้เลือกเอง | ui | P2 | OverlayPanel.tsx:1478 |
| OV-K2 | snapshot 3D → bezel PNG + persist pose | หมุน→snapshot→อัปเป็น image; imgQuad IDENT; view persist; backend Resolve ไม่สน modelId/view | ui | P2 | OverlayPanel.tsx:1500-1522 |

---

# 💰 GMV (TAK-153) — 11 เคส
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| GMV-1 | ยอดขายสด 2 ทศนิยม | totalGmv=84.99 → แสดง `฿84.99` (ไม่ปัด ฿85) | ui | P0 | GmvPanel.tsx:8-32 |
| GMV-2 | parse เฉพาะ segments[0] | มีหลาย segment → นับ seg[0] เท่านั้น (ไม่ double-count) | api | P0 | gmv.go:203-225 |
| GMV-3 | counts เป็น string ไม่พังทั้ง response | sales="12" ฯลฯ → unmarshal สำเร็จ, Units=12 | api | P0 | gmv.go:179-240 |
| GMV-4 | count ว่าง/แปลงไม่ได้ → 0 | sales="" → 0 | api | P1 | gmv.go:231-240 |
| GMV-5 | count ทศนิยม string "10.0" | → 10 (ตัดเศษ) | api | P2 | gmv.go:235 |
| GMV-6 | GMV=0 / segments ว่าง | code 0, seg=[] → `฿0.00`, ขาย 0, สินค้า 0, ไม่มี top | api/ui | P1 | gmv.go:199-201 |
| GMV-7 | code≠0 (cookie หมด) | คืน nil,nil → ไม่ publish → panel คงค่าเดิม | api | P1 | gmv.go:196-198 |
| GMV-8 | currency symbol จาก payload | currency_symbol="$" → นำหน้า `$` | api | P2 | gmv.go:214-215 |
| GMV-9 | top 5 อันดับ เรียง GMV | >5 products → 5 ตัว, tie-break Units | api | P2 | gmv.go:243-260 |
| GMV-10 | top ชื่อว่าง | name="" → แสดง `—` | ui | P2 | GmvPanel.tsx:40 |
| GMV-11 | GMV อัปเดตแม้ปิดหน้าต่าง oracle | ปิด oracle, รอ poll → ยังอัปเดต (cookie in-memory) | e2e | P1 | gmv.go:87-125 |

---

# 💬 Chat emote (TAK-154) — 10 เคส
> **พฤติกรรมสุดท้าย** (46ba35f ทับ 4fb349a): มีรูป→รูป, ไม่มีรูป→**raw `[code]` ไม่ใช่ emoji**
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| CHAT-1 | มี emote image → แสดงรูป | emotes=[{placeholder:"[hi]",url}] → `<img h-5 w-5 alt="[hi]">` | ui | P0 | chat-emotes.ts:30; LiveChatPanel.tsx:89 |
| CHAT-2 | ไม่มีรูป → raw code (ไม่ใช่ glyph) | "[wow]" ไม่มี key → แสดง `[wow]` ดิบ (ไม่มี 😮) | ui | P0 | chat-emotes.ts:21-37 |
| CHAT-3 | ไม่มี emote data → ข้อความคงเดิม | emotes=undefined → text token เดียว | ui/api | P1 | chat-emotes.ts:21 |
| CHAT-4 | entry ไม่มี url | "[hi]" คงเป็น text ดิบ | ui/api | P1 | chat-emotes.ts:24 |
| CHAT-5 | รูปโหลดพัง (url ตาย) | onError → fallback `[hi]` เป็นข้อความ (ไม่ใช่รูปเสีย) | ui | P1 | LiveChatPanel.tsx:20-30 |
| CHAT-6 | หลาย emote + text ปน | "[hi] เธอ [wow]" → img,text,img เรียงถูก | ui | P2 | chat-emotes.ts:27 |
| CHAT-7 | placeholder ไม่ใช่ emote | "[ลด50%]" คงเป็น text | ui/api | P2 | chat-emotes.ts:32 |
| CHAT-8 | oracle จับคู่ url กับ bracket | extractEmotes → {placeholder,url} ใช้ emoteImageUrl ก่อน | api | P1 | oracle.js:138-163 |
| CHAT-9 | oracle: 1 emote ไม่มี index | ใช้ bracket เดียวในข้อความ | api | P2 | oracle.js:168 |
| CHAT-10 | E2E: emote ไหล oracle→SSE→chat | คอมเมนต์ emote จริง → เว็บแสดงรูป; ถ้า oracle ไม่ได้ url → `[code]` ดิบ | e2e | P1 | oracle.js:118; LiveChatPanel.tsx:89 |

---

# 🛒 ปักตะกร้า / Basket (TAK-186) — 7 เคส
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| BSK-1 | เลือกทั้งหมด | คลิก → PUT selected:true เฉพาะที่ยังไม่เลือก (ทุกชุด); flip ทุก checkbox; label→"เอาออกทั้งหมด"; busy disable | e2e | P1 | BasketPanel.tsx:74-102 |
| BSK-2 | เอาออกทั้งหมด | allSelected → คลิก → PUT selected:false ต่อตัว; label→"เลือกทั้งหมด" | e2e | P1 | BasketPanel.tsx:79 |
| BSK-3 | indeterminate (บางส่วน) | 0<sel<all → กล่อง primary + Minus, checked=false | ui | P2 | BasketPanel.tsx:34-99 |
| BSK-4 | **import ใหม่ = ไม่ถูกเลือก default** | import สำเร็จ → ทุก Selected=false; หัว "เลือกทั้งหมด" | api | P0 | basket/service.go (Selected:false) |
| BSK-5 | thumbnail ต่อแถว | มี image → `<img size-10>`; ว่าง/พัง → 📦 fallback | ui | P2 | BasketPanel.tsx:131; product-thumb.tsx |
| BSK-6 | toggle รายตัว optimistic | PUT ตัวเดียว; cache อัปเฉพาะตัวนั้น; busy disable | e2e | P1 | BasketPanel.tsx:117 |
| BSK-7 | ปุ่ม import ไม่โผล่บน browser | ไม่มี takraDesktop → empty state "เปิดบนแอป desktop…", ไม่มีปุ่ม | ui | P2 | BasketPanel.tsx:20-151 |

---

# 👤 บัญชีไลฟ์ / Accounts — 22 เคส

## Unsaved-changes guard (TAK-185)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| ACC-1 | เตือนก่อนสลับแท็บขณะ dirty | แก้จน dirty → คลิกแท็บอื่น → เก็บ pendingTab, เปิด UnsavedChangesDialog | e2e | P0 | AccountDetailPage.tsx:122-350 |
| ACC-2 | "ออกโดยไม่บันทึก" | ทิ้ง draft (setDirty false) + สลับ pendingTab | ui | P1 | AccountDetailPage.tsx:133 |
| ACC-3 | "อยู่ต่อ" / Esc / backdrop | คงแท็บเดิม + draft ยังอยู่; blocker.reset() | ui | P1 | AccountDetailPage.tsx:142 |
| ACC-4 | เตือนตอนนำทางออก (sidebar/back) ขณะ dirty | useBlocker → guardOpen; proceed/reset | e2e | P0 | AccountDetailPage.tsx:116-144 |
| ACC-5 | เตือนเนทีฟตอนปิด/รีโหลด | beforeUnload=()=>dirty → prompt เนทีฟ | e2e | P2 | AccountDetailPage.tsx:118 |
| ACC-6 | ไม่เตือนเมื่อไม่มี draft | dirty=false → สลับ/ออกทันที | ui | P1 | AccountDetailPage.tsx:123 |

## Upload video in wizard (TAK-187)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| ACC-7 | อัปวิดีโอใน step "เลือกวิดีโอ" ตอนคลังว่าง | กด "อัปโหลดวิดีโอ" → UploadVideoDialog; สำเร็จ → invalidate → grid รีเฟรชเอง | e2e | P0 | VideoTab.tsx:89-106 |
| ACC-8 | ปุ่มอัปเหนือ grid เมื่อมีวิดีโอแล้ว | ปุ่ม outline เปิด dialog เดียวกัน | ui | P1 | VideoTab.tsx:110-123 |
| ACC-9 | ครอบ 3 surface (wizard/detail/LiveSettings) | ทุก surface มีปุ่ม (แก้ที่ VideoTab จุดเดียว) | ui | P2 | VideoTab.tsx:96-121 |

## Takra Hub link on banner (TAK-188)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| ACC-10 | banner lapsed + มี hubUrl | `<a target=_blank>` "ต่ออายุแพ็กเกจที่ Takra Hub" + ExternalLink (entitlement-hub-link) | ui | P0 | EntitlementBanner.tsx:35-66 |
| ACC-11 | banner none + hubUrl | CTA "สมัครแพ็กเกจที่ Takra Hub" | ui | P1 | EntitlementBanner.tsx:69 |
| ACC-12 | hubUrl ไม่ตั้ง → ไม่มีลิงก์ตาย | ไม่มี `<a>`; span fallback "ติดต่อผู้ดูแล…" | ui | P1 | EntitlementBanner.tsx:32; hub-link.ts:10 |
| ACC-13 | ลิงก์เปิด system browser (desktop) | คลิก → เปิดเบราว์เซอร์ระบบ | e2e | P2 | EntitlementBanner.tsx:36 |
| ACC-14 | ไม่แสดง banner ตอน active/loading | คืน null | ui | P2 | EntitlementBanner.tsx:85 |

## Display name / @username (TAK-137)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| ACC-15 | การ์ด/หัวแสดงชื่อ TikTok ไม่ใช่ host | name??nickname??uniqueId??host → แสดง nickname (ไม่โชว์ webcast.tiktok.com) | ui | P0 | account-display.tsx:18 |
| ACC-16 | บรรทัด @handle | มี uniqueId→`@id`; ไม่มี→`@—` | ui | P2 | AccountCard.tsx:86 |
| ACC-17 | ชื่อคงเส้นคงวาทุก surface | การ์ด/detail/dialog ใช้ accountDisplayName() เหมือนกัน | ui | P1 | account-display.tsx:18 |

## Edit dialog aligned to TikTok login (TAK-139)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| ACC-18 | dialog แก้ไขไม่มี curl textarea | desktop → ปุ่ม TikTok "เข้าสู่ระบบด้วย TikTok อีกครั้ง" (edit-account-relogin) | ui | P0 | EditAccountDialog.tsx:150-171 |
| ACC-19 | reconnect: capture curl → PATCH (curl write-only) | login สำเร็จ → mutate {id,curl,name?}; status→unverified; bindOracleSession; curl ไม่ render | e2e | P0 | EditAccountDialog.tsx:91-121 |
| ACC-20 | บน browser ทำได้แค่ rename | ไม่มี addViaLogin → โน้ต "ต้องทำบนแอป desktop" | ui | P1 | EditAccountDialog.tsx:51-179 |
| ACC-21 | บันทึกเปิดเฉพาะเมื่อชื่อเปลี่ยน | nameChanged; ล้างว่าง=เปลี่ยน(→NULL); PATCH name-only คง cookie | ui | P1 | EditAccountDialog.tsx:58-194 |
| ACC-22 | error ล้างเมื่อเริ่มพิมพ์ | พิมพ์ → reset()/setLoginError(null) | ui | P2 | EditAccountDialog.tsx:63-186 |

---

# 🛍️ Shop console fallback (TAK-178) — 29 เคส
> **หมายเหตุ:** มี **AC7** (cookie หมด→ปิด popup+toast+เด้ง /accounts) ที่ implement แล้ว · return protocol **4 แบบ**: `{ok:true}` / `{ok:false,loggedOut}` / `{ok:false,closed}` (เงียบ) / `{ok:false,error}`

## Visibility / gating (AC1/AC2)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| SHOP-1 | desktop+live+resolvable → ปุ่มข้าง หยุดไลฟ์ | 2 ปุ่มใน session-header-actions; Shop ซ้ายของ หยุดไลฟ์ | ui | P0 | SessionDetailPage.tsx:179 |
| SHOP-2 | provisioning ก็แสดง | gate = live‖provisioning | ui | P0 | SessionDetailPage.tsx:179 |
| SHOP-3 | web (no bridge) → ปุ่มหาย, stop ปกติ | takraDesktop undefined → slot ไม่ mount | ui | P0 | SessionDetailPage.tsx:181 |
| SHOP-4 | bridge มีแต่ไม่มี method | openShopConsole undefined → null | ui | P1 | ShopConsoleButton.tsx:15 |
| SHOP-5 | non-live/terminal → หาย | ทุก state ที่ไม่ใช่ live/provisioning ซ่อน (allowlist) | ui | P0 | SessionDetailPage.tsx:179 |
| SHOP-6 | accountId resolve ไม่ได้ → หาย, stop คงอยู่ | reverse-lookup null → ไม่ render | ui | P0 | SessionDetailPage.tsx:35 |

## Click → popup + toasts (AC3/AC7)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| SHOP-7 | happy → เปิด dashboard เป็นบัญชีนั้น + desync toast | openShopConsole(accountId) 1 ครั้ง; ok → toast "เปิดหน้า TikTok Shop แล้ว"; ไม่ navigate | ui | P0 | ShopConsoleButton.tsx:18-28 |
| SHOP-8 | popup URL/partition/hardened | dashboard URL, `partition:persist:tt-<id>`, contextIsolation+sandbox, no preload | e2e | P0 | tiktok-login.js:49-106 |
| SHOP-9 | ปุ่ม disable ระหว่าง in-flight | spinner; re-enable ใน finally | ui | P1 | ShopConsoleButton.tsx:53 |
| SHOP-10 | cookie หมด → popup ปิดเอง + toast + เด้ง /accounts | {ok:false,loggedOut} → toast "Session TikTok หมดอายุ" + navigate | ui | P1 | ShopConsoleButton.tsx:29-37 |
| SHOP-11 | login-marker nav → main ปิด popup, loggedOut | did-navigate ไป login host+path → destroy | e2e | P1 | tiktok-login.js:63-158 |
| SHOP-12 | SPA in-page bounce → ปิด + loggedOut | did-navigate-in-page → เหมือนกัน | e2e | P1 | tiktok-login.js:159 |
| SHOP-13 | login-ish **query param** ไม่ใช่ bounce | `?enter_from=login` → ok, popup อยู่ต่อ (match host+path) | e2e | P1 | tiktok-login.js:64 |
| SHOP-14 | loadURL fail → error toast, no nav | {ok:false,error} → toast "เปิดหน้า TikTok Shop ไม่สำเร็จ" | ui/e2e | P1 | ShopConsoleButton.tsx:38-46 |
| SHOP-15 | bridge reject → toast, ไม่ crash | catch → toast String(e) | ui | P2 | ShopConsoleButton.tsx:47 |
| SHOP-16 | ปิด popup ก่อน settle → เงียบ | {ok:false,closed} → ไม่ toast/nav; ปุ่ม re-enable | ui | P2 | ShopConsoleButton.tsx:38 |

## Multi-account isolation (AC4)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| SHOP-17 | 2 บัญชี live → 2 หน้าต่าง partition แยก | persist:tt-acc-a vs -b; cookie ไม่ปน | e2e | P0 | tiktok-login.js:86-106 |
| SHOP-18 | title pin ต่อบัญชี | page-title-updated → preventDefault คง title | e2e | P2 | tiktok-login.js:110 |
| SHOP-19 | child window.open → system browser | deny + shell.openExternal | e2e | P2 | tiktok-login.js:120 |
| SHOP-20 | accountId เพี้ยน → reject ที่ IPC | ''/'ไทย'/42/null → {ok:false,'bad accountId'}; ไม่สร้างหน้าต่าง | e2e | P1 | tiktok-login.js:83 |

## Focus / no-duplicate (AC5)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| SHOP-21 | คลิกซ้ำขณะเปิด → focus เดิม ไม่ซ้ำ | focus() ครั้งเดียว; {ok:true} | e2e | P1 | tiktok-login.js:87-98 |
| SHOP-22 | คลิกซ้ำตอน minimize → restore+focus | restore()→focus() | e2e | P2 | tiktok-login.js:91 |
| SHOP-23 | ปิดแล้วเปิดใหม่ → หน้าต่างใหม่ | 'closed' ลบ registry → สร้างใหม่ | e2e | P1 | tiktok-login.js:139 |
| SHOP-24 | renderer crash → destroy ไม่ zombie | render-process-gone → destroy+clear | e2e | P2 | tiktok-login.js:113 |
| SHOP-25 | invoke พร้อมกันตอน nav แรก → share ผล | 1 หน้าต่าง; ทั้งคู่ได้ผลเดียวกัน | e2e | P2 | tiktok-login.js:94 |
| SHOP-26 | login bounce หลัง settle → self-heal | ปิด popup; คลิกถัดไป bounce ทันที → loggedOut | e2e | P2 | tiktok-login.js:145 |

## Oracle safety (AC6)
| ID | Scenario | Steps → Expected | Lvl | Pri | Ref |
|---|---|---|---|---|---|
| SHOP-27 | **ไม่ลง webRequest** จาก path นี้ | oracle chat/GMV/basket ยังทำงาน (0 onSendHeaders calls) | e2e | P0 | tiktok-login.js:82-179 |
| SHOP-28 | redirect-abort หลัง commit ดี → swallow | latch กลืน late reject; popup อยู่, {ok:true} | e2e | P2 | tiktok-login.js:129-171 |
| SHOP-29 | IPC channel ลงทะเบียนครบ | `tiktok:openShopConsole` handle มี | e2e | P1 | tiktok-login.js:34 |

---

## ⚠️ จุดที่ code ต่างจาก doc/spec (ต้องบันทึกให้ลีด)
1. **Overlay**: clamp ตอน**ลาก** = far-edge อยู่ในเฟรม แต่ **arrow-nudge + slider** ใช้ clamp 0..1 ธรรมดา → layer กว้างดันหลุดเฟรมได้ผ่าน slider (พฤติกรรมไม่สมมาตร — ยืนยันว่า by design หรือ bug)
2. **Shop console**: มี AC7 (cookie expiry) + return `{ok:false,closed:true}` (ปิดเงียบ) ที่ spec ไม่ครบ; `ACCOUNT_ID_RE` กว้างกว่า comment ("UUIDs only" แต่รับ `acc-1`)
3. **GMV**: parse `segments[0]` เท่านั้น (ไม่ sum ทุก segment) — ถ้า TikTok ใส่ยอดใน segment อื่นจะไม่ถูกนับ (ยืนยันว่าตรง POC จริง)
4. **Chat emote**: fallback emoji ถูกลบ (46ba35f) — ถ้าเทสเก่าคาดหวัง emoji จะ fail; ต้องคาดหวัง raw `[code]`

## หมายเหตุ e2e
Overlay (go-live/move), Shop console, Chat pipeline, upload — หลายเคสเป็น **e2e ที่ต้อง desktop + live จริง** ยังไม่เคยรัน live end-to-end (media re-encode + desktop bridge)
