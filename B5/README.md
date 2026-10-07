# Team B5 - Design Pattern Identification and Evolution in a Django based Digital Document Management Application

23CSE455 Design Patterns - Case Study. Report: `B5_Report.pdf` (LaTeX source: `B5_Report.tex`). Date: 2026-10-07.

| Roll number | Student name | Batch |
|---|---|---|
| AM.SC.U4CSE23330 | Raaghavan M S | CSE-D |
| AM.SC.U4CSE23368 | V Sriman Vashishta | CSE-D |

## The project in five lines
1. **App:** [impicode/doc_manager](https://github.com/impicode/doc_manager) v1.0.2 is a small Django app (MIT licence,
   138 lines of code). An admin uploads versions of a document, such as a Privacy Policy. Old versions are kept,
   and one version is published for visitors.
2. **Part 1:** we found 2 pattern types in 4 places: Template Method (2) and Strategy (2).
3. **Part 2:** we made 3 small, realistic changes, each with a refactoring first. Tests went 11 -> 19 -> 22 -> 25,
   and all of them pass.
4. **Part 3:** each pattern type was rewritten as a small program in Java, Python, JavaScript and C++. All 8 programs
   pass the same shared test cases.
5. **LLM:** we made one recorded Claude Opus 5.5 run per part, then checked every claim it made.

## Folder structure (follows the "Complete repository hierarchy" of the instructions)
```
B5/
|-- README.md
|-- B5_Report.pdf
|-- B5_Report.tex
|-- data/
|   |-- code/                        original application source (v1.0.2, commit 5943319)
|   |-- test_result/                 baseline test log, probe test + log, environment, screenshots (app, GitHub folder)
|-- Part1/
|   |-- patterns.csv
|   |-- Pattern_count.csv
|   |-- pattern_architecture/        diagram source (.tex) + image (.pdf, .png)
|   |-- Part1_prompt.txt
|   |-- llm.csv
|   |-- llm/                         LLM input, raw output, run info, our check of every claim
|   |-- make_csvs.py                 writes the pattern CSVs of Part 1 and Part 2 from the code
|-- Part2/
|   |-- code/                        evolved application source (after Change 3)
|   |-- changes/
|   |   |-- Change1/                 requirement, diffs, test result (+ code after Change 1)
|   |   |-- Change2/                 requirement, diffs, test result (+ code after Change 2, screenshot)
|   |   |-- Change3/                 requirement, diffs, test result
|   |   |-- commits.txt, metrics.csv, metrics.log, metrics.py
|   |-- pattern_evalution.csv
|   |-- Pattern_count.csv
|   |-- diagrams/                    updated UML (.tex + .pdf + .png)
|   |-- Part2_prompt.text
|   |-- llm.csv
|   |-- llm/                         LLM input, raw output, run info, our check, migration probe
|-- Part3/
|   |-- template_method_document_page/   java/ python/ javascript/ cpp/ (snippet, test runner, README)
|   |-- strategy_upload_check/           java/ python/ javascript/ cpp/ (snippet, test runner, README)
|   |-- test-cases/                  common specification + shared test cases
|   |-- evidence/                    test logs, timings, complexity
|   |-- run_all.py                   builds, tests, times and measures all 8 programs
|   |-- llm/
|       |-- part3_prompt.txt
|       |-- llm.csv
|       |-- pattern_crosslanguage.csv
|       |-- B5_slide.pdf             (source: B5_slide.tex)
|       |-- input, raw output, run info, our check, generated_code/ and its test log
```
The CSV file names (`Pattern_count.csv`, `pattern_evalution.csv`) and `Part2_prompt.text` are spelled exactly as in
the required hierarchy. Each CSV has one header row, is UTF-8, and uses paths that start from this `B5/` folder.

**Not uploaded:** no passwords, no dependency caches (`venv/`, `node_modules/`, `__pycache__/`) and no compiled files
(`build/`, `.class`, `.exe`). The only `SECRET_KEY` values in the code are the original project's public
test/demo keys. The two small `.mo` files in `doc_manager/locale/` are the original project's translation files; we kept
them so the source stays exactly as published.

## Application source
| | |
|---|---|
| Repository | https://github.com/impicode/doc_manager |
| Version | 1.0.2 (git tag `v1.0.2`) |
| Baseline commit | `5943319a6dd41d91807867be8d8ca0661cf93c1c` (2023-03-15) |
| Accessed | 2026-10-06 |
| Licence | MIT (`data/code/LICENSE`) |

## Environment
| | Version |
|---|---|
| OS | Windows 11 |
| Language and framework | Python 3.11.9 and Django 4.1.13 (the newest pair tested by the project itself, `tox.ini`: `py311-django41`) |
| Database | SQLite 3.45.1 (tests use an in-memory database) |
| Other packages | asgiref 3.12.1, sqlparse 0.6.0, tzdata 2026.5 |
| Measuring tool | lizard 1.17.31 (lines of code and cyclomatic complexity) |
| Part 3 | Java 25, CPython 3.11.9, Node.js 24.17.0, clang 21.1.0 (from the `ziglang` 0.16.0 pip package) |
| Diagrams and report | MiKTeX 24.1 (pdfLaTeX, TikZ), PyMuPDF 1.28.2 (PDF to PNG) |

Full list: `data/test_result/environment.txt`.

## How to run the application and its tests
```bash
cd data/code                          # or Part2/code for the evolved version
python -m venv venv
venv\Scripts\activate                 # Linux/macOS: source venv/bin/activate
pip install "Django==4.1.13"
python runtests.py                    # the project's own test command
python -m django test tests -v 2 --settings=tests.test_settings    # same tests, one line per test
```
Results: original **11/11**, after Change 1 **19/19**, after Change 2 **22/22**, after Change 3 **25/25**
(logs: `data/test_result/baseline_tests.log`, `Part2/changes/ChangeN/test_result.log`).

To see the app running:
1. `python manage.py makemigrations our_app`
2. `python manage.py migrate`
3. `python manage.py createsuperuser`
4. `python manage.py runserver`
5. Add and publish a document at http://127.0.0.1:8000/admin/, then open http://127.0.0.1:8000/see_document/.

Screenshots: `data/test_result/screenshot_see_document_original.png` and
`Part2/changes/Change2/screenshot_old_version.png`. For these, the sample document was added with `manage.py shell`
and the page was captured with headless Chrome. The screenshot of our team folder on GitHub (report, Section 7) is
`data/test_result/github_screenshot.png`.

Part 1 probe tests (run in `data/code`): `python ../test_result/probe_test.py` gives **10/10** (`probe_test.log`).

## Inspected modules (Part 1 scope)
- **Inspected:** the app package `doc_manager/`: `models.py`, `admin.py`, `views.py`, `apps.py`, `version.py` and an empty
  `__init__.py` (138 lines of code). We also read the admin template for context.
- **Excluded:**
  - `tests/` - used as evidence;
  - `example/` - a demo project that only sets `model = OurModel`;
  - `locale/` - translations;
  - `docs/` and the packaging files - no design;
  - Django itself - framework code, named only where the app plugs into it.

## Part 2 commits (local clone of the upstream repository, branch `case-study`)
| Version | Commit | What |
|---|---|---|
| original | `5943319` | upstream v1.0.2 |
| | `cadf6cc` | CH01: characterization tests for the document page |
| | `c9978f5` | CH01 refactoring: one `FILE_TYPES` table instead of four type lists |
| after_change1 | `8e5cd10` | CH01: accept plain-text (.txt) documents |
| | `3018e42` | CH02 refactoring: Extract Method `get_document()` |
| after_change2 | `62acc26` | CH02: open an older (published) version by its id |
| | `6fb6088` | CH03 refactoring: Rename Parameter `queryset` -> `document` |
| after_change3 | `145fcce` | CH03: lock the file of a published version |

Every version can also be rebuilt without git: take `data/code` and apply the `.diff` files of Change1, Change2 and
Change3 in order (`git apply`; on Windows use `git -c core.autocrlf=false apply`). We checked that this gives exactly
`Part2/changes/Change1/code`, `Part2/changes/Change2/code` and `Part2/code`. Full hashes: `Part2/changes/commits.txt`.

**Status words in `pattern_evalution.csv`:**

| Status | Meaning |
|---|---|
| baseline | the original code |
| preserved | same roles, participants and behaviour (line numbers may move) |
| modified | same roles and participants, but a participant's behaviour or configuration changed |
| extended | a new participant joined the same collaboration |
| newly_introduced | a new collaboration appeared |

`replaced` and `removed` were not needed.

## Measurement rules
- **Counting patterns:**
  - We count GoF design patterns in which at least one class or method of the app takes part.
  - Architecture styles, Django idioms and GRASP principles are described in the report but not counted.
  - One instance is one collaboration.
  - *Concrete participant classes* are the classes in the ConcreteClass / ConcreteStrategy roles.
  - *Unique participant symbols* are the distinct mapped classes, methods and attributes, each counted once.
- **Lines of code (LOC):** lizard NLOC, which means code lines without blank lines and comments.
  - Part 2 scope: `doc_manager/*.py`.
  - Part 3 scope: the production file only, without the test runner.
- **Cyclomatic complexity (CC):** lizard CCN per function. We report the highest one (and the average in Part 2).
  lizard 1.17 does not see JavaScript methods named `get(...)`, so `run_all.py` measures a temporary copy in which
  `get(` is renamed `get_(` (same lines, same branches).
- **Timing (Part 3):**
  - Compile first, then do 1 warm-up run and 5 measured runs on the same PC, and report the median.
  - The time covers the whole test process: start-up, reading the shared test-case file and running all cases.
  - Raw times: `Part3/evidence/timings.csv`.
  - The times mostly show start-up cost and are only comparable on this PC.
- **Working folder** for each Part 3 command is the language folder, e.g. `Part3/strategy_upload_check/java/`.
  `python Part3/run_all.py` (from this folder) runs everything.

## Limitations
- Part 1 covers only the app's own Python code. Patterns inside Django are not counted.
- The admin search box of the original app crashes, because `search_fields = ['file']` names a field that does not
  exist (the field is `file_obj`). We documented this but did not change it (`data/test_result/probe_test.log`).
- Part 3 timings depend on this one PC and include start-up time.

## LLM and AI use
- **Runs:** one recorded run per part with `claude-opus-5-5` (Claude Opus 5.5), through the Claude Code CLI 2.1.287
  (Claude Pro plan), on 2026-10-06 (UTC).
  - The model had no tools. It saw only the saved prompt and input.
  - Saved for each run: the prompt, the input, the raw output, the exact command (`run_info.txt`) and our check of
    every claim (`verification.md`).
  - Summary rows: `Part1/llm.csv`, `Part2/llm.csv`, `Part3/llm/llm.csv`.
- **What the LLM changed in our work:**
  - The Part 1 run found one instance we had missed (Upload Widget Choice). We proved it with a probe test before
    adding it.
  - The Part 2 run warned that Change 2 would make drafts public, so we fixed this.
- **Generated code:** the Part 3 run's code is in `Part3/llm/generated_code/`. We tested it (8/8 programs pass) but did
  not use it as our programs.
- An AI coding assistant (Claude Code) also helped prepare code, scripts and drafts. Every result was run or checked
  against the source code and the tests.
