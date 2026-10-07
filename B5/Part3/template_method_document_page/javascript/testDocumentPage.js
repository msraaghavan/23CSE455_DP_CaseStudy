// Test runner: reads the shared test cases and checks documentPage.js.
const fs = require("fs");
const { DocumentPage } = require("./documentPage");

const path = process.argv[2] || "../../test-cases/document_page_cases.txt";
let passed = 0;
let total = 0;
for (let line of fs.readFileSync(path, "utf8").split("\n")) {
  line = line.trim();
  if (!line || line.startsWith("#")) {
    continue;
  }
  const [method, versionsText, expected] = line.split("|").map((part) => part.trim());
  const versions = [];
  if (versionsText !== "-") {
    for (const item of versionsText.split(",")) {
      const [name, flag] = item.split(":");
      versions.push({ name, published: flag === "yes" });
    }
  }
  const actual = new DocumentPage(versions).dispatch(method);
  total += 1;
  if (actual === expected) {
    passed += 1;
  }
  console.log(`${actual === expected ? "PASS" : "FAIL"} ${method} ${versionsText} -> ${actual}`);
}
console.log(`passed ${passed}/${total}`);
process.exit(total > 0 && passed === total ? 0 : 1);
