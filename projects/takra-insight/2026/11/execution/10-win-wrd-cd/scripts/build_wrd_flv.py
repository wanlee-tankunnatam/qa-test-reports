"""Build a simulated live (.flv) carrying real Thai host speech at chosen times.

Why a tone bed instead of silence: the shipped audio-loss rule fires on >20 s below -60 dBFS
(wall_alerts.py AUDIO_LOST_S=20.0, SILENCE_DBFS=-60.0). The WRD cases need ~90 s between
sentences, so padding with anullsrc would raise an unrelated "เสียงไลฟ์หาย" alert and pollute the
run. A 70 Hz tone at volume=0.045 measures mean -48.0 / max -45.0 dBFS on this machine (verified,
not copied) — above the threshold, below speech range.

The level is then measured back OUT of the finished FLV through the AAC decoder, because AAC is
lossy and "I asked for -48" is not evidence the engine receives -48.

usage:
  python -I -X utf8 build_wrd_flv.py <out.flv> <total_s> <mp3>@<at_s> [<mp3>@<at_s> ...]
"""
import io
import os
import re
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

FF = r"C:\Program Files\Takra Insight UAT\resources\ffmpeg\ffmpeg.exe"
BED_GAIN = "0.045"          # measured on this machine: mean -48.0 dBFS, max -45.0 dBFS
BED_HZ = "70"

out_flv = sys.argv[1]
total = float(sys.argv[2])
spec = []
for arg in sys.argv[3:]:
    path, _, at = arg.rpartition("@")
    spec.append((path, float(at)))

work = os.path.dirname(os.path.abspath(out_flv))
wav = os.path.join(work, os.path.basename(out_flv).replace(".flv", "") + "-audio.wav")


def run(args, label):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        print(f"!! {label} failed (exit {p.returncode})")
        print((p.stderr or "")[-2500:])
        sys.exit(1)
    return (p.stderr or "") + (p.stdout or "")


# ── pass 1: the audio timeline alone, as 16 kHz mono PCM ────────────────────────────────────
ins = ["-f", "lavfi", "-t", str(total), "-i", f"sine=frequency={BED_HZ}:sample_rate=44100"]
for path, _ in spec:
    ins += ["-i", path]

parts = [f"[0:a]volume={BED_GAIN}[bed]"]
labels = ["[bed]"]
for i, (_, at) in enumerate(spec, start=1):
    ms = int(round(at * 1000))
    parts.append(f"[{i}:a]adelay={ms}|{ms}[d{i}]")
    labels.append(f"[d{i}]")
parts.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first[aout]")
fc = ";".join(parts)

print(f"building {len(spec)} utterance(s) over {total:.0f}s, bed {BED_HZ}Hz @ volume={BED_GAIN}")
for path, at in spec:
    print(f"   {at:7.1f}s  {os.path.basename(path)}")

run([FF, "-y", "-hide_banner", "-loglevel", "error", *ins,
     "-filter_complex", fc, "-map", "[aout]",
     "-t", str(total), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav], "pass 1 (audio)")

# ── pass 2: mux with a moving picture, video FIRST (single-pass mux fails with -22) ─────────
run([FF, "-y", "-hide_banner", "-loglevel", "error",
     "-f", "lavfi", "-i", "testsrc2=s=540x960:r=15", "-i", wav,
     "-shortest", "-t", str(total),
     "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-g", "30", "-b:v", "900k",
     "-c:a", "aac", "-b:a", "64k", "-ar", "16000", "-ac", "1",
     "-f", "flv", out_flv], "pass 2 (mux)")

size = os.path.getsize(out_flv)
print(f"\nwrote {out_flv}  ({size/1048576:.1f} MB)")
if size < 100_000:
    print("!! suspiciously small — the mux probably failed silently")
    sys.exit(1)


# ── verify: read the levels back OUT of the finished FLV, through the AAC decoder ───────────
def level(start, dur):
    txt = run([FF, "-hide_banner", "-ss", str(start), "-t", str(dur), "-i", out_flv,
               "-af", "volumedetect", "-f", "null", "-"], f"measure {start}-{start+dur}")
    mean = re.search(r"mean_volume:\s*(\S+)", txt)
    mx = re.search(r"max_volume:\s*(\S+)", txt)
    return (mean.group(1) if mean else "?"), (mx.group(1) if mx else "?")


print("\nlevels read back out of the finished FLV (what the engine's tap receives):")
# a bed-only stretch: just before the first utterance
first_at = min(at for _, at in spec)
probe_at = max(1.0, first_at - 16.0)
m, x = level(probe_at, min(14.0, first_at - probe_at))
print(f"   bed only   {probe_at:6.1f}s +{min(14.0, first_at-probe_at):.0f}s   mean {m} dBFS   max {x} dBFS")
bed_mean = float(m) if re.match(r"^-?\d+(\.\d+)?$", m) else None

for path, at in spec:
    m, x = level(at, 3.0)
    print(f"   speech     {at:6.1f}s +3s    mean {m} dBFS   max {x} dBFS   {os.path.basename(path)}")

# the decisive check: no stretch anywhere reads as digital silence to the engine
txt = run([FF, "-hide_banner", "-i", out_flv, "-af", "silencedetect=noise=-60dB:d=1.0",
           "-f", "null", "-"], "silencedetect")
hits = re.findall(r"silence_start:\s*(\S+)", txt)
print(f"\nsilencedetect noise=-60dB d=1.0  ->  {len(hits)} silent stretch(es)"
      + (f" at {hits[:6]}" if hits else " — none, so the audio-loss rule cannot fire"))
if hits:
    print("!! the bed is too quiet somewhere; raise BED_GAIN or the run will raise เสียงไลฟ์หาย")
    sys.exit(1)
if bed_mean is not None and bed_mean > -30.0:
    print(f"!! bed at {bed_mean} dBFS is loud enough that ASR may transcribe it")
    sys.exit(1)
print("OK")
