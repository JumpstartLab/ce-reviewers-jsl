# Performance Vulnerabilities in Code Review

## 1. Key Findings

### 1.1 The premature-optimization tension, resolved properly

Knuth's actual line (1974, "Structured Programming with Go To Statements," ACM Computing Surveys) is almost always quoted with the setup clause stripped off:

> "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil. Yet we should not pass up our opportunities in that critical 3%."

The full paragraph is not an argument against caring about performance — it's an argument against *guessing* which 3% matters. Knuth's real complaint was that programmers make "a priori judgments about what parts of a program are really critical" without measuring, and that a 12% improvement in a hot path "is never something to be sniffed at." His prescription was tooling: compilers/profilers should tell you where time actually goes so optimization is *informed*, not psychic. ([hlopko.com](https://hlopko.com/2019/08/03/premature-optimization/), [probablydance.com revisit](https://probablydance.com/2025/06/19/revisiting-knuths-premature-optimization-paper/), [Ubiquity/ACM](https://ubiquity.acm.org/article.cfm?id=1513451))

The practical takeaway for review: "premature optimization" is a legitimate objection to a reviewer who nitpicks micro-efficiency in cold, rarely-run code at the cost of clarity. It is **not** a legitimate excuse to wave off O(n²) behavior in a hot path, an unindexed query on a growing table, or an N+1 that fires on every page load — those are not "small efficiencies," they're architectural choices with compounding cost, exactly the "critical 3%" Knuth carved out.

Jeff Atwood's "[Performance is a Feature](https://blog.codinghorror.com/performance-is-a-feature/)" and the Etsy framing (Mike Brittain: performance "must be continuously monitored and tested" like any other feature) push the opposite failure mode: performance work is often deprioritized until it becomes a crisis, precisely because no user files a ticket for "was 200ms slower than necessary."

### 1.2 Casey Muratori: performance excuses are usually post-hoc rationalization

Muratori's "[Performance Excuses Debunked](https://www.computerenhance.com/p/performance-excuses-debunked)" catalogs five excuses developers give to avoid performance work — "no need" (hardware/compilers are fast enough), "too small" (gains are marginal), "not worth it" (ROI doesn't justify it), "niche" (only games/embedded care), "hotspot" (only a few spots need fixing, don't worry about the rest). He debunks each with the same evidence class: major companies (Facebook, Twitter, Uber) repeatedly did *ground-up rewrites* specifically for performance — Messenger's "LightSpeed" rewrite (75% footprint reduction), facebook.com's full rewrite, React Fiber, Twitter search rewrites, Uber moving services from Python to Go. His argument: if hotspot-only fixes or "good enough" architecture were actually sufficient, these rewrites wouldn't have been necessary. The pattern he's pointing at for reviewers: architectural performance debt doesn't show up as a fixable hotspot later — it shows up as "we have to rewrite this system."

Muratori's companion argument (from his "Clean Code, Horrible Performance" material, [SE Radio 577](https://se-radio.net/2023/08/se-radio-577-casey-muratori-on-clean-code-horrible-performance/)) is that certain widely-taught "clean code" practices (heavy indirection, one-class-per-concept, polymorphism-by-default) impose real, measurable performance costs that are rarely weighed against their readability benefit in review — i.e., review culture optimizes for one axis (apparent cleanliness) while silently accepting cost on another (cache locality, call overhead) without ever measuring either.

**Where the tension resolves for review practice:** the two camps agree more than they seem to. Knuth says measure before optimizing *code that's already written*; Muratori says architectural/data-flow decisions that determine what's *possible* to fix later must be made with performance in mind *before* they calcify into a rewrite-required system. Review's job is to catch the second category (irreversible-without-a-rewrite architectural choices) even without a profiler, while treating micro-level "make this loop 5% faster" requests with Knuth's skepticism absent measurement.

### 1.3 Statically-reviewable anti-patterns (the "read the diff and know" category)

These are the patterns experienced reviewers catch from the code shape alone, without running a profiler:

- **N+1 queries.** The single most common, most costly, most reviewable performance bug in ORM-backed apps. Root cause: ORM lazy-loading is a leaky abstraction — one query fetches a list, then N queries fetch each item's associations inside a loop. Same shape in Rails/ActiveRecord, Django, and Hibernate/JPA. Fix is eager loading (`includes`/`preload`/`eager_load` in Rails, `select_related`/`prefetch_related` in Django, `JOIN FETCH`/`@BatchSize` in JPA). Detectable in review purely from the diff: any `association.method` call sited inside a loop over a collection that came from a query is suspect. Tooling backstop: Bullet (Rails), Django Debug Toolbar, Hibernate statistics — these catch what static reading misses, and can gate CI. ([Scout APM guide](https://www.scoutapm.com/blog/rails-n1-queries-guide), [Doctolib engineering](https://medium.com/doctolib/how-to-find-fix-and-prevent-n-1-queries-on-rails-6b30d9cfbbaf), [Digma N+1 explainer](https://digma.ai/n1-query-problem-and-how-to-detect-it/), [CodeWiz JPA anti-patterns](https://codewiz.info/blog/jpa-performance-anti-patterns/))

- **Unbounded queries / missing pagination.** A query with no `LIMIT`/`TOP`/cursor bound, often combined with app-side filtering after the full result set is already pulled. Grep-able signals: `.all()`, `fetchall()`, `findAll()`, `Model.where(...)` with no `.limit`/`.page` downstream, an API endpoint that returns a collection with no pagination params. This is exactly the class of bug that **passes all tests in dev/staging** (small dataset) and only surfaces in production once a table crosses some row-count threshold — it produces correct output at low N, so it survives code review by inspection unless the reviewer explicitly asks "what happens when this table has 10M rows," and survives testing because CI fixtures are small. It also doubles as a security/DoS issue: an unbounded endpoint is a one-request amplification attack. ([dev.to writeup](https://dev.to/sanmish4/unbounded-data-fetching-a-silent-performance-anti-pattern-in-api-and-database-layers-1dnk), [Azure Architecture Center: Extraneous Fetching antipattern](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/extraneous-fetching/))

- **Missing indexes for new query patterns.** A new `WHERE`/`JOIN`/`ORDER BY` clause added in a PR against a column with no supporting index is invisible in a diff unless the reviewer cross-references the schema. This is the strongest case for "ask for the query plan" as a review artifact rather than trying to eyeball it — `EXPLAIN (ANALYZE, BUFFERS)` showing `Seq Scan` with a high row count and a small fraction of rows actually matching (e.g., 955,000 of 1M rows filtered out) is the smoking gun. Caveat reviewers should hold: sequential scans are *correct* on small tables and on queries returning >~60% of rows — flagging every Seq Scan is a false-positive generator. ([Crunchy Data on scan types](https://www.crunchydata.com/blog/postgres-scan-types-in-explain-plans), [Percona on seq scans](https://www.percona.com/blog/decoding-sequential-scans-in-postgresql/))

- **O(n²) in loops over collections.** Nested iteration over the same or related collections, especially with an `.include?`/`.find`/linear search inside an outer loop turning "amortized O(n)" into O(n·m). Statically visible when both loop bounds trace back to unbounded, user-controlled, or growing data (user records, uploaded rows) rather than a small fixed-size config list.

- **Chatty I/O in loops.** Any network/API/DB call made per-iteration instead of batched — the distributed-systems sibling of N+1. Same detection heuristic: an I/O-shaped call (HTTP client, DB call, queue publish) sited textually inside a `for`/`each` whose bound is data-derived.

- **Synchronous work in hot/request paths.** Blocking calls (file I/O, external API calls, heavy computation, synchronous email/webhook dispatch) inside a request-response cycle that should be queued/backgrounded. Reviewable by asking "does this line block the response, and can its input size or latency vary unboundedly?"

- **Unbounded memory growth / caching without eviction.** In-process caches, memoization, or accumulator collections with no size cap or TTL — reviewable by checking whether a cache/`Hash`/`Dict`/list that's appended to has any bound at all, and whether its key space is attacker- or user-controlled (unbounded key space + no eviction = guaranteed OOM given enough time or requests).

- **Connection/thread pool exhaustion.** Missing `finally`/`ensure`/`with` blocks around connection acquisition (leak on exception path), long-held connections spanning slow external calls, and missing timeouts on connection acquisition. Connection pool exhaustion is especially dangerous because it's invisible until it cascades — the DB may have spare CPU/memory while the app looks fully "down" because every thread is blocked waiting on a saturated pool. Review checklist: does every code path that acquires a connection/lock release it on the exception path; are there timeouts on acquisition and on the query itself (fail fast rather than block indefinitely); are queues bounded rather than allowed to grow without limit. ([oneuptime.com](https://oneuptime.com/blog/post/2026-01-24-thread-pool-exhausted-errors/view), [Microsoft Learn: ThreadPool starvation](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/debug-threadpool-starvation))

### 1.4 Empirical research on performance bugs

The literature on performance bugs (distinct from correctness bugs) consistently finds:

- Performance bugs are defined in the research literature as "defects where relatively simple source code changes can significantly speed up software, while preserving functionality" — i.e., most real perf bugs are *not* subtle algorithmic redesigns, they're missing eager-loads, missing indexes, and misused APIs, the same catalog above. ("Understanding and Detecting Real-World Performance Bugs," [ResearchGate](https://www.researchgate.net/publication/238049144_Understanding_and_Detecting_Real-World_Performance_Bugs))
- They are harder to discover than functional bugs because they have **no fail-stop symptom** — the program returns the right answer, just slowly, so nothing crashes or trips an assertion, and it takes production-scale load or production-scale data to manifest at all.
- They take measurably longer to find and fix than functional defects in the same codebases, consistent with the "invisible until it costs real money" pattern architects describe. ("A qualitative study on performance bugs," [ResearchGate](https://www.researchgate.net/publication/254040765_A_qualitative_study_on_performance_bugs))

This is the strongest argument for treating performance as a **review-time concern rather than a purely post-hoc profiling concern**: the failure mode of "ship it, profile it later" is that perf bugs specifically evade the signal (crashes, wrong output) that would normally prompt someone to go look.

### 1.5 Performance regression testing in CI

Mature ecosystems don't rely on review judgment alone for the "critical 3%" — they gate on measured benchmarks in CI:

- Continuous-benchmarking services (e.g., Bencher) run the same benchmark suite on every PR on consistent hardware and fail the build on regression; one example cited threshold: a "serious regression" defined as ≥30% increase in a benchmark's minimum execution time, historically catching "dozens of serious performance regressions" since being introduced. ([bencher.dev](https://bencher.dev/learn/engineering/sqlite-performance-tuning/))
- This is the honest resolution of the Knuth/Muratori tension at the tooling level: don't ask a human reviewer to eyeball whether a diff is "fast enough" — run the actual benchmark and let the number decide. Review's job then narrows to: is there a benchmark covering this hot path at all, and does the PR touch code with no regression-test coverage.

### 1.6 Migration and index-creation lock safety

Database migrations are the highest-blast-radius category of performance review because a "fast" migration can still cause a full outage through lock queueing, not lock duration:

- In Postgres, DDL like `ALTER TABLE ADD COLUMN` (without a default, pre-11) or index creation via plain `CREATE INDEX` takes an `ACCESS EXCLUSIVE` lock. The danger isn't that this blocks other writers for the duration of the DDL — it's that **every other statement needing any lock on that table queues behind the waiting DDL**, including plain `SELECT`s that only need `ACCESS SHARE`. A DDL statement that itself waits behind one long-running transaction can back up the entire table's traffic behind it. ([Xata: migrations and exclusive locks](https://xata.io/blog/migrations-and-exclusive-locks))
- Review checklist for migrations: (a) is `CREATE INDEX CONCURRENTLY` used instead of plain `CREATE INDEX`; (b) is `lock_timeout` set to a small value (sub-2s) so a blocked DDL fails fast and retries instead of queueing the whole table; (c) for Postgres 11+, does `ADD COLUMN ... DEFAULT` avoid a table rewrite (true since PG11) — MySQL and older Postgres don't get this for free; (d) for genuinely large tables, is a tool like `pt-online-schema-change`/`gh-ost` (MySQL) or a ghost-table strategy used instead of a direct blocking `ALTER`; (e) does the reviewer have the target table's actual row count/size, since "a 10K-row ALTER on an internal table reads differently from a 200M-row ALTER on invoices" and that context is exactly what's missing from a bare diff. ([Bytebase: ALTER large MySQL tables](https://www.bytebase.com/reference/mysql/how-to/how-to-alter-large-table-mysql/), [oneuptime.com migration strategies](https://oneuptime.com/blog/post/2026-02-20-database-migration-strategies/view))

### 1.7 Scalability review: idempotency, retry storms, cache stampedes, hot keys

- **Cache stampede / thundering herd.** When a hot cache entry expires, every one of the (possibly thousands of) concurrent requests misses simultaneously and hits the origin/DB at once. Two standard review-worthy mitigations: lock-based (single request repopulates, others wait/retry from cache) and probabilistic early refresh (XFetch — refresh probability rises as expiry approaches, spreading recomputation over time instead of concentrating it at the exact expiry instant). Reviewable signal: any cache-aside pattern (`get-or-compute-and-set`) with no locking/single-flight around the "compute" branch is a stampede risk if the value is expensive and the key is hot. ([bs-code.dev](https://bs-code.dev/posts/the-thundering-herd-problem), [web-alert.io](https://web-alert.io/blog/cache-stampede-thundering-herd-prevention-guide/))
- **Retry storms.** A second-order failure where clients retrying on timeout amplify load on an already-struggling dependency. Review checklist: does every retry use exponential backoff *with jitter* (not fixed-interval retry, which synchronizes retries into new stampedes); is there a retry budget/circuit breaker rather than unbounded retry.
- **Idempotency.** Any retried operation (payment, webhook handler, queue consumer, "at-least-once" delivery target) needs a stable idempotency key representing user intent (not the transport attempt) and durable dedup storage so replays are safe. Stripe's public framing: consistent retries + safe (idempotent) retries + responsible retries (backoff+jitter) as the three properties to check for. Concrete implementation detail wasn't published by Stripe's blog itself, but the pattern (key → stored first-result → replay on duplicate key) is the industry-standard shape reviewers should look for. ([Stripe: designing robust idempotent APIs](https://stripe.com/blog/idempotency), [AlgoMaster idempotency overview](https://blog.algomaster.io/p/idempotency-in-distributed-systems))
- **Hot keys / partition skew.** Hash-based sharding balances aggregate storage but not access *frequency* — a single viral key still routes to one node/partition regardless of cluster size, and no amount of adding shards fixes it. Review-relevant mitigations to look for when a new access pattern targets a single, potentially-viral key: key salting/splitting, replication of hot keys across nodes, or an application-level cache in front of the partition. ([systemdr.systemdrd.com](https://systemdr.systemdrd.com/p/handling-hot-keys-in-distributed), [systemoverflow.com](https://www.systemoverflow.com/learn/design-fundamentals/scalability-fundamentals/hotspots-and-skew-when-one-shard-takes-all-the-heat))
- **Queue backpressure.** Symmetric to connection-pool exhaustion: an unbounded queue in front of a slower consumer just moves the OOM downstream instead of preventing it. Review signal: is there a bound (size cap, backpressure signal, load shedding) on any queue/buffer whose producer can outrun its consumer.

### 1.8 Big-O review judgment and calibration numbers

Jeff Dean's (via Peter Norvig's earlier table) "[Numbers Every Programmer Should Know](https://brenocon.com/dean_perf.html)" — L1 cache ~0.5ns, main memory ~100ns, SSD random read ~150µs, same-datacenter round trip ~500µs, disk seek ~10ms — remains the standard calibration set for "is this loop/call actually expensive." Its review value isn't the exact numbers (they drift with hardware) but the *relative ratios*: memory access is ~200x an L1 hit, a network round trip is ~10,000x a memory access, and a disk seek is ~100,000x a memory access. This is why "N+1 queries" and "chatty I/O in loops" dominate the cost-ranked list below — the anti-pattern isn't O(n²) arithmetic (cheap per-operation, so n has to be huge to matter) but O(n) *network/disk round trips* (expensive per-operation by 4-5 orders of magnitude, so even small n hurts). A reviewer who internalizes this ordering knows to weight "one query in a loop" far higher than "one extra array scan in a loop" even though both are technically "O(n) inside O(n)."

The corollary for review practice: **Big-O without a stated data-size assumption is close to meaningless.** O(n²) over a 20-item config array is fine forever; O(n²) over a user-uploaded CSV is a future incident. Good review comments on complexity name the assumption explicitly ("this is O(n²) — is `items` bounded, or can a user grow it unboundedly?") rather than asserting a verdict, because the reviewer reading a diff usually cannot see the runtime data-size distribution and the author usually can.

### 1.9 What profilers/APM catch that review cannot, and vice versa

Static review (reading the diff) can reliably catch *shape*-level problems: N+1 patterns, missing pagination, missing index for an obviously new query pattern, unbounded caches/queues, missing backoff/jitter, lock-unsafe migrations, connection leaks on exception paths. It cannot reliably catch: actual hot-path identification (which of five plausible O(n) operations is the one that matters — needs a profiler), real production data-shape/skew (needs APM/production metrics), lock contention and GC pause behavior under real concurrency (needs a profiler/continuous profiling tool), and whether a "regression" is real versus noise (needs a benchmark, not a read). ([Datadog Continuous Profiler](https://www.datadoghq.com/blog/datadog-continuous-profiler/), general profiling-vs-static-analysis framing via [CodeScene](https://codescene.com/blog/what-is-a-static-code-analysis))

The practical division of labor: review's job is to prevent the introduction of *shape*-level anti-patterns whose cost scales with data/time regardless of current measurements, and to demand a benchmark/profiling artifact exists for genuinely hot paths; a profiler's job is to find out which of the "shape is fine but might still be slow" code is actually worth spending effort on.

---

## 2. Concrete Review Heuristics / Checklist (by layer)

### Algorithm / in-process
- [ ] Any nested loop over the same or related collection — is either bound provably small/fixed, or does it scale with user/data growth?
- [ ] Any linear search (`.find`, `.include?`, `indexOf`) inside a loop — should this be a Set/Hash/index lookup instead?
- [ ] Does the PR state (in description or comment) the expected size/cardinality of the data this code operates over? If not, ask.
- [ ] Is complexity growth tied to something bounded by product design (page size, config list) or to something that grows without bound (all users, all rows, all events)?

### Database
- [ ] Any association/relation access inside a loop over a query result → N+1 candidate. Ask: does this need `.includes`/`select_related`/`JOIN FETCH`?
- [ ] Any new `WHERE`/`JOIN`/`ORDER BY` on a column — is there a supporting index? Ask for `EXPLAIN (ANALYZE, BUFFERS)` on the actual table size if uncertain.
- [ ] Any query returning a collection with no `LIMIT`/pagination — bounded by design, or a future incident waiting for the table to grow?
- [ ] Any DDL (`ALTER TABLE`, `CREATE INDEX`) — does it use `CONCURRENTLY`/online-schema-change tooling on large tables, and is `lock_timeout` set so a blocked DDL fails fast instead of queueing all traffic behind it?
- [ ] Does the migration state (or can the reviewer look up) the target table's row count? A "trivial" migration on a 200M-row table is not trivial.
- [ ] Is a raw SQL string being built inside a loop (batch-inserts done one row at a time instead of bulk)?

### I/O / network
- [ ] Any HTTP/RPC/queue-publish call sited inside a loop whose bound is data-derived — batchable?
- [ ] Does every external call have a timeout? Does the caller distinguish "fail fast" from "block forever"?
- [ ] Is retry logic present for calls that can transiently fail, and does it use exponential backoff + jitter (not fixed-interval)?
- [ ] For anything retried, is the operation idempotent — stable key representing intent, dedup storage, safe replay?
- [ ] For a hot/popular cache key or endpoint, is there single-flight/locking or probabilistic early refresh to prevent stampede on expiry?

### Memory
- [ ] Any in-process cache, memoization table, or accumulator — does it have a size cap or TTL? Is its key space bounded, or can a user/attacker grow it unboundedly?
- [ ] Any large intermediate collection built in memory (`.to_a`, `.map` over a full table) that could instead be streamed/batched?
- [ ] Any queue/buffer with no backpressure or max size in front of a slower consumer?

### Concurrency / resource pools
- [ ] Every connection/lock acquisition — is release guaranteed on the exception path (`finally`/`ensure`/`with`/`using`)?
- [ ] Is there a timeout on connection/lock acquisition itself (not just on the work done once acquired)?
- [ ] Long-held connections spanning a slow external call — can the connection be released before the slow part runs?
- [ ] Sync work (file I/O, heavy compute, external calls) inside a request-response hot path — should this be backgrounded/queued?

---

## 3. Anti-Patterns Ranked by Real-World Frequency / Cost

Ranking synthesizes: how often the pattern actually appears in review discussions/postmortems, how cheap it is to introduce accidentally, and how disproportionate its cost is relative to how it looks in a diff (per the latency-ratio argument in §1.8).

1. **N+1 queries.** Most frequently cited ORM performance bug across every framework community searched (Rails, Django, Hibernate/JPA); trivially easy to introduce (one line inside a loop), invisible in small dev datasets, multiplies request latency directly by row count.
2. **Unbounded queries / missing pagination.** Passes all tests at small N by construction; becomes a production incident purely as a function of data growth, with zero code change required to trigger it — arguably the most "silent" of all the patterns here, and doubles as a DoS vector.
3. **Missing index for a new query pattern.** Extremely common because it requires cross-referencing the schema, which a diff-only review doesn't surface; degrades gracefully at small N then falls off a cliff.
4. **Migration-induced lock queueing.** Lower frequency but catastrophic blast radius (can take an entire table offline app-wide even though the DDL itself "looks fast"); the gap between what the diff shows and what actually happens in production is largest here.
5. **Chatty I/O in loops (non-DB).** Same shape as N+1 but for external APIs/queues; common in integration-heavy codebases, cost dominated by network RTT (§1.8's 10,000x multiplier).
6. **Cache stampede / thundering herd on expiry.** Lower frequency (requires a genuinely hot key) but produces dramatic, correlated failure spikes exactly at cache-expiry boundaries — classic "why did everything die at the same second" postmortem shape.
7. **Retry storms without backoff/jitter.** Compounds an existing incident into an outage; frequently the actual root cause of "the retry logic we added to be safe took the service down."
8. **Connection/thread pool exhaustion from leaked connections.** Insidious because the DB/dependency looks healthy while the app looks fully down; usually traced to a missing `finally`/`ensure` on one exception path.
9. **Unbounded in-process caches/memory growth.** Slow-burn (OOM after hours/days), often missed in review because the cache "working" in the PR's manual test gives no signal about its eventual size.
10. **O(n²) algorithmic complexity in application code.** Real, but lower real-world frequency than the I/O-bound patterns above because pure in-process CPU work rarely reaches the row counts needed to matter before a network/DB call in the same request already dominates latency (again, §1.8's ratio argument).
11. **Hot-key/partition skew.** Lowest frequency of this list (requires a specific access-pattern shape — viral content, celebrity user, singleton config key) but effectively unfixable by scaling out, making it a "we now need a redesign" class bug when it does hit.

---

## 4. Implications for an AI Performance Reviewer Persona

**Reliably detectable from a diff alone (high-confidence, assert as findings):**
- Association/relation access textually inside a loop over a query result (N+1 shape) — this is a syntactic pattern, not a judgment call.
- Collection-returning query/endpoint with no `LIMIT`/pagination construct anywhere in the call chain shown in the diff.
- DDL (`ALTER TABLE`, `CREATE INDEX`) not using `CONCURRENTLY`/online-schema tooling, or no visible `lock_timeout`.
- Connection/lock acquisition with no corresponding `finally`/`ensure`/`with` on the same code path.
- Retry loop with fixed-interval sleep and no jitter term.
- Cache/memoization structure with no visible eviction, TTL, or size bound, keyed on unbounded input (user ID space, arbitrary string).
- External/API/queue call inside a loop bound by a data-derived collection.

**Requires data-size/production context the diff doesn't contain (phrase as a question, not a verdict):**
- Any O(n²) or worse complexity — the finding should be "this is O(n²) in `X` — what's the expected/max size of `X` in production?" not "this is slow." The reviewer usually cannot see the runtime cardinality; the author usually can.
- Missing-index calls — "this filters on `column` with no visible index; what's the row count on `table`, and can you paste an `EXPLAIN`?" rather than asserting the query is slow, since small tables and low-selectivity queries correctly use sequential scans.
- Migration lock risk — ask for the target table's row count before asserting the migration is dangerous; a 10K-row ALTER and a 200M-row ALTER are different bugs entirely, and the diff alone can't distinguish them.
- Hot-key risk — depends on whether the targeted key is realistically viral/skewed, which is a product judgment, not a code judgment.

**Not reviewable from a diff at all (defer to profiler/APM/benchmark, and say so explicitly rather than guessing):**
- Whether a given O(n) operation is *the* bottleneck versus one of several plausible candidates — needs a profiler.
- Actual latency/throughput impact of a change — needs a benchmark (regression-tested in CI where one exists) or production measurement.
- Lock contention, GC pause behavior, real concurrency effects — needs continuous profiling under real load.
- Whether an "acceptable-looking" cache stampede mitigation actually holds under real traffic skew — needs load testing.

**False-positive control — practical phrasing rules:**
1. Never assert "this is slow" without either (a) a syntactic pattern from the high-confidence list above, or (b) an explicit request for the missing data-size context. Assertions without one of these two anchors are exactly the "premature optimization" noise Knuth's quote is deployed against, and they train authors to ignore the reviewer.
2. When flagging Big-O, state the assumption being made about input size and invite correction — this converts an unfalsifiable style complaint into a checkable claim the author can either confirm ("yes, unbounded, good catch") or dismiss with actual information ("this list is capped at 20 by the UI").
3. Distinguish "this pattern is *always* wrong" (missing `finally` around a connection, no jitter on retry) from "this pattern is *sometimes* wrong depending on scale" (Seq Scan, O(n²), unindexed filter) in the finding's own wording — collapsing these two categories into one confidence level is the single biggest source of reviewer-credibility loss on performance comments specifically, because the second category is right often enough to seem authoritative and wrong often enough to erode trust when it isn't.
4. Cite the ratio, not just the pattern, when justifying severity: "a DB call in this loop costs ~10,000x a memory access at this row count" is a falsifiable, teachable claim; "this could be optimized" is not.
5. When no regression benchmark exists for a path the diff calls "hot," the correct finding is "no benchmark covers this path" (a testing-infrastructure gap) rather than a guess at the actual regression — this keeps the reviewer inside what's actually verifiable from the diff plus repo state, per Google's own review guidance that reviewers should focus on verifiable code-health impact rather than speculative future-proofing ([google.github.io/eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)).

---

## Sources

- [Premature Optimization — hlopko.com](https://hlopko.com/2019/08/03/premature-optimization/)
- [Revisiting Knuth's "Premature Optimization" Paper — probablydance.com](https://probablydance.com/2025/06/19/revisiting-knuths-premature-optimization-paper/)
- [Ubiquity: The Fallacy of Premature Optimization — ACM](https://ubiquity.acm.org/article.cfm?id=1513451)
- [Performance Excuses Debunked — Casey Muratori, computerenhance.com](https://www.computerenhance.com/p/performance-excuses-debunked)
- [SE Radio 577: Casey Muratori on Clean Code, Horrible Performance?](https://se-radio.net/2023/08/se-radio-577-casey-muratori-on-clean-code-horrible-performance/)
- [Performance is a Feature — Jeff Atwood, Coding Horror](https://blog.codinghorror.com/performance-is-a-feature/)
- [N+1 Queries in Rails: Detection and Prevention — Scout APM](https://www.scoutapm.com/blog/rails-n1-queries-guide)
- [How To Find, Fix, and Prevent N+1 Queries on Rails — Doctolib Engineering](https://medium.com/doctolib/how-to-find-fix-and-prevent-n-1-queries-on-rails-6b30d9cfbbaf)
- [What is the N+1 query problem and how to detect it? — Digma](https://digma.ai/n1-query-problem-and-how-to-detect-it/)
- [11 JPA Performance Killers — CodeWiz](https://codewiz.info/blog/jpa-performance-anti-patterns/)
- [Unbounded Data Fetching: A Silent Performance Anti-Pattern — dev.to](https://dev.to/sanmish4/unbounded-data-fetching-a-silent-performance-anti-pattern-in-api-and-database-layers-1dnk)
- [Extraneous Fetching antipattern — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/antipatterns/extraneous-fetching/)
- [How to Read Postgres EXPLAIN: A Guide to Scan Types — Crunchy Data](https://www.crunchydata.com/blog/postgres-scan-types-in-explain-plans)
- [Decoding Sequential Scans in PostgreSQL — Percona](https://www.percona.com/blog/decoding-sequential-scans-in-postgresql/)
- [Schema changes and the Postgres lock queue — Xata](https://xata.io/blog/migrations-and-exclusive-locks)
- [How to ALTER large table in MySQL — Bytebase](https://www.bytebase.com/reference/mysql/how-to/how-to-alter-large-table-mysql/)
- [How to Plan and Execute Database Migrations Safely — oneuptime.com](https://oneuptime.com/blog/post/2026-02-20-database-migration-strategies/view)
- [Cache Stampede: The Thundering Herd Problem — bs-code.dev](https://bs-code.dev/posts/the-thundering-herd-problem)
- [Cache Stampede and Thundering Herd: Prevention Guide — web-alert.io](https://web-alert.io/blog/cache-stampede-thundering-herd-prevention-guide)
- [Designing robust and predictable APIs with idempotency — Stripe](https://stripe.com/blog/idempotency)
- [What is Idempotency in Distributed Systems? — AlgoMaster](https://blog.algomaster.io/p/idempotency-in-distributed-systems)
- [Handling "Hot Keys" in Distributed Databases — systemdrd.com](https://systemdr.systemdrd.com/p/handling-hot-keys-in-distributed)
- [Hotspots and Skew: When One Shard Takes All the Heat — systemoverflow.com](https://www.systemoverflow.com/learn/design-fundamentals/scalability-fundamentals/hotspots-and-skew-when-one-shard-takes-all-the-heat)
- [Connection Pool Exhaustion: The Silent Killer — howtech.substack.com](https://howtech.substack.com/p/connection-pool-exhaustion-the-silent)
- [Debug ThreadPool Starvation — Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/core/diagnostics/debug-threadpool-starvation)
- [Understanding and Detecting Real-World Performance Bugs — ResearchGate](https://www.researchgate.net/publication/238049144_Understanding_and_Detecting_Real-World_Performance_Bugs)
- [A qualitative study on performance bugs — ResearchGate](https://www.researchgate.net/publication/254040765_A_qualitative_study_on_performance_bugs)
- [Why SQLite Performance Tuning made Bencher 1200x Faster — Bencher](https://bencher.dev/learn/engineering/sqlite-performance-tuning/)
- [Latency Numbers Every Programmer Should Know / "Numbers Everyone Should Know" — Jeff Dean via brenocon.com](https://brenocon.com/dean_perf.html)
- [What to look for in a code review — Google eng-practices](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [Characteristics of Useful Code Reviews: An Empirical Study at Microsoft — ResearchGate](https://www.researchgate.net/publication/308735251_Characteristics_of_Useful_Code_Reviews_An_Empirical_Study_at_Microsoft)
- [Analyze code performance in production with Datadog Continuous Profiler](https://www.datadoghq.com/blog/datadog-continuous-profiler/)

Notes on unverifiable/dropped claims: the Microsoft "20-30% fewer defects reaching production" figure and the specific claim that Google research found code review "more effective than testing/static analysis/formal verification when measured in isolation" surfaced only in secondary-source search summaries without a traceable primary citation — included above only as general code-review-effectiveness context, not relied on for any performance-specific claim, and should be treated as unverified if reused elsewhere. Stripe's blog post does not actually document key-storage/TTL/locking implementation details despite being the most commonly cited "idempotency" reference — flagged explicitly in §1.7 rather than invented.
