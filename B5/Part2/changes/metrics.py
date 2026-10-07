"""Part 2 before/after metrics for the four saved versions of the app.

Same scope and tool for every version:
  scope = the app package doc_manager/*.py (tests, example project and docs excluded)
  tool  = lizard 1.17.31 (NLOC = code lines without blank lines and comments,
          CCN = cyclomatic complexity of one function)
It also runs each version's own test suite and records passed/total.

Run from the B5 folder:   python Part2/changes/metrics.py
Writes Part2/changes/metrics.csv and Part2/changes/metrics.log
"""
import csv
import glob
import os
import re
import subprocess
import sys

import lizard

VERSIONS = [
    ("original", "data/code"),
    ("after_change1", "Part2/changes/Change1/code"),
    ("after_change2", "Part2/changes/Change2/code"),
    ("after_change3", "Part2/code"),
]
OUT = "Part2/changes"


def measure(folder):
    files = sorted(glob.glob(os.path.join(folder, "doc_manager", "*.py")))
    results = [lizard.analyze_file(f) for f in files]
    functions = [fn for r in results for fn in r.function_list]
    ccn = [fn.cyclomatic_complexity for fn in functions]
    return {
        "source_files": len(files),
        "nloc": sum(r.nloc for r in results),
        "functions": len(functions),
        "max_ccn": max(ccn),
        "avg_ccn": round(sum(ccn) / len(ccn), 2),
    }, functions


def run_tests(folder):
    command = [sys.executable, "-m", "django", "test", "tests",
               "--settings=tests.test_settings"]
    env = dict(os.environ, PYTHONPATH=".")
    output = subprocess.run(command, cwd=folder, env=env, text=True,
                            capture_output=True).stderr
    total = int(re.search(r"Ran (\d+) test", output).group(1))
    failed = sum(int(n) for n in re.findall(r"(?:failures|errors)=(\d+)", output))
    return total - failed, total


rows, log = [], []
for version, folder in VERSIONS:
    numbers, functions = measure(folder)
    passed, total = run_tests(folder)
    rows.append({"version": version, "folder": folder, **numbers,
                 "tests_passed": passed, "tests_total": total})
    log.append(f"== {version} ({folder}) ==")
    for fn in functions:
        log.append(f"  {fn.filename.replace(os.sep, '/'):60} {fn.name:28} "
                   f"NLOC={fn.nloc:3} CCN={fn.cyclomatic_complexity}")
    log.append(f"  total: {numbers} tests {passed}/{total}\n")

with open(os.path.join(OUT, "metrics.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
with open(os.path.join(OUT, "metrics.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(log) + "\n")
print("\n".join(log))
