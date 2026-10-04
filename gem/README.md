# Framework GPT (Google Gemini Gem)

FrameWise started as **Framework GPT**, an AI agent built as a Gem on Google Gemini (Gems are Gemini's
platform for custom AI agents). `framewise-gem-system-prompt.md` is its original system prompt, kept so you can
run the same mentor on Gemini. Inside the prompt the agent introduces itself as "FrameWise Gem".

**Make the Gem:** Gemini → Gems → New Gem → name it "Framework GPT" → paste `framewise-gem-system-prompt.md`
into Instructions → Save. Framework GPT's knowledge files (expert documents on filmmaking and film criticism)
are added to the Gem as files; see the Roadmap in the main README for how they will come to the Claude skill.

**Reviewing your own video with it:** Gemini can watch an unlisted YouTube link with sound, so it does not need
the file. Use the Production Review questions in
[`../skills/framewise/references/production-review.md`](../skills/framewise/references/production-review.md)
as your message, and ask for the "FIX LIST FOR THE EDITOR" at the end so you can paste it straight into your
editing agent.

The Claude skill in `skills/framewise/` keeps the Gem's method, priorities and modes, and adds the Production
Review mode, a video-to-contact-sheet script (Claude cannot play video) and sound targets.
