# The Code Review Process: What Makes Reviews Effective

Research dimension for: how great technical code reviews are done. Focus: process, not tooling.

---

## 1. Key Findings

### 1.1 The purpose of review isn't mainly "catch bugs" — it's evolvability + knowledge transfer

The foundational empirical study here is **Bacchelli & Bird, "Expectations, Outcomes, and Challenges of Modern Code Review" (Microsoft Research / ICSE 2013)** — observations, interviews, and a survey of Microsoft developers, plus manual classification of hundreds of review comments.
[Microsoft Research PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf) · [MSR publication page](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)

Key finding: developers *expect* review to primarily find defects, but the actual, measured outcome is different — review's biggest realized benefits are **knowledge transfer, increased team awareness of the code, and creation of alternative solutions**, with defect-finding being real but secondary and mostly catching shallow issues, not deep logic bugs. This is the single most load-bearing empirical fact in this research area: there is a persistent **mismatch between what managers/orgs think review is for (catching severe defects) and what it actually delivers**.

This is corroborated by later comment-classification studies: reporting suggests **up to ~75% of code review comments concern evolvability/maintainability** (naming, structure, readability, documentation) rather than functional correctness, with **well under 15–25% of comments being bug-related**. (Caveat: I could not verify the exact "75%" figure against a single primary source in this pass — it recurs across secondary sources citing the Microsoft/OSS comment-classification literature, e.g. Bosu, Greiler, and follow-on studies referenced by [The New Stack summary](https://thenewstack.io/code-review-catches-maintainability-bugs/) and [arXiv 2510.05450, "What Types of Code Review Comments Do Developers Most Frequently Resolve?"](https://arxiv.org/abs/2510.05450). Treat the precise percentage as directionally correct, not exact.) That second paper adds a useful, more specific data point: bug-related and readability-related comments have measurably **higher resolution/acceptance rates** than design-related comments — reviewers are more successful influencing code when they flag concrete bugs or readability issues than when they contest design choices after the fact. Design disagreements are the comments most likely to be argued with or dropped.

**Implication:** an AI reviewer that only hunts for correctness bugs is solving the smaller half of the problem. A great review process needs a maintainability/evolvability lens as a first-class citizen, not an afterthought — and it should expect that correctness findings land better and faster than architectural ones, so architectural feedback needs different handling (see §4).

### 1.2 Review coverage and participation are causally linked to defects post-release

**McIntosh, Kamei, Adams, Hassan, "An Empirical Study of the Impact of Modern Code Review Practices on Software Quality" (EMSE, extended from MSR 2014)** — case study of Qt, VTK, ITK.
[Full PDF](https://rebels.cs.uwaterloo.ca/papers/emse2016_mcintosh.pdf)

Three variables studied: **review coverage** (fraction of changes actually reviewed), **review participation** (how much reviewer engagement a reviewed change gets — comments, discussion, not just a rubber-stamp), and **reviewer expertise**. All three are independently and significantly associated with post-release defects. Low coverage or low participation is estimated to produce components with **up to 2 (coverage) and 5 (participation) additional post-release defects**. The paper's headline point: it isn't enough that a review *happened* — a review with no real reviewer engagement (i.e., rubber-stamped) provides little of the quality benefit of one with substantive back-and-forth. **Participation matters more than the binary fact of "was it reviewed."**

**Implication:** "a human clicked approve" is not a quality signal. What matters is depth of engagement — number of substantive comments, iterations, and reviewer domain expertise. For an AI panel, this argues for measuring/requiring genuine engagement depth (not just running one pass and stopping), and for routing changes to reviewers (human or AI persona) who actually have context in that code area.

### 1.3 Reviewer skill varies enormously, and expertise is the top predictor of catching real defects

Multiple sources converge: reviewer effectiveness is highly individual — one widely cited empirical result found **the weakest reviewer roughly 10x less effective than the strongest reviewer** at the same organization, and that **reviewer expertise/domain familiarity is the strongest predictor of catching real defects** (see the Kononenko et al. "Code Review Quality: How Developers See It," ICSE 2016, [PDF](https://plg.uwaterloo.ca/~migod/papers/2016/icse16.pdf), and the McIntosh coverage/participation/expertise study above). Classic (human) code review across the literature finds on average **around 60% of injected defects**, with high variance — it is not a reliable safety net on its own, which is consistent with why organizations layer review with tests, static analysis, and CI rather than relying on review alone.

**Implication:** a single generic reviewer pass is weak. Specialization (multiple reviewers each with a distinct lens/expertise) should outperform one generalist doing everything — this is direct empirical support for a multi-persona review panel design, *provided* each persona actually carries distinct, real expertise rather than being redundant copies asking the same questions.

### 1.4 Review size and pace directly govern defect-detection rate — there's a hard ceiling

The **SmartBear/Cisco Systems study** (as documented in Jason Cohen's *Best Kept Secrets of Peer Code Review*, summarized at [SmartBear's Best Practices page](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/) and [11 Best Practices PDF](http://viewer.media.bitpipe.com/1253203751_753/1284482743_310/11_Best_Practices_for_Peer_Code_Review.pdf)) is the largest empirical study of its kind: **2,500 reviews, 3.2M LOC, 10 months, 50 engineers**, with defect logs tied to review size and pace.

Concrete, load-bearing numbers:
- **200–400 LOC is the ceiling for effective review in one sitting** — beyond it, defect-detection effectiveness drops sharply.
- A review of that size done over **60–90 minutes yields 70–90% defect discovery**.
- **Inspection rate matters independently of size**: defect density found drops off sharply above roughly **500 LOC/hour** — reviewing fast is as damaging as reviewing too much at once.
- Average empirical defect density found was **~32 defects/KLOC**, at a detection rate of **~13 defects/hour**, and defect density found was **inversely related to change size** — smaller changes surface proportionally more defects per line.
- A **"spot-check" strategy reviewing only ~20–33% of a large change** produced *lower* defect density found than reviewing all of it in the same time budget — i.e., past a certain size, thorough review of a subset beats shallow review of everything.

Google's own internal guidance (see §1.5 below) converges independently on the same order of magnitude (100 lines "reasonable," 1,000 "usually too large"), despite being derived from different data (developer behavior/speed rather than a controlled defect-detection experiment) — two independent lines of evidence pointing at the same size regime is a strong signal, not a coincidence.

**Implication for an AI reviewer**: this is arguably the single most transferable, mechanically-enforceable finding. A diff-size gate (or an explicit "split this into N reviewable chunks" step before deep review) isn't process theater — it's the biggest lever on defect yield in the entire literature. An AI panel reviewing a 3,000-line diff in one pass is very likely to underperform the same panel reviewing 8 chunks of ~300–400 lines, even holding total compute constant. This also argues for an explicit **pacing control** — an AI could "read" arbitrarily fast, but the human research on why fast review fails (missed context-dependent defects, pattern-matching instead of reasoning) likely still applies to what an LLM reviewer actually attends to; treat this as a candidate design constraint even though it's not verified for LLM reviewers specifically.

### 1.5 Google's Engineering Practices: "improvement, not perfection," and small-CL discipline

Google's public eng-practices docs are the most widely adopted normative (not just empirical) standard in the industry.
[Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) · [What to Look For](https://google.github.io/eng-practices/review/reviewer/looking-for.html) · [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) · [Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html) · [repo](https://github.com/google/eng-practices)

Core principle, quoted directly: *"reviewers should favor approving a CL once it is in a state where it definitely improves the overall code health of the system being worked on, even if the CL isn't perfect... There is no such thing as a 'perfect' CL — there is only better code."* This is the organizing philosophy for the entire standard: reviewers who block on non-blocking preferences (as opposed to real problems) are trading long-run codebase health for short-run "correctness" of their own opinion, and that trade is a net loss because it disincentivizes future contributions.

Decision framework for disagreements, in explicit precedence order:
1. **Technical facts and data** override opinion.
2. **Style guide** is the arbiter of style; where the guide is silent, it's the author's call, not the reviewer's preference.
3. **Engineering principles**, not personal taste, settle design disagreements — if the author claims two approaches are equally valid, the burden is on the author to demonstrate that, not on the reviewer to refute it.
4. **Consistency with the existing codebase** is the tiebreaker of last resort.

Complete "what to look for" checklist (this is the actual review dimension list Google trains reviewers on): **Design, Functionality, Complexity, Tests, Naming, Comments, Style, Consistency, Documentation, Every line, Context, Good things** (explicitly telling reviewers to call out good work, not just problems). Notably, "Complexity" explicitly instructs reviewers to push back on **speculative generality / solving problems the author doesn't yet have** — over-engineering is treated as a first-class review defect, on par with bugs.

Small-CL discipline is treated as a review-quality lever, not merely a workflow nicety: **~100 lines is "usually reasonable," 1,000 is "usually too large."** The stated mechanism matches the SmartBear data above almost exactly — large diffs get skimmed, comments get lost in back-and-forth, and if a reviewer discovers the overall direction is wrong at line 800, all the review time before that was wasted. Google also codifies **speed norms**: reviewers should respond within one business day; the goal is to keep authors from being blocked, even if the reviewer can't complete a full review immediately (send a "haven't forgotten you" or a partial response).

Google's own case study of its practice — **Sadowski et al., "Modern Code Review: A Case Study at Google" (ICSE-SEIP 2018)**, [PDF](https://sback.it/publications/icse2018seip.pdf) / [research.google page](https://research.google/pubs/modern-code-review-a-case-study-at-google/) — reports the practice actually achieves: median time-to-first-feedback under an hour for small changes (~5 hours for very large ones), overall median review latency **under 4 hours**; **>35% of changes touch a single file**, **90% touch fewer than 10 files**; and — a deliberate speed/rigor tradeoff — **over 75% of reviews have exactly one reviewer**. This is markedly faster than the ~15–20 hour median approval times Rigby & Bird report for AMD/Chrome OS/three Microsoft projects, and Google attributes the difference explicitly to enforced small-CL discipline plus tooling, not to reviewers working harder.

### 1.6 Checklists (perspective-based reading) beat unstructured/ad-hoc reading

Root of the field: **Fagan inspection (IBM, 1976)** — the original structured, role-based, formal inspection process, predating modern lightweight PR review by decades. [Overview](https://vfast.org/journals/index.php/VTSE/article/download/920/862/2727).

The inspection-literature refinement most relevant to designing a *multi-role* reviewer panel is **Perspective-Based Reading (PBR)**: instead of one reviewer applying one generic checklist, different reviewers each read the same artifact from a distinct role-perspective (e.g., user, designer, tester), each with a role-specific checklist. Empirical comparisons (multiple controlled experiments, summarized in the requirements/design-inspection literature — e.g. ["How Perspective-Based Reading Can Improve Requirements Inspections"](https://www.researchgate.net/publication/2955334_How_Perspective-Based_Reading_Can_Improve_Requirements_Inspections)) found **PBR detects more unique defects than checklist-based reading (CBR), and does so at lower cost per defect found**, because different perspectives are more likely to be individually blind to different defect classes and collectively cover more of the space (a diversity argument, not just a "more checklists" argument). Plain **checklist-based reading also reliably beats unstructured/ad-hoc reading** in head-to-head experiments, though it doesn't reach PBR's coverage. The generalizable finding across this whole literature: **structure beats freeform reading, and role-diverse structure beats single-perspective structure.**

**Implication:** this is direct, decades-old empirical grounding for exactly the "multiple specialized reviewer personas > one generalist checklist" design already implicit in a panel approach — but it also implies the personas need to be genuinely differently-lensed (distinct defect classes/questions they're uniquely positioned to catch), not just differently-named instances of the same generic reviewer, or the diversity benefit doesn't materialize.

### 1.7 Human/social factors are not a soft add-on — they determine whether findings get acted on

**Michael Lynch, "How to Do Code Reviews Like a Human"** (two-part essay + conference talk), [Part 1](https://mtlynch.io/human-code-reviews-1/) · [Part 2](https://mtlynch.io/human-code-reviews-2/) · [HN discussion](https://news.ycombinator.com/item?id=15475902) — one of the most-cited practitioner writeups on review as a social process, not just a technical one.

Concrete techniques (full list in §2), but the throughline: reviewers who ignore the social dimension get worse compliance and slower merges even when their technical judgment is correct, because authors argue with or route around feedback that reads as personal or absolute. Framing matters mechanically: requests > commands, "we"/passive voice > "you," ground objections in a cited principle/style-guide/doc rather than personal preference (this maps directly onto Google's technical-facts-over-opinion hierarchy in §1.5), and — importantly — **stop nitpicking the same pattern repeatedly**: flag it 2–3 times then ask the author to sweep the rest themselves, rather than commenting on every instance (both Lynch and Google's docs converge on this independently).

Shopify's engineering blog ([Great Code Reviews](https://shopify.engineering/great-code-reviews), [When Culture and Code Reviews Collide](https://shopify.engineering/code-reviews-communication)) reinforces this from a different institution: PRs should be small (~200–300 LOC target), one concern per PR, feedback framed as "our code" not personal criticism, reviewers chosen for actual contextual expertise (not just whoever's free), and PR descriptions should proactively answer *why*, *for whom*, *what alternatives were considered*, and *what's risky* — not just restate the diff. Their explicitly named anti-pattern: weeks of isolated work → one giant PR → superficial review → merge-and-pray. Chelsea Troy's ["Reviewing Pull Requests"](https://chelseatroy.com/2019/12/18/reviewing-pull-requests/) frames the reviewer's job as *taking partial ownership of finishing what the author started* (i.e., reviewers should be prepared to be accountable for the code, which argues for genuine engagement over rubber-stamping) — consistent with McIntosh's "participation" finding in §1.2.

**Implication for an AI panel:** an AI reviewer doesn't have ego, but its *output framing* still determines whether a human author acts on findings. Findings phrased as absolute commands, or that relitigate style-guide-settled questions as if they were open opinions, will get argued with or ignored — wasting the value of a correct finding. The presentation layer (how findings are phrased/prioritized) is not cosmetic; it's load-bearing for whether the review actually improves the code.

### 1.8 Author-side preparation (self-review, PR descriptions, small diffs) shifts the whole cost curve

Convergent, if less rigorously "empirical," practitioner consensus (Shopify, Google eng-practices, multiple dev-blog writeups surveyed): the highest-leverage single thing an author can do before requesting review is **self-review the diff first** — catches the class of error (typos, debug code, obvious logic gaps, dead code) that costs a reviewer real time to find but costs the author almost nothing to catch themselves, because they already hold the context. Second: **write a description that explains *why*, not just *what*** — the diff already shows what changed; the description's job is to carry intent, alternatives considered, and risk, which the reviewer cannot reconstruct from the code alone. Third: **keep changes small and single-concern** (ties back to §1.4/§1.5's size ceiling — this is the author-side lever that produces the review-size regime reviewers depend on).

**Implication:** for an AI review pipeline, this suggests a **pre-review gate**: an automated or AI self-review pass against the author's own stated intent (from a description/ticket) before the "real" multi-perspective panel runs, both to strip out the cheap-to-catch category and to give the panel a stated intent to check the diff against (directly enabling the "Functionality: does it behave as the author intended" checklist item from §1.5, which is otherwise unanswerable without a stated intent).

---

## 2. Concrete heuristics/checklists great reviewers use

**Review dimensions (Google's "what to look for," the most complete public checklist):** Design → Functionality → Complexity → Tests → Naming → Comments → Style → Consistency → Documentation → every line → surrounding context/system health → explicitly call out good work. ([source](https://google.github.io/eng-practices/review/reviewer/looking-for.html))

**Size/pace discipline:**
- Target ~100–400 LOC per review unit; treat >1,000 LOC as a near-automatic "split this" ([Google](https://google.github.io/eng-practices/review/developer/small-cls.html), [SmartBear](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/))
- Cap effective review pace around ~400–500 LOC/hour; don't let review speed outrun comprehension
- If a diff can't be split and is large, spot-checking a representative ~20-30% deeply beats skimming 100% shallowly

**Precedence for resolving disagreement (Google):** facts/data > style guide > engineering principles > existing-codebase consistency > (only then) reviewer preference — and reviewer preference alone is never sufficient grounds to block.

**Framing feedback (Lynch, Shopify):**
- Request, don't command ("Could we...?" not "Change this")
- Depersonalize: "we"/passive voice, never "you did X wrong"
- Tie every non-trivial objection to a principle, doc, or style guide — not taste
- Mark optional/non-blocking feedback explicitly (Google's "Nit:" convention)
- Cap repeated-pattern comments at 2-3 instances, then ask author to sweep the rest
- Lead with something the author did well before critique

**Sequencing:** architecture/design first, syntax/naming/style last — don't bikeshed naming in the same pass as challenging the approach (Lynch; implicit in Google's design-first checklist ordering).

**Approval bar:** approve once the change is a net improvement to code health, not once it's flawless; block only on things that are actually wrong (bugs, real complexity/maintainability regressions, missing tests), not on "I would have done it differently."

**Author-side prep before requesting review:** self-review the diff, remove debug/dead code, ensure it builds/passes tests/lints clean, write a description that covers *why* + alternatives + risk (not just *what*), keep it single-concern.

---

## 3. Anti-patterns of bad review

- **Rubber-stamp / drive-by LGTM** — approval with no real engagement; empirically linked to *more* post-release defects than low coverage alone, because it looks like quality assurance happened when it didn't ([McIntosh et al.](https://rebels.cs.uwaterloo.ca/papers/emse2016_mcintosh.pdf))
- **Reviewing too large a diff in one pass** — defect-detection rate collapses past ~400 LOC regardless of reviewer skill ([SmartBear/Cisco](https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/))
- **Reviewing too fast** — pace above ~500 LOC/hr independently tanks defect density found, even at moderate size
- **Bikeshedding / nitpicking** — spending review budget on trivial, already-settled-by-style-guide items (Parkinson's Law of Triviality) while missing design or correctness issues
- **Relitigating style-guide-settled questions as if they were open opinion** — wastes author trust and reviewer time on questions with a documented answer
- **Blocking on personal preference** rather than facts/principles/consistency — directly named by Google as the failure mode that disincentivizes future contributions
- **Weeks-long solo work landing as one giant PR** — the single-biggest structural anti-pattern named by Shopify; guarantees either a rubber stamp or a demoralizing wall of feedback delivered too late to act on cheaply
- **Feedback framed as personal ("you")** rather than about the code — measurably increases defensiveness/argument, per Lynch and Shopify's culture writeup
- **No stated intent/description** — reviewers cannot evaluate "does this behave as intended" (Google's #1 checklist item) if intent was never written down
- **Mismatch between what the org rewards review for (bug-catching) and what it actually delivers (maintainability + knowledge transfer)** — leads to reviewers being judged/judging themselves against the wrong yardstick (Bacchelli & Bird's core finding)
- **Single generalist reviewer covering everything** — measurably weaker than either (a) an expert in the relevant area, or (b) multiple reviewers each carrying a distinct perspective (PBR literature, Kononenko et al.)

---

## 4. Implications for designing an AI reviewer panel + orchestrator

**1. Separate reviewer roles should map to genuinely distinct *lenses*, not duplicate generalists.** The PBR literature's core result — diverse perspectives catch more, cheaper, than N copies of the same checklist — is direct justification for a panel over a single "review this diff" call, but only if each persona is scoped to a real, distinct question class (e.g., correctness/logic, maintainability/evolvability, test adequacy, security, architecture/design-fit, API/contract stability) rather than all reading the whole checklist redundantly. Given §1.1's finding that ~most of review's real value is maintainability + knowledge transfer rather than bug-hunting, a panel that is *all* bug-hunters is mis-weighted — at least one persona should be explicitly evaluating readability/evolvability/naming/structure, and it should not be treated as the "junior" reviewer role.

**2. Gate on diff size before deep review runs.** This is the most mechanically transferable, empirically strongest lever in the whole literature (§1.4, corroborated independently by §1.5). An orchestrator should chunk or reject-and-request-split large diffs rather than run the full panel over an undifferentiated 2,000-line change. If a large diff can't be split (e.g., a generated migration), prefer depth-on-a-representative-subset over shallow-pass-on-everything, mirroring the SmartBear spot-check result.

**3. Require a stated intent before review, and check behavior against it — not just against static rules.** Google's #1 checklist dimension ("does it behave as the author likely intended") and the self-review/PR-description literature (§1.8) both require an explicit intent artifact. An orchestrator should treat "no description / no linked issue" as a pre-review gate failure, or should synthesize intent from context (commit messages, linked ticket) before dispatching to reviewers — otherwise reviewers can only check internal consistency, not intent-fit, which is the check most likely to catch what §1.1 calls "real" defects.

**4. Sequence findings, don't just merge them flat.** Lynch's and Google's shared "high-level before low-level" ordering suggests the synthesis/orchestrator stage should present design/architecture-level findings *before* style/naming findings, and should be willing to suppress or defer low-level comments entirely if a high-level finding suggests the diff's whole direction needs to change (avoiding the classic "wasted effort" failure Google's small-CL doc names explicitly).

**5. Weight and phrase findings by what predicts author action, not just by severity.** §1.1's resolution-rate data (bug and readability comments get fixed more often than design comments) suggests design-level findings need either stronger justification (cite a principle/consistency argument, per Google's precedence order) or a different delivery mechanism (a question, not a directive) to actually land — an orchestrator's confidence-gating and phrasing shouldn't be uniform across finding categories.

**6. Treat "engagement depth," not "did a reviewer run," as the quality signal.** McIntosh's participation finding (§1.2) argues against a single fast pass with a binary pass/fail. An AI panel's internal quality bar should look more like "did each reviewer produce specific, groundable findings tied to actual lines/behavior" than "did the pipeline complete" — closer to an adversarial-verify step than a rubber stamp.

**7. Dedicate one role to complexity/over-engineering, explicitly.** Google treats speculative generality as a first-class review defect on par with bugs — most naive AI-reviewer designs skew toward "what's wrong" (bugs, missing tests) and under-weight "what's unnecessarily complex here," which the literature says is just as much what good reviewers are for.

**8. Cap repeated-pattern noise.** Both Lynch and Google independently converge on "flag a repeated issue 2-3 times, then ask for a sweep" rather than N nearly-identical comments — directly actionable as a dedup rule in a findings-merge/synthesis stage, and important for LLM reviewers specifically since they're prone to exhaustively re-flagging every instance of a pattern rather than summarizing it.

**9. Unverified/uncertain areas to flag rather than assert:** the exact "75% maintainability / <15-25% bugs" comment-classification ratio is directionally well-supported but I could not pin to one clean primary citation in this pass; and none of the size/pace/detection-rate numbers in §1.4 have been re-validated for LLM reviewers reading diffs rather than humans reading printouts — it is a reasonable working hypothesis that similar size effects apply, but that transfer is not itself empirically established and should be labeled as an assumption if used to justify hard limits in a system design.

---

## Source list

- Bacchelli & Bird, *Expectations, Outcomes, and Challenges of Modern Code Review* (ICSE 2013): https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf
- McIntosh, Kamei, Adams, Hassan, *An Empirical Study of the Impact of Modern Code Review Practices on Software Quality*: https://rebels.cs.uwaterloo.ca/papers/emse2016_mcintosh.pdf
- Sadowski et al., *Modern Code Review: A Case Study at Google* (ICSE-SEIP 2018): https://sback.it/publications/icse2018seip.pdf
- SmartBear, *Best Practices for Peer Code Review* (Cisco Systems study): https://smartbear.com/learn/code-review/best-practices-for-peer-code-review/
- Google, *The Standard of Code Review*: https://google.github.io/eng-practices/review/reviewer/standard.html
- Google, *What to Look For in a Code Review*: https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Google, *Small CLs*: https://google.github.io/eng-practices/review/developer/small-cls.html
- Google, *Speed of Code Reviews*: https://google.github.io/eng-practices/review/reviewer/speed.html
- Kononenko et al., *Code Review Quality: How Developers See It* (ICSE 2016): https://plg.uwaterloo.ca/~migod/papers/2016/icse16.pdf
- *What Types of Code Review Comments Do Developers Most Frequently Resolve?* (arXiv 2510.05450): https://arxiv.org/abs/2510.05450
- The New Stack, *The code review bug hunt is dead*: https://thenewstack.io/code-review-catches-maintainability-bugs/
- Michael Lynch, *How to Do Code Reviews Like a Human*, Part 1: https://mtlynch.io/human-code-reviews-1/ ; Part 2: https://mtlynch.io/human-code-reviews-2/
- Shopify Engineering, *Great Code Reviews — The Superpower Your Team Needs*: https://shopify.engineering/great-code-reviews
- Shopify Engineering, *When Culture and Code Reviews Collide, Communication is Key*: https://shopify.engineering/code-reviews-communication
- Chelsea Troy, *Reviewing Pull Requests*: https://chelseatroy.com/2019/12/18/reviewing-pull-requests/
- Perspective-Based Reading: *How Perspective-Based Reading Can Improve Requirements Inspections*: https://www.researchgate.net/publication/2955334_How_Perspective-Based_Reading_Can_Improve_Requirements_Inspections
- Fagan Inspection overview: https://vfast.org/journals/index.php/VTSE/article/download/920/862/2727
- Gergely Orosz, *Good Code Reviews, Better Code Reviews*, The Pragmatic Engineer: https://blog.pragmaticengineer.com/good-code-reviews-better-code-reviews/
