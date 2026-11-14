---
name: coding-guidelines
description: The house style for Python and config files in this repository - object-oriented design, file conventions, docstrings, modeling, errors and tests. Use before writing or modifying any Python or YAML file, and as the standard a change is reviewed against.
---

# Coding Guidelines

Object-oriented, Pythonic design that remains understandable and economical to maintain.
These rules apply to every new or modified Python file and config, including where lint
configuration cannot enforce them. Passing tests and lint checks are evidence, not
substitutes for this assessment.

[Object-oriented design](#object-oriented-design),
[Python file conventions](#python-file-conventions) and [Config files](#config-files) are the
house style. They take precedence over general guidance where the two differ, as PEP 8 itself
lets a project's guide take precedence over it.

Existing code does not yet follow every rule. Apply them to what you write or change; do not
rewrite unrelated code to conform. Rules specific to one project live in the `## Project`
section of `CLAUDE.md`, which wins over this page.

## Before writing

- Read the repository guidance, the relevant configuration, the callers and the tests before
  changing an isolated implementation.
- Identify compatibility requirements, supported Python versions, optional dependencies and
  intentional limitations. Distinguish documented intent from inferred rationale.
- Check the project's own machinery, the standard library and the declared dependencies
  before implementing a mechanism. A parallel implementation drifts from the one it copies.
- Describe the end-to-end flow in ordinary language: what starts the operation, which
  components participate, what each owns, and where data and failures go. A flow you cannot
  describe is not ready to be written.

## Design principles and patterns

Use principles as reasoning tools, not as a checklist of abstractions to introduce. For each
decision, identify the concrete problem, the simplest viable change and its tradeoff. A
pattern's name is not evidence that the design needs it.

| Principle | Questions to ask |
| --- | --- |
| **KISS** | Can a reader follow the normal path directly? Could fewer concepts, branches, configuration options or layers preserve the same behavior? Count complexity moved into helpers and callers, not just lines removed. |
| **YAGNI** | Does this abstraction solve a present requirement or protect a credible extension boundary? Defer unused backends, registries, factories and policy systems. |
| **DRY** | Is the same business rule or invariant maintained in multiple places? Share that knowledge at its natural owner; do not merge merely similar code with different reasons to change. |
| **Single responsibility** | Do a component's operations serve one coherent responsibility? Separate independently changing policy, transport, execution and presentation when doing so clarifies ownership. |
| **Open/closed, dependency inversion** | Can another backend implement a stable contract without modifying shared orchestration? Do shared components depend on declared domain contracts rather than undocumented backend shapes? |
| **Liskov substitution** | Can an implementation replace another while honoring input, output, failure and lifecycle semantics? Check behavior, not just matching signatures. |
| **Interface segregation** | Does each consumer require every capability in its interface? Avoid forcing implementations to supply irrelevant operations or accept ignored configuration. |
| **Composition over inheritance** | Is inheritance expressing a genuine behavioral relationship or only sharing code? Prefer explicit collaborators when they avoid fragile initialization or unrelated overrides. |
| **Least surprise** | Are side effects, mutation, configuration precedence, ownership and failure behavior visible? Do names and defaults match what callers reasonably expect? |
| **Least knowledge** | Does a consumer use a collaborator's public contract, or navigate its internal object or dictionary structure? Keep third-party internals behind the adapter. |

Prefer the smallest object model that serves today's behavior and credible extension points.
Small is not the same as flat: a set of cohesive classes with named responsibilities is
preferred over a module of free functions, even when the functions would be shorter.

Do not add configuration fields that tune an internal mechanism, such as a depth or a
heuristic threshold. Once released they freeze the implementation. Prefer behavior that
follows from the model structure, or an opt-in declaration that can be added later without
breaking anything.

## Object-oriented design

The domain is modeled as objects, each owning one responsibility. A module of loose functions
is not a design: behavior lives on the class whose data or concept it belongs to.

### Give every responsibility an owner

- Put behavior on the object that holds the data (Information Expert): a config loads the
  object it describes, a data source loads and summarizes itself, a schedule writes itself
  into the component it belongs to.
- Name a class for what it is, not for where it is used, and plainly for its job rather than
  with a metaphor the reader has to decode. A class implementing a pattern carries the
  pattern's role in its name: `DatasetMixtureLoader`, `ReportWriterConfig`. A catch-all such
  as `TrainingHelpers` mixes responsibilities under a vague name.
- When two methods do similar work, their names state what sets them apart:
  `validate_arguments` runs while the config is validated, `validate_run` once the data is
  loaded. Generic pairs such as `check` and `verify` leave the difference to the docstring.
- Name methods as verb phrases that state the outcome: `resolve_step_interval`,
  `requires_calibration_data`, `to_generation_kwargs`. Avoid `process`, `handle`, `run`.
- Name parameters and variables for what they hold, including what a collection maps and in
  which order: `experiment_logger`, `train_dataset`, `metrics_by_split`. Bare nouns such as
  `logger`, `data` or `cfg` leave the reader to guess the shape and the unit.
- A name spells the whole meaning even when it gets long, and a rename covers every
  reference: Python, YAML configs, tests and docs.

### Replace conditional dispatch with polymorphism

A `match` or `if` chain that selects behavior from a type code is a missing class hierarchy.
Use the pattern that fits, and name it in the class docstring:

| Pattern | Use it for |
| --- | --- |
| **Strategy** | interchangeable behaviors behind one contract, selected in configuration |
| **Template Method** | a fixed lifecycle with narrow subclass hooks |
| **Specification** | business rules evaluated independently, such as one validator per rule |
| **Registry** | selecting a strategy by key, such as commands discovered by module name |
| **Null Object** | the "nothing to do" case, instead of `None` checks |
| **Adapter** | third-party execution behind a small application-owned contract |
| **Composition root** | wiring collaborators in one clear place |

Configuration is the composition root wherever it can express the wiring: do not add a
second, Python-side factory for what a config can already build, nor an orchestration layer
between an entry point and the object doing the work unless that layer owns real behavior.
Template-method hooks that subclasses may override are protected; a hook every subclass must
provide is a public abstract method.

Keep `match` for parsing external input, not for dispatching behavior.

### Choose between class methods and instances

- **Stateless utilities** are classes with `@classmethod` and `@staticmethod` only. They have
  no instances and are never singletons.
- Use `@classmethod` when the method dispatches through `cls`, `@staticmethod` when it needs
  neither the class nor an instance. This holds in instance classes too: a private helper
  that reads neither `self` nor `cls` is a `@staticmethod`, so the reader sees it uses no
  state. A default hook that subclasses override stays an instance method.
- **Never create an object at module level and import it elsewhere.** It hides construction,
  makes dependencies implicit and shares state across callers. Immutable values are
  constants, not objects in this sense, and a module's own
  `logger = logging.getLogger(__name__)` is never imported elsewhere. The shared Rich
  `console` in `utils/console.py` is the one deliberate exception: a second console would
  interleave with the logging handler.
- Use **instances** when an object holds state or is selected polymorphically. Strategies are
  instances even when they hold no state, because they are passed around and selected.

### Inheritance and contracts

- Inherit for a genuine is-a relationship with a shared lifecycle. Declare the contract on an
  abstract base class with `@abstractmethod`, and mark every override with `typing.override`.
- An abstract base the project owns also extends `overrides.EnforceOverrides`, which rejects,
  at class creation, any override that lacks `@override`; without it the decorator is only a
  hint for the type checker. Add the `overrides` package with the first such base. On class
  and static methods, put `@override` below `@classmethod` or `@staticmethod`.
- Polymorphic class attributes are declared as `ClassVar` on the base and set by subclasses.
  They are not constants.
- Inject collaborators that hold state through the constructor; reach stateless utilities
  directly through their class.

### Randomness and reproducibility

- A run has one seed. Pass it explicitly to everything that draws. Never seed or draw from a
  module-level generator, nor through the `random` or `numpy.random` module functions.
- The same seed must give the same output on any machine: iterate over ordered collections
  (lists, dicts, sorted sets) whenever the order feeds a random draw.
- When an entity must be drawn the same way wherever it appears, derive its own generator
  from a string naming the run's seed, the entity and the purpose:
  `Random(f"{seed}/{dataset_id}/sample")`. Never seed with `hash()`, which Python salts per
  process, nor with arithmetic on integer seeds (`seed + index`), whose streams overlap.

### Check before acting

- Exceptions are not control flow. When an operation can only apply under conditions, expose
  them as a query and check it first, so the operation then succeeds.
- An exception raised after a check passed signals a broken contract, not an expected outcome
  to retry.
- Validate every input before the expensive or irreversible step: a model load, an upload, a
  paid request, a long computation.
- Write workflows as a short sequence of named steps, each a method or a private helper.

### Fail loudly

- Raise a named, domain-specific exception rather than returning `None` or silently skipping.
  A fallback must be explicit and visible in the method that applies it. Exceptions are
  narrow, actionable and carry no secrets.
- Do not catch `Exception` only to log and re-raise, or to log and continue. Log with
  standard `logging` at the boundary where an event occurs; never `print` from application
  code.
- A configuration model checks, when it loads, both directions of its contract with the code:
  it rejects what the code cannot use and requires what the code relies on. A gap found later
  is reported by the wrong component, often long after the run started.

## Python file conventions

- **No module docstring.** The classes document the module.
- **No `from __future__ import annotations`.** The project requires Python 3.12+; use
  `typing.Self` for methods that return their own class. A name imported under
  `TYPE_CHECKING` is annotated as a quoted string.
- **Type every signature and boundary.** Prefer models, dataclasses, protocols, enums and
  precise collections over `Any`, untyped dictionaries or broad unions.
- **One job per function.** Each function does one coherent job with visible side effects and
  a consistent return type. Split unrelated modes instead of selecting them with a boolean
  flag. Do not return tuples from helpers: return a typed model, or split the helper in two.
- **Constants** are `UPPER_SNAKE_CASE`, without a leading underscore even when private, and
  are not class attributes. A literal used across a package lives in the `constants.py` of
  its package scope; a constant used by one module stays at that module's top. Comment the
  reason for any non-obvious value. Values a user may tune belong in configuration.
- **Private methods** start with an underscore and carry a one-line docstring saying what
  they return or do, in domain terms.
- **Instance attributes are private**: every attribute set in `__init__` starts with an
  underscore. An object exposes behavior through methods, not its state. Fields of Pydantic
  models are the exception: they are the data the model exists to carry.
- **Modules are cohesive.** One module per concept, and no catch-all modules such as
  `base.py`, `utils.py` or `common.py`. Gather the config models of an area into one module,
  keep exceptions in one `exceptions.py` per package scope, and move a family of
  implementations into a subpackage with one module each.
- **Optional dependencies stay optional.** Code from an optional group or extra is imported
  inside the function that needs it, never at the module level of a config module, so
  importing and validating configs does not require the group.
- **Imports are absolute.**
- **Model copies** are changed through typed attributes on a deep copy
  (`config = source.model_copy(deep=True)`, then `config.seed = seed`), never through
  `model_copy(update={...})`, whose string keys refactoring tools cannot follow.
- **Generated code** is never edited by hand. Change the template or the generator and
  regenerate.
- **Lint.** Ruff uses a 100-character line length. Do not add blanket lint exclusions; use a
  local `# ruff:ignore[rule-name]` only when satisfying the rule would make the code less
  clear or less correct.

### Docstrings

Google style, with single backticks for inline code. Ruff and flake8/pydoclint enforce the
format; types belong in the signature, never in the docstring. Document contracts and
non-obvious behavior, not what names and types already say.

- **Classes:** a summary line, then what the class owns and, if any, the pattern it
  implements. `Attributes:` lists class-level fields only; state set in `__init__` is
  documented by the `Args:` of `__init__`. Document Pydantic fields with
  `Field(description=...)`, stating the field's effect rather than its type or the plumbing
  behind it.
- **Public methods and functions:** a summary line saying what the function returns or does,
  then `Args:`, `Returns:` and `Raises:`. `Raises:` lists only exceptions raised in the body,
  because Ruff (DOC501, DOC502) compares it with the method's own `raise` statements;
  exceptions that propagate from a collaborator are described in the summary prose.
- **An entry point's `main()`** opens with a paragraph that stands alone, since a CLI shows
  it as the command's help.
- **Heuristics** say so in the summary and name the inputs they get wrong.
- **Abstract methods** carry the full contract. **Public overrides** carry a full docstring
  too, so a reader of a subclass never has to open the base class. Private overrides carry a
  one-line docstring.
- **One-line docstrings** carry no sections. **Properties** carry a one-line summary
  describing the value.

```python
def create_dataset_loader(dataset_spec: DatasetSpec, seed: int) -> DatasetLoader:
    """Build the loader a dataset spec names, seeded for the run.

    Args:
        dataset_spec: A single dataset or a mixture of them.
        seed: The run's seed, used for every shuffle the loader performs.

    Returns:
        The loader, ready to `load()`.
    """
```

### Comments

Comments explain only non-obvious invariants, security constraints, algorithmic choices,
library quirks, generated-code caveats or deliberate deviations from the obvious approach.
Never narrate the code or preserve change history; that belongs in the commit. If a comment
feels necessary, first try renaming a symbol or extracting a function.

### Readable bodies

A reader should understand a method's purpose and sequence by reading its body once, without
opening every helper. Keep the main flow at one level of abstraction and delegate each
cohesive step to a private helper whose name states what it does, including mutation or side
effects. A workflow written as `_validate_resume_identity()`, `_prepare_tasks()`,
`_execute_tasks()` and `_normalize_results()` reveals its story before the reader opens any
of them.

- A helper encapsulates a meaningful step, not an arbitrary group of lines.
- Slice and index through named private helpers, not through bare offsets in the main flow.
- A comprehension has at most two `for` clauses; beyond that, extract a named helper.
- A method that tries alternatives returns the first success through one expression or one
  loop, not through flags.
- Separate the steps of a body with blank lines: guards, then the change, then the return.
- Where a result is assembled from several helper calls whose outcome is worth inspecting,
  assign each piece to a named variable, build the result into a named variable and return
  it, so every intermediate is visible in a debugger. Do not apply this to every one-liner.
- Judge nesting, branching, state changes and cognitive load, not an arbitrary line count.

## Config files

Configs under `configs/` are part of the public workflow surface: users copy them, and other
configs refer to them.

- Before writing a config, find a similar one in `configs/` and copy its layout.
- Populate every field, defaults included, so the file doubles as documentation.
- A config model is read as a feature's contract: each class opens with a docstring saying
  what it defines, each field has a `description`, and `model_config` goes after the fields.
- Configs name classes and fields as strings that no import checks. After renaming a class or
  a field, search the YAML for the old name and run the project's config validation.
- A comment in a config describes the value next to it; one describing a field the config
  does not set is stale.

## Proper modeling and maintainable references

Domain concepts and stable structures are represented in code, not in strings. A rename must
be discoverable through symbol references rather than by searching for scattered literals.
Apply this to tests as strictly as to production code.

- **Named constants** for fixed values such as artifact filenames, metadata keys and protocol
  namespaces. Define each at its natural owner and reuse it rather than repeating the
  literal.
- **Enums** for a closed set of meaningful choices. Pass and compare members internally;
  convert to external values at serialization or integration boundaries.
- **Pydantic models** for domain data and contracts that need validation or serialization,
  including the values an entry point passes between its steps. Keep them strict: fields and
  validators, not hidden coercion. Build them with keyword arguments only.
- **Typed attributes over string-keyed dictionaries.** Keep mappings for genuinely dynamic
  collections or external payloads, and normalize those into typed structures at the
  boundary.
- **Templates** print values but do not decide: compute the outcome in Python and pass it in.
- Human-readable messages and deliberate external-format fixtures can remain literals. The
  concern is encoding domain structure through strings that refactoring tools cannot follow.

### Construct models explicitly

For data assembled in Python, construct models with named arguments, not
`Model.model_validate({...})`. Constructor arguments make the schema visible to readers and
static tooling.

- Do not build a dictionary, or dump an existing model, only to validate another known model
  from it. Map the typed attributes explicitly, in a named conversion helper when the mapping
  is a meaningful operation.
- Reserve `model_validate()` and `model_validate_json()` for parsing boundaries, such as
  external payloads or saved files.
- Do not use `model_construct()` to skip validation.

### Derive import paths from symbols

When Python code needs a dotted import path, derive it from the referenced class instead of
repeating its module and name in a string:

```python
target_path = f"{writer_class.__module__}.{writer_class.__qualname__}"
```

Keep static import strings only where the format requires them, as in YAML, or where
importing the symbol would break optional-dependency isolation; validate those at the
boundary. In tests, derive configuration targets from the implementation under test and patch
the object where the consumer looks it up.

## Interfaces and future extension

- Trace dependencies across boundaries, including configuration, model types, exceptions,
  artifact paths and imports. A neutral name alone does not make a contract independent of a
  backend.
- Work through adding one hypothetical alternative implementation: list what it would
  implement and which existing files would need changes. Do not build it.
- Keep third-party objects and execution details within their adapter. Normalize them into
  explicit shared contracts at the boundary.
- Document contract semantics: identity, status, partial results, retries, resume,
  configuration precedence, ownership and artifact location.
- A public config field or class is a compatibility contract once released. Weigh every
  addition as something users will depend on.

## Duplication and Pythonic implementation

- Look for repeated decisions and invariants, not merely similar syntax. Factor shared policy
  at its natural owner; keep backend-specific policy in the backend.
- Prefer standard Python constructs, context managers, explicit data flow and appropriate
  collections over hidden mutable state or unnecessary machinery.
- Examine inheritance and composition for lifecycle assumptions, initialization side effects,
  duplicated setup and subclasses overriding unrelated behavior.
- Identify unused concepts, redundant state, unnecessary copies and repeated conversions.

## Correctness and operational behavior

Trace successful, partial, failed, interrupted, retried and resumed operations. Check
validation timing, resource cleanup, persistence ordering, idempotency, configuration
mutation, provenance and exception propagation. Inspect concurrency assumptions where state
or external identities are shared.

Verify third-party assumptions against the installed implementation or authoritative
documentation, not from memory, and state when a claim could not be verified.

## Tests

- Tests live in `tests/` and mirror the package layout.
- Favor contract and integration coverage over tests that mirror private implementation
  details. Never assert on source text.
- A test asserts what the rule it is named after decides, not only that its lines run.
- Assert hand-computed or closed-form expected values, never values captured from the current
  implementation.
- A test must be able to fail: check it by breaking the code it protects. An assertion under
  an `if` on generated data may never run; build or parametrize each case.
- Build fixtures with typed constructors, enum members and constants. Keep raw dictionaries,
  YAML or JSON only when the test exercises parsing, malformed input or an external format;
  there, explicit expected strings protect the format on purpose.
- A test that needs an optional group skips without it (`pytest.importorskip`) rather than
  failing the default environment.
- Coverage is a diagnostic, never a goal. Never add a test to move the number.

## Verify

```bash
make format && make lint && make lint-doc && make test
```

Do not silently change dependencies, download large artifacts or contact paid services to
validate a change. Report what could not be checked.

## References

- [PEP 8](https://peps.python.org/pep-0008/): a project's own guide takes precedence over it.
- [PEP 257](https://peps.python.org/pep-0257/): a docstring documents the exceptions raised.
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html): `Raises:`
  lists the exceptions relevant to the interface (3.8.3). It prefers module-level functions
  to static methods (2.17), where this guide keeps behavior on its class.
- [ruff DOC502](https://docs.astral.sh/ruff/rules/docstring-extraneous-exception/): `Raises:`
  is checked against the method's own `raise` statements.
- [Python `random`](https://docs.python.org/3/library/random.html): a `str` seed uses all its
  bits, while `str` hashes are salted per process.
