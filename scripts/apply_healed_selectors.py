import json
import argparse  
from pathlib import Path
from datetime import datetime

CACHE_FILE = Path("reports/selector_cache.json")
TESTS_DIR = Path("tests")  # Adjust if your tests or Page Objects live elsewhere

# ----------------------------------------------------------------------
# Helper: locate the latest healing report produced by pytest‑self‑healer
# ----------------------------------------------------------------------
def _latest_report_path() -> Path | None:
    report_files = sorted(
        Path("reports").glob("healing_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return report_files[0] if report_files else None


def extract_mappings(data: dict) -> dict[str, str]:
    # Original implementation works for the nested‑dict format.
    # We keep it for backward compatibility.
    mappings = {}
    for url, selectors in data.items():
        if not isinstance(selectors, dict):
            continue
        for old_sel, new_sel in selectors.items():
            if isinstance(new_sel, str) and old_sel != new_sel:
                mappings[old_sel] = new_sel
    return mappings


# ----------------------------------------------------------------------
# New: pull mappings out of the *standard* healing report format
# ----------------------------------------------------------------------
def extract_from_report(report: dict) -> dict[str, str]:
    """
    The default report looks like:
    {
        "url": "https://example.org/",
        "healed_selectors": [
            {"old_selector": "button#old", "new_selector": "button#new"},
            ...
        ],
        ...
    }
    This helper normalises it to the flat {old: new} dict used by the
    replacement loop.
    """
    mappings = {}
    healed = report.get("healed_selectors", [])
    for entry in healed:
        old_sel = entry.get("old_selector")
        new_sel = entry.get("new_selector")
        if old_sel and new_sel and old_sel != new_sel:
            mappings[old_sel] = new_sel
    return mappings


def apply_fixes() -> None:
    # --------------------------------------------------------------
    # 0️⃣ Parse optional single‑test argument
    # --------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Apply healed selectors to test files."
    )
    parser.add_argument(
        "--test",
        type=Path,
        help="Path to a single test file to patch (default: all *.py under tests/)",
    )
    args = parser.parse_args()
    single_test_path: Path | None = args.test

    # 1️⃣ Try the explicit cache file first (kept for backward compat)
    cache_path = CACHE_FILE if CACHE_FILE.exists() else None

    # 2️⃣ If not found, fall back to the latest healing report
    if not cache_path:
        cache_path = _latest_report_path()
        if not cache_path:
            print("❌ No selector cache or healing report found in ./reports.")
            return

    data = json.loads(cache_path.read_text(encoding="utf-8"))

    # The report may be a list (multiple runs) or a single dict.
    if isinstance(data, list):
        mappings = {}
        for entry in data:
            mappings.update(extract_mappings(entry) or extract_from_report(entry))
    else:
        mappings = extract_mappings(data) or extract_from_report(data)

    if not mappings:
        print("⚠️ No healed selectors found in the report.")
        return

    # ------------------------------------------------------------------
    # Replacement loop – now respects optional single‑test target
    # ------------------------------------------------------------------
    updated_files = 0
    # If a specific test file was provided, limit the search to that file.
    files_to_process = (
        [single_test_path] if single_test_path else TESTS_DIR.rglob("*.py")
    )
    for py_file in files_to_process:
        if not py_file.is_file():
            continue
        content = py_file.read_text(encoding="utf-8")
        new_content = content

        for old_sel, new_sel in mappings.items():
            safe_replacement = repr(new_sel)
            for quote in ('"', "'"):
                target = f"{quote}{old_sel}{quote}"
                if target in new_content:
                    new_content = new_content.replace(target, safe_replacement)

        if new_content != content:
            py_file.write_text(new_content, encoding="utf-8")
            updated_files += 1
            print(f"✅ Updated selectors in: {py_file}")

    print(f"🛠️  Done. Modified {updated_files} file(s).")
    
if __name__ == "__main__":
    apply_fixes()