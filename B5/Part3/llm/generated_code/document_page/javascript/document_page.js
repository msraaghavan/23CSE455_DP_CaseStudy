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
