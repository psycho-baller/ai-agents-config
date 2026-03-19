---
name: content-research
description: Deep research on a raw transcript - validates and invalidates every claim with 10+ cited web sources, outputs a research.md file. Run this as the first step before content-hooks or content-writer.
---

# content-research

validates and invalidates every claim in a raw transcript using deep web research. produces a structured research file as input for the next pipeline steps.

## inputs

- `file`: path to a transcript `.md` file (required)
- output goes to `/Users/rami/Documents/life-os/notes-processing/{filename}/research.md`
  where `{filename}` = the source file's name without extension

## steps

1. read the transcript file in full
2. extract every claim, assertion, statistic, and strong opinion the speaker makes - list them before researching
3. for each claim, do a targeted web search to validate or invalidate it:
   - search for direct evidence (studies, data, expert consensus)
   - search for counterarguments or contradicting evidence
   - note the source url, publication, and date
   - aim for 10+ sources total across all claims
4. for the topic overall, do 1-2 searches for broader context the transcript may have missed
5. write research.md

## output format

```markdown
# research: {transcript title}

**source:** {original file path}
**researched:** {date}

## executive summary

{2-3 sentences: overall accuracy of the transcript's claims and the strongest insight from research}

## claims

### "{exact quote or close paraphrase of claim}"
- **verdict:** validated | invalidated | nuanced | unverifiable
- **evidence:** {what the research found - be specific, cite numbers/studies where possible}
- **sources:** [{title}]({url}), [{title}]({url})

{repeat for each claim}

## what the transcript missed

{bullet points: important angles, facts, or counterarguments not covered in the transcript that are worth knowing}
```

## notes

- be honest: if a claim is wrong, say so clearly
- "nuanced" means partially true or context-dependent - explain exactly how
- "unverifiable" means no reliable sources exist either way - don't fabricate
- create the output folder if it doesn't exist
