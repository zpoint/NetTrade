from .JSLGetter import JSLGetter

getter_map = {
    "jsl": JSLGetter
}

class GetterFactory(object):
    def create_getter(self, source="jsl"):
        if source not in getter_map:
            raise NotImplementedError("date getter: %s not Implemented" % (source, ))
        return getter_map[source]()
