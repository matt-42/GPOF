import multiprocessing as mp
import numpy as np
from runset import open_runset
from tempfile import mkstemp
import yaml

def runset_parallel_run_process(rs, params):
    return rs.run_impl(params)

class Runner:
    def __init__(self, to_optimise, filename, run_name = None, nprocesses = 4):
        self.to_optimise = to_optimise
        self.runset = open_runset(filename, run_name)
        self.nprocesses = nprocesses



    def run_impl(self, params):

        # Convert numpy types.
        for k in list(params.keys()):
            a = params[k]
            if type(a).__module__ == np.__name__:
                params[k] = a.item()

        # Check if the paramset has not already run.
        run = self.runset.find_run(params)
        if run:
            return run
        
        # Create the result file.
        _,fn = mkstemp()

        # Run the function.
        self.to_optimise(params, fn)

        # Load the result yaml file.
        f=open(fn, 'r')
        r = yaml.load(f)
 
        # Merge params and result dicts.
        run = params.copy()
        run.update(r)

        return run
        
    def run(self, params):

        run = self.run_impl(params)

        # Record.
        self.runset.record(run)

        return run;
    
    def parallel_run(self, paramsets):
        pool = mp.Pool(self.nprocesses)

        args = [[self, ps] for ps in paramsets]
        runs = pool.map(runset_parallel_run_process, args)

        for r in runs:
            self.runset.record(r)
