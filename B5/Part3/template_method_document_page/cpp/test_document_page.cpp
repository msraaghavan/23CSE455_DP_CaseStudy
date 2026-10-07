// Test runner: reads the shared test cases and checks document_page.hpp.
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "document_page.hpp"

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
    std::ifstream cases(argc > 1 ? argv[1] : "../../test-cases/document_page_cases.txt");
    std::string line;
    int passed = 0;
    int total = 0;
    while (std::getline(cases, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') {
            continue;
        }
        std::vector<std::string> parts = split(line, '|');
        std::vector<Version> versions;
        if (parts[1] != "-") {
            for (const std::string& item : split(parts[1], ',')) {
                std::vector<std::string> pair = split(item, ':');
                versions.push_back({pair[0], pair[1] == "yes"});
            }
        }
        std::string actual = DocumentPage(versions).dispatch(parts[0]);
        total++;
        if (actual == parts[2]) {
            passed++;
        }
        std::cout << (actual == parts[2] ? "PASS " : "FAIL ") << parts[0] << " " << parts[1] << " -> " << actual << "\n";
    }
    std::cout << "passed " << passed << "/" << total << "\n";
    return total > 0 && passed == total ? 0 : 1;
}
