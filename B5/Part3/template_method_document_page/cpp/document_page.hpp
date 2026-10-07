// Template Method - the "Published Document Page" from doc_manager, made small.
#pragma once
#include <map>
#include <string>
#include <utility>
#include <vector>

// One saved version of the document.
struct Version {
    std::string name;
    bool published;
};

// AbstractClass. dispatch() is the fixed recipe (like Django's View.dispatch).
class View {
public:
    virtual ~View() = default;

    std::string dispatch(const std::string& method) const {
        if (method != "GET") {
            return "405 Method Not Allowed";
        }
        return get();  // the step a subclass fills in
    }

protected:
    virtual std::string get() const = 0;
};

// ConcreteClass. Fills in get() (like doc_manager's DocumentView.get).
class DocumentPage : public View {
public:
    explicit DocumentPage(std::vector<Version> versions) : versions_(std::move(versions)) {}

protected:
    std::string get() const override {
        static const std::map<std::string, std::string> contentTypes = {
            {"pdf", "application/pdf"}, {"html", "text/html"}};
        for (const Version& version : versions_) {
            if (version.published) {
                std::string extension = version.name.substr(version.name.rfind('.') + 1);
                return "200 " + contentTypes.at(extension);
            }
        }
        return "404 Not Found";
    }

private:
    std::vector<Version> versions_;
};
