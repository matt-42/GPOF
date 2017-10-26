import json,sys

class LinearizedDictKey:
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "/".join(self.path)

    def __lt__(self, other):
        return str(self) < str(other)
    
class LinearizedDict:

    def __init__(self, parameters):
        self.root = parameters;
        self.allkeys = []
        self.index(parameters, [])

    def index(self, parameters, path):
        for k in sorted(parameters.keys()):
            if type(parameters[k]) is dict:
                self.index(parameters[k], path + [k])
            else:
                self.allkeys += [LinearizedDictKey(path + [k])]

    def keys(self):
        return self.allkeys;
    
    def __getitem__(self, k):
        cur = self.root;
        for i in k.path:
            cur = cur[i]
        return cur;

def linearized_to_deep_dict(d):
    res = {}
    for k in d.keys():
        if type(k) is LinearizedDictKey:
            x = res;
            for i in k.path[0:-1]:
                x = x.setdefault(i, {})
            x[k.path[-1]] = d[k]                
        else:
            res[k] = d[k]
    return res
