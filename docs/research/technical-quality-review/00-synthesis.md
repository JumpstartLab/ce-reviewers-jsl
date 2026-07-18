# Technical Quality Review: Research Synthesis and Design Strategy

Groundwork for a software-quality orchestrator + reviewer team — the crew that deep-dives
on testing, abstraction, contracts, reuse, framework patterns, comments, performance, and
documentation. Not user-facing functionality (Angie's territory), not security (Cass's).

Eight research agents each investigated one dimension and produced a full cited report
(files `01`–`08` in this directory). This document synthesizes what they found into
cross-cutting principles, a proposed roster, and an orchestrator design.

---

## 1. The five findings that should drive the whole design

**1. Specialized lenses aren't a style choice — they're empirically necessary for coverage.**
Three independent lines of evidence converge: Perspective-Based Reading experiments (the
inspection literature) show role-diverse reviewers catch more unique defects at lower cost
than one reviewer with a bigger checklist; reviewer expertise varies ~10x and is the top
predictor of catching real defects (Kononenko et al.); and a 146-PR parallel run of four
commercial AI reviewers found **93.4% of findings were caught by exactly one tool — zero
convergence**. A panel only realizes this benefit if each persona carries a genuinely
distinct question class, not a renamed copy of a generic reviewer. (Reports 01, 08)

**2. Noise is the existential risk, and the cure is subtraction, not addition.**
Noise is the #1 documented reason teams abandon AI review (15–25% low-value comments
across Copilot/CodeRabbit audits; AI comments get acted on at 0.9–19.2% vs. 60% for
humans). Cloudflare's production 7-agent panel (131K reviews/month) averages **1.2
findings per review** because every persona carries an explicit "do NOT flag" exclusion
list — "telling an LLM what not to do is where the actual prompt engineering value
resides." Every persona we write needs an exclusion list as long as its checklist.
(Report 08)

**3. Every finding needs an evidence tier, and confidence must be tied to the tier.**
This pattern emerged independently in four dimensions:
- *Contracts*: (1) verified by schema-diff/contract-test tool → (2) verified by repo-wide
  search → (3) inferred from diff alone, phrase as question.
- *Performance*: (1) always-wrong syntactic shapes (leaked connection, retry without
  jitter) assertable from the diff → (2) scale-dependent patterns (Seq Scan, O(n²))
  must be phrased as questions naming the data-size assumption → (3) hot-path
  identification deferred to profiler/benchmark, and say so.
- *Testing*: static smells (weak assertions, tautology-via-aliasing, over-mocking) are
  reviewable from the diff; the single most powerful check — "would this test fail if
  the behavior broke" — is fundamentally dynamic (mutation testing / revert-and-rerun)
  and must be labeled a scope boundary.
- *Docs*: mechanical checks (commented-out code, orphaned TODOs, signature-changed-
  without-comment-changed, stale symbol refs) run cheap and high-confidence; content
  truth is a judgment call scoped to lines the mechanical pass flagged.
Collapsing tiers into one confidence level is the single biggest credibility destroyer —
the scale-dependent findings are right often enough to sound authoritative and wrong
often enough to erode all trust. (Reports 02, 04, 06, 07)

**4. Verification passes only help when they're adversarial and asymmetric.**
Naive "review the review" measurably makes things worse — multi-turn re-review increases
false positives faster than recall (context contamination). What works: a second pass
with a *different objective* (disprove, not confirm), *less context* than the finder
(so it must independently re-derive the claim), grounding in executable checks
(grep/ast-grep/linter), and an explicit stop condition. (Report 08)

**5. Most of review's real value is maintainability, not bug-catching — and
"don't abstract" is a first-class finding.**
Bacchelli & Bird: review's realized benefit is evolvability + knowledge transfer, with
defect-finding secondary. Google treats speculative generality as a review defect on par
with bugs. LLM reviewers specifically are documented to cargo-cult SOLID and speculate
"best practices" orthogonal to the requirement (arXiv 2603.00539). So the design panel
must be able to output "leave this alone: Rule of Three not met / shallow-module test
failed / no concrete second use case" as a named recommendation, not silence — and no
persona may cite a principle name (SRP, DRY, DIP) as the finding itself; it must name
the concrete future change the design makes harder. (Reports 01, 03)

---

## 2. Cross-cutting operating rules (orchestrator-level, apply to every persona)

1. **Diff-size gate before dispatch.** Defect detection collapses past ~200–400 LOC per
   review unit (SmartBear/Cisco, 2,500 reviews; Google converges independently at ~100
   ideal / 1,000 too large). Chunk large diffs; if unsplittable, deep-review a
   representative subset rather than skimming everything.
2. **Stated intent before dispatch.** "Does it behave as the author intended" — Google's
   #1 check — is unanswerable without a stated intent. No description/linked issue →
   synthesize intent from commits/tickets first, or fail the pre-review gate.
3. **Lint-boundary check before any finding posts.** If a lint rule could catch it with
   no false positives, the finding is "add a lint rule," filed once — never a per-PR
   comment. (Google policy; Go's gofmt precedent; AIP linter-before-reviewer pattern.)
4. **Source-citation hierarchy for style/idiom findings:** external canon (Go wiki,
   Effective Java item, Rails Doctrine) > project ADRs/style guide > local codebase
   precedent — with Google's caveat that local consistency stops justifying a match
   once it would spread an existing deviation. Uncited taste is not a finding.
5. **Weight severity by churn.** Hotspot research (Tornhill): ~1–2% of a codebase drives
   most maintenance cost. The same smell is a top finding in a weekly-edited file and
   noise in a stable one. Give personas a cheap churn signal (`git log --oneline -- file
   | wc -l`).
6. **Cap repeated patterns at 2–3 instances** then request a sweep (Lynch + Google
   converge). Dedup is the orchestrator's job before anything posts.
7. **Sequence findings: design before style.** Suppress low-level comments entirely when
   a high-level finding says the direction needs to change.
8. **Bias toward approval.** Approve on net improvement, not perfection (Google's
   Standard). Cloudflare's approval-rubric state machine + 0.6% human override rate is
   the template: block only on concrete, severe, verified findings.
9. **Sycophancy control.** First-pass personas never see the author's self-justification
   or PR prose — only the code and the stated intent. Author rationale re-enters at
   synthesis, where it can answer questions the personas raised.
10. **Output shape:** hunk-level, high code-to-text ratio, concise, severity-grouped,
    total findings capped (~5–10). These are the empirically strongest predictors of a
    comment actually being acted on.
11. **Curate context, don't maximize it.** Neighboring-function + co-change-history
    context measurably helps (+3.76pp); piling more on top measurably hurts ("When More
    Retrieval Hurts"). The context pack per persona: the hunks, enclosing functions,
    call sites of changed shared code, churn counts, the style guide/ADRs, and the
    rejected-findings ledger. Stop there.
12. **Ledger of rejected findings.** Same mechanism Angie already uses
    (`docs/audits/<scope>-ledger.md`): findings Jeff rejected with a reason are passed
    to personas as "don't re-surface." This is how the panel compounds instead of
    re-litigating.

---

## 3. Proposed roster: six lenses

Each lens = one persona with its own checklist, exclusion list, and evidence-tier rules.
Section 4 of each numbered report is effectively the first draft of each persona's prompt.

| Lens | Owns | Sharpest checks | Must NOT flag |
|---|---|---|---|
| **Test quality** (02) | Would the suite catch a real break? | Weak/tautological assertions (aliasing), over-mocking internal collaborators vs. true I/O boundaries, change-detector shape, sleep()/mystery-guest flake precursors, bug-fix PRs without a red-first regression test | All mocking; fixture changes during refactors; coverage % as verdict; PBT everywhere |
| **Abstraction & design** (03) | Deep vs. shallow modules, wrong abstractions, cognitive load | Metz parameter/conditional stretching test, information leakage, interface-to-implementation ratio, "what must this NOT know," Rule of Three; explicit "don't abstract" recommendations | Principle-name-as-finding, small-function dogma, DRY-ing 2 occurrences, uniform intensity on low-churn files |
| **Contracts & reuse** (04) | API boundaries, breaking changes, validation division | New-public-surface deliberateness, additive vs. narrowing changes, error-contract changes (the most-missed break), silent coercion at boundaries, deprecation-window compliance, Hyrum-exposure questions | Tier-3 (diff-only) inferences asserted as breaks; both-sides-validation demands; semver trust |
| **Framework fit & idiom** (05) | Working with vs. against the framework | Concern/service-object domain-semantics test ("what noun does this name?"), reinvented framework primitives, monkey-patch/private-API coupling (Uchitelle's three-question gate), consistency arbitration | Anything a linter covers; uncited "not idiomatic" taste; local consistency that spreads a deviation |
| **Comments & docs** (06) | Comment content, doc-code match | Mechanical pass first (commented-out code, orphaned TODOs, signature-changed-comment-didn't, stale symbol refs, dead examples), then judgment scoped to flagged lines: why-vs-what, interface-comment contamination, missing units/nullability/bounds, docs-in-same-PR gate | Comment presence as virtue; restating-code comments as "documentation"; auditing stable unrelated files |
| **Performance & scale** (07) | Shape-level perf debt review can catch pre-merge | N+1 shape, unbounded queries, DDL without CONCURRENTLY/lock_timeout, connection leaks on exception paths, retry without jitter, unbounded caches; Big-O phrased as data-size questions | "This is slow" without pattern or measurement; micro-optimization of cold code; Seq-Scan reflexes |

Overlap with the existing roster is real and should be resolved at build time: Corey
already owns test-strategy review (hourglass) and Sandi owns OO design. Options: the new
test-quality persona takes the mechanical/smell layer while Corey keeps strategy; or
Corey and Sandi join this crew for their dimensions. The research says split by
*evidence type*, which favors keeping strategy (Corey) and mechanics (new) distinct.

## 4. Orchestrator shape

Phased with gates, in the house style (Angie is the structural template):

1. **Intake gate** — scope + diff-size check (chunk or split), stated intent required,
   load rejected-findings ledger, build the shared context pack once (Cloudflare's
   shared-cache pattern: every persona reviews the same grounded facts).
2. **Risk-tiered dispatch** — orchestrator picks which lenses run: docs-only diff
   doesn't get the performance persona; a migration gets performance + contracts at
   minimum; full roster for large or shared-surface changes. (Anthropic
   orchestrator-workers pattern + Cloudflare's 2/4/7-agent tiering.)
3. **Review** — personas run in parallel on the shared context pack, each emitting
   schema-structured findings: {lens, severity, evidence-tier, file:line, claim,
   citation, suggested fix}.
4. **Adversarial verify** — candidate blocking/warning findings get a refuter pass:
   different objective (disprove), less context, grounded in grep/AST/linter checks,
   explicit stop condition. Tier-3 findings convert to questions instead of dying or
   posting as assertions.
5. **Synthesize** — dedup, cap repeated patterns, sequence design-before-style, apply
   the approval rubric (approve / approve-with-comments / request-changes), cap total
   findings, group by severity.
6. **Compound** — recurring accepted findings become lint rules, style-guide entries, or
   persona exclusion-list updates; rejected findings go to the ledger with reasons.
   This phase is what makes the panel get quieter and sharper over time instead of
   noisier.

## 5. Decisions to make at build time

- **Persona naming** — the roster convention is real-practitioner names (Sandi, Corey,
  Avi). Natural candidates per lens: Ousterhout for abstraction/design, Hyrum or Bloch
  for contracts, Jorge (Manrubia) for framework fit. Jeff's call.
- **Corey/Sandi integration** vs. net-new personas (see §3).
- **Cross-model refutation** — the strongest verify pattern uses a different model
  family for the refuter; our stack is all-Claude, so approximate with asymmetric
  context + different objective, or wire a second provider later.
- **Dynamic checks** — mutation testing and revert-and-rerun are the only sound answers
  to "would this test catch the break." Worth deciding whether the test persona gets
  Bash access to actually run targeted suite subsets, or stays static with the scope
  boundary stated.
- **Mode split** — one orchestrator with lens-dispatch (recommended, per risk-tiering
  evidence) vs. Angie-style named modes.

## 6. Flagged as unverified by the research agents

Kept honest for future citation: the exact "75% maintainability / <25% bugs" comment
ratio (directionally supported, no single primary source); whether human size/pace
detection curves transfer to LLM reviewers (plausible, unestablished); Tornhill's
1–2%/70% and Ousterhout's 10–20% numbers (secondary-source only); all vendor-run
benchmark numbers in report 08 (directional marketing claims); "reinvented framework
features" as a named review discipline (first-principles heuristic, not literature).
