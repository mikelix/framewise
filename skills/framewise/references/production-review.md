# Production Review

A review of the user's own film, for a festival or a professional client. The user will act on it, often by
pasting your fix list into a coding agent that edits the video (showtime, hyperframes), so precision beats prose.

## 1. Gather what you need

- **The video.** Run `scripts/prepare_review.py` on the file (see SKILL.md) and read `summary.md` and every
  contact sheet. Read `frame0.jpg` too: it is what feeds and chat apps show before anyone presses play.
- **Context.** The user's description of the film: the conceit, the audience, the platform, what is fact and what
  is imagined. If they gave none, write one line of what you assume and continue; do not stall on questions.
- **Any brief or earlier notes** (a STYLE-BRIEF.md, FINDINGS.md, an earlier fix round). Check whether earlier
  fixes landed and do not re-raise what the user already decided against.

What the summary can and cannot tell you:
- Sheets show one frame every few seconds. A 1-frame flash, a ghosted digit or a stutter between samples will not
  appear. If a moment matters, extract more frames there:
  `python scripts/prepare_review.py <video> --out <dir> --from 75 --to 80 --every 0.25`.
- Loudness, silence and cut times are measured. When showtime is installed, the summary also has the music's
  tempo, key, energy sections (LOW / MEDIUM / HIGH / VOID) and sudden drops and surges, and `--transcribe` adds a
  word-level transcript. Mood, whether the score "supports the arc", is your judgment from those plus what is on
  screen at that moment; say so.
- You do not hear the music. Do not describe instruments, melodies or voices you cannot know.
- Pacing notes (holds too short to read, too long to stay interesting) use the numbers in `sound-review.md` §6.

## 2. The eight questions

Cite a timestamp (m:ss) for every point.

1. **First impression:** what a stranger thinks at 5 s, 30 s and at the end. Frame 0 counts.
2. **Story and pacing:** does the central device land? Where does attention dip (long holds, repeated beats, a
   flat loudness stretch with no new picture)? Is the main turn clear and does it move?
3. **Visual design:** typography, readability on a phone (text under about 3.5 % of frame height is hard to read on a
   phone), colour, icons, transitions, consistency across the film.
4. **Sound:** read `sound-review.md` first. Does the loudness and energy shape follow the story's arc (build,
   breath, resolve)? Name stretches that are empty or too loud with their times and measured LUFS; say whether a
   VOID section is a deliberate breath or a dip, judging from what is on screen. Check delivery loudness, the
   voice-to-music gap if there is a voice, and effects density and sync. End with: a human should listen on
   laptop speakers and headphones before publishing.
5. **Ideas and honesty:** are the facts, dates and numbers on screen accurate (check the arithmetic of any scale or
   clock; say which ones you are sure of)? Is speculation clearly labelled and kept apart from fact? Does the ending
   say something worth saying?
6. **Compared with similar work:** what is distinctive, what is generic. Name the genre or well-known reference
   (for example, Cosmic Calendar-style explainers) without inventing details about it.
7. **The 3 most important improvements,** each with a timestamp, ranked by impact on the viewer.
8. **Packaging:** recommended title, thumbnail frame (a timestamp you actually saw, and why it works small), and
   the first line of the YouTube description.

End with a one-paragraph verdict and one of: **ship / ship after fixes / do not ship**.

## 3. Fix list for the editor

After the verdict, add this section so the user can paste it straight into their editing agent:

```
FIX LIST FOR THE EDITOR
1. <m:ss or start-end s> <what is wrong>. Fix: <exact change: copy, line break with "/", seconds, dB, px or %>.
2. ...
```

- Numbered, at most 10, ordered by impact. One problem per item.
- Exact values, not adjectives: "lift the bed 4 dB at 20-28 s", not "make the start louder";
  "Carbon pulled from the sky / by the gigatonne", not "fix the line break".
- Mark an item **(taste)** when it is your preference rather than a defect, so the user can skip it cleanly.
- Respect the user's stated decisions (their copy, a fixed length, a chosen order). If you still disagree, say so
  once in the review, not in the fix list.

## 4. Tone

Honest and specific; praise only what earns it, with the timestamp that earns it. Write for the maker: they know
the film better than you, so explain what a stranger experiences, not what the maker intended.

## Example fix-list items (from a real round on a 3-minute type-led film)

```
1. 2:17-2:20 A hard-edged darker rectangle sits behind the towers from mid-frame to the right edge. Fix: remove the panel; use a soft radial glow.
2. 1:49 After "Everything so far really happened." the clock jumps to day two. Fix: land the clock on 00:00:00.000 on the midnight bell, then start day two.
3. Day two titles (2027 beat; 2:17) Line breaks split phrases. Fix: "AI agents work for weeks / on their own"; "Carbon pulled from the sky / by the gigatonne".
4. 0:20-0:28, 1:50-2:00 Bed too quiet under the titles. Fix: +4 dB. 1:25-1:40: duck music -2 dB.
5. 1:16 Progress dot jumps when the bar rescales to "LAST 2 SECONDS". Fix: slide it over 0.4 s.
```
