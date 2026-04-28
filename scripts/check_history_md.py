#!/usr/bin/env python3
"""Check that each modified Odoo addon has a readme/HISTORY.md file
and that the manifest version is mentioned in it."""
import ast
import re
import sys
from pathlib import Path


def find_addon_root(file_path: Path, repo_root: Path) -> Path | None:
    """Return the addon root directory for a given file, or None."""
    for candidate in file_path.parents:
        if (candidate / "__manifest__.py").exists():
            try:
                rel = candidate.relative_to(repo_root)
                if len(rel.parts) == 1:
                    return candidate
            except ValueError:
                pass
    return None


def get_manifest_version(addon: Path) -> str | None:
    """Return the version string from __manifest__.py, or None."""
    manifest_path = addon / "__manifest__.py"
    try:
        tree = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
        return tree.get("version")
    except Exception:
        return None


def check_version_in_history(history_path: Path, version: str) -> bool:
    """Return True if version appears as a markdown heading in HISTORY.md."""
    content = history_path.read_text(encoding="utf-8")
    # Match lines like: ## 18.0.2.2.2 or ## 18.0.2.2.2 (2026-04-28)
    pattern = re.compile(r"^#{1,3}\s+" + re.escape(version) + r"(\s|$)", re.MULTILINE)
    return bool(pattern.search(content))


def main() -> int:
    repo_root = Path.cwd()
    checked = set()

    for arg in sys.argv[1:]:
        file_path = Path(arg).resolve()
        addon = find_addon_root(file_path, repo_root)
        if addon is None:
            continue
        addon_rel = str(addon.relative_to(repo_root))
        if addon_rel in checked:
            continue
        checked.add(addon_rel)

        history = addon / "readme" / "HISTORY.md"
        if not history.exists():
            print(f"WARNING: {addon_rel} — lipsește readme/HISTORY.md")
            continue

        version = get_manifest_version(addon)
        if not version:
            print(f"WARNING: {addon_rel} — nu s-a putut citi versiunea din __manifest__.py")
            continue

        if not check_version_in_history(history, version):
            print(
                f"WARNING: {addon_rel} — versiunea {version} din manifest "
                f"nu apare în readme/HISTORY.md"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
