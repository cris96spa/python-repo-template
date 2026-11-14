---
name: writing-guidelines
description: How to write natural-language text in this repository for its reader - the documentation pages in docs/pages/ and their figure captions, READMEs, CLAUDE.md and the skills, pull request descriptions, commit messages, review reports, docstring and comment prose, log and error messages. Use before writing, rewriting, reviewing or restructuring any of them.
---

# Writing Guidelines

Most of what we write is read by someone who knows the field but not the thing in front of
them: an engineer starting a project from the template, a maintainer reviewing a change, or an
agent following the project's rules. They should finish a page knowing what it is about, why it
matters and what to do next, without having to piece the story together themselves. These
guidelines describe how to write for that reader: decide what kind of text you are producing,
put it where that reader looks, lead with the big picture, say only what the reader needs,
write prose that moves from one idea to the next, and test everything you tell them to do.

They apply to every text written in natural language in this repository: `README.md`, the
documentation pages in `docs/pages/` and their figure titles and captions, `CLAUDE.md` and the
skills, pull request descriptions, commit messages and review reports. Docstrings and comments
follow the [coding guidelines](../coding-guidelines/SKILL.md#docstrings) for their format and
this page for their prose.

The documentation's longer pages take their model from the long-form guides that Hugging Face
publishes on the engine that builds this documentation: the Smol Training Playbook, the
Ultra-Scale Playbook, the LLM Evaluation Guidebook and the Ultimate MoE Training Handbook.
Their techniques for carrying a reader through a long text are collected in
[Guide the reader through a long text](#guide-the-reader-through-a-long-text) and
[Back claims with evidence](#back-claims-with-evidence).

## Workflow

1. Name the reader and the question they bring, then pick the kind of text from the table
   below.
2. Decide where the text lives. If another page already covers the fact, link to it instead
   of writing it again.
3. Tell yourself the story in three or four sentences, and name the two to four ideas that
   frame it. That story becomes the opening.
4. Draft the text, expanding one part of the story per section.
5. Run every command and snippet you describe, and check every path, port and output against
   the repository.
6. Review the draft with the [checklist](#before-you-publish) at the end, then cut until
   removing anything more would lose meaning.
7. When a documentation page changed, run `npm run format --prefix docs` and
   `make doc-check`, then read the page as `make doc` serves it.

## Know what you are writing

The first decision is not what to say but what kind of text you are writing. Each kind
answers a different question, and that question decides how much weight code and configs
deserve.

| Text | The reader asks | Lead with | Code and configs |
| --- | --- | --- | --- |
| Landing page (`README.md`) | What is this, and how do I start? | what it is, then the shortest path to a run | only the quick-start commands; everything else is a link |
| Tutorial (the overview's quick start) | Can I get something working? | the result the reader will have | central: complete commands and files to copy, with a visible result after each step |
| How-to guide (updating from the template) | How do I do this? | the task and its result | central: a working command or snippet, explained as the reader uses it |
| Reference (config fields, CLI help, command tables, frontmatter fields) | What exactly does this accept? | the contract | central and complete: every field, type and default, and what it does not cover |
| Explanation (an overview or design page) | How does this work, and why this way? | the problem and the idea that solves it | a detail: name a class or field only where the reader needs a handle on it |
| Figure title and caption (`HtmlEmbed` `title` and `desc`, `Image` `caption`) | What am I looking at, and can I trust it? | the claim the figure supports | none; state the data source, and say when values are illustrative |
| Agent instructions (`CLAUDE.md`, `.claude/skills/`) | What must I do or avoid here? | the rule, with its reason when not obvious | paths and commands exactly as they are typed |
| Pull request description | What changes, why, and what should I look at? | the motivation and the design | rarely: reviewers read the diff, and a snippet earns its place only when it is the clearest statement of an interface |
| Commit message | What does this commit do, and why? | a one-line Conventional Commits summary | none |
| Review report | What is wrong, how badly, and what should change? | the verdict, then findings by priority | a file and line for every finding |

Mixing these registers is the most common way a text goes wrong. An explanation that
reproduces config blocks buries its rationale under details the reader will look up later
anyway. A how-to guide that explains the architecture before showing the command makes the
reader wait for the one thing they came for. A tutorial that offers choices ("you can use
either base class") stalls a learner who cannot yet judge them, so a tutorial makes the
choices and a how-to guide explains them.

A pull request description deserves a closer look, because it is the text most often written
as an inventory. Reviewers want to understand the change well enough to judge the code they
are about to read. Tell them what problem the change solves, the idea behind the solution and
the alternatives it was preferred to, what it means for existing users, and how it was
verified. The diff already shows every file, field and test; repeating them adds length
without adding understanding.

## Put each fact in one place

The documentation is one site, served by `make doc` and published on GitHub Pages. Each page
in `docs/pages/` owns one subject, and `docs/pages/pages.json` lists the pages in reading
order. Put a fact on the page whose reader needs it, and add to an existing page before adding
a new one. `README.md` introduces the project to visitors on GitHub and links to the site,
`docs/README.md` explains the `docs/` folder, and `CLAUDE.md` gives agents the project's rules
and points to the skills that hold its standards.

Give each fact one home, chosen by the reader who needs it, and link to it from anywhere else
it matters. Two copies of a port number, a file path or a procedure drift apart, and the reader
who finds the stale one has no way to tell. A short restatement is fine when the reader needs
it to follow the current page, as long as the details stay in one place.

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

## Guide the reader through a long text

The Hugging Face playbooks keep readers with them across tens of thousands of words, and the
techniques they use work as well for a multi-page documentation site or a single long page.

Open with the question the reader brings, or with a claim and its evidence, and then say what
the text gives them. The evaluation guidebook opens on "How can one know if a model is
_good_?". The MoE handbook opens on "The frontier is sparse." and backs it in the next
sentence: 18 of the 20 highest-scoring open-weights models are mixtures of experts. Either
way, the reader knows within one paragraph why the text exists. A history of the project or a
list of its features cannot do that.

Say who the text is for and how to read it. State what the reader must already know and
have, then give each kind of reader a path. The MoE handbook sends readers who have trained a
dense model to its setup chapter, and readers more curious about how MoEs work than about
running one straight to its anatomy chapter. It also gives readers with one GPU, or none, a
section saying what they can still run and what to read for the method alone. Here, the
equivalent reader browses the repository on GitHub without installing anything, so say what
they can learn from the page as it stands.

Name the frame early and return to it. The Ultra-Scale Playbook reduces every technique to
three constraints (memory, compute and communication) and weighs each new method against
them. The MoE handbook names three new challenges (the router, the load balance and the
token exchange) and gives each its own sections. A frame of two to four parts lets the reader
place every later detail. Name it in the opening, keep the same names throughout, and do not
add a fifth part halfway through.

Let each section answer the question the previous one leaves open. The MoE handbook ends
almost every section by stating what is settled and asking what is not: "Crowded experts are
the first real failure mode of an MoE, so how do we keep tokens spread evenly over the
experts while the router keeps learning?" The next section opens by answering it. That bridge
turns a sequence of topics into one argument, and it tells the reader why the next section
exists before they start it. Use it at section boundaries, and always answer the question in
the next section's opening.

Introduce a concept when the reader first needs it, not in a block of definitions up front.
Define it in plain words at that point, inline or with `Glossary`, and give an abstract idea a
familiar comparison. The evaluation guidebook explains contamination as "evaluating a student
on questions it already knows in advance". The MoE handbook turns monitoring on at the start,
but introduces each metric in the section that first uses it.

Show the destination early. The Ultra-Scale Playbook puts its memory calculator in the
introduction and tells readers not to worry if it means nothing yet, because the book is
there to explain it. A finished result near the top, such as the output of the command the
page builds up to, shows readers what they will be able to do.

After a long stretch of explanation, turn it into a recipe. The Ultra-Scale Playbook pauses at
"Our journey up to now" for a numbered recipe built from the previous sections, followed by a
worked example with real numbers. The evaluation guidebook closes long sections with a short
note of takeaways. A recap is the one place where repeating earlier content earns its place,
because it changes the content's form from explanation to procedure.

Organize troubleshooting by what the reader sees. The MoE handbook's map starts from how a run
fails, names the first signal of the failure, and points to the section that explains the
cause. A reader with a problem knows the symptom, not the cause, so the map starts there.

Not everything in these guides transfers. They are long, informal and occasionally hurried.
Leave out superlatives in titles, an emoji on every callout, and first-person opinions on pages
no single author signs. Keep humor to a `Sidenote`, where a joke that misses costs the reader
nothing, and never put it in a step or a contract.

## Choose what to say

Relevance matters more than completeness. For every piece of information, ask whether this
reader needs it at this point to understand or to act. The big picture always earns its
place. A mechanism earns it when it explains behavior the reader would otherwise find
surprising. Everything else belongs in the code, the reference pages or the commit history.

Four kinds of content almost never do:

- The history of the work: what an earlier commit did, what was tried and reverted, what a
  later commit fixed. Documentation describes how things are, so words like "now", "new",
  "currently" and "no longer" have no place in it. A pull request describes its final state,
  because that is what reviewers will merge.
- Inventories the reader can get elsewhere, such as every changed file, every field of a
  config or every test added.
- Bookkeeping about the writing itself, such as "as mentioned above", "this section
  describes", or which parts were moved, kept or cut.
- Knowledge that lives only in a chat, a review thread or someone's memory ("as discussed",
  "per the review"). State the fact or the reason itself, so it stands on its own.

Leaving things out is only half of it; the other half is not skipping what matters. Say why a
design was chosen over the obvious alternative, which limitation a reader will run into and
what to do about it, and what changes for people already using the code. State a limitation
once, where the reader would first expect the missing behavior. If a reader would finish a
paragraph asking "why?", the answer belongs in that paragraph.

Keep it true. Text that contradicts the code is worse than no text: a rename, a moved file or
a changed default updates the docs, docstrings, comments and config comments that mention it,
in the same change.

## Back claims with evidence

The playbooks earn the reader's trust by showing their working. Report what you observed and
under which conditions, and give the number when there is one. The MoE handbook shows the
actual output of each benchmark command from its own cluster, records which nodes and
settings produced it, and keeps a source note for every measurement. Say what a result cannot
show as plainly as what it shows. The same handbook points out that its default and tuned runs
used different node pairs, so their difference cannot isolate the effect of the tuning.
Report what did not work, too, such as a step that ran only after local fixes, because the
reader will hit the same wall.

Help the reader decide, including when not to do something. The Smol Training Playbook opens
by arguing that most readers do not need to train a model at all, and gives a test: spend a
few days building on an existing model, and train only if that fails. A guide that says when
an option is the wrong choice is more useful than one that presents every option as viable.
In this repository, that means saying, for example, that a config loaded from several files
needs `YamlBaseModel` rather than `YamlBaseSettings`, or that a project without figures
removes `diagrams/` rather than keeping it unused. When a statement is a judgment rather than
a fact, say so and give the reason.

## Write fluent prose

Write in paragraphs of complete sentences, joined by the words that carry reasoning:
*because*, *so*, *which means*, *unless*, *instead*. Those words turn a set of facts into an
explanation. A bulleted list drops them and leaves the reader to rebuild the logic. A run of
short declarative sentences does the same: "uv owns the dependencies. Ruff checks the style."
reads as a list with the bullets removed.

Use a list only for items that are truly parallel and independent, such as the steps of a
procedure, the options of a command or the breaking changes of a release. Keep lists one
level deep, and do not open every item with a bold label: when every line is emphasized,
nothing is. A short set of rules is the exception. When each rule is followed by a paragraph
that explains it, as in the Smol Training Playbook's "Rules of Engagement", the rule can open
its paragraph in bold, because the result is a series of short arguments rather than a list.

A few habits make prose easier to follow:

- Use one term per concept, and define it once. If it is "the launcher's store" in one
  paragraph, it is not "the agent store" in the next.
- Prefer plain words to coined phrases. "The run directory" is clearer than "the
  serialization directory agreement mechanism".
- Name a code identifier when the reader will search for it, type it or see it in a log;
  otherwise name the concept. In an explanation, "the config class" reads better than
  `YamlBaseModel` repeated in every sentence.
- Write in the active voice, with the actor as the subject: "the command rejects the config",
  not "the config is rejected".
- Address the reader as "you" and write in the present tense: "the build writes
  `docs/dist`", not "the build will write". Use "we" only to report what the maintainers did
  or observed, such as the output of a real run.
- Ask a question only when the next sentence or section answers it. One question can frame a
  section or a decision; a run of rhetorical questions reads as stalling.
- Leave out "simply", "just", "easy" and "obviously". They add nothing for a reader who
  succeeds and tell a reader who struggles that the fault is theirs.
- Make link text say where it goes: `see the [sync procedure](/updating-from-template/)`,
  not `click [here](/updating-from-template/)`. Readers scan links, and screen readers list
  them out of context.
- Split a sentence that needs parentheses, stacked qualifications or a chain of semicolons
  into two.
- State each fact once, with the confidence it deserves. Do not hedge every claim, and do not
  restate a point in other words.

## Write procedures that work

A reader following a procedure is doing two things at once, so every step must be
unambiguous and checkable.

- State the prerequisites before the first step: the tools and versions, and where commands
  run. In this repository, commands run from the repository root.
- Write one action per step, in the imperative. Number the steps when their order matters.
- Put each command in its own code block, without a shell prompt, so it copies cleanly.
- After a step that changes something visible, say what the reader should see: a URL, a
  heading, a file. That tells them they are on track.
- When a command prints a result, show the relevant lines from a real run and say how to read
  them: which value matters, what a passing result looks like, and what to do when it fails.
- Name the versions a step depends on, such as the Python or the Node.js release, so the
  code the reader reads matches the code they run.
- Give readers who cannot run a step a way through it: say what the step demonstrates, so
  they can read it for the method.
- Mark placeholders in capitals, such as `YOUR-OWNER`, and say what replaces them. Never put
  tokens, credentials or personal details in an example.
- Warn before a step that is hard to undo, such as a command that overwrites a file or a
  push that publishes, not after it.
- Say what to do when the expected result does not appear. A troubleshooting table works
  well: the symptom as the reader sees it, then what to try.

Test the procedure before publishing it. Run every command and snippet in a disposable copy
of the repository and describe the output you observed, not the output you expect. Ports,
paths and target names change; check them against the `Makefile`, `pyproject.toml` and
`docs/package.json` rather than against another page.

## Code, configs and diagrams

Code, configs and diagrams support the prose; they do not replace it. Introduce each one with
a sentence saying what it shows, and keep it to the smallest excerpt that shows it: three
relevant lines of YAML rather than the whole file.

In tutorials, how-to guides and references the example is often the main content, so it must
be complete, runnable and identical to what lives in the repository. A documentation page
cannot include a file from the repository, which means its snippets are copies: update each
one in the change that edits the code or config it quotes. In explanations and pull request
descriptions, a sentence that names the idea is usually better than the code that implements
it.

A diagram earns its place when it shows a structure or a flow that prose describes poorly:
steps that run across several processes, the components a request passes through, or what
depends on what. Draw one idea per diagram, label it in plain words rather than identifiers,
and keep it small enough to read without scrolling. A diagram that restates a three-item list
adds nothing.

The file type decides how to draw it. In a documentation page, which is MDX, a diagram is a
figure like any other: draw it as an HTML embed placed with `HtmlEmbed`, never as a Mermaid
fence. An embed follows the theme through the engine's CSS variables, switches to a layout
that fits a phone, and can highlight the part of the structure the prose is discussing.
Mermaid gives none of that, so in MDX it is always the weaker figure. An embed is one HTML
file in `docs/embeds/`, with its model kept apart from its rendering code and with accessible
controls; the [create-html-embed](../create-html-embed/SKILL.md) skill holds the conventions.
A static figure built by `diagrams/` is an image in `docs/assets/image/`, placed with
`Image`.

Mermaid fences belong only in plain Markdown, such as `README.md`, `docs/README.md` and pull
request descriptions, where GitHub renders them and an embed cannot run. There, keep every
label to a few words, at most about 25 characters per line, and break a longer one with
`<br/>`. Mermaid widens a node to fit its text, but it does not wrap subgraph titles or edge
labels, which are cut off or run over other shapes when they are long. In both formats, a
label names a step; the explanation of the step belongs in the prose around the diagram.

## Use the components with intent

The documentation pages use the engine's components, and each one has a job.

- `Accordion` holds what only some readers need: installing a tool, an optional derivation, a
  complete file to copy. The main text must read as a whole with every accordion closed, and
  each accordion title names a task the reader would choose, such as "Rename the package",
  not a topic such as "Naming".
- `Note` marks something the reader must not miss, such as a step that publishes. Use it
  rarely, because a page of notes has no emphasis left. Give each note a title that states its
  point, as a rule or as the reader's question: the Smol Training Playbook titles its notes
  "Modify one thing at a time" and "When not to mid-train", never "Note" or "Tip". A note can
  also open a section, telling readers who already know its content where to skip to, or
  close a long section with two or three takeaways.
- `Sidenote` and `Glossary` carry a short clarification, a source, an aside or a definition
  without breaking the argument.
- A live `HtmlEmbed` needs a sentence that says what to try and what changes as a result,
  such as "Drag the slider: the curve follows the learning rate".
- Every image needs alt text that conveys its information and a caption that states its role
  and source.

The [page-frontmatter](../page-frontmatter/SKILL.md) skill lists the frontmatter every page
starts with.

## Structure and length

Give each topic space in proportion to its importance to the reader. In a pull request that
introduces one main feature alongside supporting changes, the feature gets most of the
description and each supporting change gets a sentence or two. Order the sections from what
every reader needs to what only some do: the summary first, then how it works, then the
details, limitations and verification.

Keep headings short, and make them say what their section establishes or what the reader
does there: "Resolve a conflict", not "Conflict resolution". When the draft is done, cut
until removing anything more would lose meaning.

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

- whether the opening says which question the text answers, who it is for and how to read it;
- whether the headings and the first sentence of each paragraph tell the story on their own;
- whether each section ends where the next one begins, and every question asked is answered;
- whether each claim about behavior shows what you observed, and each judgment is marked as
  one;
- whether reading it aloud trips you up anywhere, since that is where a reader trips too;
- whether a paragraph leaves a "why?" unanswered;
- whether a sentence describes the history of the work or your own process rather than the
  subject;
- whether the register fits: config blocks in an explanation, or a how-to guide without a
  working example;
- whether you ran every command and snippet, and each step says what the reader should see;
- whether each fact has one home, and the other pages link to it rather than repeat it;
- whether placeholders are marked and no credentials or personal details appear;
- whether every `Note` title states its point;
- whether every diagram in a documentation page is an HTML embed, with Mermaid only in plain
  Markdown;
- whether the documentation still builds and its links resolve: `make doc-check`.

## References

The four Hugging Face guides are worth reading for their structure as much as their subject:

- [The Ultimate MoE Training Handbook](https://huggingface.co/spaces/huggingface/moe-blogpost):
  audience paths, section bridges, real command output with its conditions, and a
  troubleshooting map organized by symptom.
- [The Ultra-Scale Playbook](https://huggingface.co/spaces/nanotron/ultrascale-playbook): one
  storyline from the simplest technique to the most refined, a three-part frame, and recaps
  that turn explanation into a recipe with a worked example.
- [The Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook):
  a reading guide for a text too long to read at once, advice on when not to act, and
  callouts whose titles state their point.
- [The LLM Evaluation Guidebook](https://huggingface.co/spaces/OpenEvals/evaluation-guidebook):
  an opening built on the reader's question, guidance split by reader role, definitions by
  analogy, and takeaways at the end of long sections.

The general principles come from:

- [Diátaxis](https://diataxis.fr/) separates tutorials, how-to guides, reference and
  explanation, because each serves a different need; the table above follows the same idea.
- [Google developer documentation style guide](https://developers.google.com/style): active
  voice, plain words, consistent terminology, and procedures with one action per step.
- George Gopen and Judith Swan, "The Science of Scientific Writing", *American Scientist*,
  1990: readers expect old information at the start of a sentence and new information at the
  end, and a paragraph's opening to say what it is about.
