# ============================================================
# BIOQUA: AI-Assisted Water Quality Monitoring System
#
# Authors         : Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D.
# Year            : 2026
# License         : MIT License
#
# This project is the original work of the authors.
# Unauthorized removal of this notice is prohibited.
# ============================================================

"""
Verify Credit Headers
======================
Scans all project source files and checks that the
BIOQUA co-author credit header is present.
Flags any files where the header has been removed or tampered with.

HOW TO RUN:
  python verify_credits.py

WHAT YOU SHOULD SEE:
  - A list of all source files with OK/MISSING status
  - A summary showing how many files pass
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PROJECT_ROOT

CREDIT_MARKER = "Agreda, G.M., Joven, C.L., Mendez, A.V., Tangao, W., Zamora, G.D."

# File extensions to check
SOURCE_EXTENSIONS = {'.py', '.ino', '.cpp', '.h'}

# Directories to skip
SKIP_DIRS = {'__pycache__', '.git', 'venv', 'node_modules', 'models',
             'training_data', 'results', '.gitkeep'}


def scan_files():
    """Scan all source files for the credit header."""
    results = {"ok": [], "missing": [], "skipped": []}

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip irrelevant directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            if ext not in SOURCE_EXTENSIONS:
                continue

            rel_path = os.path.relpath(filepath, PROJECT_ROOT)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    # Only check the first 15 lines (header area)
                    header_lines = ''.join(f.readline() for _ in range(15))

                if CREDIT_MARKER in header_lines:
                    results["ok"].append(rel_path)
                else:
                    results["missing"].append(rel_path)
            except Exception as e:
                results["skipped"].append((rel_path, str(e)))

    return results


def main():
    print("=" * 60)
    print("  BIOQUA Credit Verification")
    print("  Checking for: " + CREDIT_MARKER)
    print("=" * 60)
    print()

    results = scan_files()

    # Show results
    if results["ok"]:
        print(f"  VERIFIED ({len(results['ok'])} files):")
        for f in results["ok"]:
            print(f"    [+] {f}")

    if results["missing"]:
        print()
        print(f"  MISSING CREDITS ({len(results['missing'])} files):")
        for f in results["missing"]:
            print(f"    [!] {f}")

    if results["skipped"]:
        print()
        print(f"  SKIPPED ({len(results['skipped'])} files):")
        for f, reason in results["skipped"]:
            print(f"    [?] {f} ({reason})")

    # Summary
    total = len(results["ok"]) + len(results["missing"])
    print()
    print("-" * 60)
    if results["missing"]:
        print(f"  WARNING: {len(results['missing'])} of {total} files are missing the credit header!")
        print(f"  The following credit line must appear in the first 15 lines:")
        print(f"    {CREDIT_MARKER}")
        sys.exit(1)
    else:
        print(f"  All {total} source files verified. Credits intact.")
        sys.exit(0)


if __name__ == "__main__":
    main()
