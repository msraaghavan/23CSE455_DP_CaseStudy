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
