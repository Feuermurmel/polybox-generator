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


    def omitted(self, polyview):
        fid = str(polyview.face_id)
        F = self._c["polybox"]["faces"]

        if fid in F.keys() and "omitted" in F[fid].keys():
            return F[fid]["omitted"]
        else:
            return False


    def __getitem__(self, polyview):
        eid = str(polyview.edge_id)
        eido = str(polyview.opposite.edge_id)
        D = self._c["polybox"]["default"]["edges"]
        E = self._c["polybox"]["edges"]

        if eid in E.keys():
            T = E[eid]["tenon"]
        elif eido in E.keys():
            T = E[eido]["tenon"]
        elif self.omitted(polyview.adjacent):
            if "tenon_omitted" in D:
                T = D["tenon_omitted"]
            else:
                T = D["tenon"]
        else:
            T = D["tenon"]

        C = T["class"]
        A = T["args"]
        return self._construct_tenon_class(C, A)
