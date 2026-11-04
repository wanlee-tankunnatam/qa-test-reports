"""Decode what the app actually put on the wire to api.telegram.org.

The tap recorded each request body verbatim and forwarded it unchanged, so this is the message
Telegram received, not a reconstruction. Both halves of TC-AUD-D.1's line-1 claim are checked
here: the <b> tags AND parse_mode, because tags without parse_mode=HTML render literally.

usage: python -I -X utf8 show_outbox.py <telegram-outbox.json>
"""
import io
import json
import re
import sys
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

records = json.load(open(sys.argv[1], encoding="utf-8"))
print(f"records captured: {len(records)}")

for r in records:
    print("=" * 72)
    print(f"method={r.get('method')}  http={r.get('status')}  at={r.get('at')}")
    body = r.get("body") or ""
    # main sends JSON; fall back to form encoding if a build ever changes that
    try:
        fields = {k: [v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)]
                  for k, v in json.loads(body).items()}
    except Exception:
        fields = urllib.parse.parse_qs(body, keep_blank_values=True)
    text = (fields.get("text") or fields.get("caption") or [""])[0]
    for k, v in sorted(fields.items()):
        if k in ("text", "caption"):
            continue
        shown = v[0]
        if k in ("chat_id", "parse_mode", "disable_web_page_preview", "disable_notification"):
            print(f"  {k} = {shown}")
        else:
            print(f"  {k} = {shown[:60]}")
    if not text:
        print("  (no text/caption field — binary or absent)")
        continue
    print("\n  --- message, exactly as sent (HTML intact) ---")
    for line in text.split("\n"):
        print("  | " + line)
    print("  --- end ---\n")
    print("  --- how a client renders it (tags stripped) ---")
    for line in re.sub(r"<[^>]+>", "", text).split("\n"):
        print("  | " + line)
    print("  --- end ---\n")

    bold = re.findall(r"<b>(.*?)</b>", text, re.S)
    links = re.findall(r'<a href="([^"]+)">(.*?)</a>', text, re.S)
    print(f"  bold runs : {bold}")
    print(f"  links     : {links}")
    print(f"  parse_mode: {(fields.get('parse_mode') or ['(ABSENT)'])[0]}")
    digits = re.findall(r"\d+\s*(?:วิ|วินาที|s\b)", text)
    print(f"  second-counts in the text: {digits or 'none'}")
    print(f"  lines     : {len(text.split(chr(10)))}")
