# Sound review: numbers to judge against

Distilled from the sound-designer, music and pacing references of showtime (the open-source local video studio,
github.com/FavioVazquez/showtime). Use it for Production Review question 4 (sound) and for pacing notes. These
are the targets a sound designer mixes to, so a note that cites them is one the editor can act on.

You cannot listen. You have measurements (`summary.md`: loudness per 5 s, silences, and, when showtime is
installed, `beats.json`: tempo, key, energy sections, drops and surges). Judge the arc from those plus what is on
screen at the same time. Never describe instruments, melodies or a voice's tone you did not measure, and end the
sound section by telling the user a human must listen on laptop speakers and on headphones before publishing.

## 1. Delivery loudness

| Target | Integrated | True peak | Note |
|---|---|---|---|
| YouTube, social, web (default) | -14 LUFS ± 0.5 | ≤ -1 dBTP | louder gets turned down by the platform; quieter just sounds weak |
| Podcast, audio-first | -16 LUFS | ≤ -1 dBTP | |
| Broadcast | -23 LUFS (EBU R128) / -24 (ATSC) | ≤ -1 / -2 dBTP | only when asked |

- True peak above -1 dBTP: a defect (clipping after the platform's encode). Fix: master with a true-peak limiter.
- A compressed review copy can read higher peaks than its master (AAC re-encode). If the user also has the
  master, judge peaks on the master.
- LRA (loudness range): 5-10 LU suits a scored short film; under 4 LU feels flat and loud; above 15 LU makes
  quiet parts vanish on phone speakers.

## 2. Reference levels inside the mix

| Element | Level |
|---|---|
| Voice-over / dialogue | about -16 LUFS short-term |
| Music alone (no voice) | about -20 LUFS |
| Music under a voice | about -32 LUFS short-term (ducked 10-14 dB, 12 dB default) |
| Ambience / room tone | about -32 LUFS |
| UI clicks, text pops | about -24 LUFS momentary, peaks ≤ -8 dBFS |
| Impacts, hits | about -14 LUFS momentary |

Voice-to-music gap: 10-20 dB. Under 8 dB, words get masked: fix by ducking the music 12 dB under each line
(or a moderate 6-8 dB duck plus a mid-frequency carve). Over 25 dB the bed sounds like it vanished: raise it.

## 3. The arc (what the score should do over time)

Read the energy sections and the loudness curve together with the contact sheets:

- **Build toward the climax.** Energy level and LUFS should rise into the story's peak. A peak whose loudness is
  no higher than the section before it will not feel like a peak.
- **A drop or silence must be intentional.** A `VOID` section or a stretch more than 6 dB below its neighbours is
  either a deliberate breath (a reveal, a turn, a title) or an attention dip. Check what is on screen. A
  breath of 0.25-0.5 s of near-silence before a reveal is a strong device; 5-8 s of near-silence under ordinary
  content is a dip.
- **Resolve at the end.** The last section should settle (lower energy, steady LUFS) and end on a button (a
  final hit or chord on the last card), never a fade in mid-phrase.
- **Openings:** music audible within the first second. A quiet first 10-30 s loses the scroll.
- Name each problem as a time range with its measured LUFS: "0:20-0:28 sits at -18 LUFS against -14 around it;
  lift the bed about 4 dB".

## 4. Sound effects

- How many: explainer, data story or essay: 1-3 designed sounds in the whole video; a polished product or
  motion piece: one cue every 2-3 s at most; one per visual event that matters, not one per cut.
- Whooshes only for big moves or scene changes. Text pops on 20-40 % of text entrances at most.
- One sound family per video. No game-UI sounds (pop, ding, coin, success chime) in serious work.
- Sync: the hit (transient) lands on the frame of the visual event; sound never trails the picture by more
  than 2 frames (66 ms). A riser's peak lands on the reveal downbeat.

## 5. Music and the edit

- `pacing: beat_cut` (steady pulse): hard cuts may sit on beats; cut 1-2 frames before the beat; moves that
  must land start 40-190 ms early. `pacing: phrase_flow` (sparse, drumless): pace by phrases and energy, never
  hard-cut on a grid.
- Readable text stays at least 1 beat; a sentence at least 2 beats.
- Tempo from `beats.json` can be double or half the felt tempo (a 60 bpm score may read as 120). Key detection
  often swaps a minor key for its relative major (D minor read as F). Say "measured" and hedge.
- Music choice for the tone: explainers, data, reports and serious essays sound premium with restraint
  (underscore, ambient pad, minimal pulse, solo piano) or no music. Avoid plucked or mallet leads, claps above
  110 bpm under data, and EDM build-and-drop under charts.

## 6. Pacing checks that pair with sound

- Fast in, then hold: never pull text before it can be read. Minimum settled holds: label 0.8 s, headline
  max(1.2, 0.3 × words) s, text with no voice max(1.0, 0.5 + characters / 13) s, number 1.2 s after it lands,
  diagram or chart 1.5-2.5 s, end card ≥ 2.5 s.
- Reading ceiling: about 3 words/s (≤ 17 characters/s for captions).
- Short-form: something changes every 2-4 s; vary shot lengths (short-short-long); one held beat of 1-2 s.
- Narration word budget: duration × 2.5 words/s × 0.85.
- Flash safety: at most 3 flashes in any 1-second window; full-frame white flashes at most once or twice per video.

## 7. Writing sound fixes

Exact, and in the units a mixer uses:

- "0:20-0:28 and 1:50-2:00: lift the bed +4 dB." / "1:25-1:40: duck the music -2 dB."
- "1:49: land a soft bell hit on the clock reaching 00:00:00.000 (hit aligned to that frame)."
- "Master to -14 LUFS / -1 dBTP; it measures -14.1 LUFS but +2.5 dBTP on this copy."

If the project was made with showtime, these map onto `score.js` (composed film scores) or `audio/mix.json`
(tracks with `gain_db`, `duck`, `align: "hit"`), and `showtime audio meter <video> --ffmpeg` verifies the result.
You don't need to name the file; the editor's agent will.
