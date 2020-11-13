class DefaultDict:
    def __init__(self, default):
        self.default = default
        self.dictionary = {}

    def __getitem__(self, item):
        if item not in self.dictionary:
            if callable(self.default):
                self.dictionary[item] = self.default()
            else:
                self.dictionary[item] = self.default
        return self.dictionary[item]

    def as_dict(self):
        return self.dictionary
