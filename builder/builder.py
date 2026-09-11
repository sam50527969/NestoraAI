from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
BUILDER_DIR = ROOT / "builder"
CONFIG_PATH = BUILDER_DIR / "config.json"
STATE_PATH = BUILDER_DIR / "state.json"
ROADMAP_PATH = ROOT / "ROADMAP.md"
RULES_PATH = BUILDER_DIR / "rules.md"


class BuilderError(RuntimeError):
    pass


@dataclass(frozen=True)
class RoadmapTask:
    section: str
    name: str

    @property
    def slug(self) -> str:
        value = self.name.lower()
        value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
        return value[:48] or "task"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BuilderError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BuilderError(f"Invalid JSON in {path}: {exc}") from exc


def save_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise BuilderError(f"git {' '.join(args)} failed: {message}")
    return result.stdout.strip()


def assert_safe_git_state(config: dict) -> None:
    branch = run_git("branch", "--show-current")
    if branch in {"main", "develop"} and config.get("mode") != "dry_run":
        raise BuilderError(
            f"Refusing write-capable mode while checked out on protected branch '{branch}'."
        )

    status = run_git("status", "--porcelain")
    if status:
        raise BuilderError(
            "Working tree is not clean. Commit, stash, or discard existing changes first."
        )


def extract_version_1_tasks(markdown: str) -> list[RoadmapTask]:
    lines = markdown.splitlines()
    in_v1 = False
    current_section: str | None = None
    tasks: list[RoadmapTask] = []

    for raw in lines:
        line = raw.strip()
        if line == "## Version 1.0":
            in_v1 = True
            current_section = None
            continue
        if in_v1 and line.startswith("## "):
            break
        if not in_v1:
            continue
        if line.startswith("### "):
            current_section = line[4:].strip()
            continue
        if current_section and line.startswith("- "):
            tasks.append(RoadmapTask(current_section, line[2:].strip()))

    if not tasks:
        raise BuilderError("No Version 1.0 roadmap tasks were found.")
    return tasks


def search_repo_for_task(task: RoadmapTask) -> list[str]:
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", task.name)
        if len(token) >= 4
    ]
    if not tokens:
        return []

    ignored = {
        ".git",
        ".venv",
        "venv",
        "venv312",
        "node_modules",
        "dist",
        "build",
        ".pytest_cache",
    }
    matches: list[str] = []

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        if path.stat().st_size > 1_000_000:
            continue
        if path.suffix.lower() not in {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".md",
            ".json",
            ".css",
        }:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        score = sum(1 for token in tokens if token in text)
        if score:
            matches.append(str(path.relative_to(ROOT)))

    return matches[:20]


def choose_task(tasks: Iterable[RoadmapTask], state: dict) -> RoadmapTask:
    completed = {
        item.get("task")
        for item in state.get("history", [])
        if item.get("status") == "completed"
    }
    for task in tasks:
        if task.name not in completed:
            return task
    raise BuilderError("All Version 1.0 roadmap tasks are marked completed in builder state.")


def build_plan(task: RoadmapTask, config: dict) -> dict:
    evidence = search_repo_for_task(task)
    approval_terms = {
        "authentication": "authentication",
        "billing": "billing",
        "deployment": "deployment",
        "production database": "database_migration",
        "user workspaces": "authorization",
    }
    approval_reason = None
    lowered = task.name.lower()
    for term, reason in approval_terms.items():
        if term in lowered:
            approval_reason = reason
            break

    return {
        "task": task.name,
        "section": task.section,
        "proposed_branch": f"{config['agent_branch_prefix']}{task.slug}",
        "mode": config["mode"],
        "approval_required": approval_reason is not None,
        "approval_reason": approval_reason,
        "repository_evidence": evidence,
        "verification": config.get("verification", {}),
    }


def dry_run() -> int:
    config = load_json(CONFIG_PATH)
    state = load_json(STATE_PATH)
    assert_safe_git_state(config)

    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    tasks = extract_version_1_tasks(roadmap)
    task = choose_task(tasks, state)
    plan = build_plan(task, config)

    state.update(
        {
            "status": "planned",
            "mode": config["mode"],
            "current_task": task.name,
            "current_branch": plan["proposed_branch"],
            "attempt": 0,
            "last_error": None,
            "approval_required": plan["approval_required"],
        }
    )
    save_json(STATE_PATH, state)

    print("=" * 72)
    print("NESTORA BUILDER v0.1 - DRY RUN")
    print("=" * 72)
    print(f"Task             : {plan['task']}")
    print(f"Roadmap section  : {plan['section']}")
    print(f"Proposed branch  : {plan['proposed_branch']}")
    print(f"Approval required: {plan['approval_required']}")
    if plan["approval_reason"]:
        print(f"Approval reason  : {plan['approval_reason']}")
    print("\nRelevant repository evidence:")
    if plan["repository_evidence"]:
        for item in plan["repository_evidence"]:
            print(f"  - {item}")
    else:
        print("  - No obvious existing implementation references found.")
    print("\nVerification gate:")
    for area, commands in plan["verification"].items():
        print(f"  {area}:")
        for command in commands:
            print(f"    - {command}")
    print("\nNo application files were modified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Nestora autonomous builder")
    parser.add_argument(
        "command",
        choices=["dry-run"],
        help="v0.1 currently supports guarded planning only",
    )
    args = parser.parse_args()

    try:
        if args.command == "dry-run":
            return dry_run()
    except BuilderError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
