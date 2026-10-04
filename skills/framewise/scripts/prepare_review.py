#!/usr/bin/env python3
"""Turn a video into things a model can review: timestamped contact sheets, frame 0,
cut times, a per-second loudness curve, silent and black stretches, and summary.md.

Needs ffmpeg and ffprobe on PATH. Standard library only.

    python prepare_review.py film.mp4 --out review/
    python prepare_review.py film.mp4 --out review/ --from 75 --to 80 --every 0.25   # zoom into a moment
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def mmss(t):
    t = max(0.0, t)
    m = int(t // 60)
    s = t - 60 * m
    return f"{m}:{s:05.2f}" if s % 1 else f"{m}:{int(s):02d}"


def probe(path):
    code, out, err = run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate",
                          "-of", "json", path])
    if code != 0:
        sys.exit(f"ffprobe failed: {err.strip()}")
    return json.loads(out)


def font_arg():
    for f in ("C:/Windows/Fonts/arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial.ttf"):
        if os.path.exists(f):
            return "fontfile='" + f.replace(":", "\\:") + "':"
    return ""


def grab(path, t, dst, width, label):
    vf = f"scale={width}:-2"
    if label:  # time goes in a strip above the frame so it never covers the picture
        fs = max(16, width // 24)
        strip = fs + 10
        txt = mmss(t).replace(":", "\\:")
        vf += (f",pad=iw:ih+{strip}:0:{strip}:color=0x202020,"
               f"drawtext={font_arg()}text='{txt}':x=8:y=5:fontsize={fs}:fontcolor=white")
    code, _, err = run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                        "-vf", vf, "-q:v", "3", dst])
    if code != 0 and label:  # drawtext unavailable: keep going without the burned-in time
        return grab(path, t, dst, width, False)
    return code == 0


def tile(frames_dir, names, dst, cols, rows):
    lst = os.path.join(frames_dir, "_list.txt")
    with open(lst, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write(f"file '{n}'\n")
        for _ in range(cols * rows - len(names)):  # pad the last sheet with the last frame
            fh.write(f"file '{names[-1]}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-vf", f"tile={cols}x{rows}:padding=4:color=black", "-frames:v", "1", "-q:v", "3", dst])
    os.remove(lst)


def scene_cuts(path, t0, t1, thresh):
    code, _, err = run(["ffmpeg", "-v", "info", "-ss", str(t0), "-to", str(t1), "-i", path, "-an",
                        "-vf", f"scale=320:-2,select='gt(scene,{thresh})',showinfo", "-f", "null", "-"])
    cuts = []
    for m in re.findall(r"pts_time:([0-9.]+)", err):
        c = round(t0 + float(m), 2)
        if not cuts or c - cuts[-1] > 0.5:  # one flash or push can score on several frames
            cuts.append(c)
    return cuts


def black_spans(path, t0, t1):
    _, _, err = run(["ffmpeg", "-v", "info", "-ss", str(t0), "-to", str(t1), "-i", path, "-an",
                     "-vf", "scale=320:-2,blackdetect=d=0.4:pix_th=0.10", "-f", "null", "-"])
    return [(round(t0 + float(a), 2), round(t0 + float(b), 2))
            for a, b in re.findall(r"black_start:([0-9.]+) black_end:([0-9.]+)", err)]


def audio_stats(path, t0, t1):
    # framelog lines (one per 0.1 s) are only printed at -v verbose
    _, _, err = run(["ffmpeg", "-v", "verbose", "-nostats", "-ss", str(t0), "-to", str(t1), "-i", path, "-vn",
                     "-af", "ebur128=peak=true:framelog=verbose,silencedetect=n=-45dB:d=1", "-f", "null", "-"])
    per_sec = {}
    for t, s in re.findall(r"t:\s*([0-9.]+)\s+TARGET.*?S:\s*(-?[0-9.]+|-inf)", err):
        sec = int(float(t))
        if s != "-inf" and float(s) > -70:
            per_sec[sec] = float(s)  # last short-term (3 s window) value in each second
    integrated = re.findall(r"I:\s*(-?[0-9.]+) LUFS", err)
    lra = re.findall(r"LRA:\s*(-?[0-9.]+) LU", err)
    peak = re.findall(r"Peak:\s*(-?[0-9.]+|-inf) dBFS", err)
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", err)]
    silences = []
    for i, a in enumerate(starts):
        b = ends[i] if i < len(ends) else (t1 - t0)
        silences.append((round(t0 + max(0, a), 2), round(t0 + b, 2)))
    return {
        "integrated_lufs": float(integrated[-1]) if integrated else None,
        "lra_lu": float(lra[-1]) if lra else None,
        "true_peak_dbtp": float(peak[-1]) if peak and peak[-1] != "-inf" else None,
        "short_term_per_second": {t0 + k: v for k, v in sorted(per_sec.items())},
        "silences": silences,
    }


def find_showtime():
    """The showtime CLI (open-source video studio) if installed: env SHOWTIME_BIN, PATH, or the Claude Code plugin cache."""
    env = os.environ.get("SHOWTIME_BIN")
    if env and os.path.exists(env):
        return env
    on_path = shutil.which("showtime")
    if on_path:
        return on_path
    import glob
    exe = "showtime.cmd" if os.name == "nt" else "showtime"
    hits = glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "plugins", "cache", "showtime", "showtime",
                                  "*", "skills", "showtime", "bin", exe))

    def ver(p):
        v = p.split(os.sep)[-5]
        return tuple(int(x) if x.isdigit() else 0 for x in v.split("."))
    return max(hits, key=ver) if hits else None


def st_cmd(st, *args):
    if os.name != "nt" and not os.access(st, os.X_OK):
        return ["sh", st, *args]
    return [st, *args]


def music_analysis(st, video, out):
    """showtime audio beats: tempo, key, beat grid, energy sections, drops and surges."""
    dst = os.path.join(out, "beats.json")
    code, so, se = run(st_cmd(st, "audio", "beats", video, "-o", dst))
    if code != 0 or not os.path.exists(dst):
        return {"error": (se or so).strip()[-300:]}
    with open(dst, encoding="utf-8") as fh:
        b = json.load(fh)
    return {k: b.get(k) for k in ("bpm", "bpm_confidence", "key", "key_confidence", "rhythmic", "pacing",
                                  "onset_rate", "sections", "moments")}


def transcribe(st, video, out):
    """showtime transcribe (local Whisper): is there speech, and what does it say?"""
    tdir = os.path.join(out, "transcript")
    code, so, se = run(st_cmd(st, "transcribe", video, "--edit-dir", tdir, "--force"))
    files = []
    for root, _, names in os.walk(tdir):
        files += [os.path.join(root, n) for n in names if n.endswith((".json", ".txt", ".srt"))]
    words = None
    for f in files:
        if f.endswith(".json"):
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
                ws = d.get("words") if isinstance(d, dict) else None
                if ws is None and isinstance(d, dict):
                    ws = [w for s in d.get("segments", []) for w in s.get("words", [])]
                if ws is not None:
                    words = len(ws)
                    break
            except (ValueError, OSError):
                pass
    return {"ok": code == 0, "files": files, "words": words, "log": (so + se).strip()[-300:]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", required=True, help="folder for the review pack")
    ap.add_argument("--every", type=float, default=0, help="seconds between frames (default: about 48 frames)")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=0.0)
    ap.add_argument("--width", type=int, default=480, help="width of each sheet frame in px")
    ap.add_argument("--scene", type=float, default=0.25, help="scene-change threshold for hard-cut detection")
    ap.add_argument("--no-showtime", action="store_true", help="skip showtime's music analysis even if installed")
    ap.add_argument("--transcribe", action="store_true",
                    help="also transcribe speech with showtime (slow: about 20 min for 3 min of scored audio, "
                         "because it separates voice from music first)")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH")
    info = probe(a.video)
    dur = float(info["format"]["duration"])
    t0, t1 = a.t0, (a.t1 or dur)
    t1 = min(t1, dur)
    span = t1 - t0
    every = a.every or max(0.5, round(span / 48, 2))
    os.makedirs(a.out, exist_ok=True)
    fdir = os.path.join(a.out, "frames")
    os.makedirs(fdir, exist_ok=True)

    # frames, with the time burned in, sampled in the middle of each slot
    times, t = [], t0 + every / 2
    while t < t1:
        times.append(round(t, 3))
        t += every
    names = []
    for i, tt in enumerate(times):
        n = f"f{i:03d}_{tt:08.2f}s.jpg"
        if grab(a.video, tt, os.path.join(fdir, n), a.width, True):
            names.append(n)
    if t0 == 0:
        grab(a.video, 0.0, os.path.join(a.out, "frame0.jpg"), 960, False)

    cols, rows = 4, 3
    sheets = []
    for k in range(0, len(names), cols * rows):
        chunk = names[k:k + cols * rows]
        dst = os.path.join(a.out, f"sheet_{len(sheets) + 1:02d}.jpg")
        tile(fdir, chunk, dst, cols, rows)
        first = float(chunk[0].split("_")[1][:-5])
        last = float(chunk[-1].split("_")[1][:-5])
        sheets.append({"file": os.path.basename(dst), "from": first, "to": last})

    cuts = scene_cuts(a.video, t0, t1, a.scene)
    blacks = black_spans(a.video, t0, t1)
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    audio = audio_stats(a.video, t0, t1) if has_audio else None

    st = None if a.no_showtime else find_showtime()
    music = speech = None
    if st and has_audio and t0 == 0 and a.t1 in (0, dur):  # whole-film analyses only
        music = music_analysis(st, a.video, a.out)
        if a.transcribe:
            speech = transcribe(st, a.video, a.out)

    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    summary = {
        "video": os.path.abspath(a.video), "duration_s": round(dur, 3), "range": [t0, t1],
        "size_mb": round(int(info["format"].get("size", 0)) / 1048576, 1),
        "width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"),
        "frame_every_s": every, "sheets": sheets, "cuts": cuts, "black": blacks, "audio": audio,
        "showtime": st, "music": music, "speech": speech,
    }
    with open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)

    L = [f"# Review pack: {os.path.basename(a.video)}", "",
         f"- {v.get('width')}x{v.get('height')}, {v.get('r_frame_rate')} fps, {mmss(dur)} ({dur:.2f} s), "
         f"{summary['size_mb']} MB",
         f"- Range reviewed: {mmss(t0)}-{mmss(t1)}; one frame every {every} s; "
         f"{len(sheets)} contact sheets of {cols}x{rows} (time in the grey strip above each frame)",
         "- frame0.jpg = the first frame (what feeds show as a thumbnail)" if t0 == 0 else ""]
    if audio:
        L += [f"- Loudness: {audio['integrated_lufs']} LUFS integrated, LRA {audio['lra_lu']} LU, "
              f"true peak {audio['true_peak_dbtp']} dBTP (YouTube target about -14 LUFS, <= -1 dBTP)"]
    else:
        L += ["- No audio track"]
    L += ["", "## Contact sheets", ""] + [f"- {s['file']}: {mmss(s['from'])}-{mmss(s['to'])}" for s in sheets]
    L += ["", f"## Hard cuts ({len(cuts)} detected at scene>{a.scene})", "",
          ", ".join(mmss(c) for c in cuts) or "none",
          "", "Pushes, dissolves and cuts between similar dark frames do not register here. "
          "Judge pacing from the contact sheets, not from this count."]
    L += ["", "## Black stretches (>= 0.4 s)", "",
          ", ".join(f"{mmss(x)}-{mmss(y)}" for x, y in blacks) or "none"]
    if audio:
        L += ["", "## Silences (below -45 dB for >= 1 s)", "",
              ", ".join(f"{mmss(x)}-{mmss(y)}" for x, y in audio["silences"]) or "none",
              "", "## Loudness curve (short-term LUFS, averaged per 5 s)", "",
              "| time | LUFS | bar |", "|---|---:|---|"]
        st = audio["short_term_per_second"]
        b = t0
        while b < t1:
            vals = [x for k, x in st.items() if b <= k < b + 5]
            if vals:
                m = sum(vals) / len(vals)
                L.append(f"| {mmss(b)} | {m:.1f} | {'#' * max(0, int(m + 36))} |")
            else:
                L.append(f"| {mmss(b)} | silent | |")
            b += 5
    if music and "error" not in music:
        st_ = audio["short_term_per_second"] if audio else {}

        def lufs(x, y):
            vals = [val for k, val in st_.items() if x <= k < y]
            return f"{sum(vals) / len(vals):.1f}" if vals else "silent"
        L += ["", "## Music (showtime audio beats; see beats.json)", "",
              f"- Tempo {music['bpm']} bpm (confidence {music['bpm_confidence']}); may be read at double or half "
              "the felt tempo, so check it against the pace on screen",
              f"- Key {music['key']} (confidence {music['key_confidence']}); a relative major/minor mix-up "
              "(F vs D minor) is common",
              f"- Pacing type: {music['pacing']} ({'cuts may sit on beats' if music['pacing'] == 'beat_cut' else 'follow phrases and energy, not a beat grid'})",
              "", "| from | to | energy | level | LUFS |", "|---|---|---|---:|---:|"]
        for s in music.get("sections") or []:
            L.append(f"| {mmss(s['start'])} | {mmss(s['end'])} | {s['level']} | {s['energy']:.2f} | "
                     f"{lufs(s['start'], s['end'])} |")
        mom = music.get("moments") or []
        L += ["", "Moments (sudden energy changes): " +
              (", ".join(f"{m_['type']} {mmss(m_['t'])}" for m_ in mom) or "none"),
              "VOID = near-empty music; check the picture there for an intended pause or an attention dip."]
    elif music:
        L += ["", f"## Music analysis failed: {music['error']}"]
    elif not st:
        L += ["", "## Music analysis skipped (showtime not installed); judge the arc from the loudness curve"]
    if speech:
        L += ["", "## Speech (showtime transcribe)", "",
              f"- words: {speech['words'] if speech['words'] is not None else 'unknown'}; files: "
              + (", ".join(os.path.relpath(f, a.out) for f in speech["files"]) or "none")
              + ("" if speech["ok"] else f"; transcribe failed: {speech['log']}")]
    L += ["", "Limits: frames are samples, so 1-frame flashes and flicker between samples are not visible; "
          "re-run with --from/--to/--every to zoom in. Loudness is measured; the music's character is not."]
    with open(os.path.join(a.out, "summary.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(x for x in L if x is not None) + "\n")
    print(os.path.join(a.out, "summary.md"))


if __name__ == "__main__":
    main()
