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
