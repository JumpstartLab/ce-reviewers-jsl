# CE Reviewers (Test)

Test repo for validating the pluggable reviewer system in the Compound Engineering plugin.

## Usage

Add to your `reviewer-registry.yaml`:

```yaml
sources:
  - name: test-reviewers
    repo: JumpstartLab/ce-reviewers-test
    branch: main
    path: .
```

Then run `/ce:refresh`.
