"""Probe TikTok live status for the .env.development candidates, read-only.

Two sessions disagreed about which rooms were live at 09:2x (one said @juniorshop4 was live,
the other said every env room was off-air), and whether a room is live decides whether the
C+D cases can run at all. So probe it here rather than trusting either list.

status 2 = live, 4 = ended (per the other session's reading; anything else printed raw).

usage: python -I -X utf8 probe_live.py <handle> [<handle> ...]
"""
import io
import json
import sys
import time
import urllib.error
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

URL = ("https://www.tiktok.com/api-live/user/room/"
       "?aid=1988&sourceType=54&uniqueId={handle}")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

MEANING = {2: "LIVE", 4: "ended"}

rows = []
for raw in sys.argv[1:]:
    handle = raw.lstrip("@")
    req = urllib.request.Request(URL.format(handle=handle),
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            payload = json.loads(r.read().decode("utf-8", "replace"))
        room = (payload.get("data") or {}).get("liveRoom") or {}
        status = room.get("status")
        title = (room.get("title") or "").strip()
        note = MEANING.get(status, f"status={status!r}")
        if status is None and not room:
            note = "no liveRoom in response"
        rows.append((handle, status, note, title[:46]))
    except urllib.error.HTTPError as e:
        rows.append((handle, None, f"HTTP {e.code}", ""))
    except Exception as e:
        rows.append((handle, None, f"error: {str(e)[:40]}", ""))
    time.sleep(0.7)

print(f"probed at {time.strftime('%H:%M:%S')} local\n")
print(f"{'handle':26} {'status':7} {'meaning':22} title")
print("-" * 96)
for handle, status, note, title in rows:
    print(f"{handle:26} {str(status):7} {note:22} {title}")

live = [h for h, s, _, _ in rows if s == 2]
print(f"\nLIVE now ({len(live)}): {', '.join('@' + h for h in live) if live else 'none'}")
