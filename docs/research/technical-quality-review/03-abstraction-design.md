# Abstraction, Software Design, and Maintainability Review

Research dimension: how expert reviewers judge whether code is well-factored — coupling/cohesion, abstraction quality, module boundaries, and when *not* to abstract.

---

## 1. Key Findings

### 1.1 Ousterhout: complexity as dependencies + obscurity, deep vs. shallow modules

John Ousterhout's *A Philosophy of Software Design* frames the entire discipline around one claim: **complexity is whatever makes software hard to understand and modify**, and it has exactly two root causes:

- **Dependencies** — code that cannot be changed independently of other code. Dependencies can't be eliminated, but design work should minimize them and make the ones that remain "simple and obvious." ([summary](https://carstenbehrens.com/a-philosophy-of-software-design-summary/), [system-design.space](https://system-design.space/en/chapter/philosophy-design-book/))
- **Obscurity** — important information that isn't obvious to the reader, creating "unknown unknowns."

From this, Ousterhout derives the **deep vs. shallow module** distinction: a *deep* module provides powerful functionality behind a simple interface (large ratio of implementation-complexity-hidden to interface-complexity-exposed); a *shallow* module's interface is complex relative to the functionality it actually provides — the abstraction barely pays for itself. He explicitly argues this cuts against the mainstream "classes should be small" intuition: many small classes tend to be shallow, and a system of shallow classes has *more* total complexity than one with fewer, deeper modules, because the *interfaces* — not the implementations — are what readers have to hold in their heads. ([Carsten Behrens summary](https://carstenbehrens.com/a-philosophy-of-software-design-summary/); [Ousterhout's own site](https://web.stanford.edu/~ouster/cgi-bin/aposd.php))

**Information leakage** is his diagnostic for a bad boundary: a design decision is reflected in more than one module, so that a change to the decision requires touching all of them. Leakage can be explicit (a dependency baked into an interface) or implicit (multiple modules assume something about a shared format, protocol, or ordering that isn't declared anywhere). Information hiding — pushing a design decision fully inside one module's implementation — is the mechanism that produces deep modules in the first place.

He also distinguishes **tactical vs. strategic programming**: tactical programming ("get the feature out fast") accumulates exactly the complexity described above; strategic programming treats "produce a good design" as a first-class goal alongside "make it work," and he suggests investing roughly 10–20% of task time in design — slower per-task at first, faster in aggregate because complexity stops compounding. ([system-design.space](https://system-design.space/en/chapter/philosophy-design-book/))

### 1.2 The Ousterhout–Martin (Clean Code) debate

Ousterhout and Robert "Uncle Bob" Martin conducted a structured public debate, later published as a [GitHub repo](https://github.com/johnousterhout/aposd-vs-clean-code), covering method length, comments, and TDD. This is a rare case of two influential authors directly confronting where their advice diverges, and it's a good corrective against treating either book as unopposed gospel:

- **Method length.** Martin: "The first rule of functions is that they should be small. The second rule of functions is that *they should be smaller than that*." Ousterhout counters that once a function is down to a few dozen lines, further splitting rarely helps readability and often hurts it — small methods create shallow interfaces and "entanglement," forcing the reader to jump between fragments to reconstruct one coherent operation. ([GitHub debate](https://github.com/johnousterhout/aposd-vs-clean-code); [tryingthings.wordpress.com summary](https://tryingthings.wordpress.com/2025/02/25/aposd-vs-clean-code-a-debate/))
- **Comments.** Martin: "Comments are always failures... their use is not a cause for celebration" — he prefers long, self-documenting names and treats comments with suspicion (verify before trusting). Ousterhout treats comments as a necessary, complementary tool for capturing information code literally cannot express (rationale, invariants, non-obvious constraints), and estimates missing/wrong comments cost far more than the (rare) case of a stale one.
- **TDD.** Martin's tiny red/green/refactor cycles vs. Ousterhout's skepticism that mandating tiny increments has a compensating benefit.

The meta-lesson for a reviewer: "small function" and "self-documenting code, no comments" are *opinions with an articulate opposing camp*, not settled law. A design reviewer citing Clean Code rules as if uncontested is cargo-culting one side of a live debate.

### 1.3 Sandi Metz: "The Wrong Abstraction" and duplication-as-lesser-evil

Metz's [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) (2016, developed from a RailsConf 2014 talk) describes the classic decay pattern precisely:

1. A programmer sees duplication, extracts it into a shared abstraction, gives it a name.
2. A new requirement arrives that's *almost* — but not quite — served by the existing abstraction.
3. Out of "sunk cost" pressure to reuse what's there, the next programmer adds a parameter and a conditional branch to the shared code rather than reconsidering the abstraction.
4. Repeat, until the shared code is "a condition-laden procedure which interleaves a number of vaguely associated ideas."

**Diagnostic heuristic**: *if you find yourself threading new parameters and conditional branches through shared code to make it fit a new case, the abstraction is wrong* — not the new case, the abstraction. **Fix**: "the fastest way forward is back" — inline the abstraction back into every call site, delete what each caller doesn't need, let the now-visible duplication show you what's actually common, and re-extract from there. Her guiding principle, widely quoted (sometimes over-quoted) as "duplication is far cheaper than the wrong abstraction," is explicitly a *tolerance* claim, not a mandate to always duplicate — she recommends tolerating duplication until you understand the problem well enough to abstract correctly.

This claim isn't universally accepted. [Code with Jason's rebuttal](https://www.codewithjason.com/duplication-cheaper-wrong-abstraction/) and [terriblesoftware.org's "Duplication Is Not the Enemy"](https://terriblesoftware.org/2025/05/28/duplication-is-not-the-enemy/) push back that duplication has its own compounding cost (N places to fix a bug instead of 1) and that Metz's framing can be used to justify never abstracting. The honest synthesis: both wrong abstraction and rampant duplication are real failure modes; the skill is judging *which* code has actually stabilized enough to name.

Metz's separate, more mechanical **four rules for developers** (deliberately provocative, meant to be argued with, not obeyed blindly): classes ≤ 100 lines, methods ≤ 5 lines, ≤ 4 parameters per method, one instance variable per view/one object per controller in Rails. ([thoughtbot](https://thoughtbot.com/blog/sandi-metz-rules-for-developers)) These sit closer to the Clean-Code end of the spectrum than Ousterhout's — worth noting as a genuine, unresolved tension in the field between "small is safe" and "deep is better," not a contradiction to paper over.

### 1.4 Code smells and empirical defect/churn correlation

Fowler's *Refactoring* catalog names smells (Duplicated Code, Long Method, Large Class / God Class, Feature Envy, Shotgun Surgery, Divergent Change, etc.) as *symptoms* to prompt investigation, not defects in themselves. Empirical software-engineering research has tested whether these symptoms actually predict trouble:

- A majority of empirical studies found a **positive correlation between code smells and defects**, but the correlation size varies a lot across studies/languages and is sometimes weak. ([Queen's University Belfast study](https://pure.qub.ac.uk/en/publications/software-code-smells-and-defects-an-empirical-investigation/); [PDF](https://pureadmin.qub.ac.uk/ws/portalfiles/portal/467641289/Software_code_smells_and_defects_an_empirical_investigation.pdf))
- **God Class / God Method** are the smells most consistently and strongly correlated with defects across the largest number of independent studies — i.e., if you can only chase one smell, chase this one.
- Smells characterized by size/complexity (Complex Class, Long Method) are both the most *diffuse* (common) in real codebases and the ones with a measurably higher change- and fault-proneness than smell-free code. ([Springer empirical study](https://link.springer.com/article/10.1007/s10664-017-9535-z))
- **Churn and smells interact**: files with frequent changes are more likely to accumulate smells, and combining churn metrics with smell metrics measurably improves defect-prediction models over either alone — i.e., smell-in-isolation is a weaker signal than smell-plus-instability.

Net takeaway for a reviewer: don't flag every smell equally. God Class/God Method and "this file changes constantly and is also tangled" are the two patterns with the strongest empirical backing; a long parameter list in a rarely-touched utility is a much lower-value flag.

### 1.5 YAGNI, speculative generality, rule of three

- **YAGNI** (Extreme Programming, popularized further by [Fowler's bliki](https://martinfowler.com/bliki/Yagni.html)): build only what current requirements need. The cost model behind it: the "option value" of an unbuilt feature is usually smaller than the carrying cost (complexity, maintenance, wrong-guess risk) of building it before it's needed.
- **Speculative generality** (a named Fowler smell): parameterization, hook points, or abstract classes built for a hypothetical future need that may never arrive. The danger is specifically that it's *not visible* as waste in the moment — it looks like "good engineering" and only reveals itself as dead weight once the anticipated future fails to materialize (or arrives in a shape the speculative generality doesn't actually fit, at which point it becomes a wrong abstraction per §1.3).
- **Rule of Three**: wait for a third real occurrence of duplicated logic before extracting an abstraction. First occurrence: write it concretely. Second: copy-and-modify, deliberately not abstracting yet. Third: now you have enough examples to see what's actually invariant vs. incidental, and only then extract. This is the practical antidote to premature abstraction — it converts "do I abstract?" from a guess into an observation.

### 1.6 Cognitive load as the unifying frame ("Cognitive load is what matters")

[zakirullin/cognitive-load](https://github.com/zakirullin/cognitive-load) (a widely circulated, actively maintained community doc, also covered by [Simon Willison](https://simonwillison.net/2024/Dec/26/cognitive-load-is-what-matters/)) reframes most of the above under one operational constraint: working memory holds roughly 4 chunks before overload. Concrete, review-usable heuristics it derives:

- Prefer early returns over nested conditionals — once you're past a guard clause, the reader can *discard* that fact from working memory ("we don't care about earlier returns, if we're here then all good").
- Extract complex boolean conditions into a named intermediate variable — trades one cheap abstraction (a name) for removing a live multi-term expression from working memory.
- "A little copying is better than a little dependency" — echoes Metz; every dependency the code takes on becomes something the reader must load into memory to understand this code, including everything transitively pulled in by a framework.
- Layers of abstraction aren't free: each hop the reader has to jump (function → indirection → interface → impl) has to be held in working memory simultaneously with the goal that sent them there. Add a layer only when it demonstrably reduces total load (e.g., it hides real complexity), never merely for "architecture."
- Frameworks/magic cut initial cognitive load (fast MVP) but raise it long-term, because "how does this actually work" requires learning the framework's internals on top of the domain.
- Too many shallow microservices reproduce the shallow-module problem at a distributed-systems scale ("distributed monolith") — the same failure mode Ousterhout describes, just with network hops between the shallow pieces instead of function calls.

### 1.7 Hotspots: churn × complexity (Tornhill / CodeScene)

Adam Tornhill's *Your Code as a Crime Scene* and the CodeScene product built on it add the dimension that's missing from purely-structural smell detection: **behavioral/historical data from version control**.

- **Hotspot** = a file that is both complex *and* changes often. Tornhill's empirical claim: 1–2% of a codebase (its hotspots) typically accounts for up to 70% of the actual maintenance effort/defect load — meaning most of a codebase's structural imperfections simply don't matter because nobody touches that code. ([Tornhill's site](https://www.adamtornhill.com/articles/crimescene/codeascrimescene.htm); [pragprog](https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/))
- **Change coupling** (a.k.a. temporal/logical coupling): files that are repeatedly committed together reveal a real dependency even when no static analysis tool would flag one — often the sharpest signal of hidden architectural coupling (a change to A quietly requires a change to B, discoverable only from git history, not from imports).
- **Prioritization framing** (CodeScene's "Technical Debt Friction"): unhealthy code that is *also* a hotspot is worth fixing; unhealthy code that nobody touches is not — chasing it is waste. This is the historical/quantitative version of the same judgment call in §1.4: smell density alone is a weak signal, smell × churn is a strong one. ([CodeScene docs](https://codescene.io/docs/guides/technical/prioritize-technical-debt.html))

Practical implication for review: a single-PR diff review is structurally blind to this axis (it has no git-log access to churn), so a reviewer's "this is over-engineered" judgment on a rarely-touched file is lower-stakes than the same judgment on a file the team edits weekly — if that context is available, use it.

### 1.8 SOLID: what holds up, what's misleading

[tedinski's "Deconstructing SOLID design principles"](https://www.tedinski.com/2019/04/02/solid-critique.html) is the most substantive single critique found, and each point is reviewer-actionable:

- **SRP** — "single responsibility" is vague and invites bikeshedding ("is this two responsibilities?"). The sharper question a reviewer should ask instead: *what must this module NOT expose, and what dependencies must it NOT have?* That's Ousterhout's information-hiding framing wearing a different name — arguably SRP is a restatement of "encapsulate the thing likely to change," not a headcount rule on responsibilities.
- **OCP (Open-Closed)** — critiqued as backwards in its usual reading: it treats "extensible via subclassing/inheritance" as always superior to "just modify the data/object directly," ignoring that extensibility is a cost you should pay only at genuine system/plugin boundaries. Inside a single team's codebase, "easy to modify" usually beats "closed to modification, open to extension." A reviewer citing OCP to block direct modification of an internal, single-owner class is very likely mis-applying it.
- **LSP** — the least controversial, but its main real-world consequence is: *implementation inheritance routinely violates it*, which is the actual argument for composition-over-inheritance, more than any abstract virtue of composition. Inheritance is safe only fully-internal (never exposed across a module boundary) or inside an ADT the author fully controls.
- **ISP** — its useful core ("prefer several small, focused interfaces over one fat one") mostly matters at system/API boundaries where you can't freely change all callers; inside a codebase you control, it's lower-stakes.
- **DIP (Dependency Inversion)** — called "partly backwards": the real goal isn't "depend on abstractions instead of concretions" (many concretions *are* the right abstraction to depend on) — it's "don't expose concretions that callers shouldn't be coupled to." Read literally, DIP pushes people toward interface-for-everything, which — combined with DI containers and mocking frameworks to compensate — often *raises* total complexity rather than lowering it. This directly echoes the "SOLID codebases littered with interfaces nobody needed" critique found across multiple sources.

Composition-over-inheritance and "depend in the direction that isolates the volatile decision" survive the critique; SOLID-as-a-uniform-checklist mostly doesn't. A reviewer who says "this violates SRP" or "add an interface for DIP" without naming the actual future change being protected against is pattern-matching on vocabulary, not judging risk.

### 1.9 Coupling/cohesion, restated for economics (Kent Beck, *Tidy First?*)

Beck's 2024 book reframes coupling/cohesion in economic terms useful for review conversations: **cohesion = putting everything that changes together in one place** ("put all the manure in one pile"), and **the actual design goal is balancing the cost of coupling against the cost of decoupling** — decoupling (adding an abstraction boundary) is not free, it has its own maintenance cost, so it's only worth it when the coupling cost it removes is larger. ([tidyfirst.substack.com summary](https://tidyfirst.substack.com/p/cohesion); [workingsoftware.dev summary](https://www.workingsoftware.dev/summary-of-tidy-first-book/)) This is the same "abstraction has a price, only pay it when it buys something" thread running through Metz, Ousterhout, and the cognitive-load doc, from a different angle: sometimes better cohesion (moving related things next to each other) is a cheaper fix than trying to eliminate coupling outright.

---

## 2. Concrete Heuristics for Judging Abstraction Quality in Review

Ranked roughly by how directly they translate into a review comment:

1. **Interface-to-implementation ratio.** Ask: how much does the caller have to know/pass/configure vs. how much complexity does this hide? If the interface is nearly as complex as just inlining the logic would be, it's a shallow module — flag it, don't praise it for being "small."
2. **The parameter/conditional smell test (Metz).** If a shared function/class picked up a new boolean flag, an `if mode == :x` branch, or an optional parameter to handle a new caller's slightly-different need — that's the signature of a wrong abstraction being stretched, not evidence the abstraction is working. Suggest inlining-then-re-extracting over adding another branch.
3. **Information leakage check.** Does this design decision (a data format, an ordering assumption, a protocol detail) show up in more than one module? If two modules would both need to change together for one conceptual decision, they're not really decoupled regardless of file/class boundaries.
4. **"What must this NOT know?"** instead of "does this have one responsibility?" — ask what the module is hiding, not how to count its responsibilities. This reframes SRP debates into something falsifiable.
5. **Occurrence count before abstraction.** Is this the first, second, or third occurrence of the pattern? First/second: let it duplicate. Third+: worth asking what's actually invariant.
6. **Working-memory cost of the change as reviewed**, not just as written: how many files/layers does a reader have to hold open simultaneously to understand this diff? A change that's "clean" per-file but requires jumping across five thin layers to trace one request has *increased* total system complexity even though no single file looks bad.
7. **Change-history context, when available.** Is this file a hotspot (frequently changed) or a stable corner nobody touches? Over-engineering concerns are worth raising harder on hotspots; on stable, rarely-touched code, "this could be cleaner" is lower priority than on code the team edits weekly.
8. **Does the abstraction correspond to a real, current requirement, or a hypothetical one?** If the justification for an interface/strategy pattern/plugin point is "so it's easy to extend later" and no second implementation exists today, that's speculative generality — ask what concrete near-term need it serves.
9. **Directional test for DIP/interfaces**: does this interface exist because there are (or will imminently be) multiple real implementations, or because "depend on abstractions" was applied as a rule rather than a response to an actual volatility? An interface with exactly one implementation and no test-double need is a candidate for deletion, not praise.
10. **Naming as a proxy for boundary quality.** If you can't name a class/method without "And," "Manager," "Helper," "Util," or a conjunction, that's often a symptom the boundary is wrong, not that the name needs work — the fix may be splitting or merging, not renaming.
11. **Does this fit the existing architecture, or does it introduce a second way to do the same thing?** A change that's individually well-factored but establishes a parallel pattern to an existing one (two ORMs, two error-handling conventions, two module layouts) adds systemic complexity even if the diff itself is clean — this is a strategic-vs-tactical (Ousterhout) judgment that requires knowing the surrounding codebase, not just the diff.

---

## 3. Anti-Patterns Ranked by Real-World Cost

Ordered by strength of evidence + typical blast radius, drawing on the empirical smell/defect literature (§1.4) and hotspot research (§1.7):

1. **God Class / God Method that is also a churn hotspot.** Strongest empirical correlation with defects of any smell studied, and when it's also frequently modified, it's the single highest-leverage thing to flag — this is where CodeScene's "Technical Debt Friction" and the QUB defect study point to the same conclusion from different methods.
2. **Information leakage across supposedly independent modules** (a shared assumption about format/ordering/protocol baked into 2+ places with no single owner). Costs compound silently — every future change has to remember to touch N places, and nothing enforces that; this is Ousterhout's core complexity driver and the mechanism behind "shotgun surgery."
3. **Wrong abstraction under active stretching** (Metz pattern: params + conditionals accreting onto shared code). Cost compounds *specifically* because each new caller's fix makes the abstraction harder to safely modify for the next caller — a super-linear cost curve, not linear.
4. **Shallow modules proliferating** (many small classes/services each with interface complexity close to their implementation complexity). Individually cheap, collectively expensive: total system complexity is dominated by the sum of interfaces a reader must hold, not by any one file's line count. The "distributed monolith" of too-fine microservices is this same failure at the architecture level.
5. **Speculative generality / unexercised extension points.** Lower urgency than the above (it doesn't actively cause bugs), but a steady tax on comprehension — every reader has to evaluate and discard the unused flexibility, and it often becomes the site of the *next* wrong-abstraction problem once someone tries to actually use the hook for something it wasn't quite designed for.
6. **SOLID-cargo-culted interfaces/DI** (an interface with one implementation, introduced "for testability" or "for DIP" without a concrete second use). Individually low-cost, but scales badly across a codebase — the tedinski critique's "littered with interfaces... IoC containers and mocking frameworks" spiral is exactly this pattern repeated hundreds of times.
7. **Duplicated code that has NOT yet reached a third occurrence.** Lowest cost on this list, and often mis-ranked higher than it deserves — reviewers pattern-match on "duplication" as inherently bad, but per the Rule of Three and Metz, two occurrences without a clear invariant should usually be left alone.

Note on rank 7: this is deliberately the anti-pattern *reviewers most often over-flag* relative to its actual empirical cost — it's included to counterbalance the instinct to comment "DRY this up" reflexively.

---

## 4. Implications for an AI Design/Maintainability Reviewer Persona

**Context it needs beyond the raw diff** (a design reviewer working only from a unified diff is structurally handicapped on several of the heuristics above):

- **Call-site visibility.** To apply the Metz parameter/conditional test or judge whether an abstraction is being stretched, the reviewer needs to see *all* current callers of a modified shared function/class, not just the lines that changed.
- **Churn/history signal**, even approximate (e.g., "this file changed in the last 5 PRs" or a `git log --oneline -- <file> | wc -l`), to weight severity per §1.7 — the same smell is a top priority in a hotspot and noise in a stable file.
- **Existing architectural precedent.** Whether this diff introduces a second pattern for something the codebase already has a convention for (error handling, data access, module layout) — this requires a map of the codebase's existing conventions, not just the diff.
- **The actual future need being protected against**, when a reviewer is tempted to ask for an interface/abstraction "for flexibility" — if there's no near-term second use case in view (roadmap, ticket, adjacent code), the request is speculative generality and should be down-weighted or dropped, not asserted as best practice.
- **Whether the surrounding code is greenfield/prototype vs. established/high-traffic** — the same "shallow module" comment is much lower priority pre-product-market-fit than in a stable core library.

**How to avoid pedantic SOLID-cargo-culting** (this is an empirically documented failure mode of LLM reviewers specifically — see [arXiv 2603.00539, "Are LLMs Reliable Code Reviewers? Systematic Overcorrection"](https://arxiv.org/abs/2603.00539) and [arXiv 2508.12358](https://arxiv.org/html/2508.12358v1), which found LLM code reviewers infer non-existent constraints, speculate about failures without evidence, and overfit to stylistic "best practices" orthogonal to the actual requirement, sometimes producing *both* high false-negative and high false-positive rates simultaneously):

- Never cite a principle name (SRP/OCP/DIP) as the finding itself. Require the comment to name the *concrete future change* the current design would make harder, per §1.8 — "if X changes, these N places have to change together" is a finding; "this violates SRP" alone is not.
- Treat "add an interface/abstraction here" requests as needing the same evidentiary bar as any other suggestion: a real second implementation, a named upcoming requirement, or an existing pain point (bug, slow test, blocked feature) — not "more testable in principle" or "more SOLID."
- Explicitly budget attention using the hotspot framing: spend more scrutiny on frequently-changed, high-traffic code, and consciously less on stable, low-traffic code, rather than applying uniform intensity everywhere (which is how "5,000 nitpicks" reports happen and get ignored wholesale).
- Recognize genuinely contested territory (Ousterhout vs. Martin on method length/comments; Metz vs. duplication-skeptics) and don't present house-style preferences as universal law — flag them as judgment calls tied to *this* codebase's stated conventions when no convention exists, say so explicitly rather than asserting one side.

**When to explicitly recommend *not* abstracting** — this should be a first-class, nameable output of the persona, not just an absence of comment:

- Fewer than 3 occurrences of a pattern exist (Rule of Three not yet met) → recommend leaving the duplication, note *why* (not laziness — an explicit "wait for a third case" call).
- A proposed abstraction's interface complexity approaches its implementation complexity (shallow-module test) → recommend inlining or merging instead of extracting.
- An abstraction is being extended with a new parameter/conditional to fit a case it wasn't designed for (Metz signature) → recommend inlining back to callers and re-deriving the abstraction, rather than adding the branch.
- The only justification offered is "for future flexibility/testability" with no concrete near-term second use → recommend YAGNI/speculative-generality flag, suggest building the interface only once a second real caller exists.
- The code is in an explicitly prototype/spike/low-traffic context where the cost of the wrong abstraction (if it turns out wrong) is low and reversible → lower priority entirely, note it as optional rather than a required change.

---

## Sources

- Ousterhout, *A Philosophy of Software Design* — summaries: [Carsten Behrens](https://carstenbehrens.com/a-philosophy-of-software-design-summary/), [system-design.space](https://system-design.space/en/chapter/philosophy-design-book/), [Janmeppe](https://www.janmeppe.com/blog/a-philosophy-of-software-design-john-ousterhout/), [Pragmatic Engineer review](https://blog.pragmaticengineer.com/a-philosophy-of-software-design-review/)
- [aposd-vs-clean-code debate (GitHub)](https://github.com/johnousterhout/aposd-vs-clean-code); secondary summary: [tryingthings.wordpress.com](https://tryingthings.wordpress.com/2025/02/25/aposd-vs-clean-code-a-debate/)
- Sandi Metz, ["The Wrong Abstraction"](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) (2016); counterpoints: [Code with Jason](https://www.codewithjason.com/duplication-cheaper-wrong-abstraction/), [terriblesoftware.org](https://terriblesoftware.org/2025/05/28/duplication-is-not-the-enemy/)
- [Sandi Metz's Rules For Developers (thoughtbot)](https://thoughtbot.com/blog/sandi-metz-rules-for-developers)
- Fowler, *Refactoring* — code smell catalog; empirical validation: [QUB "Software code smells and defects"](https://pure.qub.ac.uk/en/publications/software-code-smells-and-defects-an-empirical-investigation/) ([PDF](https://pureadmin.qub.ac.uk/ws/portalfiles/portal/467641289/Software_code_smells_and_defects_an_empirical_investigation.pdf)), [Springer "diffuseness and impact on maintainability of code smells"](https://link.springer.com/article/10.1007/s10664-017-9535-z)
- Martin Fowler, [bliki: Yagni](https://martinfowler.com/bliki/Yagni.html)
- [zakirullin/cognitive-load (GitHub)](https://github.com/zakirullin/cognitive-load); coverage: [Simon Willison](https://simonwillison.net/2024/Dec/26/cognitive-load-is-what-matters/)
- Adam Tornhill, *Your Code as a Crime Scene* — [author site](https://www.adamtornhill.com/articles/crimescene/codeascrimescene.htm), [Pragmatic Programmers](https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/); CodeScene technical-debt framework: [codescene.io docs](https://codescene.io/docs/guides/technical/prioritize-technical-debt.html), [codescene.com](https://codescene.com/manage-and-reduce-technical-debt)
- tedinski, ["Deconstructing SOLID design principles"](https://www.tedinski.com/2019/04/02/solid-critique.html) (2019)
- Kent Beck, *Tidy First?* — summaries: [tidyfirst.substack.com "Cohesion"](https://tidyfirst.substack.com/p/cohesion), [workingsoftware.dev](https://www.workingsoftware.dev/summary-of-tidy-first-book/)
- On LLM code-review failure modes: [arXiv 2603.00539, "Are LLMs Reliable Code Reviewers? Systematic Overcorrection in Requirement Conformance Judgement"](https://arxiv.org/abs/2603.00539); [arXiv 2508.12358, "Uncovering Systematic Failures of LLMs in Verifying Code Against Natural Language Specifications"](https://arxiv.org/html/2508.12358v1)

**Notes on verification**: All claims above are attributed to a specific fetched or searched source; none are asserted from unverified memory. Where sources disagreed (Metz vs. duplication-skeptics; Ousterhout vs. Martin; SOLID defenders vs. tedinski), both sides are represented rather than picking a winner. The specific numeric claims from Tornhill ("1–2% of code, up to 70% of effort") and Ousterhout ("10–20% design-time investment") are as reported in secondary summaries of the books, not independently verified against the primary text — flagged here for the synthesis stage in case a stronger primary citation is wanted.
