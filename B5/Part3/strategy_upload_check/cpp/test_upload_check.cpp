// Test runner: reads the shared test cases and checks upload_check.hpp.
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "upload_check.hpp"

static std::string trim(const std::string& text) {
    std::size_t first = text.find_first_not_of(" \t\r");
    std::size_t last = text.find_last_not_of(" \t\r");
    return first == std::string::npos ? "" : text.substr(first, last - first + 1);
}

static std::vector<std::string> split(const std::string& text, char separator) {
    std::vector<std::string> parts;
    std::stringstream stream(text);
    std::string item;
    while (std::getline(stream, item, separator)) {
        parts.push_back(trim(item));
    }
    return parts;
}

int main(int argc, char** argv) {
    std::ifstream cases(argc > 1 ? argv[1] : "../../test-cases/upload_check_cases.txt");
    std::string line;
    int passed = 0;
    int total = 0;
    while (std::getline(cases, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') {
            continue;
        }
        std::vector<std::string> p = split(line, '|');
        Upload upload{p[0], p[1], std::stol(p[2])};
        std::string actual = documentField(std::stol(p[3])).clean(upload);
        total++;
        if (actual == p[4]) {
            passed++;
        }
        std::cout << (actual == p[4] ? "PASS " : "FAIL ") << p[0] << " " << p[1] << " " << p[2] << " -> " << actual << "\n";
    }
    std::cout << "passed " << passed << "/" << total << "\n";
    return total > 0 && passed == total ? 0 : 1;
}
