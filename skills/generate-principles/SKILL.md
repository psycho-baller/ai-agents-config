---
name: generate-principles
version: 1.0.0
description: Generate evidence-backed personal principles from one markdown note or a batch of markdown notes, especially reflections, transcripts, generated metadata, journal entries, and Obsidian notes. Use this skill whenever the user asks to extract life principles, decision rules, lessons to live by, Ray Dalio-style principles, Atomic Habits-based behavior systems, or practical rules from reflections. This skill is agent-driven: the agent performs semantic extraction and the bundled script renders and validates the structured principles report.
---

# Generate Principles

Use this skill to turn markdown notes into personal principles Rami can actually live by.

The output is not motivational advice. A useful principle is a reusable decision rule backed by evidence from Rami's own notes.

This skill creates a principles report. It does not update note frontmatter and it does not maintain the recurring pattern files. Use `generate-metadata` for per-note metadata and `update-patterns` for living pattern files.

The agent owns judgment. The script owns structure.

- The agent reads the note or notes and decides which principles are real.
- The script renders the principles report from a JSON payload and validates required structure.
- The script does not call an AI API and cannot infer principles by itself.

## Core Outcome

For each target file or batch, produce a markdown report that answers:

- What principles does Rami already seem to live by?
- What principles should Rami live by based on repeated problems, mistakes, fears, desires, and wins?
- What evidence from the source notes supports each principle?
- How should each principle become a behavior system using Atomic Habits?
- Which principles are strong enough to adopt now and which are only candidates?

The report should help Rami decide how to behave differently. If the output only describes what the notes said, the skill failed.

Default to writing the report into scratch space, for example:

```bash
../scratch/generate-principles/
```

Only write permanent vault notes if the user explicitly asks.

## Principle Model

Use this working definition:

`When [situation or trigger], I will [specific behavior], because [evidence-backed reason].`

Good principles are:

- specific enough to guide behavior in a real situation
- grounded in source notes, not generic self-help
- reusable across future situations
- blunt about the failure mode they are correcting
- paired with a habit system so they can be practiced

Do not extract every takeaway as a principle. A takeaway becomes a principle only when it can guide future behavior in repeated situations.

Weak principles sound like slogans:

- `Be more confident.`
- `Work harder.`
- `Communicate better.`
- `Stay focused.`

Rewrite them into decision rules:

- `When an important conversation is coming, prepare the opening minute before the call so you do not enter the room vague or powerless.`
- `When attraction spikes before real-world knowledge exists, separate facts from fantasy before emotionally investing.`
- `Before starting work, decide what is explicitly not happening today so your mental RAM is not consumed by every possible task.`

Read `references/framework.md` only when you need the theory behind the framework or source links.

## Inputs To Use

Accept one markdown file or any number of markdown files.

When notes have `generate-metadata` frontmatter, use these fields as high-signal inputs:

- `summary`
- `core_themes`
- `practical_takeaways`
- `communication_flaws`
- `relationship_patterns`
- `identity_beliefs`
- `recurring_fears`
- `decision_principles`
- `open_problems`
- `experiments_to_run`
- `people_mentioned`
- `projects_mentioned`

Still read the body. Frontmatter is a map; the note body contains the real evidence, wording, and emotional texture.

If metadata and body disagree, trust the body and mention the tension in the reasoning.

## Status Values

Use one status per principle:

- `observed`: Rami already appears to live by this principle.
- `candidate`: the evidence suggests this principle, but it needs testing.
- `adopted`: the principle is strong, useful, and ready to become a living rule.
- `contradicted`: the notes contain meaningful evidence against this principle.
- `retired`: the principle is outdated or no longer useful.

Prefer `candidate` when uncertain. Use `adopted` only when the principle is specific, supported, and actionable.

## Domains

Use the closest domain:

- `communication`
- `relationships`
- `identity`
- `productivity`
- `career`
- `product_entrepreneurship`
- `life_philosophy`
- `health_spirituality`
- `personal_growth`

The schema is expandable. Add new domains to `schema.json` before using them.

## Principle Quality Score

Score every principle from 1 to 5 on each dimension. The script totals the score out of 25.

- `clarity`: Does the principle name a clear trigger and behavior?
- `evidence`: Is it supported by specific source notes or direct phrases?
- `actionability`: Can Rami practice it today or this week?
- `identity_alignment`: Does it connect to the kind of person Rami is becoming?
- `habit_design`: Does it include cue, response, reward, implementation intention, and friction design?

Interpretation:

- `21-25`: adopted-ready
- `16-20`: strong candidate
- `10-15`: needs more evidence or sharper behavior
- `<10`: rewrite or discard

Do not inflate scores. A principle with weak evidence should not score above 3 on evidence.

## Atomic Habits Design

Each principle needs a behavior system:

- `identity`: Who Rami is becoming when he lives by this principle.
- `cue`: The situation that should trigger the behavior.
- `craving`: The meaningful reason the behavior should feel worth doing.
- `response`: The smallest concrete behavior.
- `reward`: The immediate satisfying feedback after the behavior.
- `implementation_intention`: `When [time/place/situation], I will [behavior].`
- `habit_stack`: `After [existing habit/event], I will [new behavior].`
- `environment_design`: How to make the behavior obvious, easy, and visible.
- `friction_to_reduce`: What to remove so the good behavior is easier.
- `friction_to_add`: What to make harder so the old failure mode is less automatic.

Map the system to the practical habit laws:

- make it obvious through the cue and environment design
- make it attractive through the craving and identity
- make it easy through the response and friction reduction
- make it satisfying through the reward and review loop

If a field feels generic, make it smaller and more concrete.

## Quality Gate

Before writing the payload, check every principle:

- Does it follow `When [trigger], I will [behavior], because [reason]`?
- Does it cite at least one source note?
- Does it name the failure mode it prevents?
- Does it include a behavior small enough to practice this week?
- Does it avoid generic advice that could apply to anyone?

If a principle fails these checks, rewrite it, lower its score, or leave it out.

## Evidence Rules

Use wiki-links to source notes when possible.

Good evidence:

- `[[Sense of control determines communication performance]]: Rami notices his speaking improves when he feels in control before the interaction.`
- `[[Crush on Lebanese Girl and Unhealthy Expectations]]: attraction becomes fantasy before enough facts exist.`

Weak evidence:

- `Rami should communicate better.`
- `This seems important.`

Prefer direct phrases from the note when they identify the exact moment or problem. Keep quotes short.

## Execution Protocol

1. Resolve the target markdown file or files.
2. Read each full note, including frontmatter and body.
3. Identify principles using the principle model.
4. Score each principle honestly.
5. Write a JSON payload to `/tmp/generate-principles-<short-name>.json`.
6. Run the bundled script to render the report.
7. Run validation on the rendered report.
8. Report the output path and any principles that scored below 16.

For one report:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/generate-principles/scripts/generate_principles.py render --payload-file /tmp/generate-principles.json --output ../scratch/generate-principles/principles-report.md
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/generate-principles/scripts/generate_principles.py validate-report ../scratch/generate-principles/principles-report.md
```

To inspect the current schema:

```bash
uv run python /Users/rami/Documents/life-os/ai-agents-config/skills/generate-principles/scripts/generate_principles.py schema
```

## Payload Format

Use this JSON shape:

```json
{
  "report_title": "Principles from April transcriptions",
  "sources": [
    "Transcriptions/Sense of control determines communication performance.md"
  ],
  "principles": [
    {
      "title": "Prepare control before high-stakes conversations",
      "status": "candidate",
      "domain": "communication",
      "confidence": "medium",
      "source_notes": [
        "[[Sense of control determines communication performance]]"
      ],
      "principle": "When an important conversation is coming, I will prepare the opening minute before the call because my communication gets worse when I enter unclear and powerless.",
      "reasoning": "The note repeatedly connects communication performance to feeling in control before speaking.",
      "evidence": [
        "[[Sense of control determines communication performance]]: Rami links smoother communication to feeling prepared and in control."
      ],
      "identity": "I am the kind of person who creates calm before important conversations instead of hoping clarity appears live.",
      "cue": "A meeting, interview, hard conversation, or pitch is on the calendar.",
      "craving": "Feel grounded before entering the interaction.",
      "response": "Write the first minute, the desired outcome, and one question.",
      "reward": "Check off the preparation and enter the call with less mental noise.",
      "implementation_intention": "When a high-stakes conversation appears on the calendar, I will write the opening minute before the call starts.",
      "habit_stack": "After checking tomorrow's calendar, I will mark any conversation that needs a prepared opening minute.",
      "environment_design": "Keep a conversation-prep template visible in the daily note.",
      "friction_to_reduce": "Remove the need to invent the prep format each time.",
      "friction_to_add": "Do not join the call until the opening minute has been written.",
      "failure_mode": "Overpreparing into a script instead of creating calm direction.",
      "experiment": "For the next five important conversations, prepare the opening minute and rate communication control afterward.",
      "review_cadence": "Review after five conversations.",
      "score": {
        "clarity": 5,
        "evidence": 4,
        "actionability": 5,
        "identity_alignment": 4,
        "habit_design": 5
      }
    }
  ]
}
```

## Output Standard

Every principle must include:

- title
- status
- domain
- confidence
- source notes
- principle
- reasoning
- evidence
- Atomic Habits design
- failure mode
- experiment
- review cadence
- score

If the note does not support any real principle, say so and do not invent one.
