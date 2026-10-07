// Test runner: reads the shared test cases and checks uploadCheck.js.
const fs = require("fs");
const { documentField } = require("./uploadCheck");

const path = process.argv[2] || "../../test-cases/upload_check_cases.txt";
let passed = 0;
let total = 0;
for (let line of fs.readFileSync(path, "utf8").split("\n")) {
  line = line.trim();
  if (!line || line.startsWith("#")) {
    continue;
  }
  const [name, contentType, size, maxSize, expected] = line.split("|").map((part) => part.trim());
  const actual = documentField(Number(maxSize)).clean({ name, contentType, size: Number(size) });
  total += 1;
  if (actual === expected) {
    passed += 1;
  }
  console.log(`${actual === expected ? "PASS" : "FAIL"} ${name} ${contentType} ${size} -> ${actual}`);
}
console.log(`passed ${passed}/${total}`);
process.exit(total > 0 && passed === total ? 0 : 1);
