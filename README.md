# Jumpstart Lab Reviewers

Custom reviewer personas for the [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) Claude Code plugin.

## Plan Reviewers

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

## Code Reviewers

| Reviewer | Focus |
|----------|-------|
| Sandi Metz | OO design — SRP, dependency injection, duck typing |
| Corey (Testing) | Test strategy, hourglass testing, acceptance tests |
| Jim Weirich (Git) | Git hygiene, commits as storytelling |
| Abby (Synthesis) | Cross-reviewer synthesis PM, prioritizes findings |

## Usage

Add to your `reviewer-registry.yaml`:

```yaml
sources:
  - name: jsl-reviewers
    repo: JumpstartLab/ce-reviewers-jsl
    branch: main
    path: .
```

Then run `/ce:refresh`.
