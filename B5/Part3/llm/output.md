Each program takes the cases file as its only argument. For each case it prints `PASS case N: ...` or `FAIL case N: expected '...', got '...'`. The last line is `passed X/Y`. The exit code is 0 only if all cases passed, 1 if any case failed, and 2 for a missing or unreadable file (where the language checks for this). I wrote these programs but have not compiled or run them; I only traced them by hand against the 15 cases.

---

## Problem 1: Template Method (`View` / `DocumentPage`)

FILE: document_page/java/DocumentPageTest.java
```java
import java.nio.file.*;
import java.util.*;

record Version(String name, boolean published) {}

abstract class View {                                   // AbstractClass
    public final String dispatch(String method) {       // fixed recipe, cannot be overridden
        if (!method.equals("GET")) return "405 Method Not Allowed";
        return get();
    }
    protected abstract String get();                    // the step
}

class DocumentPage extends View {                       // ConcreteClass
    private static final Map<String, String> TYPES = Map.of("pdf", "application/pdf", "html", "text/html");
    private final List<Version> versions;
    DocumentPage(List<Version> versions) { this.versions = versions; }

    @Override protected String get() {
        for (Version v : versions)
            if (v.published()) {
                int i = v.name().lastIndexOf('.');
                String ext = i < 0 ? "" : v.name().substring(i + 1).toLowerCase(Locale.ROOT);
                return "200 " + TYPES.get(ext);
            }
        return "404 Not Found";
    }
}

public class DocumentPageTest {
    public static void main(String[] args) throws Exception {
        if (args.length < 1) { System.err.println("usage: java DocumentPageTest <cases file>"); System.exit(2); }
        int passed = 0, total = 0;
        for (String raw : Files.readAllLines(Path.of(args[0]))) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = line.split("\\|");
            String method = f[0].trim(), list = f[1].trim(), expected = f[2].trim();
            List<Version> versions = new ArrayList<>();
            if (!list.equals("-"))
                for (String item : list.split(",")) {
                    String[] p = item.trim().split(":");
                    versions.add(new Version(p[0].trim(), p[1].trim().equals("yes")));
                }
            String actual = new DocumentPage(versions).dispatch(method);
            total++;
            if (actual.equals(expected)) { passed++; System.out.println("PASS case " + total + ": " + actual); }
            else System.out.println("FAIL case " + total + ": expected '" + expected + "', got '" + actual + "'");
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(passed == total ? 0 : 1);
    }
}
```

FILE: document_page/python/document_page.py
```python
import sys
from abc import ABC, abstractmethod

CONTENT_TYPES = {"pdf": "application/pdf", "html": "text/html"}


def extension(name):
    _, dot, ext = name.rpartition(".")
    return ext.lower() if dot else ""


class View(ABC):                                  # AbstractClass
    def dispatch(self, method):                   # fixed recipe
        if method != "GET":
            return "405 Method Not Allowed"
        return self.get()

    @abstractmethod
    def get(self):                                # the step
        ...


class DocumentPage(View):                         # ConcreteClass
    def __init__(self, versions):
        self.versions = versions                  # list of (name, published)

    def get(self):
        for name, published in self.versions:
            if published:
                return "200 " + CONTENT_TYPES[extension(name)]
        return "404 Not Found"


def parse_versions(text):
    if text == "-":
        return []
    return [(n.strip(), p.strip() == "yes") for n, p in (i.rsplit(":", 1) for i in text.split(","))]


def main(path):
    passed = total = 0
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            method, versions, expected = (x.strip() for x in line.split("|"))
            actual = DocumentPage(parse_versions(versions)).dispatch(method)
            total += 1
            if actual == expected:
                passed += 1
                print(f"PASS case {total}: {actual}")
            else:
                print(f"FAIL case {total}: expected '{expected}', got '{actual}'")
    print(f"passed {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python document_page.py <cases file>")
    sys.exit(main(sys.argv[1]))
```

FILE: document_page/javascript/document_page.js
```javascript
"use strict";
const fs = require("fs");

const CONTENT_TYPES = { pdf: "application/pdf", html: "text/html" };
const extension = (name) => {
  const i = name.lastIndexOf(".");
  return i < 0 ? "" : name.slice(i + 1).toLowerCase();
};

class View {                                            // AbstractClass (by convention)
  dispatch(method) {                                    // fixed recipe
    if (method !== "GET") return "405 Method Not Allowed";
    return this.get();
  }
  get() { throw new Error(`${this.constructor.name} must implement get()`); } // the step
}

class DocumentPage extends View {                       // ConcreteClass
  constructor(versions) { super(); this.versions = versions; } // [{name, published}]
  get() {
    const v = this.versions.find((x) => x.published);
    return v ? "200 " + CONTENT_TYPES[extension(v.name)] : "404 Not Found";
  }
}

function main(path) {
  let passed = 0, total = 0;
  for (const raw of fs.readFileSync(path, "utf8").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const [method, list, expected] = line.split("|").map((s) => s.trim());
    const versions = list === "-" ? [] : list.split(",").map((item) => {
      const [name, flag] = item.split(":").map((s) => s.trim());
      return { name, published: flag === "yes" };
    });
    const actual = new DocumentPage(versions).dispatch(method);
    total++;
    if (actual === expected) { passed++; console.log(`PASS case ${total}: ${actual}`); }
    else console.log(`FAIL case ${total}: expected '${expected}', got '${actual}'`);
  }
  console.log(`passed ${passed}/${total}`);
  return passed === total ? 0 : 1;
}

if (process.argv.length < 3) { console.error("usage: node document_page.js <cases file>"); process.exit(2); }
process.exitCode = main(process.argv[2]);
```

FILE: document_page/cpp/document_page.cpp
```cpp
#include <cctype>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

static std::string trim(const std::string& s) {
    auto b = s.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) return "";
    return s.substr(b, s.find_last_not_of(" \t\r\n") - b + 1);
}
static std::vector<std::string> split(const std::string& s, char sep) {
    std::vector<std::string> out; std::stringstream ss(s); std::string part;
    while (std::getline(ss, part, sep)) out.push_back(trim(part));
    return out;
}
static std::string extension(const std::string& name) {
    auto i = name.rfind('.');
    if (i == std::string::npos) return "";
    std::string ext = name.substr(i + 1);
    for (auto& c : ext) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return ext;
}

struct Version { std::string name; bool published; };

class View {                                             // AbstractClass
public:
    virtual ~View() = default;
    std::string dispatch(const std::string& method) {    // fixed recipe (non-virtual)
        if (method != "GET") return "405 Method Not Allowed";
        return get();
    }
protected:
    virtual std::string get() = 0;                       // the step (pure virtual)
};

class DocumentPage : public View {                       // ConcreteClass
public:
    explicit DocumentPage(std::vector<Version> v) : versions_(std::move(v)) {}
protected:
    std::string get() override {
        static const std::map<std::string, std::string> types{{"pdf", "application/pdf"}, {"html", "text/html"}};
        for (const auto& v : versions_)
            if (v.published) return "200 " + types.at(extension(v.name));
        return "404 Not Found";
    }
private:
    std::vector<Version> versions_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) { std::cerr << "usage: document_page <cases file>\n"; return 2; }
    std::ifstream in(argv[1]);
    if (!in) { std::cerr << "cannot open " << argv[1] << "\n"; return 2; }
    int passed = 0, total = 0;
    std::string line;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') continue;
        auto f = split(line, '|');
        std::vector<Version> versions;
        if (f[1] != "-")
            for (const auto& item : split(f[1], ',')) {
                auto p = split(item, ':');
                versions.push_back({p[0], p[1] == "yes"});
            }
        std::string actual = DocumentPage(versions).dispatch(f[0]);
        ++total;
        if (actual == f[2]) { ++passed; std::cout << "PASS case " << total << ": " << actual << "\n"; }
        else std::cout << "FAIL case " << total << ": expected '" << f[2] << "', got '" << actual << "'\n";
    }
    std::cout << "passed " << passed << "/" << total << "\n";
    return passed == total ? 0 : 1;
}
```

---

## Problem 2: Strategy (`Validator` / `ExtensionValidator` / `UploadField` / `documentField`)

FILE: upload_check/java/UploadCheckTest.java
```java
import java.nio.file.*;
import java.util.*;

record Upload(String name, String contentType, long size) {}

interface Validator {                                    // Strategy
    String check(Upload upload);                         // error text, or null = no error
}

class ExtensionValidator implements Validator {          // ConcreteStrategy
    private final List<String> allowed;
    ExtensionValidator(List<String> allowed) { this.allowed = allowed; }
    @Override public String check(Upload u) {
        int i = u.name().lastIndexOf('.');
        String ext = i < 0 ? "" : u.name().substring(i + 1).toLowerCase(Locale.ROOT);
        return allowed.contains(ext) ? null : "ERROR extension not allowed";
    }
}

class UploadField {                                      // Context
    private static final List<String> TYPES = List.of("application/pdf", "text/html");
    private final List<Validator> validators;
    private final long maxSize;
    UploadField(List<Validator> validators, long maxSize) { this.validators = validators; this.maxSize = maxSize; }

    String clean(Upload u) {
        for (Validator v : validators) { String e = v.check(u); if (e != null) return e; }
        if (!TYPES.contains(u.contentType())) return "ERROR file type not supported";
        if (u.size() > maxSize) return "ERROR file too big";
        return "OK";
    }
}

public class UploadCheckTest {
    static UploadField documentField(long maxSize) {     // Client
        return new UploadField(List.of(new ExtensionValidator(List.of("pdf", "html"))), maxSize);
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 1) { System.err.println("usage: java UploadCheckTest <cases file>"); System.exit(2); }
        int passed = 0, total = 0;
        for (String raw : Files.readAllLines(Path.of(args[0]))) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = Arrays.stream(line.split("\\|")).map(String::trim).toArray(String[]::new);
            Upload upload = new Upload(f[0], f[1], Long.parseLong(f[2]));
            String actual = documentField(Long.parseLong(f[3])).clean(upload), expected = f[4];
            total++;
            if (actual.equals(expected)) { passed++; System.out.println("PASS case " + total + ": " + actual); }
            else System.out.println("FAIL case " + total + ": expected '" + expected + "', got '" + actual + "'");
        }
        System.out.println("passed " + passed + "/" + total);
        System.exit(passed == total ? 0 : 1);
    }
}
```

FILE: upload_check/python/upload_check.py
```python
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Upload:
    name: str
    content_type: str
    size: int


def extension(name):
    _, dot, ext = name.rpartition(".")
    return ext.lower() if dot else ""


# Strategy: not declared - any object with check(upload) -> str | None works (duck typing)

class ExtensionValidator:                         # ConcreteStrategy
    def __init__(self, allowed):
        self.allowed = allowed

    def check(self, upload):
        return None if extension(upload.name) in self.allowed else "ERROR extension not allowed"


class UploadField:                                # Context
    CONTENT_TYPES = ("application/pdf", "text/html")

    def __init__(self, validators, max_size):
        self.validators = validators
        self.max_size = max_size

    def clean(self, upload):
        for validator in self.validators:
            error = validator.check(upload)
            if error:
                return error
        if upload.content_type not in self.CONTENT_TYPES:
            return "ERROR file type not supported"
        if upload.size > self.max_size:
            return "ERROR file too big"
        return "OK"


def document_field(max_size):                     # Client
    return UploadField([ExtensionValidator(["pdf", "html"])], max_size)


def main(path):
    passed = total = 0
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, ctype, size, max_size, expected = (x.strip() for x in line.split("|"))
            actual = document_field(int(max_size)).clean(Upload(name, ctype, int(size)))
            total += 1
            if actual == expected:
                passed += 1
                print(f"PASS case {total}: {actual}")
            else:
                print(f"FAIL case {total}: expected '{expected}', got '{actual}'")
    print(f"passed {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python upload_check.py <cases file>")
    sys.exit(main(sys.argv[1]))
```

FILE: upload_check/javascript/upload_check.js
```javascript
"use strict";
const fs = require("fs");

const extension = (name) => {
  const i = name.lastIndexOf(".");
  return i < 0 ? "" : name.slice(i + 1).toLowerCase();
};

// Strategy: not declared - any object with check(upload) -> string | null works (duck typing)

class ExtensionValidator {                              // ConcreteStrategy
  constructor(allowed) { this.allowed = allowed; }
  check(upload) { return this.allowed.includes(extension(upload.name)) ? null : "ERROR extension not allowed"; }
}

class UploadField {                                     // Context
  constructor(validators, maxSize) { this.validators = validators; this.maxSize = maxSize; }
  clean(upload) {
    for (const v of this.validators) { const error = v.check(upload); if (error) return error; }
    if (!["application/pdf", "text/html"].includes(upload.contentType)) return "ERROR file type not supported";
    if (upload.size > this.maxSize) return "ERROR file too big";
    return "OK";
  }
}

const documentField = (maxSize) => new UploadField([new ExtensionValidator(["pdf", "html"])], maxSize); // Client

function main(path) {
  let passed = 0, total = 0;
  for (const raw of fs.readFileSync(path, "utf8").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const [name, contentType, size, maxSize, expected] = line.split("|").map((s) => s.trim());
    const actual = documentField(Number(maxSize)).clean({ name, contentType, size: Number(size) });
    total++;
    if (actual === expected) { passed++; console.log(`PASS case ${total}: ${actual}`); }
    else console.log(`FAIL case ${total}: expected '${expected}', got '${actual}'`);
  }
  console.log(`passed ${passed}/${total}`);
  return passed === total ? 0 : 1;
}

if (process.argv.length < 3) { console.error("usage: node upload_check.js <cases file>"); process.exit(2); }
process.exitCode = main(process.argv[2]);
```

FILE: upload_check/cpp/upload_check.cpp
```cpp
#include <algorithm>
#include <cctype>
#include <fstream>
#include <iostream>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

static std::string trim(const std::string& s) {
    auto b = s.find_first_not_of(" \t\r\n");
    if (b == std::string::npos) return "";
    return s.substr(b, s.find_last_not_of(" \t\r\n") - b + 1);
}
static std::vector<std::string> split(const std::string& s, char sep) {
    std::vector<std::string> out; std::stringstream ss(s); std::string part;
    while (std::getline(ss, part, sep)) out.push_back(trim(part));
    return out;
}
static std::string extension(const std::string& name) {
    auto i = name.rfind('.');
    if (i == std::string::npos) return "";
    std::string ext = name.substr(i + 1);
    for (auto& c : ext) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    return ext;
}

struct Upload { std::string name, contentType; long long size; };

class Validator {                                        // Strategy
public:
    virtual ~Validator() = default;
    virtual std::optional<std::string> check(const Upload& upload) const = 0;
};

class ExtensionValidator : public Validator {            // ConcreteStrategy
public:
    explicit ExtensionValidator(std::vector<std::string> allowed) : allowed_(std::move(allowed)) {}
    std::optional<std::string> check(const Upload& u) const override {
        if (std::find(allowed_.begin(), allowed_.end(), extension(u.name)) != allowed_.end()) return std::nullopt;
        return "ERROR extension not allowed";
    }
private:
    std::vector<std::string> allowed_;
};

class UploadField {                                      // Context
public:
    UploadField(std::vector<std::unique_ptr<Validator>> v, long long maxSize)
        : validators_(std::move(v)), maxSize_(maxSize) {}
    std::string clean(const Upload& u) const {
        for (const auto& v : validators_)
            if (auto error = v->check(u)) return *error;
        if (u.contentType != "application/pdf" && u.contentType != "text/html") return "ERROR file type not supported";
        if (u.size > maxSize_) return "ERROR file too big";
        return "OK";
    }
private:
    std::vector<std::unique_ptr<Validator>> validators_;
    long long maxSize_;
};

UploadField documentField(long long maxSize) {           // Client
    std::vector<std::unique_ptr<Validator>> v;
    v.push_back(std::make_unique<ExtensionValidator>(std::vector<std::string>{"pdf", "html"}));
    return UploadField(std::move(v), maxSize);
}

int main(int argc, char* argv[]) {
    if (argc < 2) { std::cerr << "usage: upload_check <cases file>\n"; return 2; }
    std::ifstream in(argv[1]);
    if (!in) { std::cerr << "cannot open " << argv[1] << "\n"; return 2; }
    int passed = 0, total = 0;
    std::string line;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') continue;
        auto f = split(line, '|');
        std::string actual = documentField(std::stoll(f[3])).clean({f[0], f[1], std::stoll(f[2])});
        ++total;
        if (actual == f[4]) { ++passed; std::cout << "PASS case " << total << ": " << actual << "\n"; }
        else std::cout << "FAIL case " << total << ": expected '" << f[4] << "', got '" << actual << "'\n";
    }
    std::cout << "passed " << passed << "/" << total << "\n";
    return passed == total ? 0 : 1;
}
```

**How to run** (from the folder that holds the case files, Java 17+ needed for `record`):
`java document_page/java/DocumentPageTest.java document_page_cases.txt` ·
`python document_page/python/document_page.py document_page_cases.txt` ·
`node document_page/javascript/document_page.js document_page_cases.txt` ·
`g++ -std=c++17 -o dp document_page/cpp/document_page.cpp && ./dp document_page_cases.txt`
(and the same for `upload_check`).

---

## Comparison

| | Java | Python | JavaScript (Node.js) | C++17 |
|---|---|---|---|---|
| **AbstractClass `View`** | `abstract class` + `protected abstract get()`; `dispatch` is `final` | `ABC` + `@abstractmethod get()`; `dispatch` cannot be made final | Ordinary class; `get()` throws an error ("abstract" only by convention); `dispatch` cannot be made final | Class with pure virtual `get() = 0`; `dispatch` is non-virtual |
| **Strategy `Validator`** | `interface Validator`; "no error" is `null` | Not declared; duck typing; "no error" is `None` | Not declared; duck typing; "no error" is `null` | Abstract class with pure virtual `check`; "no error" is `std::optional` (`nullopt`); held by `unique_ptr` |
| **Missing method found** | Compile time: a subclass that is not `abstract` must implement `get()` / `check()` | Run time: `View` subclass fails when the object is created (`TypeError`); a missing `check` fails only when it is called (`AttributeError`) | Run time: only when the method is called (thrown `Error` / `TypeError: v.check is not a function`) | Compile time: an object of a class with an unimplemented pure virtual function cannot be created |
| **Other expected difference** | Medium length; JVM start-up is the slowest (about 0.3–1 s with source-file mode, which also compiles) | Shortest code; start-up about 30–60 ms | Short code; start-up about 40–80 ms | Longest code (hand-written `trim`/`split`, ownership via `unique_ptr`); needs a separate compile step but runs as a native binary with the fastest start-up (a few ms) |

The timings are typical expectations, not measurements. For only 7–8 test cases, start-up time dominates the total runtime.