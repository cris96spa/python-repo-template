---
name: review-guidelines
description: How to review a change, branch or pull request in this repository - scoping, the design and house-style checks, the report structure, the finding format and the P0-P3 priorities. Use whenever asked to review, audit or give feedback on code.
---

# Review Guidelines

A review explains whether a change solves its intended problem with a clear, Pythonic design
that remains understandable and economical to maintain. Review both observable behavior and
the reasoning behind the structure. Passing tests and lint checks are evidence, not
substitutes for this assessment.

The standard a change is held to is the
[coding guidelines](../coding-guidelines/SKILL.md), and the prose of the report follows the
[writing guidelines](../writing-guidelines/SKILL.md). This page is the procedure: how to scope
a review, what to check and how to deliver the result. Where the two seem to differ, the
coding guidelines win.

## Establish the scope

- Record the base and head revisions and the intended user outcome.
- Read `CLAUDE.md`, the documentation of the area the change touches, the relevant configs,
  callers and tests before judging an isolated implementation.
- Identify compatibility requirements, supported Python versions, the optional dependencies
  the change needs and intentional limitations. Distinguish documented intent from inferred
  rationale.
- Understand how the change integrates with existing behavior before judging its parts.
- Only what the default branch already ships can break. Changes to unreleased features are
  not breaking changes.
- Existing code does not yet follow every rule. Review what the change writes or modifies; do
  not report untouched code for not conforming, but do report a change that copies a
  non-conforming pattern into new code.
- Review first. Do not implement refactors or change behavior unless asked.

## Assess the design

Describe the end-to-end flow in ordinary language: what starts the operation, which
components participate, what each owns, and where data and failures go. Then, for every
substantial component or abstraction, ask:

- What responsibility does it own, and why is that responsibility needed?
- Are its inputs, outputs, dependencies and side effects explicit?
- Does it have a distinct reason to change, or duplicate another component's job?
- Could it be removed or merged without losing a useful boundary?
- Would an additional boundary reduce actual coupling or complexity? Name the concrete
  benefit before recommending another interface, service or layer.
- Does the implementation match the documented design and existing conventions?

Use the [design principles](../coding-guidelines/SKILL.md#design-principles-and-patterns) as
reasoning tools, not as a checklist of abstractions to introduce. For each recommendation,
name the concrete problem, the simplest viable change and its tradeoff.

- Prefer the smallest object model that serves today's behavior. A module of free functions
  where behavior belongs on a class is a finding; so is a speculative registry, factory or
  layer.
- Work through adding one hypothetical alternative implementation of a contract the change
  touches: list what it would implement and which existing files would need changes. Do not
  build it. Report any contract gap it reveals.
- Recommend a new pattern only when a concrete change or failure scenario demonstrates its
  benefit. Explain which responsibility it clarifies, what code it removes and what
  indirection it adds. State explicitly when the existing design is the better choice.

## Check the house style

Walk the change through the house-style sections of the coding guidelines. These checks are
the ones most often missed.

**Object-oriented design.**

- Does each behavior live on the object that holds its data, or has a `match`/`if` chain on a
  type code replaced a missing class hierarchy?
- Is every override marked `typing.override`, and does a new abstract base enforce it?
- Is anything constructed at module level and imported elsewhere?
- Does every random draw take the run's seed explicitly?
- Is every input validated before the expensive or irreversible step, and does a failure
  raise a named exception?

**File conventions and docstrings.**

- No module docstring, no `from __future__ import annotations`, private instance attributes,
  constants at the right scope, user-tunable values in configuration.
- Is an optional dependency imported at the module level of a config module?
- Was generated code edited by hand rather than regenerated?
- Does `Raises:` list exactly the exceptions the body raises?

**Methods tell their story.** For each changed method:

1. Read only its main flow. Can you explain what it does, in order, from the names?
2. Identify blocks that force the reader to decode implementation details before
   understanding the next step. They should be cohesive private helpers.
3. Check that names express intent and expected outcomes, including mutation or side effects.
4. Flag comments that would become redundant with better names and structure.
5. Check that extraction clarifies the flow rather than scattering it across trivial
   wrappers.

**Domain structure is modeled, not spelled in strings.** Look for hardcoded statuses, roles,
field names, filenames, protocol keys and import targets; dictionaries built only to be
validated into a known model; `model_copy(update={...})`; and dotted class paths written by
hand. Do not report a static string where the format requires one, such as YAML, or where
importing the symbol would break optional-dependency isolation; check instead that the path
is validated at the boundary.

**Config files.** Did a renamed or moved class leave a config naming it by string? The
project's config validation must pass.

## Check correctness

Trace successful, partial, failed, interrupted, retried and resumed operations. Check
validation timing, resource cleanup, persistence ordering, idempotency, configuration
mutation, provenance and exception propagation. Inspect concurrency assumptions where state
or external identities are shared.

Review changes to shared infrastructure against every existing consumer, not just the new
feature. Check optional-dependency isolation and packaging. Verify third-party assumptions
against the installed implementation or authoritative documentation; state when a claim could
not be verified.

## What to look for

Beyond the design questions above, these defects recur. Group findings under them when it
helps the reader.

| Category | Examples |
| --- | --- |
| **Reinvented wheels** | Reimplementing the project's own machinery; hand-copying fields of a third-party dataclass instead of deriving them; a hand-rolled algorithm a declared dependency already provides. |
| **Overcomplicated** | A method that ignores `self` and forwards to a function; a generic or abstract layer with one concrete user; a union alias with one member; a function-level import working around a cycle the layering created. |
| **Dead code and leftovers** | Scratch files, committed `TODO`s about the file being edited, parameters no caller passes, defaults restated in several places so some are unreachable, values computed and then discarded. |
| **Compliance** | Undeclared direct dependencies; local path sources or absolute paths in `pyproject.toml` and example files; `except Exception` that only logs; a default whose change silently alters existing configs; untyped signatures. |
| **Tests** | New behavior with no tests; tests asserting values captured from the implementation; tests reading source text instead of exercising behavior; tests that cannot fail. |
| **Comments and docs** | Comments that are wrong, stale, restate the code or are longer than what they say; docstrings describing code that is not there; docs that no longer match the code. |

Leave to the tooling what the tooling checks: do not fill the review with formatting and lint
observations.

## Evidence and validation

- Read tests for intended behavior and missing scenarios. Check that they assert
  hand-computed or closed-form values, and that each can fail: break the code it protects.
- Run `make format-check`, `make lint`, `make lint-doc` and the focused tests when feasible.
  Do not download large artifacts, change dependencies or contact paid services without
  asking.
- For each defect, give a concrete trigger, affected behavior and precise code reference.
  Distinguish reproduced failures from reasoned risks.
- Report what could not be checked, and do not imply that mocked tests validate the
  third-party integration.

## Review deliverable

Human time is precious. The review must be condensed but complete: minimize the reader's
effort while preserving everything needed to assess the change and act on the findings. This
applies to both the review document and the message presenting it.

- Lead with the conclusion and highest-impact findings. Make priorities and next actions
  immediately visible.
- State each finding once: the problem, concrete evidence or trigger, impact and recommended
  action. Include precise references instead of reproducing large code blocks or narrating
  the investigation.
- Group related observations by root cause. Remove repeated explanations, filler, exhaustive
  inventories and details that do not affect a decision.
- Scale detail to the change's complexity and risk. Cover relevant review dimensions without
  forcing a separate section for every checklist item.
- Preserve material tradeoffs, uncertainty and validation limits. Brevity must not hide
  qualifications or leave the reader to reconstruct the reasoning.
- When delivering a separate report, keep the accompanying message to the overall assessment,
  essential findings, validation limits and a link to the report.
- Before delivery, remove any sentence that adds no distinct information.

### Contents

Start with the overall assessment and the most consequential findings. Include:

1. The architectural narrative and rationale, including boundaries worth retaining.
2. Prioritized findings with file and line references, evidence, impact and a proportionate
   recommendation. Group related symptoms under their root cause.
3. The alternative-implementation walkthrough and any resulting contract gaps.
4. House-style, naming, documentation and duplication improvements, separated from defects.
5. Validation performed, remaining uncertainty and questions requiring author input.
6. A suggested order for addressing the findings, without making those changes as part of the
   review.

### Finding format

Give each finding an identifier, a priority, the problem with its evidence, the action as a
checkbox, and a **Check**: a concrete, observable condition that shows the finding is
resolved. A check turns "fixed" from an opinion into something the author and the reviewer
can both verify.

```markdown
### B1. Metric application reimplements `RowOperatorBatcher` — **P1**

`_apply_metric` and `_apply_metrics` ([rollout_evaluation.py:385-402](path#L385-L402))
dispatch every row at once with no concurrency limit, duplicating `RowOperatorBatcher`,
which bounds concurrency with a semaphore.

- [ ] Replace both with `RowOperatorBatcher`, converting the frame at the boundary.

**Check:** `grep -c "asyncio.gather" rollout_evaluation.py` returns 0, or a comment names
the reason the batcher was not usable.
```

Prefer checks that are cheap to run: a command and its expected output, a test that must
exist and pass, a scenario that must now fail loudly instead of silently. Omit the check only
when the action itself is the verification, as in "fix the sentence".

### Priorities

- **P0 — Critical:** immediate, broad failure or serious irreversible harm, such as a run
  that silently uses the wrong data or overwrites a published artifact.
- **P1 — High:** a significant supported workflow is broken or a central design requirement
  is blocked; address before merging.
- **P2 — Medium:** a concrete edge-case defect or material maintainability problem.
- **P3 — Low:** a localized clarity improvement or optional simplification.

Label design recommendations and preferences explicitly; do not present them as runtime
defects. A structural question that needs the author's decision rather than a code change is
labeled as such. Explain tradeoffs and credit deliberate choices when evidence supports them.
