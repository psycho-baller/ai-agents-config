---
name: content-writer
description: Writes a master long-form piece from a raw transcript, research, and hooks. The raw transcript is the foundation - research adds depth, hooks provide the angle. Requires research.md and hooks.md to exist first.
---

# content-writer

writes one master long-form piece per transcript. stays close to rami's original voice and structure. infuses research where it deepens a point. opens with the highest-scoring hook.

## inputs

- `file`: path to a transcript `.md` file, or folder name inside `notes-processing/`
- requires `research.md` and `hooks.md` in `notes-processing/{filename}/`
- output: `notes-processing/{filename}/content.md`

## preprocessing

before writing, clean the transcript:
- strip YAML frontmatter (between `---` markers at the top)
- convert wiki-links: `[[Note|display]]` → `display`, `[[Note]]` → `Note`
- remove `## Related Notes` section and everything after it
- write from clean text — the final piece should contain none of this syntax

## steps

1. read: clean transcript, research.md, hooks.md
2. pick the highest overall ICE-scored hook from hooks.md — this becomes the title and opening angle
3. write the master piece (see rules below)
4. write content.md

## writing rules

**the transcript is sacred.**
- follow the order and structure of rami's original thoughts — don't reorganize
- preserve his examples, personal stories, and strong phrasing exactly
- only touch what research improves: add a stat, reframe an overstatement, deepen a point
- if a claim was fully invalidated in research.md, reframe it to the nuanced version — don't fabricate, don't cut his genuine experience

**infuse research, don't cite it.**
- weave evidence into the flow naturally — no "research says" headers
- research should feel like rami discovered these facts himself, not like a bibliography
- one or two data points per piece is enough — don't over-reference

**rami's voice — read `/Users/rami/Documents/life-os/ai-agents-config/skills/rami-voice/SKILL.md` for the full rules. the NON-NEGOTIABLE RULES section is the one you need. critical rules below:**

structural:
- lowercase conversational — no corporate polish, no capitalization except proper names
- **normal prose paragraphs** — this is an article, not a poem. group related sentences into paragraphs of 2-5 sentences. do not put each sentence on its own line.
- builds personal → universal: starts with his specific experience, ends at a principle anyone can use
- the closer is the sharpest line — not a summary, not a CTA — something that makes you stop
- no hashtags, no emoji clusters, no leading questions as opening hooks
- vulnerable but not soft — struggles are evidence for a point, not sympathy bait
- honest about mistakes without shame — shares what didn't work because it's useful to others
- names concepts when the opportunity is natural ("chalant", "freedom of emotion")
- do not add moral lessons or tidy conclusions rami didn't express himself
- keep paragraph breaks natural — break when the thought shifts, not after every sentence

never (hard rules, no exceptions):
- **no em dashes** — use a comma, colon, parentheses, or a new sentence instead
- **no semicolons**
- **no hedging qualifiers**: "it's worth noting", "it's important to consider", "one could argue", "it's interesting that"
- **no "you should"** — use direct imperatives: "do this", not "you should do this"
- **no corporate vocabulary**: leverage (as verb), utilize, implement, unpack, delve, game-changing, paradigm shift
- **no summary conclusions** — the close is a charge or a challenge. never a recap of what was just said
- **no formal transitions**: furthermore, additionally, in conclusion, moving on, with that said

**length:** as long as the content demands. no padding, no filler. short transcripts produce short pieces — that's fine.

## output format

```markdown
# {title — best hook from hooks.md}

{master long-form piece}

---
*source: {original transcript path}*
*hook used: {hook text} (ICE {score})*
```
