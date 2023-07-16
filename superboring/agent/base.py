class BaseAgent(object):
    @property
    def function_specs(self):
        raise NotImplementedError

    @property
    def name(self):
        return self.function_specs.get("name", "")


    def run(self, args):
        raise NotImplementedError
