"""Template Method - the "Published Document Page" from doc_manager, made small."""


class View:
    """AbstractClass. dispatch() is the fixed recipe (like Django's View.dispatch)."""

    def dispatch(self, method):
        if method != "GET":
            return "405 Method Not Allowed"
        return self.get()  # the step a subclass fills in

    def get(self):
        raise NotImplementedError


class DocumentPage(View):
    """ConcreteClass. Fills in get() (like doc_manager's DocumentView.get)."""

    CONTENT_TYPES = {"pdf": "application/pdf", "html": "text/html"}

    def __init__(self, versions):
        self.versions = versions  # list of (file name, published?)

    def get(self):
        for name, published in self.versions:
            if published:
                extension = name.rsplit(".", 1)[-1]
                return "200 " + self.CONTENT_TYPES[extension]
        return "404 Not Found"
