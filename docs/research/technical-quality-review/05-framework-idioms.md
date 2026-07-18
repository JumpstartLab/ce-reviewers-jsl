# Framework Patterns and Idiomatic Code as a Review Dimension

Research into how expert reviewers — and codified review cultures — evaluate whether
code works *with* its framework/language rather than against it. Covers Rails,
Go, Python, Java, the linter/human boundary, reinvention anti-patterns, upgrade
risk, and how house style gets codified beyond linters.

---

## 1. Key findings

### 1.1 Rails: "fighting the framework" has a name and a doctrine behind it

The Rails Doctrine itself gives reviewers vocabulary for this. Its "convention
over configuration" pillar frames deviation as something that needs to earn its
keep: "You're not a beautiful and unique snowflake" — individuality yields to
collective efficiency, and "most impulses to be a beautiful and unique snowflake
are ill considered." The doctrine's "no one paradigm" / conceptual-compression
pillar is the other half: Rails deliberately blends paradigms (functional views,
OO models, an Active Record pattern that intentionally blurs database and domain
concerns) rather than dogmatically committing to one, because "most individual
paradigms do very well within a certain slice of the problem space, but become
awkward or rigid when applied beyond its natural sphere of comfort."
([rubyonrails.org/doctrine](https://rubyonrails.org/doctrine))

That gives a reviewer a concrete test: *if you're consistently working against
an established convention, the prior is that you've misunderstood the problem,
not that you've found the exception.* The burden of proof is on the deviation.

Jorge Manrubia (37signals) operationalizes this at the architecture-review level
in **"Vanilla Rails is Plenty"**. His claim: the standard critique that Rails
"encourages poor separation of concerns" and needs DDD-style layering to scale
is wrong when the domain layer is done well. 37signals doesn't separate
application-level and domain-level artifacts — models expose real public
interfaces and controllers call them directly. He quotes the original DDD book
against the DDD-in-Rails cargo cult: "the more common mistake is to give up too
easily on fitting the behavior into an appropriate object, gradually slipping
towards procedural programming." His verdict on the standard "service object
between every controller and model" pattern: it produces either boilerplate or
an anemic domain model — "dogmatic takes" that solve a problem Rails doesn't
have. Proof point offered: Basecamp's ~9-year-old codebase, 400 controllers,
500 models, vanilla stack, still maintainable at scale.
([dev.37signals.com/vanilla-rails-is-plenty](https://dev.37signals.com/vanilla-rails-is-plenty/))

Manrubia's companion piece **"Good Concerns"** gives the review heuristic for
the mechanism 37signals uses instead of service objects: concerns. The
distinguishing test between a good and bad concern is *domain semantics, not
file-size relief*. A good concern "captures a single trait of its host model"
and reflects a real domain role ("has trait X", "acts as Y") — his example is
`User` including `Examiner` to encapsulate HEY's clearance-petition logic, where
the concern's name alone communicates its purpose. A bad concern is "an
arbitrary container of behavior... to split a large model into smaller parts"
with no semantic identity — "will cause more harm than good otherwise." Concerns
should complement OOP (inheritance, composition, delegation to small POROs for
genuinely complex work), not replace it.
([dev.37signals.com/good-concerns](https://dev.37signals.com/good-concerns/))

**Review heuristic this yields:** when a PR introduces a concern, service
object, or new abstraction layer, ask "what noun does this name, and could you
say it out loud as a sentence about the domain?" If the answer is "it's just
where I put the stuff that didn't fit," that's the smell — not the LOC count of
the model.

### 1.2 Go: idiom is externally codified, not left to reviewer taste

Go is the cleanest example of a review-idiom canon existing as a standalone,
citable artifact separate from "style" in the formatting sense. The
[**Go Code Review Comments wiki**](https://go.dev/wiki/CodeReviewComments) —
explicitly a supplement to *Effective Go*, written as "a laundry list of common
style issues" reviewers actually leave — factors cleanly into two tiers:

- **Fully mechanical, never a human comment:** formatting is delegated whole to
  `gofmt`/`goimports`. This is stated as policy, not preference.
- **Idiom that *is* a legitimate human review comment**, because it requires
  judgment gofmt can't apply:
  - Interfaces belong in the *consuming* package, not the producing one — a
    constructor should return a concrete type; let the caller define the
    interface it needs. This is the single most-cited Go anti-pattern: producer
    packages defining `Thinger` interfaces "for mockability" that no consumer
    asked for.
  - Errors are values, never discarded with `_`; error strings are
    uncapitalized/unpunctuated because they get wrapped into other messages;
    normal-path code stays unindented, error branches return early.
  - `context.Context` is the first parameter, threaded explicitly through call
    chains — never stashed on a struct.
  - Receiver-type consistency (don't mix pointer and value receivers on one
    type) and package-name redundancy (`chubby.File`, not `chubby.ChubbyFile`)
    are idiom checks that require understanding the *type's* semantics, not a
    syntax rule.

This is useful as a contrast case: Go's review culture treats "does this fight
the language" as a *finite, enumerable list* a reviewer can cite by name
("that's a CodeReviewComments interface-placement violation") rather than a
vibe. That's a reproducible pattern for an AI reviewer persona: maintain a
citable idiom list per ecosystem, and require findings to cite the specific
rule, not "this feels un-idiomatic."

### 1.3 Python: "Pythonic" as a review culture, weaker canon than Go's

PEP 8 covers formatting/naming (largely linter territory today via
Black/Ruff). "Pythonic" is a fuzzier, more culturally-transmitted standard
sitting above PEP 8: idiomatic use of comprehensions/generators over manual
loops, EAFP over LBYL, context managers over manual
try/finally-with-cleanup, unpacking over indexing. Unlike Go's wiki, there's no
single canonical "Python Code Review Comments" document with the same
authority — Pythonic-ness is judged against Guido's stated design principle
that "code is read much more often than it is written," and reviewers lean on
community consensus (Real Python, the Hitchhiker's Guide to Python) rather than
one citable spec.
([peps.python.org/pep-0008](https://peps.python.org/pep-0008/),
[docs.python-guide.org/writing/style](https://docs.python-guide.org/writing/style/))

**Implication:** an AI reviewer covering Python idiom has a weaker external
citation to lean on than for Go, and should compensate by treating
project-local precedent (how does *this* codebase already do the equivalent
thing?) as the tiebreaker more heavily than for Go, where the wiki settles most
arguments outright.

### 1.4 Java: idiom encoded as a numbered, citable "Item"

*Effective Java* (Joshua Bloch) is structurally interesting as a review
artifact even though it's a book, not a wiki: each rule is an "Item" (e.g.
"favor composition over inheritance," "minimize mutability") — short,
standalone, numbered, citable by number in a review comment the way
`CodeReviewComments` entries are. That numbered-item structure is exactly what
makes a heuristic reviewable rather than just "good advice": a reviewer can
write "Item 18 — this should be composition, not inheritance" and both sides
know precisely what's being invoked. Bloch himself led design of the Java
Collections Framework, so the items are framework-authorial in the same way
DHH's Rails Doctrine is — the person who built the thing telling you how it
wants to be used.
([oracle.com/java/technologies/effectivejava](https://www.oracle.com/java/technologies/effectivejava.html))

### 1.5 The linter/human boundary is an explicit, stated policy at Google

Google's eng-practices docs are unusually precise about this line, and it's
worth quoting directly because it's the cleanest normative statement found:

> "On matters of style, the style guide is the absolute authority. Any purely
> style point (whitespace, etc.) that is not in the style guide is a matter of
> personal preference... Technical facts and data overrule opinions and
> personal preferences." — [Standard of Code
> Review](https://google.github.io/eng-practices/review/reviewer/standard.html)

> "Make sure the CL follows the appropriate style guides" but "don't block CLs
> from being submitted based only on personal style preferences," and
> non-mandatory polish points get prefixed **"Nit:"**. —
> [looking-for.html](https://google.github.io/eng-practices/review/reviewer/looking-for.html)

Google's own style guides go further and rank *consistency itself* into a
hierarchy — file > team > project > codebase — with an explicit escape hatch:
local consistency stops being a valid excuse the moment it would "worsen an
existing style deviation, expose it in more API surfaces, expand the number of
files in which the deviation is present, or introduce an actual bug." At that
point the CL should fix the local deviation instead of extending it.
([google.github.io/styleguide](https://google.github.io/styleguide/))

The practical takeaway repeated across multiple sources: formatters (gofmt,
Black/Ruff, Prettier) own *mechanical* style with zero exceptions; linters
(RuboCop, ESLint, golangci-lint) own *rule-based-but-not-purely-cosmetic*
issues — unused variables, suspicious coercions, missing awaits, N+1 patterns —
because these are "bugs, not style preferences" once codified as a rule; human
(or AI) review is reserved for what requires *judgment about intent* — does
this interface belong here, is this abstraction premature, does this concern
name a real domain concept. If a finding could be turned into a lint rule with
no false positives, it shouldn't be a standing human review comment — it should
be a PR to the lint config instead.

### 1.6 Consistency as an explicitly named quality attribute

Ousterhout (*A Philosophy of Software Design*) treats consistency as a direct
lever on system-level complexity: consistency lets a developer learn a pattern
once and reuse that knowledge everywhere; inconsistency forces learning every
instance separately. He's explicit that consistency decays without active
maintenance — new contributors don't know unwritten conventions — and
recommends the same two-part enforcement Google institutionalizes: *document*
the convention, then *enforce it with a tool* that blocks violations before
merge. Reviewers should therefore treat "does this match how we already do the
adjacent thing" as a first-class question, not a nice-to-have, and Google's
style guide encodes the resolution when local and global consistency conflict
(fix the local deviation rather than propagate it).

### 1.7 Reinvented framework features: thin evidence, strong first-principles heuristic

Direct research literature specifically on "review for reinvented framework
features" (hand-rolled auth instead of Devise/Rails' has_secure_password,
manual joins instead of ORM scopes, custom job runners instead of
ActiveJob/Sidekiq) is sparse as a named discipline — this is folded into
general "don't reinvent the wheel" commentary rather than a dedicated
methodology, and the search surfaced mostly generic build-vs-buy takes. The one
transferable framing found: "reinventing the wheel only makes sense when the
wheel you need doesn't exist" — i.e. the review question is always "does the
framework already solve this, and if the author believes it doesn't, did they
say why?" Treat unverified/unsupported here rather than overclaim a citation
that doesn't exist.

### 1.8 Upgrade-path risk: deprecated APIs and monkey-patching are a well-documented failure mode

Eileen Uchitelle (Rails core team, via Shopify Engineering) gives the sharpest
treatment of monkey patching as a reviewable risk, and the mechanism matters
for a review persona: **Rails only issues deprecation warnings for its *public*
API.** A patch against a private/internal API gets no warning before it breaks
— it just silently stops working, or silently keeps the old (possibly
vulnerable) behavior after an upgrade. Concrete risks she names:

- **Upgrade lock-in**: patches against internals can make major-version
  upgrades practically blocked.
- **Security regression**: "if you're patching code that is later found to
  have a vulnerability, you won't be protected unless you" replicate the
  security fix in your patch too — an upstream CVE fix can be silently
  bypassed by your own patch.
- **Global, non-local blast radius**: patches affect every caller, not just
  the code path the author was thinking about — her example: a query-cache
  patch that cost "weeks" to debug because of behavior it silently changed
  elsewhere.
- **Debt accumulation via "what's one more"** rationalization.

Her recommended review gate, useful directly as a checklist: before allowing a
patch, ask (1) would upgrading just fix this instead, (2) is the library being
used correctly in the first place, (3) can this go upstream as a real PR. If a
patch is unavoidable: isolate it in a dedicated directory (e.g.
`lib/patches/`), keep it minimal and prefer `super`/inheritance over full
overrides, link the upstream issue in a comment, write tests specifically for
the patched behavior, and track a removal date.
([shopify.engineering/the-case-against-monkey-patching](https://shopify.engineering/the-case-against-monkey-patching))

This generalizes past Rails: any private/internal-API dependency (undocumented
config internals, `_private` methods, un-pinned assumptions about a
third-party library's internal structure) is a deprecation-blind spot by
definition, because the library's own deprecation policy doesn't cover it.

### 1.9 ADRs as review reference, not review substitute

Martin Fowler's definition: an ADR is a short document (context, decision,
consequences) using an inverted-pyramid structure, stored as markdown in-repo
(commonly `docs/adr/`), immutable once accepted — superseded, never edited, by
a new record when the decision changes.
([martinfowler.com/bliki/ArchitectureDecisionRecord](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html))

The AWS/architect-community guidance found adds the review-specific piece:
ADRs function as a *citable precedent* during code review the same way a style
guide does for formatting — "the team uses the ADRs as a reference during code
and architectural reviews," and when a change violates a recorded decision, the
reviewer's move is to link the ADR, not re-litigate the tradeoff from scratch.
The caution attached: a corpus of ADRs nobody revisits drifts out of sync with
what's actually running, so the same discipline that keeps a style guide alive
(periodic re-read, explicit supersession) applies to ADRs too. One source
explicitly separates the two artifacts' scope: "the decision is purely
cosmetic (code style, naming conventions) — these belong in a style guide," not
an ADR — ADRs are for decisions with real consequences and alternatives
considered, not formatting preference.

---

## 2. Concrete heuristics for reviewing framework-fit and idiom

1. **Name the abstraction test.** For any new class/module/concern/service
   object introduced, ask: can you say its name as a sentence about the
   domain ("a Recording *has* an Incineration")? If the honest answer is "it's
   where I put code that didn't fit elsewhere," that's the tell for both a bad
   Rails concern (per Manrubia) and premature abstraction generally.

2. **Burden-of-proof inversion for deviations.** Treat "this fights the
   framework's convention" as guilty until proven innocent, per the Rails
   Doctrine framing — require the PR to state *why* the standard path doesn't
   fit, not just that it chose a different one.

3. **Ask "does the framework already have this?" before reviewing a
   hand-rolled mechanism.** Custom auth, hand-written SQL where a scope/
   `where` chain would do, bespoke background-job plumbing, manual retry loops
   — each is a signal to check whether a first-party primitive (Devise/
   has_secure_password, ActiveRecord scopes, ActiveJob/Sidekiq, framework
   retry/backoff) was consciously rejected or simply not known about.

4. **Distinguish mechanical style from idiom style, and route accordingly.**
   If a finding is "this violates a rule that could be a lint rule with zero
   false positives," it belongs in the linter config, not a standing review
   comment (Google's stated policy, and the general RuboCop/ESLint/
   golangci-lint division of labor). If it requires judgment about the
   *type's* or *domain's* semantics (interface placement, receiver
   consistency, concern cohesion), it's a legitimate human/AI review comment —
   cite the specific rule (Go wiki entry, Effective Java Item number, house
   ADR) rather than asserting taste.

5. **Check private/internal-API coupling as an upgrade-risk category on its
   own**, separate from general dependency review: does this PR call into
   something the library itself doesn't consider part of its contract
   (undocumented internals, monkey-patched core classes, `_private` methods,
   relying on an implementation detail of a third-party gem/package)? If yes,
   apply Uchitelle's gate — upgrade instead? used correctly? push upstream? —
   and require isolation/documentation/a removal plan if the patch is kept.

6. **Consistency arbitration, Google's rule.** When new code diverges from
   the local pattern, check whether adopting local consistency would spread an
   existing deviation further (more files, more API surface, or an actual
   bug). If so, the right move is fixing the local deviation in this PR (or a
   preceding one), not extending it.

7. **Cite the source, don't just assert idiom.** A framework-patterns finding
   is strongest when it can point at something citable — the Go wiki entry,
   the specific PEP 8/Pythonic idiom, the Effective Java item number, the
   team's own ADR or style guide section. "This isn't idiomatic" without a
   citation is exactly the kind of unaccountable style opinion Google's
   guidelines tell reviewers not to block on.

8. **Deprecation and version-pin smell.** Flag `# TODO: remove after upgrading
   to Rails X` / pinned gem/package versions with no tracked ticket, and any
   `Gem.loaded_specs` / monkey-patch-detection workaround — these are the
   textbook shape of an upgrade trap per §1.8.

## 3. Anti-patterns

- **Cargo-culted layering.** Adding a service-object layer, a repository
  layer, or DDD-style application/domain separation *because* it's considered
  best practice elsewhere, without the complexity that motivates it — the
  exact failure mode Manrubia targets: produces either boilerplate or an
  anemic domain model, and papers over an author's discomfort with putting
  behavior in the right object rather than solving a real problem.

- **Arbitrary-container concerns/modules.** Splitting a large class into
  concerns purely to reduce file size, with no shared domain semantics across
  the extracted methods — "arbitrary containers of behavior," per Manrubia's
  explicit bad-concern definition.

- **Producer-defined interfaces "for testability."** The Go anti-pattern of a
  package defining an interface around its own concrete type so callers can
  mock it — inverts Go's idiom that interfaces are defined by consumers,
  and typically signals the interface was never validated against a second
  real implementation.

- **Framework reinvention without a stated reason.** Hand-rolled auth,
  bespoke ORM-bypassing queries, custom job/retry infrastructure — reviewable
  by asking "did the PR explain why the built-in primitive doesn't work,"
  not just noting that a custom path exists.

- **Private/internal-API coupling and silent monkey-patches.** Undocumented,
  untested, untracked patches into a library's internals — Uchitelle's "what's
  one more" debt spiral, and the single biggest source of silent upgrade
  breakage because it sits outside the library's own deprecation contract.

- **Style-opinion review comments with no citation.** A "this isn't
  idiomatic"/"I wouldn't write it this way" comment that isn't backed by a
  style guide, a language's canonical idiom list, or a specific technical
  consequence — exactly what Google's eng-practices tells reviewers not to
  block on ("technical facts and data overrule opinions and personal
  preferences").

- **Local consistency used to justify spreading a known deviation.** Matching
  an existing bad pattern instead of fixing it, when the match would expand
  the deviation's surface area or file count — the case Google's style guide
  explicitly calls out as *not* a valid use of the consistency argument.

## 4. Implications for an AI framework-patterns reviewer persona

**Learning house style should be layered, not flat.** Three distinct sources
of truth, in priority order for citation: (1) the ecosystem's external
canon where one exists and is authoritative (Go wiki, PEP 8, Effective
Java/Bloch items, the Rails Doctrine) — cite by name/item number; (2) the
project's own codified decisions — ADRs, a living style guide, CLAUDE.md/
AGENTS.md-style docs — which should outrank generic ecosystem idiom when the
two conflict, because the team already made and recorded that tradeoff; (3)
observed local precedent in the codebase itself, used as the tiebreaker of
last resort and always framed as "here's how this repo already does the
adjacent thing," with Google's caveat baked in — local consistency stops
being a valid defense once it would spread an existing deviation.

**The linter-vs-reviewer boundary should be enforced structurally, not
just as a instruction.** Before an AI reviewer persona flags something, it
should check: is there a lint rule (RuboCop/ESLint/golangci-lint/Ruff) that
already covers this, or *could* cover this with no realistic false positive?
If yes, either confirm the CI lint config already has it (and skip the
comment — a passed lint gate means it's settled) or file the finding as "add
a lint rule for X" rather than a per-PR nag. This keeps the persona's
findings scoped to what actually needs judgment: naming an abstraction after
a real domain concept, interface placement, whether a "convention deviation"
is justified, whether a private API dependency was disclosed — the Item 18 /
Go-wiki-interfaces / Manrubia-concern-cohesion class of finding, not
whitespace or import ordering.

**Per-ecosystem specialization is not optional — the canons aren't
equivalent in strength.** Go has a citable, near-complete idiom wiki;
Rails/Ruby has doctrine-level essays (Rails Doctrine, Manrubia's posts) plus
RuboCop for mechanics, but "good Rails" judgment calls (concern cohesion,
service-object necessity) are less enumerable than Go's; Python's "Pythonic"
culture sits on PEP 8 plus community consensus with no single canonical
review-comment list; Java's Effective Java gives numbered items but they're a
book, not a living wiki that gets revised with the language. A persona that
treats all four the same way will either under-cite in Ruby/Python (where the
canon is thinner and precedent-based) or under-use the strong external canon
available for Go. Practical design: maintain a per-ecosystem citation table
(source name, URL, what it's authoritative on) and require every "fights the
idiom" finding to name which tier (external canon / project ADR-or-style-doc /
local precedent) it's drawing from — this also makes the finding falsifiable
and arguable by the PR author, which mirrors Google's "technical facts and
data overrule opinions" standard rather than asserting reviewer taste.

**Upgrade-risk and private-API coupling deserve a standing check, not an
occasional one**, because the failure mode is specifically *silent* — no
deprecation warning fires, so nothing else in CI will catch it. A dedicated
pass that greps for monkey-patch patterns (`class_eval`, `alias_method`
overriding a framework method, `send` into `_private`-looking internals,
prepend/refinement on library classes) and checks each against Uchitelle's
three-question gate (upgrade instead? used correctly? upstream-able?) is a
concrete, automatable-adjacent addition to the reviewer's toolkit that pure
idiom-checking would miss.

---

## Sources

- [Rails Doctrine](https://rubyonrails.org/doctrine)
- [Vanilla Rails is plenty — 37signals Dev (Jorge Manrubia)](https://dev.37signals.com/vanilla-rails-is-plenty/)
- [Good concerns — 37signals Dev (Jorge Manrubia)](https://dev.37signals.com/good-concerns/)
- [Go Wiki: Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
- [Effective Go](https://go.dev/doc/effective_go)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Code Style — The Hitchhiker's Guide to Python](https://docs.python-guide.org/writing/style/)
- [Effective Java — Oracle overview](https://www.oracle.com/java/technologies/effectivejava.html)
- [What to look for in a code review — Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [The Standard of Code Review — Google eng-practices](https://google.github.io/eng-practices/review/reviewer/standard.html)
- [Google Style Guides](https://google.github.io/styleguide/)
- [The Case Against Monkey Patching — Shopify Engineering (Eileen Uchitelle)](https://shopify.engineering/the-case-against-monkey-patching)
- [bliki: Architecture Decision Record — Martin Fowler](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html)
- [Architectural Decision Records — adr.github.io](https://adr.github.io/)
- [Architectural decision record process — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
- Ousterhout, *A Philosophy of Software Design* — summarized via secondary reviews ([carstenbehrens.com summary](https://carstenbehrens.com/a-philosophy-of-software-design-summary/), [S.I.R World review](https://sir-rasel.github.io/blogs/73-philosophy-software-design-book-review/)); primary text not directly fetched, treat direct quotes from it as unverified.

**Unverified / not independently confirmed — flagged rather than asserted
above:** any claim about "reviewing for reinvented framework features" as a
named, established review discipline; specific Ousterhout wording (only
secondary summaries were fetched, not the book itself).
