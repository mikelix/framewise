# FrameWise Gem (Google Gemini)

FrameWise started as a custom Gem on Google Gemini. `framewise-gem-system-prompt.md` is its original system
prompt, kept so you can run the same mentor on Gemini.

**Make the Gem:** Gemini → Gems → New Gem → name it "FrameWise Gem" → paste `framewise-gem-system-prompt.md`
into Instructions → Save.

**Reviewing your own video with it:** Gemini can watch an unlisted YouTube link with sound, so it does not need
the file. Use the Production Review questions in
[`../skills/framewise/references/production-review.md`](../skills/framewise/references/production-review.md)
as your message, and ask for the "FIX LIST FOR THE EDITOR" at the end so you can paste it straight into your
editing agent.

The Claude skill in `skills/framewise/` keeps the Gem's method, priorities and modes, and adds the Production
Review mode, a video-to-contact-sheet script (Claude cannot play video) and sound targets.
