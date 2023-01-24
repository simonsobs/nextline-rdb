from nextlinegraphql import spec

class Plugin:

    @spec.hookimpl
    def configure(self):
        pass

