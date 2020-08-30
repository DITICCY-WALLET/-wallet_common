class CodeStatus(dict):
    def __init__(self, **kwargs):
        self.d = {}
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            self.d[k] = v

    def __getitem__(self, item):
        return self[item]

    def __setitem__(self, key, value):
        self.d[key] = value
        setattr(self, key, value)



