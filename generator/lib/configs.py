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
        fid = polyview.face_id
        F = self._c["polybox"]["faces"]
        if str(fid) in F.keys() and F[str(fid)]["omitted"]:
            return True
        else:
            return False


    def __getitem__(self, polyview):
        eid = polyview.edge_id
        eido = polyview.opposite.edge_id

        D = self._c["polybox"]["default"]["edges"]
        E = self._c["polybox"]["edges"]

        if str(eid) in E.keys():
            T = E[str(eid)]["tenon"]
        elif str(eido) in E.keys():
            T = E[str(eido)]["tenon"]
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
