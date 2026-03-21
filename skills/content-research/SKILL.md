---
name: content-research
description: Deep research on a raw transcript - validates and invalidates every claim with cited web sources, outputs a research.md file. Run this as the first step before content-hooks or content-writer.
---

# content-research

validates and invalidates every claim in a raw transcript using deep web research. produces a structured research file as input for the next pipeline steps.

## inputs

- `file`: path to a transcript `.md` file (required)
- output goes to `/Users/rami/Documents/life-os/notes-processing/{filename}/research.md`
  where `{filename}` = the source file's name without extension

## preprocessing (do this before anything else)

transcripts contain Obsidian syntax that must be cleaned before processing:
- strip YAML frontmatter (everything between `---` and `---` at the top)
- convert wiki-links: `[[Note|display]]` → `display`, `[[Note]]` → `Note`
- remove `## Related Notes` section and everything after it
- work with the clean plain text from here on

## steps

1. read and clean the transcript (see preprocessing above)
2. assess transcript length:
   - **short** (< 150 words): the whole transcript is likely one insight — treat it as a single claim and do deep research on that one idea, producing 3-5 sources
   - **medium** (150-500 words): extract 3-5 claims
   - **long** (500+ words): extract every significant claim, assertion, statistic, and strong opinion — aim for 10+ sources total
3. for each claim, do targeted web searches to validate or invalidate:
   - search for direct evidence (studies, data, expert consensus)
   - search for counterarguments or contradicting evidence
   - note source url, publication, and date
4. do 1-2 searches for broader context the transcript may have missed
5. write research.md

## handling scattered / multi-topic transcripts

if the transcript jumps between many unrelated topics, identify the 1-2 dominant threads (the ideas the speaker returns to or spends the most time on) and focus research there. note the other topics briefly under "what the transcript missed" as "out of scope for this run."

## output format

```markdown
# research: {transcript title}

**source:** {original file path}
**researched:** {date}

## executive summary

{2-3 sentences: overall accuracy of the claims and the strongest insight from research}

## claims

### "{exact quote or close paraphrase}"
- **verdict:** validated | invalidated | nuanced | unverifiable
- **evidence:** {specific findings — cite numbers/studies where possible}
- **sources:** [{title}]({url}), [{title}]({url})

{repeat for each claim}

## what the transcript missed

{bullet points: important angles, facts, or counterarguments not in the transcript}
```

## notes

- be honest: if a claim is wrong, say so clearly
- "nuanced" = partially true or context-dependent — explain exactly how
- "unverifiable" = no reliable sources either way — don't fabricate
- create the output folder if it doesn't exist
