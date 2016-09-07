from GPOF.strategies import grid_sampling
from GPOF.runner import command_runner

conf={
  'param1': numpy.arange(0,5, 1), # [0,1,2,3,4]
  'param2': 12,
  'param3': [2.3, 4.1, 5.6],
}

r = command_runner("./eval %config_file %result_file", "runset.rs")
grid_sampling(r, conf)
