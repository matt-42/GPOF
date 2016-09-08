import multiprocessing as mp
import numpy as np
from tempfile import NamedTemporaryFile
import subprocess as sbp
import os

from GPOF.runset import open_runset
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
        
        # Run the function.
        r = self.to_optimise(params)

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

class cmd_runner_functor:

    def __init__(self, cmd):
        self.cmd = cmd
    def __call__(self, params):

        # Write the parameters file
        paramfile = NamedTemporaryFile(mode="w", delete=False)
        for k in list(params.keys()):
            paramfile.write("%s = %s\n" % (k, params[k]))
        paramfile.close()

        # Run the evaluation
        resultfile = NamedTemporaryFile(delete=False)
        resultfile.close()

        cmd_str = self.cmd.replace("%config_file", paramfile.name).replace("%result_file", resultfile.name)
        sbp.call(cmd_str, shell=True)

        # Parse the result file
        resultfile = open(resultfile.name, 'r')
        res = yaml.load(resultfile)
        os.remove(resultfile.name)
        os.remove(paramfile.name)
        return res

def command_runner(cmd, runset_file):
    return Runner(cmd_runner_functor(cmd), runset_file)
