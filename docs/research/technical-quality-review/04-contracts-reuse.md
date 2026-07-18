# Reviewing Contracts, Interfaces, and Reuse

Dimension research for: how great technical code reviews evaluate API boundaries — internal module interfaces and external/public APIs — including design-by-contract discipline, breaking-change hygiene, and when to extract shared abstractions vs. accept duplication.

---

## 1. Key Findings

### 1.1 Design by Contract — the original discipline

Bertrand Meyer's Design by Contract (DbC), introduced with Eiffel, frames every routine as a legal agreement between caller and callee:

- **Preconditions** — obligations the *caller* must satisfy before invoking a routine.
- **Postconditions** — guarantees the *routine* makes about the resulting state, conditional on the precondition having held.
- **Class invariants** — properties that must hold for every instance both before and after any public call.

The core mechanism: "if [preconditions] are true before O is invoked, the routine is under obligation to obey the postcondition... the routine, on its side, is not required to do anything" if the caller failed to meet the precondition — an explicit division of responsibility, not defensive coding by everyone at every layer. ([Meyer, DbC chapter, se.inf.ethz.ch](https://se.inf.ethz.ch/~meyer/publications/old/dbc_chapter.pdf); [Wikipedia overview](https://en.wikipedia.org/wiki/Design_by_contract))

Modern practical descendants a reviewer will actually encounter, none of which use the word "contract":
- Assertion libraries / `assert` at function boundaries.
- Type systems and refined/branded types encoding invariants ("parse, don't validate" — see 1.6).
- Runtime schema validation at process/service boundaries (JSON Schema, Zod, io-ts, Pydantic).
- Contracts-as-tests: a contract can double as a test oracle, removing the need for a hand-written oracle per test case ([ScienceDirect overview](https://www.sciencedirect.com/topics/computer-science/design-by-contract)).

**Review implication:** the useful question isn't "did they write `assert`" — it's "is it clear, at this boundary, whose job it was to validate what, and does the code actually enforce that division?" A function that silently re-validates everything its caller already guaranteed is doing the caller's job for it (masking bugs upstream); a function that assumes validity it never checked is a contract violation waiting to happen.

### 1.2 API design review at scale: Google AIP

Google's API Improvement Proposals (aip.dev) are the closest thing to a documented, at-scale "how we review APIs" process:

- AIPs are living design docs, split into **Guidance AIPs** (design rules API producers must follow, e.g. "AIP-131: standard methods: Get") and **Process AIPs** (how the AIP system itself runs). ([AIP-1](https://google.aip.dev/1), [google.aip.dev](https://google.aip.dev/))
- Formal states: Draft → Reviewing → Approved (or Rejected/Withdrawn). Reviewing requires one editor's signoff; Approved requires two editors' signoff, and either can be blocked by open objections — i.e., **API review is asynchronous, editor-gated consensus, not a single owner's rubber stamp**.
- Crucially, human review is backstopped by a linter: **linter.aip.dev** runs automatically on check-in — "the first line of defence... well before it ever hits an API reviewer" — so reviewers spend their attention on judgment calls (naming, resource modeling, consistency with the rest of the API surface) instead of mechanical rule violations caught earlier and cheaper. ([Chuniversiteit: Scaling API design review at Google](https://chuniversiteit.nl/papers/api-governance-at-scale))

**Review implication:** separate "linter-checkable contract rules" (naming conventions, required fields, pagination shape) from "judgment calls" (is this the right resource model, does this endpoint belong). An AI reviewer should not spend its limited attention rediscovering what a linter already catches — it should focus where judgment is needed, and treat linter/schema-diff output as an input signal, not its main job.

### 1.3 Stripe: absorb the cost of change internally, review before you ship

Stripe's philosophy, distilled from their versioning writeup ([stripe.com/blog/api-versioning](https://stripe.com/blog/api-versioning)):

- "An API represents a contract for communication that can't be changed without considerable cooperation and effort" — the contract framing is explicit and load-bearing, not decorative.
- Stripe has never broken backward compatibility since 2011. Instead of `v1`/`v2`, they use **date-based rolling versions** (e.g. `2024-10-01`); each account is pinned to the version active on its first request, and upgrades are opt-in, per-account, and staged. Starting with the `2024-09-30.acacia` release, new versions ship monthly with *no* breaking changes, and breaking-change releases happen only twice a year. ([averagedevs.com summary](https://www.averagedevs.com/blog/stripe-api-versioning-explained))
- Internally: old-version behavior is isolated in "self-contained modules that handle transformations" at the edge, so the core system only ever speaks the current shape — the versioning cost is paid once, centrally, not scattered through business logic.
- Most load-bearing: **they try to avoid ever needing a version bump** via a lightweight pre-ship API design review — a short doc circulated to a broad internal mailing list specifically "to improve the likelihood that we'll catch errors and inconsistencies before they're released." Review happens *before* the contract exists, because after it exists, changing it costs someone else's integration.

**Review implication:** the highest-leverage moment for an API reviewer is pre-merge on a *new* endpoint/field/type — cheap to change now, expensive after the first external caller. Once merged, review shifts entirely to "is this compatible with what's already promised," which is a different, narrower, more mechanical question.

### 1.4 Hyrum's Law — why "we didn't document that" isn't a defense

> "With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody." ([hyrumslaw.com](https://www.hyrumslaw.com/))

Named by Titus Winters after Hyrum Wright's observation at Google. The consequence for review: an *implicit* interface — response ordering, error message text, timing, field presence when logically absent, HTTP status code choice among near-equivalents — becomes just as binding as the *documented* interface once enough consumers exist. "Over time, the implementation becomes the interface." ([Nordic APIs](https://nordicapis.com/what-does-hyrums-law-mean-for-api-design/))

This is why "it wasn't part of the documented contract" is a weak defense for a change that breaks callers — the real question is exposure (how many consumers, how likely to depend on that detail), not documentation.

**Review implication:** when reviewing a change to *internal* behavior of an already-shipped, widely-consumed endpoint (ordering, formatting, incidental fields, timing), the reviewer should ask "how many callers exist and could plausibly depend on this specific detail," not just "did we promise this in the docs." This is fundamentally a whole-system/telemetry question a diff alone cannot answer (see §4).

### 1.5 Semver: correct in theory, leaky in practice

- SemVer compresses "what changed, how many users are affected, how severe" into one integer bump — Jeremy Ashkenas's well-known critique argues this is structurally lossy: a major bump "1.0 like everything else" tells a consumer nothing about *how much* work the upgrade actually requires. ([gist: "Why Semantic Versioning Isn't"](https://gist.github.com/jashkenas/cbd2b088e20279ae2c8e))
- Empirically, violations are common even among well-maintained projects: one study found 1 in 6 of the top 1000 Rust crates violated semver at least once ([predr.ag FOSDEM 2024](https://predr.ag/blog/semver-in-rust-tooling-breakage-and-edge-cases/)); another found breaking changes routinely ship in Maven Central minor/patch releases, though the rate has been improving over 14 years (84.4%→30.1% of breaking changes correctly bumping minor; 59.7%→9.6% for patch) — evidence that **tooling-enforced discipline, not the version number scheme itself, is what actually improved outcomes** ([arxiv 2110.07889](https://arxiv.org/pdf/2110.07889)).
- Practical guidance converges on: intentional breaking changes need cost-justification and a public migration plan, not just a version bump ([Zuplo](https://zuplo.com/learning-center/semantic-api-versioning)).

**Review implication:** don't trust a version-bump number as evidence a change is safe or unsafe — verify the actual diff against the actual rule set (see 1.8 tooling). Semver is a communication convention layered on top of a compatibility judgment a human or a diff tool still has to make.

### 1.6 Consumer-Driven Contract testing (Pact) — the contract as an artifact, not a document

CDC testing inverts the traditional "provider writes docs, consumer trusts docs" flow: the **consumer** encodes its actual expectations as an executable contract, the provider replays and verifies against it in CI. Mechanism ([Pact docs](https://docs.pact.io/), [Pactflow explainer](https://pactflow.io/what-is-consumer-driven-contract-testing/)):

1. Consumer writes a test against a Pact mock; Pact records the interaction into a `.pact` JSON file.
2. That file is published to a Pact Broker.
3. The provider pulls the pact and replays the recorded requests against its real implementation; failures mean the provider would break that specific consumer.

This turns "does this change break someone" from a guess into a CI-gated fact, and importantly captures *actual observed usage* rather than documented spec — directly mitigating Hyrum's Law by making the implicit interface explicit and testable, per-consumer.

**Review implication:** where a contract-test suite exists, a diff that fails provider verification is an unambiguous, high-confidence breaking-change signal — stronger than static schema diffing because it reflects real consumer behavior, not just declared types. Where it doesn't exist, that absence is itself a finding for interfaces with multiple internal or external consumers.

### 1.7 Postel's Law — the "liberal in what you accept" principle, and why modern practice pushes back

Classic formulation: be conservative in what you send, liberal in what you accept. Modern critique, well-documented:

- **Security**: liberal acceptance of malformed input is a primary vector — "pretty much every security exploit begins with a slightly malformed input" that a stricter parser would have rejected outright ([lobste.rs discussion of "Harmful Consequences of the Robustness Principle"](https://lobste.rs/s/enszyj/harmful_consequences_robustness)).
- **Debuggability**: silently accepting or silently discarding bad input makes misbehaving integrations hard to diagnose on both ends; loud, immediate rejection is now generally preferred to silent leniency ([devopedia](https://devopedia.org/postel-s-law)).
- **Compounding complexity**: every accepted variant an implementation tolerates becomes a de facto part of its interface (this is Hyrum's Law again, from the input side) — liberal parsers accumulate ad hoc tolerance logic that itself becomes unremovable.

**Review implication:** flag boundary code that silently coerces, defaults, or swallows malformed input instead of rejecting it with a clear error — that leniency is a liability, not a courtesy, especially in security- or payment-adjacent code. The modern default at a boundary should be strict validation with a clear, typed error (see "parse, don't validate," 1.6-adjacent), not permissive best-effort acceptance.

### 1.8 API-diff and breaking-change tooling — verifying compatibility mechanically

Reviewers (human or AI) should not manually reason about compatibility when tooling exists to compute it:

- **oasdiff** (OpenAPI): purpose-built to classify every OpenAPI spec change as breaking / non-breaking across 8 categories (schema, parameters, paths/operations, security, responses, request body, headers, components) — ~500 distinct recognized change types. It supports a hosted PR-review workflow where breaking changes must be explicitly approved before merge, gating the commit status. ([oasdiff.com](https://www.oasdiff.com/), [GitHub](https://github.com/oasdiff/oasdiff))
- **buf breaking** (Protobuf/gRPC): diffs schema against a prior ref (branch, tag, BSR module) with explicit compatibility *categories* — FILE, PACKAGE, WIRE_JSON, WIRE — because "breaking" means different things depending on whether you care about wire compatibility, JSON compatibility, or generated-code source compatibility. Runs in CI, comments inline on the PR. ([Buf docs](https://buf.build/docs/breaking/))
- Language/package-ecosystem equivalents exist for the same reason (Rust's semver-checking tooling referenced in 1.5, `api-extractor` for TypeScript, `japicmp`/`revapi` for Java, etc.) — the pattern is consistent: **compatibility is a mechanically computable diff against a prior schema/surface snapshot, not a matter of reading the code and guessing.**

**Review implication:** for typed/schema'd interfaces (protobuf, OpenAPI, GraphQL SDL, public package exports), an AI reviewer's highest-confidence move is running or simulating this class of diff, not eyeballing the change. Confidence should scale with whether such a tool ran, not with how careful the prose review was.

### 1.9 Reuse review: when to extract, when to duplicate

- **Rule of Three** (Fowler/Roberts): two occurrences of similar code don't yet justify abstraction; wait for a third before extracting, because "it's easier to make a good abstraction from duplicated code than it is to refactor the wrong abstraction" — premature DRY-ing risks locking in the wrong shape before enough examples reveal the actual pattern. ([Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)), [Andrew Brookins](https://andrewbrookins.com/technology/the-rule-of-three/))
- Explicit counter-risk: an "extreme drive to remove duplication yields problem-ridden components that solve too-specific problems and require constant modification" — the abstraction becomes a shared bottleneck that couples unrelated call sites, and every future divergent need forces either a parameter explosion or a fork. Coincidental similarity (same shape, unrelated business meaning) is the classic trap — merging code because it *looks* the same when it means different things.
- **Minimal-surface API design** (Joshua Bloch, "How to Design a Good API and Why it Matters," OOPSLA 2006 — [Google Research PDF](https://research.google.com/pubs/archive/32713.pdf)): "When in doubt, leave it out" is described as close to a fundamental theorem of API design, applying equally to functionality, classes, methods, and parameters — because "you can always add things later, but you can't take them away." Bloch emphasizes minimizing *conceptual weight*, not just symbol count — a small API that requires holding five interacting concepts in your head is worse than a slightly larger one with orthogonal, independent pieces.
- Casey Muratori's "semantic compression" essay ([caseymuratori.com/blog_0015](https://caseymuratori.com/blog_0015)) argues for resisting premature interface/class generalization: build the concrete case first, generalize only once the actual shared structure is visible from real usage — echoing Rule of Three from the API-design side rather than the duplication side.

**Review implication:** reuse review has two failure directions, and a good reviewer checks both — (a) duplicated logic that has now diverged accidentally (a bug fixed in one copy, not the other — genuinely dangerous), vs. (b) a shared abstraction straining under callers with different actual needs (parameter creep, boolean flags controlling unrelated behavior, "please don't touch this, three teams depend on it"). Extracting too early is now the *harder-to-detect* failure mode because it looks like good practice at extraction time and only reveals its cost several callers later — an AI reviewer looking at a single diff will systematically under-detect this.

### 1.10 Error contracts

- Modern practice treats error *shape* as part of the interface contract, not incidental to it: "error responses are part of the public interface... consumed by multiple clients, evolving over time. Error payloads should be treated as part of the interface, not as whatever falls out after a thrown exception." ([Medium: Designing API Errors](https://medium.com/@giy.marie/designing-api-errors-contracts-for-predictable-frontends-d2989aeace24))
- Concretely this means: a stable, documented set of machine-readable error codes/types (not raw exception class names or stack-trace-derived messages), paired with a human-readable message, using standard HTTP status semantics rather than repurposed or custom codes. RFC 9457 (Problem Details for HTTP APIs) and JSON:API's error object are the two converged shapes cited for this.
- **Review implication:** an error-message wording change or an exception-type change is a contract change if any consumer branches on it (string-matches an error message, checks an exception class, or switches on an error code) — this is a very common "silent break" because it doesn't touch the success-path schema that most diff tools check. This is a place where diff tooling (1.8) is weakest — most schema/API diffing focuses on success responses, and error taxonomy changes often slip through unflagged.

### 1.11 Deprecation and sunset discipline

- **RFC 8594** (`Sunset` header) and **RFC 9745** (`Deprecation` header) formalize machine-readable deprecation: `Deprecation` signals "no longer preferred, but working," `Sunset` signals a specific date it will stop working, and a `Link` header should point to migration docs. ([RFC 8594](https://www.rfc-editor.org/rfc/rfc8594.html), [Zalando REST guidelines: deprecation](https://github.com/zalando/restful-api-guidelines/blob/main/chapters/deprecation.adoc))
- Best practice explicitly separates two distinct events people conflate: "no longer recommended" vs. "will stop working on date X" — using the same signal for both under-communicates urgency in one direction or the other.
- Operationally: deprecation headers should be applied programmatically (middleware), not left to individual endpoint authors to remember; and actual usage of the deprecated path should be tracked so the team knows who's still depending on it before the sunset date arrives — otherwise "sunset" dates get pushed indefinitely because no one can say who'd break.

**Review implication:** a PR that removes/changes a public field or endpoint without going through a deprecation window (headers, migration doc, tracked-usage check) is skipping a step that exists specifically to convert an unplanned break into a planned one — this is checkable from the diff and repo conventions alone.

### 1.12 Leaky abstractions and accidental public surface

- A leaky abstraction "fails to completely hide underlying complexity," forcing callers to understand implementation details to use it correctly or debug it — the practical review symptom is an interface that *works* for the happy path but forces callers to reach past it under any stress (errors, retries, edge cases, perf) ([Wikipedia](https://en.wikipedia.org/wiki/Leaky_abstraction)).
- Prevention pattern repeatedly cited: keep an interface genuinely *private* to its module (language-level `internal`/package-private/unexported, not just "we don't mention it in the README"), so implementation classes can only be reached through the sanctioned interface — accidental public surface usually results from *not* using the language's actual visibility controls, defaulting everything to exported/public because it's the path of least resistance.
- "Leaky abstraction by omission" ([ploeh blog](https://blog.ploeh.dk/2021/04/26/leaky-abstraction-by-omission/)): an abstraction can leak not by exposing too much, but by *failing to expose something essential*, forcing callers to bypass it entirely to get needed information (e.g., an interface that hides error causes callers actually need to handle correctly) — leakiness isn't only an over-exposure problem.

**Review implication:** for a new public export (class, function, field), the reviewer's question isn't just "is this named well" but "was this exported deliberately, or because that was the default." Accidental-export is far more common than deliberate bad API design and is mechanically detectable by diffing the *exported surface*, not the whole file (see §4).

---

## 2. Concrete Heuristics / Checklist for Reviewing Contracts and Interfaces

**On any new or changed public/shared interface:**
1. Is every new symbol (type, method, field, export) *intentionally* public, or is it exported by default/laziness? Prefer the narrowest visibility that works.
2. For each parameter/field: whose job is validation — caller's or callee's — and does the code actually match that division? Don't let both sides silently re-validate (waste) or neither side validate (bug).
3. Does the diff touch a *documented* contract element (type, field, status code) or only an *undocumented but observable* one (ordering, timing, incidental field presence, error message text)? Both can break consumers (Hyrum's Law) — flag the latter with lower certainty but don't ignore it.
4. Is the change additive (new optional field/endpoint) or does it narrow/remove/rename/retype something existing? Only the former is safe without a version/deprecation story.
5. If the boundary is schema'd (OpenAPI/protobuf/GraphQL), was an actual diff tool run (oasdiff/buf breaking/equivalent) — or is "looks fine" the only evidence?
6. Does an error-shape or error-code/message change accompany this diff? Treat it with the same scrutiny as a response-schema change — most diff tooling under-covers this.
7. Is a removal/rename accompanied by a deprecation window (header, changelog, migration doc) — or is it landing as an immediate break?
8. For input boundaries: does new code reject malformed/unexpected input loudly, or silently coerce/default/ignore it? Prefer the former.

**On reuse / abstraction changes:**
9. Is a newly extracted shared function/module serving ≥3 genuinely-alike call sites, or is it generalizing from 1–2 (premature abstraction risk)? Conversely, is duplicated logic across ≥3 places that already looks aligned a missed-extraction risk?
10. Does the shared abstraction take on parameters/flags whose only purpose is to let two divergent callers coexist inside one function? That's a smell that the callers aren't actually the same operation.
11. For a proposed shared library/module: is it serving one clear conceptual operation (Bloch's "minimal conceptual weight"), or is it becoming a grab-bag because it was the easiest place to add "just one more thing"?

**On error and evolution:**
12. Does the team have a stable error taxonomy (typed codes, not string-matched messages)? Flag ad hoc exception-message contracts.
13. Is the change internal-only (no consumers outside the diff's own commit) or does it touch something with a broker/contract-test/known external consumer? Scale scrutiny to actual exposure, not to documentation completeness.

---

## 3. Anti-Patterns

- **Contract via convention, not enforcement** — a "contract" that exists only in a comment or a Slack thread, never asserted, typed, or tested. Guaranteed to drift.
- **Both-sides revalidation** — caller checks input, then callee checks it again "just in case," and neither is actually the source of truth; the real precondition is undocumented and unverifiable.
- **Version-number theater** — bumping a major/minor version without an actual compatibility audit, trusting the number instead of a diff.
- **Silent leniency at boundaries** — best-effort parsing, default-on-missing, swallow-and-continue on malformed input, in the name of "robustness" (modern Postel's-law critique).
- **Accidental public surface** — everything exported by default because the language made that the path of least resistance, rather than a deliberate choice about what's supported.
- **Premature DRY** — extracting a shared abstraction from two superficially similar call sites before a third example reveals whether they're actually the same operation; results in a bottleneck with flag-parameter creep.
- **Error contract amnesia** — success-path schema is versioned and reviewed carefully; error shape, codes, and messages are treated as free-form and change without notice, breaking consumers that branch on them.
- **Break-then-announce** — removing/renaming a field or endpoint and treating a changelog entry as sufficient, with no deprecation window, no usage telemetry on who's still calling it, no sunset header.
- **Hyrum-denial** — defending a breaking change with "that was never in the documented contract," ignoring that observed behavior with enough consumers *is* the contract regardless of documentation.
- **Coincidental-similarity merging** — unifying two code paths because they currently look alike, without confirming they mean the same thing conceptually; the first divergent future requirement then forces an awkward parameterization or a re-split.

---

## 4. Implications for an AI Contracts/Reuse Reviewer Persona

**What's reliably inspectable from a diff alone:**
- New public/exported symbols and whether their visibility looks deliberate (language-level check, cheap and high-signal).
- Structural schema changes to typed boundaries (OpenAPI/protobuf/GraphQL/exported TS types) — this is exactly the class of check tools like oasdiff/buf-breaking are built for; an AI reviewer should defer to or simulate that class of analysis rather than reason about compatibility from prose, and should say so explicitly when no such tool ran.
- Presence/absence of validation logic at a clearly identifiable boundary (request handler, public function entry, deserialization point) and whether it fails loudly vs. silently.
- Error-code/message/exception-type changes co-located in the same diff as the feature change — this needs an explicit reviewer prompt because generic schema-diff tooling tends to skip it.
- Obvious rule-of-three violations *within* the diff (e.g., a new third near-identical block appearing in the same PR that touches the first two) — but this only catches the case where all copies are visible in one diff.

**What genuinely needs whole-repo or cross-repo context, and where an AI reviewer should be explicit about reduced confidence or should escalate rather than guess:**
- **Consumer count/exposure** (Hyrum's Law calls): whether an "undocumented" behavior actually has dependents requires knowing who calls this API — internal call-site search across the repo at minimum, ideally telemetry/contract-test coverage (Pact-style) or usage analytics for external APIs. A diff-only reviewer cannot tell "nobody could possibly depend on this" from "everybody depends on this" without that search.
- **Rule-of-three duplication across the whole codebase**, not just the current diff — the third occurrence is very often in a file the diff doesn't touch at all.
- **Whether a shared abstraction is straining** — this shows up as accumulated special-casing *over time*, i.e., git history of the shared module, not visible from a single diff.
- **Whether a contract-test suite (Pact or equivalent) exists and was run** — if it exists, its pass/fail is the strongest available breaking-change signal and should be weighted above manual inference; if it doesn't exist for a multi-consumer interface, that absence is itself a finding worth surfacing, not something to route around by inferring "probably fine."
- **Deprecation-window compliance** — requires knowing repo/org convention (is there a standard deprecation period, a header middleware, a changelog format) which lives outside the diff.

**Concrete design implication:** the persona should be explicit about *evidence tier* per finding — (1) "verified via schema-diff/contract-test tool: X" (highest confidence), (2) "verified via repo-wide call-site/export search: Y" (medium, mechanical but scoped to this repo), (3) "inferred from diff context alone, exposure/consumer count unknown" (lowest — should be phrased as a question or flagged as needing owner input, not asserted as a breaking change). Treating all three tiers as equally confident findings is the main way a contracts reviewer overclaims.

---

## Sources

- [Meyer, "Design by Contract" chapter (PDF)](https://se.inf.ethz.ch/~meyer/publications/old/dbc_chapter.pdf)
- [Design by contract — Wikipedia](https://en.wikipedia.org/wiki/Design_by_contract)
- [Design By Contract — ScienceDirect Topics overview](https://www.sciencedirect.com/topics/computer-science/design-by-contract)
- [AIP-1: AIP Purpose and Guidelines](https://google.aip.dev/1)
- [google.aip.dev](https://google.aip.dev/)
- [Scaling the API design review process at Google — Chuniversiteit](https://chuniversiteit.nl/papers/api-governance-at-scale)
- [APIs as infrastructure: future-proofing Stripe with versioning — Stripe blog](https://stripe.com/blog/api-versioning)
- [Stripe's API Versioning Explained — AverageDevs](https://www.averagedevs.com/blog/stripe-api-versioning-explained)
- [Hyrum's Law](https://www.hyrumslaw.com/)
- [What Does Hyrum's Law Mean for API Design? — Nordic APIs](https://nordicapis.com/what-does-hyrums-law-mean-for-api-design/)
- ["Why Semantic Versioning Isn't" — Jeremy Ashkenas gist](https://gist.github.com/jashkenas/cbd2b088e20279ae2c8e)
- [SemVer in Rust: Tooling, Breakage, and Edge Cases — FOSDEM 2024](https://predr.ag/blog/semver-in-rust-tooling-breakage-and-edge-cases/)
- ["Breaking Bad? Semantic Versioning and Impact of Breaking Changes in Maven Central" (arXiv)](https://arxiv.org/pdf/2110.07889)
- [Semantic Versioning for APIs — Zuplo](https://zuplo.com/learning-center/semantic-api-versioning)
- [Pact docs — Introduction](https://docs.pact.io/)
- [What is Consumer-Driven Contract Testing (CDC)? — Pactflow](https://pactflow.io/what-is-consumer-driven-contract-testing/)
- [The Harmful Consequences of the Robustness Principle — Lobsters discussion](https://lobste.rs/s/enszyj/harmful_consequences_robustness)
- [Postel's Law — Devopedia](https://devopedia.org/postel-s-law)
- [oasdiff — API Change Review](https://www.oasdiff.com/)
- [oasdiff — GitHub](https://github.com/oasdiff/oasdiff)
- [Detecting breaking changes — Buf Docs](https://buf.build/docs/breaking/)
- [Rules and categories — Buf Docs](https://buf.build/docs/breaking/rules/)
- [Parse, Don't Validate — Practical Lessons (Medium)](https://medium.com/@trinitietp/parse-dont-validate-practical-lessons-df352da8a154)
- [Rule of three (computer programming) — Wikipedia](https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming))
- [The Rule of Three — Andrew Brookins](https://andrewbrookins.com/technology/the-rule-of-three/)
- [Bloch, "How to Design a Good API and Why it Matters" (Google Research PDF)](https://research.google.com/pubs/archive/32713.pdf)
- [Casey Muratori, "Semantic Compression"](https://caseymuratori.com/blog_0015)
- [Designing API Errors: Contracts for Predictable Frontends (Medium)](https://medium.com/@giy.marie/designing-api-errors-contracts-for-predictable-frontends-d2989aeace24)
- [RFC 8594 — The Sunset HTTP Header Field](https://www.rfc-editor.org/rfc/rfc8594.html)
- [Zalando REST API Guidelines — Deprecation chapter](https://github.com/zalando/restful-api-guidelines/blob/main/chapters/deprecation.adoc)
- [Leaky abstraction — Wikipedia](https://en.wikipedia.org/wiki/Leaky_abstraction)
- [Leaky abstraction by omission — ploeh blog](https://blog.ploeh.dk/2021/04/26/leaky-abstraction-by-omission/)

*Note: a few secondary claims from search-result summaries (e.g., exact AIP linter integration details, Casey Muratori's talks beyond the "Semantic Compression" essay) could not be independently verified against primary text within this research pass and are stated cautiously or omitted.*
