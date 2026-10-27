import os
import csv
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import mi_visit

# Configuration
REPO_NAME = "requests"
REPO_PATH = Path(f"repos/{REPO_NAME}")
MIN_CC = 10
MAX_FILE_LOC = 500  # Context window limit
CSV_FILE = "datasets/master_metrics.csv"

candidates = []

for py_file in REPO_PATH.rglob("*.py"):
    # Ignorevendored packages, test files, docs, and setup scripts
    if any(part in py_file.parts for part in ["tests", "test", "docs", "build", "packages"]) or py_file.name.startswith("test_") or py_file.name == "setup.py":
        continue

    try:
        code = py_file.read_text(encoding="utf-8")
    except Exception:
        continue

    file_loc = len(code.splitlines())
    if file_loc > MAX_FILE_LOC or file_loc < 20:
        continue

    try:
        blocks = cc_visit(code)
        mi_score = mi_visit(code, multi=True)
    except Exception:
        continue

    for block in blocks:
        if block.complexity >= MIN_CC:
            # Generate unique ID to prevent collisions if one file has multiple high-CC functions
            safe_file_name = py_file.stem
            unique_file_id = f"{REPO_NAME}_{safe_file_name}_{block.name}.py"
            func_loc = (block.endline - block.lineno) + 1
            
            candidates.append({
                "File_ID": unique_file_id,
                "Repo": REPO_NAME,
                "CC": block.complexity,
                "MI": round(mi_score, 2),
                "File_LOC": file_loc,
                "Func_LOC": func_loc,
                "File_Path": str(py_file),
                "Function_Name": block.name,
                "Line_Start": block.lineno,
                "Line_End": block.endline
            })

# Sort by highest complexity first
candidates.sort(key=lambda x: x["CC"], reverse=True)

# Write to CSV and print to terminal
file_exists = os.path.isfile(CSV_FILE)
with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["File_ID", "Repo", "CC", "MI", "File_LOC", "Func_LOC", "File_Path", "Function_Name", "Line_Start", "Line_End"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Only write headers if creating a brand new CSV
    if not file_exists:
        writer.writeheader()
        
    for c in candidates:
        writer.writerow(c)
        print(f"CC: {c['CC']:2d} | MI: {c['MI']:5.2f} | Func LOC: {c['Func_LOC']:3d} | {c['File_ID']} (L{c['Line_Start']}-{c['Line_End']})")