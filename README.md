# FrameWise

**Turn cinema into insight.** A film mentor and an honest film reviewer for your coding agent.

FrameWise does two jobs:

1. **Film analysis.** Give it a film, scene, director, character, genre or theme and it explains how the film
   works, why it moves people, which craft choices create that effect, and what you can learn from them. It
   connects every point the same way: *film choice → emotional effect → meaning → craft lesson*.
2. **Production Review.** Give it your own cut and it reviews it the way a festival programmer or a paying
   client would: timestamped notes on story, pacing, visuals, sound and facts, a title/thumbnail/description,
   a verdict (ship / ship after fixes / do not ship), and a numbered **fix list** with exact values that you can
   paste straight into an editing agent such as [showtime](https://github.com/FavioVazquez/showtime).

It started as a custom Gem on Google Gemini (the original prompt is in [`gem/`](gem/)) and was rebuilt as a
Claude skill.

## Install

### Claude Code (plugin)

```
/plugin marketplace add mikelix/framewise
/plugin install framewise@framewise
/reload-plugins
```

### Claude Code (plain skill)

Copy `skills/framewise/` to `~/.claude/skills/framewise/`.

### claude.ai

Download `framewise.skill` from the [latest release](https://github.com/mikelix/framewise/releases/latest), then
Settings → Capabilities → Skills → Upload skill.

### Google Gemini

See [`gem/README.md`](gem/README.md).

## Requirements

- Analysis modes: nothing.
- Production Review of a local video: **Python 3.9+** and **ffmpeg / ffprobe** on PATH (the script uses only the
  Python standard library).
- Optional: **[showtime](https://github.com/FavioVazquez/showtime)**. When its CLI is installed (on PATH, in
  `SHOWTIME_BIN`, or as the Claude Code plugin) the review also gets music analysis (tempo, key, energy sections,
  drops and surges) and, with `--transcribe`, a local speech transcript.

## Use it

Just ask. For example:

- "Break down the opening of *Parasite* as a Scene X-Ray."
- "Compare Kubrick and Tarkovsky on long takes, for a film class."
- "用中文分析《花样年华》的色彩和构图。"
- "Review my video `cuts/launch-v3.mp4` like a festival juror. 45 s, no voice-over, for YouTube."

### The 12 modes

| Request | Mode |
|---|---|
| Quick question | Quick Film Insight |
| Whole film | Full Film Analysis |
| One scene | Scene X-Ray |
| A director | Director Signature Map |
| A character | Character Study |
| A theme | Theme Analysis |
| Two or more works | Comparative Analysis |
| Essay help | Student Essay Builder (helps you think; does not write the essay for you) |
| Lessons for creators | Filmmaker Learning Mode |
| Teaching material | Classroom Mode |
| Social content | Viral Film Insight |
| **Your own video** | **Production Review** |

Answers in Chinese when you ask in Chinese, or in both languages on request. Spoiler notes before major
twists. No invented quotes, awards, box office or behind-the-scenes facts.

## How Production Review sees your video

Claude cannot play video, so FrameWise prepares it first:

```
python skills/framewise/scripts/prepare_review.py film.mp4 --out review/
```

| Output | What it is |
|---|---|
| `sheet_01.jpg` ... | contact sheets of 4x3 frames (about 48 for the whole film), the time in a strip above each frame |
| `frame0.jpg` | the first frame, which is what feeds and chat apps show as the thumbnail |
| `summary.md` | size, format, hard cuts, black and silent stretches, integrated loudness and true peak, a loudness curve per 5 s, and (with showtime) the music's tempo, key, energy sections and drops |
| `beats.json` | showtime's full music analysis (when installed) |
| `transcript/` | word-level transcript (with `--transcribe`) |

Zoom into a moment frame by frame:

```
python skills/framewise/scripts/prepare_review.py film.mp4 --out review-76s/ --from 75 --to 78 --every 0.25
```

The review then answers eight questions with a timestamp on every point: first impression at 5 s, 30 s and the
end; story and pacing; visual design and phone readability; sound against the arc; facts and the line between
fact and speculation; distinctive versus generic; the three most important improvements; and packaging. Sound is
judged against concrete targets (for example -14 LUFS / -1 dBTP for YouTube, music 10-20 dB under a voice, hits
within 2 frames of the picture) in [`references/sound-review.md`](skills/framewise/references/sound-review.md).

A fix list looks like this:

```
FIX LIST FOR THE EDITOR
1. 2:17-2:20 A hard-edged darker rectangle sits behind the towers. Fix: remove the panel; use a soft radial glow.
2. 0:20-0:28 Bed at -18 LUFS against -14 around it. Fix: lift the bed +4 dB.
3. 1:16 Progress dot jumps when the bar rescales. Fix: slide it over 0.4 s.
```

## Limits, stated plainly

- Contact sheets sample one frame every few seconds. One-frame flashes or flicker between samples are invisible
  unless you zoom in.
- Claude does not hear the music. Loudness is measured and the music's shape is analysed; mood is judged from
  those plus the picture. Always listen yourself on laptop speakers and headphones before publishing.
- Hard-cut detection misses pushes, dissolves and cuts between similar dark frames; pacing is judged from the
  sheets.
- Measured tempo can be double or half the felt tempo, and key detection can swap a minor key for its relative
  major.
- Transcription separates voice from music first: about 20 minutes for a 3-minute scored film on a desktop CPU.

## Repository layout

```
.claude-plugin/        plugin and marketplace manifests (Claude Code)
skills/framewise/
  SKILL.md             identity, method, priorities, mode router, integrity rules
  references/          modes, analysis toolkit and vocabulary, production review, sound targets
  scripts/             prepare_review.py
gem/                   the original Google Gemini Gem prompt
```

## Credits

The sound, music and pacing targets are distilled from the references of
[showtime](https://github.com/FavioVazquez/showtime) by Favio Vazquez (MIT), the open-source local video studio
this skill was built alongside.

## License

MIT, see [LICENSE](LICENSE).
