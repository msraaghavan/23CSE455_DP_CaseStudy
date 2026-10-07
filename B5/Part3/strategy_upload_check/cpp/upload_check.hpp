// Strategy - the "Upload File Checks" from doc_manager, made small.
#pragma once
#include <algorithm>
#include <cctype>
#include <memory>
#include <string>
#include <utility>
#include <vector>

struct Upload {
    std::string name;
    std::string contentType;
    long size;
};

// Strategy: every validator has the same method. "" means "no problem".
class Validator {
public:
    virtual ~Validator() = default;
    virtual std::string check(const Upload& upload) const = 0;
};

// ConcreteStrategy (like Django's FileExtensionValidator).
class ExtensionValidator : public Validator {
public:
    explicit ExtensionValidator(std::vector<std::string> allowed) : allowed_(std::move(allowed)) {}

    std::string check(const Upload& upload) const override {
        std::size_t dot = upload.name.rfind('.');
        std::string extension = dot == std::string::npos ? "" : upload.name.substr(dot + 1);
        for (char& c : extension) {
            c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        }
        if (std::find(allowed_.begin(), allowed_.end(), extension) == allowed_.end()) {
            return "ERROR extension not allowed";
        }
        return "";
    }

private:
    std::vector<std::string> allowed_;
};

// Context (like ContentTypeRestrictedFileField): runs every validator, then its own checks.
class UploadField {
public:
    UploadField(std::vector<std::shared_ptr<Validator>> validators,
                std::vector<std::string> contentTypes, long maxSize)
        : validators_(std::move(validators)), contentTypes_(std::move(contentTypes)), maxSize_(maxSize) {}

    std::string clean(const Upload& upload) const {
        for (const auto& validator : validators_) {
            std::string error = validator->check(upload);
            if (!error.empty()) {
                return error;
            }
        }
        if (std::find(contentTypes_.begin(), contentTypes_.end(), upload.contentType) == contentTypes_.end()) {
            return "ERROR file type not supported";
        }
        if (upload.size > maxSize_) {
            return "ERROR file too big";
        }
        return "OK";
    }

private:
    std::vector<std::shared_ptr<Validator>> validators_;  // the strategies
    std::vector<std::string> contentTypes_;
    long maxSize_;
};

// Client: chooses the strategy (like ContentTypeRestrictedFileField.__init__).
inline UploadField documentField(long maxSize) {
    std::vector<std::shared_ptr<Validator>> validators = {
        std::make_shared<ExtensionValidator>(std::vector<std::string>{"pdf", "html"})};
    return UploadField(validators, {"application/pdf", "text/html"}, maxSize);
}
