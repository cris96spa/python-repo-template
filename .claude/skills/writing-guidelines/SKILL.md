---
name: writing-guidelines
description: How to write natural-language text in this repository for its reader - documentation pages, READMEs, pull request descriptions, commit messages, review reports, docstring and comment prose, log and error messages. Use before writing or editing any of them.
---

# Writing Guidelines

Most of what we write is read by engineers who know the field but not the change in front of
them. They should finish a page understanding what it is about and why it matters, without
having to piece the story together themselves. These guidelines describe how to write for
that reader: decide what kind of text you are producing, lead with the big picture, say only
what the reader needs, and write prose that moves from one idea to the next.

They apply to every text written in natural language in this repository. Docstrings and
comments follow the [coding guidelines](../coding-guidelines/SKILL.md#docstrings) for their
format and this page for their prose.

## Know what you are writing

The first decision is not what to say but what kind of text you are writing. Each kind
answers a different question, and that question decides how much weight code and configs
deserve.

| Text | The reader asks | Lead with | Code and configs |
| --- | --- | --- | --- |
| Guide | How do I do this? | the task and its result | central: a working example to copy, explained as the reader uses it |
| Reference (config fields, CLI help, API) | What exactly does this accept? | the contract | central and complete: every field, type and default |
| Overview or design page | How does this work, and why this way? | the problem and the idea that solves it | a detail: name a class or field only where the reader needs a handle on it |
| Pull request description | What changes, why, and what should I look at? | the motivation and the design | rarely: reviewers read the diff, and a snippet earns its place only when it is the clearest statement of an interface |
| Commit message | What does this commit do, and why? | a one-line Conventional Commits summary | none |
| Review report | What is wrong, how badly, and what should change? | the verdict, then findings by priority | a file and line for every finding |

Mixing these registers is the most common way a text goes wrong. An overview that reproduces
config blocks buries its rationale under details the reader will look up later anyway. A
guide that explains the architecture before showing the command makes the reader wait for the
one thing they came for.

A pull request description deserves a closer look, because it is the text most often written
as an inventory. Reviewers want to understand the change well enough to judge the code they
are about to read. Tell them what problem the change solves, the idea behind the solution and
the alternatives it was preferred to, what it means for existing users, and how it was
verified. The diff already shows every file, field and test; repeating them adds length
without adding understanding.

## Lead with the narrative

Before writing, tell yourself the story in three or four sentences: what problem exists, what
this does about it, how it works at the level a newcomer needs, and what follows from it.
That story becomes the opening, and every later section expands one part of it.

Give the context before the claim. "Metrics go through the base `log`" means nothing until
the reader knows why the obvious call would be wrong. Describe the situation first, and the
decision it leads to second:

> The subclass overrides `log` to flush the metrics it has accumulated into whatever it is
> given. Logging the evaluation metrics through it would mix the two, so the callback calls
> the base `log`, which only records what it receives.

Within a paragraph, start from what the reader already knows and end on what is new, so the
next sentence can pick up where this one stopped. Open every paragraph with a sentence that
states its point. Someone who reads only the first sentence of each paragraph should still
follow the story, and someone who reads only the headings should see its outline rather than
a list of nouns.

## Choose what to say

Relevance matters more than completeness. For every piece of information, ask whether this
reader needs it at this point to understand or to act. The big picture always earns its
place. A mechanism earns it when it explains behavior the reader would otherwise find
surprising. Everything else belongs in the code, the reference pages or the commit history.

Four kinds of content almost never do:

- The history of the work: what an earlier commit did, what was tried and reverted, what a
  later commit fixed. Documentation describes how things are, so words like "now", "new" and
  "no longer" have no place in it. A pull request describes its final state, because that is
  what reviewers will merge.
- Inventories the reader can get elsewhere, such as every changed file, every field of a
  config or every test added.
- Bookkeeping about the writing itself, such as "as mentioned above", "this section
  describes", or which parts were moved, kept or cut.
- Knowledge that lives only in a chat, a review thread or someone's memory ("as discussed",
  "per the review"). State the fact or the reason itself, so it stands on its own.

Leaving things out is only half of it; the other half is not skipping what matters. Say why a
design was chosen over the obvious alternative, which limitation a user will run into, and
what changes for people already using the code. If a reader would finish a paragraph asking
"why?", the answer belongs in that paragraph.

Keep it true. Text that contradicts the code is worse than no text: a rename, a moved file or
a changed default updates the docs, docstrings, comments and config comments that mention it,
in the same change.

## Write fluent prose

Write in paragraphs of complete sentences, joined by the words that carry reasoning:
*because*, *so*, *which means*, *unless*, *instead*. Those words turn a set of facts into an
explanation. A bulleted list drops them and leaves the reader to rebuild the logic.

Use a list only for items that are truly parallel and independent, such as the steps of a
procedure, the options of a command or the breaking changes of a release. Keep lists one
level deep, and do not open every item with a bold label: when every line is emphasized,
nothing is.

A few habits make prose easier to follow:

- Use one term per concept, and define it once. If it is "the launcher's store" in one
  paragraph, it is not "the agent store" in the next.
- Prefer plain words to coined phrases. "The run directory" is clearer than "the
  serialization directory agreement mechanism".
- Name a code identifier when the reader will search for it, type it or see it in a log;
  otherwise name the concept.
- Write in the active voice, with the actor as the subject: "the command rejects the config",
  not "the config is rejected".
- Split a sentence that needs parentheses, stacked qualifications or a chain of semicolons
  into two.
- State each fact once, with the confidence it deserves. Do not hedge every claim, and do not
  restate a point in other words.

## Code, configs and diagrams

Code, configs and diagrams support the prose; they do not replace it. Introduce each one with
a sentence saying what it shows, and keep it to the smallest excerpt that shows it: three
relevant lines of YAML rather than the whole file.

In guides and references the example is often the main content, so it must be complete,
runnable and identical to what lives in the repository. Embed files with `--8<--` rather than
copying them. In overviews and pull request descriptions, a sentence that names the idea is
usually better than the code that implements it.

A diagram earns its place when it shows a structure or a flow that prose describes poorly:
steps that run across several processes, the components a request passes through, or what
depends on what. Draw one idea per diagram, label it in plain words rather than identifiers,
and keep it small enough to read without scrolling. A diagram that restates a three-item list
adds nothing.

In Mermaid, keep every label to a few words, at most about 25 characters per line, and break
a longer one with `<br/>`. Mermaid widens a node to fit its text, but it does not wrap
subgraph titles or edge labels, which are cut off or run over other shapes when they are
long. A label names a step; the explanation of the step belongs in the prose around the
diagram.

## Structure and length

Give each topic space in proportion to its importance to the reader. In a pull request that
introduces one main feature alongside supporting changes, the feature gets most of the
description and each supporting change gets a sentence or two. Order the sections from what
every reader needs to what only some do: the summary first, then how it works, then the
details, limitations and verification.

Keep headings short, and make them say what their section establishes. Each fact has one
home; other pages link to it instead of restating it. When the draft is done, cut until
removing anything more would lose meaning.

## The short forms

**Docstrings.** The first line says what the function returns or does, as a sentence ending
with a period. Document the contract: what the caller must provide, what it gets back, what
is raised and when, and side effects. Explain a non-obvious choice where it is made, in a
second paragraph, when the reader would otherwise "fix" it.

**Config field descriptions.** A field's `description` is what a user reads while writing a
config. State the field's effect and how it interacts with other fields, not its type or the
code that consumes it: "Number of times each sample of the dataset is evaluated", not "The
epochs value used by the pipeline".

**Comments.** Comments are rare, and each explains something the code cannot. A wrong comment
is the worst kind: fix or delete it. Say it in as few words as it needs, name the concrete
thing, write complete sentences, and commit no `TODO`s about the file being edited, no
commented-out code and no notes addressed to a reviewer.

**Log and error messages.** Say what happened and, for an error, what the reader can do about
it. Name the value involved: the path, the field, the received value. Never include secrets.
Use `%s` placeholders in logging calls, so formatting happens only when the line is emitted.

**Commit messages.** One line in [Conventional Commits](https://www.conventionalcommits.org/)
form, which `conventional-pre-commit` enforces and `python-semantic-release` reads: a type, an
optional scope naming the area, and a subject in the imperative mood, lower case, with no
trailing period, such as `feat(configs): reject a config linking to itself`. The subject
states the behavior the commit introduces, not the edit sequence. Add no body and no
attribution trailers.

## An example

The excerpt below is from a pull request description. Each line is accurate, but the section
reads as an inventory:

> ### Rollout evaluation
>
> - **Columns.** Each rollout carries `model_response`, `num_generated_tokens`,
>   `is_truncated` and `mean_logprob`.
> - **Best-model selection.** A `metric_for_best_model` under the callback's prefix that it
>   cannot log fails config validation. A missing metric is reported as NaN.
> - **Generation.** `generation` supports two modes: `colocate` or `server`.

A reviewer learns which fields exist but not what the feature is for, and every bullet starts
with a detail they cannot yet place. The same section written for that reader opens with the
problem and lets the details follow from it:

> Loss on the evaluation split measures how well the model predicts the reference answer one
> token at a time. It says nothing about what the model writes on its own, such as answers
> that never end. The rollout evaluation callback measures that instead: at points of the run
> chosen by its schedule, it has the model answer every evaluation prompt, scores the answers
> with the evaluation metrics, and reports the results alongside the trainer's own
> evaluation. Because the results join that evaluation, a run can pick its best checkpoint on
> them, for example on the share of answers in the expected format.

The rewrite drops the field names, which belong in the reference, and keeps the reasoning
that the original left out.

## Before you publish

Read the text again as its reader would, and check:

- whether the headings and the first sentence of each paragraph tell the story on their own;
- whether reading it aloud trips you up anywhere, since that is where a reader trips too;
- whether a paragraph leaves a "why?" unanswered;
- whether a sentence describes the history of the work or your own process rather than the
  subject;
- whether the register fits: config blocks in an overview, or a guide without a working
  example;
- whether the documentation still builds: `uv run properdocs build -f properdocs.yml`.

## References

- [Diátaxis](https://diataxis.fr/) separates tutorials, how-to guides, reference and
  explanation, because each serves a different need; the table above follows the same idea.
- [Google developer documentation style guide](https://developers.google.com/style): active
  voice, plain words and consistent terminology.
- George Gopen and Judith Swan, "The Science of Scientific Writing", *American Scientist*,
  1990: readers expect old information at the start of a sentence and new information at the
  end, and a paragraph's opening to say what it is about.
