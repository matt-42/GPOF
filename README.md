# GPOF - Generic Parameter Optimization Framework.

**Depends on:** Python, Matplotlib

GPOF is a set of tools that help understanding the parameters/output
space of any algorithm or anything taking a key->value map of
parameters and outputing a key->value map.

For now, there two ways of exploring the parameter space: The Grid
sampling of the parameter space of the gradient descent, finding the
local minimum of a user defined cost function.

Given a runable "./experiment" taking the config file path and the
output file path as command line arguments, the following examples
show how to use the project.

## Grid sampling

```python
runner = gpof.command_runner("results.rs",
                             "./experiment %config_file %result_file");
space={
  'param1': numpy.arange(0,5, 1), # [0,1,2,3,4]
  'param2': 12,
  'param3': [2.3, 4.1, 5.6],
}

gpof.grid_sampling(runner, space);

# Display a 2D projection of the space.
gpof.display_2d_points(runner.view(('param1', 'result')))
```

## Gradient descent

```python
conf=gpof.GradientDescentConfig(
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
    cost = lambda r: r['resultX']
)

r = gpof.command_runner("./eval %config_file %result_file", "runset.rs")
gpof.gradient_descent(r, conf)
```
