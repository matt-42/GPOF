import os.path
import json

class RunSet:
    def __init__(self):
        self.runs = []
        self.cache = dict()

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def __del__(self):
        self.close()

    def col(self, name):
        if len(self.runs) == 0:
            return []

        return [r[name] for r in self.runs]

    def add_run(self, r):
        self.runs.append(r)

    def record(self, r):
        json.dump(r, self.file, sort_keys=True)
        self.file.write("\n")
        self.file.flush()
        self.runs.append(r);

    def find_run(self, p):
        for r in self.runs:
            found = True
            for k in list(p.keys()):
                found = found and abs(p[k] - r[k]) < 0.00001
            if found:
                return r
        return None

# Open a runset
# Create it if it does not exists yet.
# Pass Name = None if the runset already exists.
def open_runset(filename, name = None):

    if os.path.exists(filename) and not os.path.isfile(filename):
        raise Exception("%s exists but it is not a file." % filename)
    
    if name is not None or not os.path.exists(filename):
        # Creation
        if not os.path.exists(filename):
            f = open(filename, 'w')
            f.write("%s\n" % name)
            f.close()
        # It now  exists, recall the function with name = none
        return open_runset(filename, None)

    else:
        # Open an existing runset
        if not os.path.exists(filename):
            raise Exception("Runset file %s does not exists" % filename)
        f = open(filename, 'r+')

        rs = RunSet()
        rs.name = f.readline().rstrip()
        rs.file = f
        runs_str = f.read()
        decoder = json.JSONDecoder();
        runs_str = runs_str.lstrip()
        while len(runs_str) != 0:
            obj, idx = decoder.raw_decode(runs_str);
            rs.add_run(obj)
            runs_str = runs_str[idx:].lstrip();
    
    return rs;
