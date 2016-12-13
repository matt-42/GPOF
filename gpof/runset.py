import os.path
import json

class RunSetView:
    def __init__(self, col_names, data):
        self.col_names = col_names
        self.data = data

class RunSet:
    def __init__(self):
        self.runs = []
        self.cache = dict()

    def close(self):
        if hasattr(self, 'file'):
            self.file.close()
            self.file = None

    def __del__(self):
        self.close()

    def col(self, name):
        if len(self.runs) == 0:
            return []

        return [r[name] for r in self.runs]

    def view(self, cols, filter = lambda x : True):
        rs = []
        for r in self.runs:
            if filter(r):
                row = []
                for col in cols:
                    if isinstance(col, str):
                        row.append(r[col])
                    elif callable(col):
                        row.append(col(r))
                    else:
                        raise "RunSet::view error: cols can only be str or callable."
                    
                rs.append(row)

        
        return RunSetView(cols, sorted(rs, key=lambda x : x[0]))

    def add_run(self, r):
        self.runs.append(r)

    def record(self, r):
        if hasattr(self, 'file') and self.file is not None:
            json.dump(r, self.file, sort_keys=True)
            self.file.write("\n")
            self.file.flush()
        self.runs.append(r);
        
    def find_run(self, p):
        for r in self.runs:
            found = True
            for k in list(p.keys()):
                if isinstance(p[k], str):
                    found = found and p[k] == r[k]
                else:
                    found = found and abs(p[k] - r[k]) < 0.00001
            if found:
                return r
        return None

def select_best_run(runset, cost):
    min_cost = cost(runset.runs[0])
    best_run = runset.runs[0]
    for r in runset.runs:
        c = cost(r)
        if c < min_cost:
            best_run = r
            min_cost = c
    return r

# Open a runset
# Create it if it does not exists yet.
def open_runset(filename = None):

    if filename is not None and os.path.exists(filename) and not os.path.isfile(filename):
        raise Exception("%s exists but it is not a file." % filename)
    
    rs = RunSet()

    # Creation of a in memory only runset (not saved in a file)
    if not filename:
        return rs

    # Creation of a file runset
    elif not os.path.exists(filename):
        rs.file=open(filename, 'w')
        return rs

    # Open an existing runset
    else:
        f = open(filename, 'r+')
        rs.file = f
        runs_str = f.read()
        decoder = json.JSONDecoder();
        runs_str = runs_str.lstrip()
        while len(runs_str) != 0:
            obj, idx = decoder.raw_decode(runs_str);
            rs.add_run(obj)
            runs_str = runs_str[idx:].lstrip();
    
    return rs;

def open_runset_from_google_benchmark(filename):
    f = open(filename, 'r+')
    results = json.load(f)['benchmarks']
    sets = {}
    for r in results:
        name = r['name'].split('/')[0]

        if not name in sets:
            sets.update({name: RunSet()})
        run = {}
        params = r['name'].split('/')

        run['real_time'] = r['real_time']
        run['cpu_time'] = r['cpu_time']
        if len(params) >= 2:
            run['range_x'] = float(params[1])
        if len(params) >= 3:
            run['range_y'] = float(params[2])

        sets[name].add_run(run)
    return sets
