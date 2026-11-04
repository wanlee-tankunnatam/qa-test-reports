# Build the simulated live TC-AUD-D.1 needs.
#
# The case asks an assistant to mute the mic on a real broadcast for about 40 seconds. We never
# broadcast ourselves (QA ruling), and Mac did not either: its r184 run fed the live through
# LHM_FLV_URL and sent all-zero audio for 40 s while the picture kept going. This builds the same
# timeline for Windows:
#
#   0 -  90 s   real Thai speech (from the 9 analysed clips already on this machine)
#  90 - 135 s   DIGITAL SILENCE, all zero samples  <- the "mic muted" window, 45 s
# 135 - 330 s   speech again, so the episode recovers and the once-per-episode rule is visible
#
# Video runs the whole 330 s without a break, which is what the rule requires ("while the live's
# video is still arriving"). -max_interleave_delta keeps the muxer from holding the video back
# around the audio change (the TI-699 dev-story hit exactly that as a rig artifact).
#
# ASCII only: Windows PowerShell 5.1 reads a BOM-less UTF-8 script as ANSI and any non-ASCII
# character anywhere turns into a parser error.

[CmdletBinding()]
param(
  [string]$Speech  = "$PSScriptRoot\..\voice\all-speech.wav",
  [string]$OutFlv  = "$PSScriptRoot\..\aud-d1.flv",
  [int]$SpeechLead = 90,
  [int]$SilenceSec = 45,
  [int]$TailSec    = 195
)

$ff = 'C:\Program Files\Takra Insight UAT\resources\ffmpeg\ffmpeg.exe'
if (-not (Test-Path $ff))     { throw "ffmpeg not found at $ff" }
if (-not (Test-Path $Speech)) { throw "speech source not found: $Speech" }

$total   = $SpeechLead + $SilenceSec + $TailSec
$tailEnd = $SpeechLead + $TailSec

$fc = "[0:a]atrim=0:$SpeechLead,asetpts=N/SR/TB[a1];" +
      "[2:a]atrim=0:$SilenceSec,asetpts=N/SR/TB[a2];" +
      "[1:a]atrim=${SpeechLead}:$tailEnd,asetpts=N/SR/TB[a3];" +
      "[a1][a2][a3]concat=n=3:v=0:a=1[aout]"

# Step 1 - the audio timeline on its own, as 16 kHz mono PCM (what the engine's lane expects).
$wav = Join-Path $env:TEMP 'aud-d1-track.wav'
& $ff -y -hide_banner -loglevel error `
  -i $Speech `
  -i $Speech `
  -f lavfi -i "anullsrc=r=16000:cl=mono" `
  -filter_complex $fc `
  -map "[aout]" -t $total -ar 16000 -ac 1 -c:a pcm_s16le $wav
if (-not (Test-Path $wav)) { throw 'the audio timeline was not produced' }
"audio track: {0:N1} s" -f ((Get-Item $wav).Length / 32000)

# Step 2 - mux it with a continuously moving picture (video first, as the working WRD rig did).
& $ff -y -hide_banner -loglevel error `
  -f lavfi -i "testsrc2=s=540x960:r=15" `
  -i $wav `
  -shortest -t $total `
  -c:v libx264 -preset veryfast -pix_fmt yuv420p -g 30 -b:v 900k `
  -c:a aac -b:a 64k -ar 16000 -ac 1 `
  -f flv $OutFlv

if (-not (Test-Path $OutFlv)) { throw 'FLV was not produced' }
Remove-Item $wav -Force -ErrorAction SilentlyContinue
"built: $OutFlv  ({0:N1} MB, {1} s)" -f ((Get-Item $OutFlv).Length / 1MB), $total

# Prove the silence window really is silence and the speech really is not, by measuring the
# level of each stretch the way the engine does (RMS -> dBFS). astats prints it per window.
"`n--- level check (engine threshold is -60 dBFS) ---"
foreach ($probe in @(
    @{ name = 'speech  60-70 s'; ss = 60;  t = 10 },
    @{ name = 'silence 100-130s'; ss = 100; t = 30 },
    @{ name = 'speech  150-160s'; ss = 150; t = 10 })) {
  $out = & $ff -hide_banner -nostats -ss $probe.ss -t $probe.t -i $OutFlv `
           -map 0:a -af astats=metadata=1:reset=0 -f null - 2>&1
  $rms = ($out | Select-String -Pattern 'Overall.*' -Context 0,30 |
          Select-Object -First 1).Context.PostContext |
         Select-String -Pattern 'RMS level dB: (.+)' | Select-Object -First 1
  if ($rms) { "{0,-16} RMS {1}" -f $probe.name, $rms.Matches[0].Groups[1].Value.Trim() }
  else      { "{0,-16} RMS (not reported)" -f $probe.name }
}
