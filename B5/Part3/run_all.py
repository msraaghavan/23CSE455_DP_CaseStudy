"""Part 3: build, test, time and measure the 8 snippets (2 problems x 4 languages).

Run from the B5 folder:   python Part3/run_all.py
Needs: Python 3.11, Java 25 (javac, java), Node.js 24, the "ziglang" pip package (clang C++
compiler) and lizard 1.17.31.

Rules (also in README.md):
- LOC = lizard NLOC of the production file only (no blank lines, no comments, no test runner).
- CC  = the highest lizard cyclomatic complexity of one function in that file.
  lizard 1.17 does not see JavaScript methods named get(...) (it reads `get` as getter syntax),
  so the JavaScript file is measured from a temporary copy where "get(" is renamed "get_(" -
  same lines, same branches.
- Time = the whole test process: start-up + reading the shared case file + running all cases.
  Compile first (not timed), then 1 warm-up run and 5 measured runs; we report the median in ms.

Writes: Part3/evidence/<problem>_<language>.log, Part3/evidence/timings.csv,
        Part3/evidence/metrics.txt and Part3/llm/pattern_crosslanguage.csv
        (the CSV name and place follow the "Complete repository hierarchy" of the instructions)
"""
import csv
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

import lizard

PROBLEMS = [
    ("template_method_document_page", "Template Method", "Published Document Page",
     {"python": ("document_page.py", "test_document_page.py"),
      "java": ("DocumentPage.java", "TestDocumentPage"),
      "javascript": ("documentPage.js", "testDocumentPage.js"),
      "cpp": ("document_page.hpp", "test_document_page")}),
    ("strategy_upload_check", "Strategy", "Upload File Checks",
     {"python": ("upload_check.py", "test_upload_check.py"),
      "java": ("UploadCheck.java", "TestUploadCheck"),
      "javascript": ("uploadCheck.js", "testUploadCheck.js"),
      "cpp": ("upload_check.hpp", "test_upload_check")}),
]

NOTES = {
    ("Template Method", "java"): "abstract class View with a final dispatch() (the recipe cannot be overridden) "
                                 "and an abstract get(); a missing get() is a compile error",
    ("Template Method", "python"): "plain base class; get() raises NotImplementedError, so a missing step "
                                   "is found only at run time; versions are tuples",
    ("Template Method", "javascript"): "ES class with extends/super; the base get() throws an Error (run-time "
                                       "check only); versions are plain objects",
    ("Template Method", "cpp"): "pure virtual get() makes View abstract (compile-time check); dispatch() is not "
                                "virtual, so subclasses cannot replace the recipe; header-only",
    ("Strategy", "java"): "the Strategy is an explicit interface Validator that ExtensionValidator implements; "
                          "records for Upload; null means no problem",
    ("Strategy", "python"): "the Strategy is not declared (duck typing): any object with check() works; "
                            "namedtuple for Upload; None means no problem",
    ("Strategy", "javascript"): "the Strategy is not declared (duck typing), like Python; Upload is a plain "
                                "object; null means no problem",
    ("Strategy", "cpp"): "the Strategy is an abstract class with a pure virtual check(); strategies are held as "
                         "shared_ptr; the lower-case loop adds one branch",
}


def version_of(language):
    if language == "python":
        return f"CPython {platform.python_version()}"
    if language == "java":
        first = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.splitlines()[0]
        return "Java " + first.split('"')[1] + " (javac + java)"
    if language == "javascript":
        return "Node.js " + subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
    out = subprocess.run([sys.executable, "-m", "ziglang", "c++", "--version"], capture_output=True, text=True).stdout
    return out.splitlines()[0].replace("clang version", "clang") + " (ziglang 0.16.0, -std=c++17 -O2)"


def commands(language, snippet, runner, build):
    """Returns (build command or None, run command, command text for the CSV)."""
    if language == "python":
        return None, [sys.executable, runner], f"python {runner}"
    if language == "java":
        return (["javac", "-d", build, snippet, runner + ".java"], ["java", "-cp", build, runner],
                f"javac -d build {snippet} {runner}.java && java -cp build {runner}")
    if language == "javascript":
        return None, ["node", runner], f"node {runner}"
    exe = os.path.join(build, runner + ".exe")
    return ([sys.executable, "-m", "ziglang", "c++", "-std=c++17", "-O2", "-o", exe, runner + ".cpp"], [exe],
            f"python -m ziglang c++ -std=c++17 -O2 -o {runner}.exe {runner}.cpp && {runner}.exe")


def measure(path, language):
    if language == "javascript":
        with open(path, encoding="utf-8") as f:
            code = f.read().replace("get(", "get_(")
        result = lizard.analyze_file.analyze_source_code(path.replace(".js", "_measured.js"), code)
    else:
        result = lizard.analyze_file(path)
    functions = [(fn.name, fn.cyclomatic_complexity) for fn in result.function_list]
    return result.nloc, max(cc for _, cc in functions), functions


rows, timings, metric_lines = [], [], []
os.makedirs("Part3/evidence", exist_ok=True)
for folder, pattern, instance, files in PROBLEMS:
    for language, (snippet, runner) in files.items():
        work = os.path.join("Part3", folder, language)
        build = tempfile.mkdtemp()
        build_cmd, run_cmd, text = commands(language, snippet, runner, build)
        log = [f"{pattern} - {instance} - {language}",
               f"working folder: Part3/{folder}/{language}",
               f"runtime/compiler: {version_of(language)}",
               f"command: {text}",
               "(build/ and the .exe were made in a temporary folder that was deleted afterwards)"]
        if build_cmd:
            built = subprocess.run(build_cmd, cwd=work, capture_output=True, text=True)
            log += [f"compile exit code: {built.returncode}" + (": " + built.stdout + built.stderr
                                                               if built.returncode else "")]
        first = subprocess.run(run_cmd, cwd=work, capture_output=True, text=True)
        log += ["--- test output ---", first.stdout.rstrip(), f"--- exit code: {first.returncode}"]
        times = []
        for run in range(6):                       # run 0 = warm-up, runs 1-5 measured
            start = time.perf_counter()
            subprocess.run(run_cmd, cwd=work, capture_output=True)
            ms = (time.perf_counter() - start) * 1000
            timings.append([folder, language, "warm-up" if run == 0 else run, round(ms, 1)])
            if run:
                times.append(ms)
        shutil.rmtree(build, ignore_errors=True)
        with open(f"Part3/evidence/{folder}_{language}.log", "w", encoding="utf-8") as f:
            f.write("\n".join(log) + "\n")
        result_line = [line for line in first.stdout.splitlines() if line.startswith("passed")][-1]
        loc, max_cc, functions = measure(os.path.join(work, snippet), language)
        metric_lines.append(f"{folder}/{language}/{snippet}: NLOC={loc} functions={functions}")
        rows.append({
            "pattern_name": pattern,
            "instance_name": instance,
            "language": {"python": "Python", "java": "Java", "javascript": "JavaScript", "cpp": "C++"}[language],
            "snippet_path": f"Part3/{folder}/{language}/{snippet}",
            "source_loc": loc,
            "max_function_cc": max_cc,
            "runtime_compiler": version_of(language),
            "test_command": text,
            "test_result": result_line.replace("passed ", "") + " passed",
            "median_process_ms": round(statistics.median(times), 1),
            "language_notes": NOTES[pattern, language],
        })
        print(f"{folder:32} {language:10} {result_line:12} LOC={loc:3} CC={max_cc} "
              f"median={statistics.median(times):7.1f} ms")

with open("Part3/evidence/timings.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows([["problem", "language", "run", "ms"]] + timings)
with open("Part3/evidence/metrics.txt", "w", encoding="utf-8") as f:
    f.write("lizard 1.17.31, production files only (per function: name, cyclomatic complexity)\n")
    f.write("\n".join(metric_lines) + "\n")
with open("Part3/llm/pattern_crosslanguage.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print("wrote Part3/llm/pattern_crosslanguage.csv and Part3/evidence/")
