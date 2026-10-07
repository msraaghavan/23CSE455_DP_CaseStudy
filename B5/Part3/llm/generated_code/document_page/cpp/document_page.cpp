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
