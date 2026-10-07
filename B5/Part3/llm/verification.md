# Part 3 - checking every claim of the LLM run

Run: `run_info.txt` (Claude Opus 5.5, 2026-10-06). Raw answer: `output_raw.json`, text: `output.md`.
How we checked:
- We ran the 8 generated programs without edits against our shared test cases (`generated_code_test.log`).
- We wrote a small probe for the compile-time / run-time claim (`missing_method_probe.log`).
- We compared the expected sizes and times with our own measurements (`pattern_crosslanguage.csv`).

| # | LLM claim | Our verdict | Evidence and correction |
|---|---|---|---|
| 1 | The 8 generated programs solve both problems in all 4 languages | **Correct** | All 8 compile and pass: 7/7 (Template Method) and 8/8 (Strategy) in Java, Python, JavaScript and C++ (`generated_code_test.log`). |
| 2 | Java: `abstract class View` with `abstract get()`; `dispatch` can be `final` | **Correct** | Same as our `DocumentPage.java`. |
| 3 | Python: `ABC` + `@abstractmethod`; `dispatch` cannot be made final | **Correct** | Python has no enforced `final`. (`typing.final` is only a hint for type checkers.) Our snippet uses the simpler `NotImplementedError`. |
| 4 | JavaScript: an ordinary class whose `get()` throws; no `final` | **Correct** | Same as our `documentPage.js`. |
| 5 | C++: pure virtual `get() = 0`; a non-virtual `dispatch` | **Correct** | Same as our `document_page.hpp`. |
| 6 | A missing method is found at compile time in Java and C++, at run time in Python and JavaScript | **Correct** | `missing_method_probe.log`: javac and clang stop with an error. Python fails when the object is created (ABC version) or only when `dispatch()` runs (our plain version). JavaScript fails only when `get()` is called. |
| 7 | Strategy: an explicit interface or abstract class in Java and C++; duck typing in Python and JavaScript | **Correct** | Same structure as our snippets (see the table in the report). |
| 8 | Code length: Python shortest, C++ longest | **Correct** | Our LOC: Template Method Python 20 < JavaScript 28 < Java 30 < C++ 38. Strategy Python 31 < JavaScript 40 < Java 51 < C++ 63. |
| 9 | Start-up times: Java about 0.3-1 s, Python 30-60 ms, JavaScript 40-80 ms, C++ a few ms (the LLM called these "expectations, not measurements") | **Partially correct** | The order is right: C++ fastest, Java slowest. Our medians (Template Method / Strategy): Java 202/225 ms (lower than expected, because we compile first instead of using source-file mode), Python 73/79 ms (higher), JavaScript 80/79 ms (at the top of the range) and C++ 13/13 ms (higher; on Windows, starting any process costs about 10 ms). |

**Summary:** 9 claims: 8 correct, 1 partially correct, 0 incorrect, 0 cannot confirm.
**Generated code:** kept in `generated_code/` only as evidence. It was tested (8/8 programs pass), but it is **not** used as
our snippets. Our own snippets in `Part3/<problem>/<language>/` were written separately and kept smaller, with
production code and test runner in separate files as the instructions ask.
Reviewer: team B5. Every verdict points to a log or to `pattern_crosslanguage.csv`.
