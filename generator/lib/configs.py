import re, json
from lib import tenon


def load_from_json(path):
    with open(path, encoding = 'utf-8') as file:
        lines = file.readlines()
        # Filter comments
        lines = filter(lambda l: not re.match("^\s*//.*$", l), lines)

    data = ''.join(lines)
    configuration = json.loads(data)

    return PolyBoxConfig(configuration)


class PolyBoxConfig():

    def __init__(self, configuration):
        self._c = configuration


    def _construct_tenon_class(self, classname, arguments):
        T = getattr(tenon, classname)
        return T(**arguments)


    def __getitem__(self, edge_id):

        E = self._c["polybox"]["edges"]

        if str(edge_id) in E.keys():
            T = E[str(edge_id)]["tenon"]
        else:
            T = self._c["polybox"]["default"]["edges"]["tenon"]

        C = T["class"]
        A = T["args"]
        return self._construct_tenon_class(C, A)
