class Scenario:

    def __init__(self, fname):
        self.fname = fname
        self.modules = []
        self._parse(fname)

    def _parse(self, fname):
        with open(fname, "r") as f:
            for line in f.readlines():
                self.modules.append(line)

    def process(self):
        for module_name in self.modules:
            module = __import__(module_name)
            class_ = getattr(module, module_name)
            instance = class_()
