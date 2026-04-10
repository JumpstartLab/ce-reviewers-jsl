# Jumpstart Lab — CE Reviewers & Orchestrators

Custom reviewer personas and orchestrator definitions for the [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) Claude Code plugin.

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
```

Then run `/ce:refresh`.
