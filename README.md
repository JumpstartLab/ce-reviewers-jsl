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

## Orchestrators

Orchestrators define *how* to run a project — which phases to execute, which reviewers to prioritize, when to skip steps, and how to synthesize findings.

| Orchestrator | Archetype | Style |
|---|---|---|
| **Erin** | The Enterprise Project Manager | Full process with judgment calls, compounds learnings |
| **LFG** | Standard Pipeline | No shortcuts — plan, work, review, ship |
| **Max** | The Madman | Spike fast, minimal review, maximum velocity |
| **Nelly** | Nervous Nelly | Security-first, scalability-paranoid, thorough |
| **Oscar** | The Open Source Contributor | Public API lens, docs, naming, first impressions |
| **Deck** | The Deck Builder | Slidev deck creation — narrative, craft, and audience review |
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
