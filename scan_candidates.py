import os
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import mi_visit

REPO_PATH = Path("repos/requests")
MIN_CC = 10
MAX_FILE_LOC = 500  # Keep file small enough for SLM context window

candidates = []

for py_file in REPO_PATH.rglob("*.py"):
    # Ignorevendored packages, test files, docs, and setup scripts
    if any(part in py_file.parts for part in ["tests", "test", "docs", "build", "packages"]) or py_file.name.startswith("test_") or py_file.name == "setup.py":
        continue

    try:
        code = py_file.read_text(encoding="utf-8")
    except Exception:
        continue

    loc = len(code.splitlines())
    if loc > MAX_FILE_LOC or loc < 20:
        continue

    try:
        blocks = cc_visit(code)
        mi_score = mi_visit(code, multi=True)
    except Exception:
        continue

    for block in blocks:
        if block.complexity >= MIN_CC:
            candidates.append({
                "file": str(py_file),
                "function": block.name,
                "line_start": block.lineno,
                "line_end": block.endline,
                "cc": block.complexity,
                "file_mi": round(mi_score, 2),
                "file_loc": loc
            })

candidates.sort(key=lambda x: x["cc"], reverse=True)
for c in candidates[:15]:
    print(f"CC: {c['cc']:2d} | MI: {c['file_mi']:5.2f} | LOC: {c['file_loc']:3d} | {c['file']} :: {c['function']} (L{c['line_start']}-{c['line_end']})")