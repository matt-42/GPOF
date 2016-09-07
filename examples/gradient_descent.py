from GPOF.strategies import gradient_descent
from GPOF.runner import command_runner

conf=GradientDescentConfig(
    # Maximum number of iteration
    max_iterations = 100,
    # Starting point of the descent
    starting_point = {
        'param1': 1
        'param2': 12,
        'param3': 4.1,
    },
    # Sampling to explore
    parameters = {
        'param1': numpy.arange(0,5, 1),   # [0,1,2,3,4]
        'param2': 12,
        'param3': [2.3, 4.1, 5.6],
    },
    # Cost function to optimize
    cost = lambda r: r['result2']
)

r = command_runner("./eval %config_file %result_file", "runset.rs")
gradient_descent(r, conf)
