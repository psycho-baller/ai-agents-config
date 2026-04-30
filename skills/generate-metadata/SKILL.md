---
name: generate-metadata
version: 1.1.0
description: Generate and validate structured frontmatter metadata for markdown transcriptions and spoken notes. Use this skill whenever the user asks to process raw transcriptions, enrich Letterly/voice notes, add Obsidian metadata, classify reflections, extract communication flaws, identify beliefs/fears/problems/takeaways, or prepare notes before moving them from unprocessed to final transcription outputs. This skill is especially important for agent-driven workflows because the agent performs semantic extraction and the bundled Python script performs deterministic merge/validation.
---

# Generate Metadata

Use this skill to turn a raw markdown transcription into a structured Obsidian note with queryable top-level frontmatter.

The agent owns judgment. The script owns structure.

- The agent reads the note and decides what the metadata should say.
- The script merges the metadata into YAML frontmatter and validates shape.
- The script does not call an AI API and cannot infer metadata by itself.

## Core Outcome

For each target markdown file, produce valid frontmatter metadata that helps Rami later answer:

- What kind of note is this?
- What exact situation does this note capture?
- What problems, fears, beliefs, decisions, and patterns showed up?
- What should Rami actually do differently?
- Which people, projects, and concepts should be linked in Obsidian?

Preserve existing frontmatter such as `Status`, `tags`, `Links`, and `Created`. Overwrite only the managed metadata fields.

## Managed Fields

The script manages these top-level frontmatter fields:

- `metadata_schema_version`
- `metadata_generated_at`
- `note_types`
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

Use strings and lists of strings only. Do not generate nested objects.

## Allowed Note Types

Read the current allowed values from `schema.json` when unsure. Current values:

- `self_reflection`
- `problem_solving`
- `emotional_processing`
- `communication_analysis`
- `relationship_family`
- `product_entrepreneurship`
- `content_idea`
- `task_planning`
- `career_work`
- `life_philosophy`

Use `note_types` as a list. Each note needs at least one value. Use multiple values when the note blends categories.

## How To Read A Note

Treat the main transcription body as the source of truth. Existing `## Connections`, `## Related Notes`, frontmatter, and wiki-links are useful context, but the metadata should describe what Rami actually said in the note.

When a note rambles across several topics, identify the main job the note is doing. Common jobs in Rami's notes:

- debugging a personal problem
- processing an emotional event
- extracting a lesson from a social or work interaction
- thinking through a product or entrepreneurship direction
- turning a lived experience into content
- clarifying values, identity, purpose, or life philosophy
- making a plan or deciding what to do next

Do not summarize the note as if it were a neutral article. Write metadata for future Rami trying to remember, search, and act on his own spoken thoughts.

## Field Guidance

`summary`

Write a medium-sized, specific summary. It should be enough for Rami to recognize the exact note without opening it. Mention the concrete situation, not just the abstract theme.

Good:
`Reflection after the Purpose interview where Rami notices that feeling in control makes his communication smoother, then turns that into an Audora product direction around pre-meeting preparation.`

Weak:
`A note about communication and product ideas.`

`core_themes`

Use descriptive phrases, not generic tags. Prefer `feeling in control before high-stakes conversations` over `control`.

`practical_takeaways`

Write direct commands to Rami. Make them personalized to his actual patterns and problems.

Good:
`Prepare the first minute before important conversations so you do not enter the meeting feeling vague or powerless.`

Weak:
`Preparing for conversations can be useful.`

`communication_flaws`

Use blunt direct phrases when the note reveals a communication issue. Examples:

- `overexplaining`
- `approval_seeking`
- `avoiding_direct_conflict`
- `delayed_response`
- `performing_confidence_instead_of_being_clear`

`relationship_patterns`

Capture patterns involving family, friends, romantic interest, social approval, loyalty, attachment, boundaries, or repeated interpersonal behavior.

`identity_beliefs`

Capture beliefs Rami expresses about himself, his role, his purpose, his limitations, or what kind of person he is. These can be full sentences when needed.

`recurring_fears`

Use direct phrases for fears and anxieties. Examples:

- `fear_of_rejection`
- `fear_of_losing_control`
- `fear_of_wasting_potential`
- `fear_of_being_misunderstood`
- `fear_that_opportunities_will_disappear`

`decision_principles`

Capture reusable rules Rami seems to be forming, especially around work, product, relationships, communication, time, purpose, or risk.

`open_problems`

Write unresolved questions or problems the note raises. Use clear natural language.

`experiments_to_run`

Write concrete tests Rami can try. These should be action-oriented and small enough to execute.

`people_mentioned`

Use Obsidian wiki-links when names are clear, for example `[[Connor]]`. Keep people out if the note only says generic groups like "people" or "women" unless the concept itself should be linked elsewhere.

`projects_mentioned`

Use wiki-links for concrete projects, companies, apps, communities, content projects, or ventures, for example `[[Audora]]`, `[[Purpose]]`, `[[The Chalant Society]]`.

## Wiki-Link Policy

Prefer wiki-links wherever they improve future navigation. Use them in any field, not only people/projects.

Use existing links from the note body when they fit. If a concept clearly deserves to become a note but may not exist yet, still use a wiki-link. Avoid over-linking generic words that do not help future search.

Good:
`Build [[Audora]] around pre-meeting control instead of generic meeting transcription.`

Weak:
`Build [[software]] around [[things]] and [[people]].`

## Execution Protocol

1. Resolve target files from the user request.
2. Read each full markdown file.
3. Extract metadata for each file using every managed field.
4. Put empty arrays in list fields with no signal.
5. Write the metadata payload to `/tmp/generate-metadata-<short-name>.json` or a batch file in `/tmp/`.
6. Run the bundled script to merge metadata into frontmatter.
7. Run validation after applying metadata.
8. Report which files passed and which failed.

For one file:

```bash
python3.12 /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py apply path/to/note.md --metadata-file /tmp/metadata.json
python3.12 /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py validate path/to/note.md
```

For many files:

```bash
python3.12 /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py apply-batch /tmp/metadata-batch.json
python3.12 /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py validate path/to/one.md path/to/two.md
```

To inspect the current schema:

```bash
python3.12 /Users/rami/Documents/life-os/ai-agents-config/skills/generate-metadata/scripts/generate_metadata.py schema
```

## Payload Format

Single-file payload:

```json
{
  "note_types": ["communication_analysis", "product_entrepreneurship"],
  "summary": "Reflection after a strong Purpose interview where Rami notices that feeling in control makes his communication smoother, then converts that insight into an Audora direction around pre-meeting preparation.",
  "core_themes": [
    "feeling in control before high-stakes conversations",
    "using personal communication struggles as product insight"
  ],
  "practical_takeaways": [
    "Prepare the first minute before important conversations so you enter with control instead of vagueness.",
    "Test [[Audora]] with one narrow pre-meeting use case before exploring mid-meeting feedback."
  ],
  "communication_flaws": [
    "fear_of_losing_control_mid_conversation",
    "overexplaining_when_self_concept_feels_unclear"
  ],
  "relationship_patterns": [],
  "identity_beliefs": [
    "I communicate best when I feel in control of how I explain myself and my work."
  ],
  "recurring_fears": [
    "fear_of_becoming_my_old_self_in_high_pressure_conversations"
  ],
  "decision_principles": [
    "Start with the smallest product test that proves the emotional behavior."
  ],
  "open_problems": [
    "How can [[Audora]] help someone feel in control before a meeting without becoming another generic note-taker?"
  ],
  "experiments_to_run": [
    "Run mock interviews immediately before real interviews and track whether the first minute feels more controlled."
  ],
  "people_mentioned": ["[[Connor]]"],
  "projects_mentioned": ["[[Audora]]", "[[Purpose]]"]
}
```

Batch payload:

```json
{
  "files": [
    {
      "path": "unprocessed/Example.md",
      "metadata": {
        "note_types": ["self_reflection"],
        "summary": "Specific summary of this note.",
        "core_themes": [],
        "practical_takeaways": [],
        "communication_flaws": [],
        "relationship_patterns": [],
        "identity_beliefs": [],
        "recurring_fears": [],
        "decision_principles": [],
        "open_problems": [],
        "experiments_to_run": [],
        "people_mentioned": [],
        "projects_mentioned": []
      }
    }
  ]
}
```

The script fills `metadata_schema_version` and `metadata_generated_at`; the agent does not need to provide them.

## Failure Behavior

If validation fails, leave the file where it is and report the validation errors. Do not move the file. Do not delete content. Do not rewrite unrelated frontmatter to fix style.

If a note is too vague to infer a field, use an empty array for that list field. Do not invent people, projects, or decisions.

## Quality Bar

A good output should feel useful six months later. It should be compact enough for Obsidian Properties and Dataview, but specific enough that Rami can search his vault and immediately understand why the note matters.

Avoid generic coaching language. Extract what is actually present in the note, then turn only the actionable parts into personalized commands.
