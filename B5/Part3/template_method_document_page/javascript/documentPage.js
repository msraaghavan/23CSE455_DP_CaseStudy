// Template Method - the "Published Document Page" from doc_manager, made small.

// AbstractClass. dispatch() is the fixed recipe (like Django's View.dispatch).
class View {
  dispatch(method) {
    if (method !== "GET") {
      return "405 Method Not Allowed";
    }
    return this.get(); // the step a subclass fills in
  }

  get() {
    throw new Error("a subclass must fill in get()");
  }
}

const CONTENT_TYPES = { pdf: "application/pdf", html: "text/html" };

// ConcreteClass. Fills in get() (like doc_manager's DocumentView.get).
class DocumentPage extends View {
  constructor(versions) {
    super();
    this.versions = versions; // [{ name, published }]
  }

  get() {
    for (const version of this.versions) {
      if (version.published) {
        const extension = version.name.split(".").pop();
        return "200 " + CONTENT_TYPES[extension];
      }
    }
    return "404 Not Found";
  }
}

module.exports = { View, DocumentPage };
