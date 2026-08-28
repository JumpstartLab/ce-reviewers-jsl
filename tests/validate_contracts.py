#!/usr/bin/env python3
"""Contract tests for persona and orchestrator files.

Validates that every orchestrator phase references a skill that exists in
the compound-engineering plugin and, for `mode:<value>` argument tokens,
that the target skill actually documents that mode. This is the check that
would have caught erin.md's phantom `ce:review mode:plan` phase (fixed in
PR #27, 2026-08-28) before it shipped.

Usage:
    python3 tests/validate_contracts.py --plugin-dir <path>

where <path> is the plugin root containing skills/ (e.g. a checkout of
JumpstartLab/compound-engineering-plugin at plugins/compound-engineering).

Exit code 0 on pass, 1 on any failure. Warnings never fail the run.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PERSONA_DIRS = ["orchestrators", "reviewers", "users"]

failures = []
warnings = []


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def parse_frontmatter(path):
    """Return (frontmatter dict, error string or None)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, "no YAML frontmatter block"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "unterminated frontmatter block"
    try:
        data = yaml.safe_load(text[3:end])
    except yaml.YAMLError as e:
        return None, f"frontmatter is not valid YAML: {e}"
    if not isinstance(data, dict):
        return None, "frontmatter did not parse to a mapping"
    return data, None


def resolve_skill_dir(skill_ref, plugin_dir):
    """Map a phase's skill reference to a skill directory name.

    Handles: `compound-engineering:todo-resolve` -> todo-resolve,
    `ce:review` -> ce-review, `compound-engineering:ce-compound` -> ce-compound.
    """
    name = skill_ref.strip()
    if ":" in name:
        prefix, rest = name.split(":", 1)
        if prefix == "compound-engineering":
            name = rest
            if name.startswith("ce:"):
                name = "ce-" + name[3:]
        elif prefix == "ce":
            name = "ce-" + rest
        else:
            return None, f"unrecognized skill namespace {prefix!r}"
    skill_md = plugin_dir / "skills" / name / "SKILL.md"
    if not skill_md.is_file():
        return None, f"skill directory skills/{name}/SKILL.md not found in plugin"
    return skill_md, None


ARG_TOKEN = re.compile(r"(?<!\$)\b(mode|stage|personas):([A-Za-z][A-Za-z0-9_-]*)")


def check_arg_tokens(orch, phase_name, args, skill_md):
    skill_text = skill_md.read_text(encoding="utf-8")
    for key, value in ARG_TOKEN.findall(args):
        token = f"{key}:{value}"
        if key == "mode":
            # Strict: the skill must document this exact mode token.
            if token not in skill_text:
                fail(
                    f"{orch}: phase {phase_name!r} passes {token!r} but "
                    f"{skill_md.parent.name}/SKILL.md never mentions it — "
                    f"phantom mode (the ce:review mode:plan class of bug)"
                )
        else:
            # Lenient: other keyed tokens vary; only warn when the key
            # itself is absent from the skill.
            if f"{key}:" not in skill_text:
                warn(
                    f"{orch}: phase {phase_name!r} passes {token!r} but "
                    f"{skill_md.parent.name}/SKILL.md never mentions "
                    f"{key}: tokens"
                )


def check_orchestrator(path, plugin_dir):
    fm, err = parse_frontmatter(path)
    name = path.name
    if err:
        fail(f"{name}: {err}")
        return
    if not fm.get("name"):
        fail(f"{name}: frontmatter missing required key 'name'")
    phases = fm.get("phases")
    if phases is None:
        return  # not all orchestrators are phase-driven
    if not isinstance(phases, list):
        fail(f"{name}: 'phases' must be a list")
        return
    for i, phase in enumerate(phases):
        if not isinstance(phase, dict):
            fail(f"{name}: phases[{i}] is not a mapping")
            continue
        pname = phase.get("name", f"#{i}")
        skill_ref = phase.get("skill")
        if not skill_ref:
            # Phases may carry only a gate (orchestrator-driven prose
            # phase) or a signal — both are legitimate ce-run shapes.
            continue
        if plugin_dir is None:
            continue
        skill_md, err = resolve_skill_dir(skill_ref, plugin_dir)
        if err:
            fail(f"{name}: phase {pname!r} -> {skill_ref!r}: {err}")
            continue
        args = phase.get("args") or ""
        check_arg_tokens(name, pname, str(args), skill_md)


def check_persona(path):
    fm, err = parse_frontmatter(path)
    if err:
        fail(f"{path.parent.name}/{path.name}: {err}")
        return
    if not fm.get("name"):
        fail(f"{path.parent.name}/{path.name}: frontmatter missing 'name'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--plugin-dir",
        type=Path,
        default=None,
        help="Plugin root containing skills/. Omit to skip skill-existence "
        "checks (frontmatter checks still run).",
    )
    opts = ap.parse_args()

    plugin_dir = opts.plugin_dir
    if plugin_dir is not None:
        if not (plugin_dir / "skills").is_dir():
            print(f"error: {plugin_dir}/skills not found", file=sys.stderr)
            return 1
    else:
        warn("no --plugin-dir given; skipping skill-existence and mode checks")

    for dirname in PERSONA_DIRS:
        d = REPO_ROOT / dirname
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            if dirname == "orchestrators":
                check_orchestrator(path, plugin_dir)
            else:
                check_persona(path)

    # Known-failures ratchet: entries in tests/known-failures.txt are
    # pre-existing debt being burned down. A matched entry downgrades to
    # KNOWN (non-fatal); a stale entry (listed but no longer failing)
    # fails the run so the baseline shrinks honestly. Never add to it.
    baseline_path = REPO_ROOT / "tests" / "known-failures.txt"
    baseline = set()
    if baseline_path.is_file():
        baseline = {
            line.strip()
            for line in baseline_path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        }
    known = [f for f in failures if f in baseline]
    real = [f for f in failures if f not in baseline]
    stale = sorted(baseline - set(failures))
    for s in stale:
        real.append(
            f"stale known-failures.txt entry (no longer fails — remove "
            f"it): {s}"
        )

    for w in warnings:
        print(f"WARN  {w}")
    for k in known:
        print(f"KNOWN {k}")
    for f in real:
        print(f"FAIL  {f}")
    total = sum(
        len(list((REPO_ROOT / d).glob("*.md")))
        for d in PERSONA_DIRS
        if (REPO_ROOT / d).is_dir()
    )
    print(
        f"\n{total} files checked, {len(real)} failures, "
        f"{len(known)} known, {len(warnings)} warnings"
    )
    return 1 if real else 0


if __name__ == "__main__":
    sys.exit(main())
