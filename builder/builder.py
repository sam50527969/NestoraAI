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
    unexpected = [
        line
        for line in status.splitlines()
        if not line.endswith(" builder/state.json")
    ]
    if unexpected:
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


def task_tokens(task: RoadmapTask) -> list[str]:
    stop_words = {
        "agent", "better", "button", "creation", "frontend", "panel",
        "recommended", "summary", "user", "workspaces",
    }
    return [
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]+", task.name)
        if len(token) >= 4 and token.lower() not in stop_words
    ]


def iter_repo_files() -> Iterable[Path]:
    ignored = {
        ".git", ".venv", "venv", "venv312", "node_modules", "dist",
        "build", ".pytest_cache",
    }
    allowed_suffixes = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".json", ".css",
    }

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored for part in path.parts):
            continue
        if path.stat().st_size > 1_000_000:
            continue
        if path.suffix.lower() not in allowed_suffixes:
            continue
        yield path


def search_repo_for_task(task: RoadmapTask) -> list[str]:
    tokens = task_tokens(task)
    if not tokens:
        return []

    scored: list[tuple[int, str]] = []
    for path in iter_repo_files():
        relative = str(path.relative_to(ROOT))
        if relative.startswith("builder\\") or relative.startswith("builder/"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        score = sum(1 for token in tokens if token in text or token in path.name.lower())
        if score:
            scored.append((score, relative))

    scored.sort(key=lambda item: (-item[0], item[1].lower()))
    return [relative for _, relative in scored[:20]]


def detect_existing_completion(task: RoadmapTask) -> dict:
    name = task.name.lower()
    checks: list[tuple[str, tuple[str, ...]]] = []

    if "ceo agent frontend chat" in name:
        checks = [
            ("frontend/src/pages/CEO.jsx", ("CEOChat",)),
            ("frontend/src/components/agents/ceo/CEOChat.jsx", ("askCEO", "Ask CEO")),
        ]
    elif "executive daily briefing" in name:
        checks = [
            ("frontend/src/pages/CEO.jsx", ("Executive Summary", "getCEOBrief")),
        ]

    if not checks:
        return {"complete": False, "evidence": []}

    evidence: list[str] = []
    for relative, required_terms in checks:
        path = ROOT / relative
        if not path.exists():
            return {"complete": False, "evidence": evidence}
        text = path.read_text(encoding="utf-8", errors="ignore")
        missing = [term for term in required_terms if term not in text]
        if missing:
            return {"complete": False, "evidence": evidence}
        evidence.append(relative)

    return {"complete": True, "evidence": evidence}


def choose_task(tasks: Iterable[RoadmapTask], state: dict) -> tuple[RoadmapTask, list[dict]]:
    completed = {
        item.get("task")
        for item in state.get("history", [])
        if item.get("status") in {"completed", "already_implemented"}
    }
    auto_skipped: list[dict] = []

    for task in tasks:
        if task.name in completed:
            continue
        detection = detect_existing_completion(task)
        if detection["complete"]:
            auto_skipped.append(
                {
                    "task": task.name,
                    "status": "already_implemented",
                    "evidence": detection["evidence"],
                }
            )
            continue
        return task, auto_skipped

    raise BuilderError("All Version 1.0 roadmap tasks appear completed or are marked completed in builder state.")


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
    task, auto_skipped = choose_task(tasks, state)
    plan = build_plan(task, config)

    print("=" * 72)
    print("NESTORA BUILDER v0.1 - DRY RUN")
    print("=" * 72)

    if auto_skipped:
        print("Already implemented roadmap items detected:")
        for item in auto_skipped:
            evidence = ", ".join(item["evidence"])
            print(f"  - {item['task']} [{evidence}]")
        print()

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
    print("Dry-run state was not written to disk.")
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
