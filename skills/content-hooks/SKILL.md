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

## steps

1. read the transcript and `research.md`
2. do 3-5 web searches to discover current trends related to the transcript's themes:
   - what's trending right now in this space on LinkedIn / Twitter / YouTube
   - recent viral content on these themes
   - what's resonating with young founders and entrepreneurs this week
3. generate all content assets (see mediums below)
4. score each item with ICE (see scoring below)
5. write hooks.md

## mediums

**linkedin** — 5 hooks (opening lines only, not full posts)
- one line that stops the scroll
- counterintuitive, bold, or uncomfortably personal
- no "have you ever...", no rhetorical questions leading with you

**twitter/x** — 5 full tweets
- written in full, not just hooks
- naval ravikant / dan koe style: expose a truth that sounds simple but takes paragraphs to explain
- lowercase, no hashtags, no emojis, no engagement bait
- 1-3 sentences max
- good tweet: "you don't have a focus problem. you have a values problem." — reframes, cuts deep, forces self-reflection
- good tweet: "the people who changed your life didn't try to. they just lived in a way that made you want to." — reveals something people felt but couldn't say
- rami's voice: personal, direct, names concepts, ends sharp

**instagram/tiktok** — 5 hooks + 5 headline options
- hook: the first spoken sentence of a short video (grabs in 2 seconds)
- headline: the text overlay or caption title (5-8 words, punchy)

**youtube** — 3 title + subtitle pairs + 1-2 sentence video description
- title: searchable and compelling (not clickbait)
- subtitle: expands on the title, adds intrigue or specificity

## ice scoring

score each item individually. be honest - score based on evidence from trend research, not optimism.

- **impact** (1-10): potential reach and resonance with rami's audience (young founders, entrepreneurs, gen z)
- **confidence** (1-10): how likely this is to land, based on trend data and rami's track record with similar content
- **ease** (1-10): how easily this can be produced from the existing transcript material (10 = transcript already covers it fully)
- **ice score** = (impact + confidence + ease) / 3

medium ice = average ice of all items in that medium
overall content ice = average of all medium ice scores

## output format

```markdown
# hooks: {transcript title}

**overall ice score:** {x.x}/10

---

## linkedin hooks

| # | hook | I | C | E | ICE |
|---|------|---|---|---|-----|
| 1 | ... | 8 | 7 | 9 | 8.0 |

**medium ice:** {x.x}/10

---

## twitter/x

| # | tweet | I | C | E | ICE |
|---|-------|---|---|---|-----|
| 1 | ... | | | | |

**medium ice:** {x.x}/10

---

## instagram/tiktok

### hooks
| # | hook | I | C | E | ICE |

### headlines
| # | headline | I | C | E | ICE |

**medium ice:** {x.x}/10

---

## youtube

| # | title | subtitle | description | I | C | E | ICE |
|---|-------|----------|-------------|---|---|---|-----|

**medium ice:** {x.x}/10

---

## trend context

what's currently trending that informed these hooks and scores:
- {bullet point with source}
```
