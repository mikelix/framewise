# Changelog

## 0.1.0 (2026-10-04)

First release.

- FrameWise skill for Claude Code and claude.ai, ported from the FrameWise Gem on Google Gemini
  (original system prompt kept in `gem/`).
- 12 response modes: the Gem's 11 (Quick Film Insight, Full Film Analysis, Scene X-Ray, Director Signature Map,
  Character Study, Theme Analysis, Comparative Analysis, Student Essay Builder, Filmmaker Learning Mode,
  Classroom Mode, Viral Film Insight) plus **Production Review** for your own videos.
- `scripts/prepare_review.py`: turns a video into timestamped contact sheets, frame 0, hard cuts, black and
  silent stretches and a loudness curve; zoom mode (`--from/--to/--every`) for frame-level detail.
- Optional showtime integration: music analysis (tempo, key, energy sections, drops and surges) and speech
  transcription when the showtime CLI is installed.
- `references/sound-review.md`: delivery loudness, mix reference levels, arc, effects sync and pacing targets.
