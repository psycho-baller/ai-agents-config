---
name: content-hooks
description: Generates hooks, titles, and full tweets for all content mediums from a transcript + research file. Scores everything with ICE. Requires research.md to exist first (run content-research first).
---

# content-hooks

generates distribution assets for every medium from a transcript and its research. tweets are written in full. everything else is hooks and titles. all items are scored with ICE.

## inputs

- `file`: path to a transcript `.md` file, or the folder name inside `notes-processing/`
- `research.md` must already exist at `notes-processing/{filename}/research.md`
- output: `notes-processing/{filename}/hooks.md`

## voice

all copy must sound like rami. read `/Users/rami/Documents/life-os/ai-agents-config/skills/rami-voice/SKILL.md` for the full rules. critical rules that apply to every hook and tweet you write:

- **no em dashes** — use a comma, colon, parentheses, or a new sentence instead
- **no semicolons**
- **no hedging qualifiers**: "it's worth noting", "one could argue", "it's interesting that"
- **no corporate vocabulary**: leverage (as verb), utilize, implement, unpack, delve, game-changing
- **no summary conclusions** — every closer should be a charge or a sharp stop, never a recap
- **no formal transitions**
- lowercase, no hashtags, no engagement bait ("drop it in the comments", "have you ever...")
- takes a side — observation is not enough, a take is required

## preprocessing

clean the transcript before using it:
- strip YAML frontmatter, wiki-links (`[[Note|text]]` → `text`), and `## Related Notes` section
- identify the dominant 1-2 themes (what the speaker kept coming back to) — use these as the hook lens

## steps

1. read the cleaned transcript and `research.md`
2. identify the 1-2 dominant themes — these are the lens for all hooks
3. do 3-5 web searches to discover current trends:
   - what's trending right now in this space on LinkedIn / Twitter / YouTube
   - recent viral content on these exact themes
   - what's resonating with young founders and entrepreneurs this week
4. generate all content assets (see mediums below)
5. score each item with ICE
6. write hooks.md

## mediums

**linkedin** — 5 hooks (opening lines only, not full posts)
- one line that stops the scroll
- counterintuitive, bold, or uncomfortably personal
- no "have you ever...", no rhetorical questions leading with "you"

**twitter/x** — 5 full tweets (written in full — these are final, not just hooks)
- naval ravikant / dan koe style: expose a truth that sounds simple but takes paragraphs to fully explain
- lowercase, no hashtags, no emojis, no engagement bait
- **hard limit: 1-3 sentences only.** if it's longer, cut it. tweets are not essays — they're the sharp point before the essay.
- each tweet must stand alone as a complete thought. no thread prefixes, no "1/n"
- examples that hit the right length:
  - "desire is a contract you make with yourself to be unhappy until you get what you want." — 1 sentence, reframes a universal experience
  - "you don't have a focus problem. you have a values problem." — 2 sentences, forces self-reflection
  - "i can indulge now, i'll be disciplined later — that's not a productivity strategy. that's addiction logic with better branding." — 2 sentences, uncomfortable and undeniable
  - "researchers found people choose a $20 task over a $25 one just because it has a shorter deadline. we do the same with our lives. we call it productivity." — 3 sentences, max length
- rami's voice: personal, direct, lowercase, ends sharp

**instagram/tiktok** — 5 hooks + 5 headline options
- hook: the first spoken sentence of a short video (grabs in 2 seconds)
- headline: text overlay or caption title (5-8 words, punchy)

**youtube** — 3 title + subtitle pairs + 1-2 sentence description each (2 for short-tier transcripts)
- title: searchable and compelling (not clickbait)
- subtitle: expands on the title, adds intrigue or specificity
- use section format in output (not a table — descriptions are too long for table cells)

## ice scoring

score each item individually. be honest — score based on evidence from trend research, not optimism.

- **impact** (1-10): potential reach and resonance with rami's audience (young founders, entrepreneurs, gen z)
- **confidence** (1-10): how likely this lands, based on current trends and rami's track record with similar content
- **ease** (1-10): how easily produced from existing transcript material (10 = fully covered)
- **ice** = (impact + confidence + ease) / 3

medium ice = average of all items in that medium
overall content ice = average of all medium ices

## output format

```markdown
# hooks: {transcript title}

**overall ice score:** {x.x}/10

---

## linkedin hooks

| # | hook | I | C | E | ICE |
|---|------|---|---|---|-----|
| 1 | hook text | 8 | 7 | 9 | 8.0 |

**medium ice:** {x.x}/10

---

## twitter/x

**1.** tweet text here
`I: 9 | C: 8 | E: 9 | ICE: 8.7`

**2.** tweet text here
`I: 8 | C: 9 | E: 9 | ICE: 8.7`

*(repeat for all 5)*

**medium ice:** {x.x}/10

---

## instagram/tiktok

### hooks
| # | hook | I | C | E | ICE |
|---|------|---|---|---|-----|

### headlines
| # | headline | I | C | E | ICE |
|---|----------|---|---|---|-----|

**medium ice:** {x.x}/10

---

## youtube

### 1. {title}
**subtitle:** {subtitle}
**description:** {1-2 sentences}
`I: 9 | C: 9 | E: 9 | ICE: 9.0`

*(repeat for all 3)*

**medium ice:** {x.x}/10

---

## trend context

- {bullet: what's trending that informed these hooks, with source url}
```

## note on short transcripts

if the transcript is thin (< 150 words with 1-2 ideas), generate fewer hooks per medium (3 instead of 5) and focus them tightly on the one core insight. don't pad.
