# Jumpstart Lab — CE Reviewers, Orchestrators & User Personas

Custom reviewer personas, orchestrator definitions, and user personas for the [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) Claude Code plugin.

## Reviewers

### Plan Reviewers

| Reviewer | Focus |
|----------|-------|
| Avi (Rails) | Modern Rails ecosystem, what's-next thinking |
| Charles Eames | Constraints, problem definition, systems design |
| Greg (AI) | AI pragmatism, catches LLM hype and prompt injection risks |
| Jason Fried | Scope reduction, sustainability, cuts bloat |
| Marty Cagan | Product discovery, challenges unvalidated assumptions |
| Melissa Perri | Build-trap detection, outcome vs. output focus |
| Sandy Speicher | Human-centered design, surfaces missing stakeholders |
| Steve (Frontend) | Frontend performance, simplicity, Hotwire/Stimulus |

### Code Reviewers

| Reviewer | Focus |
|----------|-------|
| Sandi Metz | OO design — SRP, dependency injection, duck typing |
| Corey (Testing) | Test strategy, hourglass testing, acceptance tests |
| Test Pruner | Redundant, fragile, and implementation-coupled test detection |
| Jim Weirich (Git) | Git hygiene, commits as storytelling |
| Abby (Synthesis) | Cross-reviewer synthesis PM, prioritizes findings |

### Writing Reviewers

The seven-voice panel for prose, run by the **Perkins** orchestrator. Each owns one dimension of Jeff's voice and cites the [voice guide](voice/voice-guide.md) by section. Dispatched by the `ce:prose-review` skill (selected via `category: writing`).

| Reviewer | Lens | Owns (voice guide) |
|----------|------|--------------------|
| Stephen King | Voice & tone — does it sound like Jeff? | §1–3, §5 reach-for |
| Gary Provost | Rhythm & cadence — the read-aloud test | §4 |
| George Orwell | Concision & AI-slop — cut filler, kill machine tells | §2.2, §5 kill-list, §10 |
| Barbara Minto | Structure & flow — answer-first, one idea per section | §6, §2.1 |
| Jakob Nielsen | Formatting — scannability, the "looks" | §7 |
| Ann Handley | Audience — will it land with the reader? | §9, §1 |
| Bryan Garner | Vocabulary — the right term of art | §9, §5 precision |

## Orchestrators

Orchestrators define *how* to run a project — which phases to execute, which reviewers to prioritize, when to skip steps, and how to synthesize findings.

| Orchestrator | Archetype | Style |
|---|---|---|
| **Edith** | The Story Architect | Scenario-first, personas as multiplexed lenses, phase-don't-cut plan review |
| **Erin** | The Enterprise Project Manager | Full process with judgment calls, compounds learnings |
| **LFG** | Standard Pipeline | No shortcuts — plan, work, review, ship |
| **Max** | The Madman | Spike fast, minimal review, maximum velocity |
| **Nelly** | Nervous Nelly | Security-first, scalability-paranoid, thorough |
| **Oscar** | The Open Source Contributor | Public API lens, docs, naming, first impressions |
| **Perkins** | The Editor | Writing workflow — develop → outline → draft → seven-voice review → compound into the voice guide |
| **Ted** | The Deck Builder | Slidev deck creation — narrative, craft, and audience review |
| **Reena** | The Retro Runner | Post-ship deck retrospective — classifies, refactors, proposes PR upstream |

## User Personas

User personas simulate distinct user archetypes to scenario-test features from real perspectives. Spawned via `/ce:user-scenarios`.

| Persona | Archetype | Catches |
|---------|-----------|---------|
| **Betty** | Power user | Partial failures, stale data, missing bulk operations |
| **Chuck** | Careless user | Missing validation, unhandled errors, skipped instructions |
| **Dorry** | Design-minded user | Visual inconsistency, alignment issues, aesthetic gaps |
| **Mark** | Mobile-first user | Responsive gaps, connectivity failures, input mode limits |
| **Nancy** | Cautious user | Missing affordances, unclear navigation, ambiguous feedback |

### Audience Personas (for decks and presentations)

| Persona | Archetype | Catches |
|---------|-----------|---------|
| **Simon** | The Skeptic | Unsupported claims, number mismatches, definitional drift, cold introductions |
| **Eileen** | The Busy Executive | Buried leads, missing TL;DR, topic-style slide titles, meandering setup |
| **Vera** | The Subject-Matter Expert | Oversimplification, broken analogies, stale references, missed nuance |
| **Pete** | The Newcomer | Unexplained jargon, missing bridges, concepts used before defined |
| **Dana** | The Decision-Maker | Vague asks, missing why-now, no differentiation, no Monday-morning plan |

## Voice Guide

`voice/voice-guide.md` is the canonical record of how Jeff writes — the ground truth every Writing Reviewer cites and the Perkins workflow drafts against. It is a **living** document: Perkins's compound phase appends a new rule every time a draft correction reveals a durable preference.

- **Canonical (version-controlled):** `voice/voice-guide.md` in this repo.
- **Live (read + written at runtime):** `~/.config/compound-engineering/voice-guide.md`, seeded from the canonical copy if absent — this is the copy Perkins updates.
- **Project override:** a repo-local `docs/writing/voice-guide.md` wins for that project.

Seed the live copy alongside the `*-sources.yaml` configs:

```bash
mkdir -p ~/.config/compound-engineering
cp voice/voice-guide.md ~/.config/compound-engineering/voice-guide.md   # seed-if-absent
```

The Perkins workflow also requires the `ce:write` and `ce:prose-review` skills from the [compound-engineering-plugin](https://github.com/JumpstartLab/compound-engineering-plugin) fork.

## Usage

Add to your source configs:

```yaml
# ~/.config/compound-engineering/reviewer-sources.yaml
sources:
  - name: jsl-reviewers
    repo: JumpstartLab/ce-reviewers-jsl
    branch: main
    path: reviewers

# ~/.config/compound-engineering/orchestrator-sources.yaml
sources:
  - name: jsl-orchestrators
    repo: JumpstartLab/ce-reviewers-jsl
    branch: main
    path: orchestrators

# ~/.config/compound-engineering/user-sources.yaml
sources:
  - name: jsl-users
    repo: JumpstartLab/ce-reviewers-jsl
    branch: main
    path: users
```

Then run `/ce:refresh`.
