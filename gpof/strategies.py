import copy
import sys
import numpy as np
from gpof.linearized_dict import LinearizedDict, LinearizedDictKey, linearized_to_deep_dict

from gpof.runner import Runner
from gpof.runner import cmd_runner_functor

# Hold a parameter range and a value.
class RV:
    def __init__(self, value, range):
        self.value = value
        self.range = range

def grid_sampling_rec(runner, params, params_keys, params_to_run, d):

    if d == len(params_keys):
        runner.run(params_to_run)
    else:
        k=params_keys[d]
        p=params[k]
        if isinstance(p, (np.ndarray, list)):
            for i in p:
                params_to_run[k]=i
                grid_sampling_rec(runner, params, params_keys, copy.deepcopy(params_to_run), d + 1);
        else:
            params_to_run[k]=params[k]
            grid_sampling_rec(runner, params, params_keys, copy.deepcopy(params_to_run), d + 1);

def grid_sampling(runner, config):
    # build the initial paramset
    paramset = dict()
    for k in list(config.keys()):
        if type(config[k]) is not list:
            paramset[k] = config[k];
        else:
            paramset[k] = config[k][0];
    return grid_sampling_rec(runner, config, list(config.keys()), paramset, 0);

def grid_sampling_cmd(cmd, config, runset_file):
    fun = cmd_runner_functor(cmd)
    runner = Runner(fun, runset_file)
    grid_sampling(runner, config)

class GradientDescentConfig:
    def __init__(self, cost, max_iterations, parameters, iterator = "linear_prediction", constraint=None,starting_point=None):
        self.cost = cost
        self.max_iterations = max_iterations
        self.parameters = LinearizedDict(parameters)
        self.iterator = iterator
        self.starting_point = LinearizedDict(starting_point)
        if constraint:
            self.constraint = constraint
        else:
            self.constraint = lambda r: True
        

def prev_value_in_range(range, v):
    for idx, e in enumerate(range):
        if (type(v) is str and v == e) or (type(v) is not str and abs(v - e) < 0.0001):
            if idx == 0:
                return None
            else:
                return range[idx - 1]

def next_value_in_range(range, v):
    for idx, e in enumerate(range):
        if (type(v) is str and v == e) or (type(v) is not str and abs(v - e) < 0.0001):
            if idx == (len(range) - 1):
                return None
            else:
                return range[idx + 1]

def position_in_range(range, v):
    for idx, e in enumerate(range):
        if (type(v) is str and v == e) or (type(v) is not str and abs(v - e) < 0.0001):
            return idx
    
def in_interval(range, v):
    return v >= range[0] and v <= range[-1]

def range_round(range, v):
    if v <= range[0]:
        return range[0]
    if v >= range[-1]:
        return range[-1]
    
    for i,rv in enumerate(range):
        if v > rv:
            prev = rv
            if i < len(range) - 1:
                next = range[i+1]
                if abs(v-next) < abs(v-prev):
                    return next
            return prev

    assert(0)
    return None

'''
Gradient descent strategy.
Minimise the cost function and try to stay in the givent constraints.

config:
  cost: lambda r: r['p1'] + 10 * r['p2']
  starting_point: paramset
  parameters:
    p1: 23.3
    p2: a starting point and a range  (parameter to optimize)
    p3: 1

constraint: lambda r: r['r1'] < 21

max_iteration: 200
iterator: step | linear_prediction
'''
def gradient_descent2(runner, config):

    # build the initial paramset
    paramset = config.starting_point
    direction = dict()
    for k in list(paramset.keys()):
        direction[k] = 1
    
    # Test if it satisfies the constraint.    
    res = runner.run(paramset)
    current_cost = config.cost(res)
    if not config.constraint(res):
        print("Gradient descent error: The initial paramset does not satisfy the givent constraint.")
        return
    
    # iterate loop until a local minimum is found or max_iteration reached.
    local_minimum=False
    for iter in range(0, config.max_iterations):
        if local_minimum:
            break
        local_minimum=True
        for k in sorted(config.parameters.keys()):
            print("=================== Optimize parameter %s" % k)
            current_value=paramset[k]
            value1 = prev_value_in_range(config.parameters[k], current_value)
            value2 = next_value_in_range(config.parameters[k], current_value)

            if direction[k] and direction[k] > 0:
                value1,value2 = value2,value1

            vs=[value1, value2];
            vcosts=[];
            for v in vs:
                if v is not None:
                    #   Fill the paramset with the next value
                    nps = copy.deepcopy(paramset)
                    nps[k] = v
                    #   Run the function
                    res = runner.run(nps)
                    nps_cost = config.cost(res)
                    print("Cost: %f, value: %f" % (nps_cost, v))
                    vcosts.append([v, nps_cost])
                    if nps_cost < current_cost:
                        break

            # Find the best direction
            bestc = None
            bestv = None
            for p in vcosts:
                if bestc is None or bestc > p[1]:
                    bestv = p[0]
                    bestc = p[1]

            #   If their is a new minimum
            if bestv is not None and bestc <= current_cost:
                direction[k] = bestv - current_value # save the direction for the next step.
                local_minimum=False
                paramset[k] = bestv
                current_cost = bestc

                print("BEST COST FOUND: %f" % bestc)
                # Save it
                if config.iterator == "linear_prediction":
                    # linear prediction iterator
                    # predict where the zero  cost is
                    prediction = current_value + ( current_cost - bestc) * (bestv - current_value)

                    # if the prediction is in the interval, use it
                    if in_interval(config.parameters[k], prediction):
                        nps = copy.deepcopy(paramset)
                        v = range_round(config.parameters[k], prediction).item()
                        nps[k] = v
                        res = runner.run(linearized_to_deep_dict(nps))
                        pred_cost = config.cost(res)
                        print("Cost: %f, value: %f" % (pred_cost, nps[k]))
                        if pred_cost < bestc: # if it does not lower the cost, fallback to a step
                            paramset[k] = v
                            current_cost = pred_cost
                            print("BEST COST FOUND: %f" % pred_cost)

                    else: # if not, step
                        paramset[k] = bestv


'''
Gradient descent strategy 2.
Minimise the cost function and try to stay in the givent constraints.

Difference with the previous version: Find the local minimum on a dimension
before passing to the next one.

config:
  cost: lambda r: r['p1'] + 10 * r['p2']
  starting_point: paramset
  parameters:
    p1: 23.3
    p2: a starting point and a range  (parameter to optimize)
    p3: 1

constraint: lambda r: r['r1'] < 21

max_iteration: 200
iterator: step | linear_prediction
'''
def gradient_descent(runner, config):

    # build the initial paramset
    paramset = dict()
    direction = dict()
    if config.starting_point is None:
        for k in list(config.parameters.keys()):
            direction[k] = 1
            if type(config.parameters[k]) is not list:
                paramset[k] = config.parameters[k];
            else:
                paramset[k] = config.parameters[k][0];
    else:
        for k in list(config.parameters.keys()):
            direction[k] = 1
            if type(config.parameters[k]) is not list:
                paramset[k] = type(config.parameters[k])(config.starting_point[k]);
            else:
                paramset[k] = type(config.parameters[k][0])(config.starting_point[k]);
            
    
    # Test if it satisfies the constraint.    
    res = runner.run(linearized_to_deep_dict(paramset))
    current_cost = config.cost(res)
    print ("first run, cost = ", current_cost)
    if not config.constraint(res):
        print("Gradient descent error: The initial paramset does not satisfy the givent constraint.")
        return

    # iterate loop until a local minimum is found or max_iteration reached.
    local_minimum=False
    for iter in range(0, config.max_iterations):
        if local_minimum:
            break
        local_minimum=True
        for k in sorted(config.parameters.keys()):
            # For each non fixed parameter
            if type(config.parameters[k]) is list:
                print("=================== Optimize parameter %s" % k)

                current_value=paramset[k]
                value1 = prev_value_in_range(config.parameters[k], current_value)
                value2 = next_value_in_range(config.parameters[k], current_value)

                if direction[k] and direction[k] > 0:
                    value1,value2 = value2,value1

                vs=[value1, value2];
                vcosts=[];
                for v in vs:
                    if v is not None:
                        #   Fill the paramset with the next value
                        nps = copy.deepcopy(paramset)
                        nps[k] = v
                        #   Run the function
                        res = runner.run(linearized_to_deep_dict(nps))
                        nps_cost = config.cost(res)
                        print("Cost: %f, %s == " % (nps_cost, str(k)), v)
                        vcosts.append([v, nps_cost])
                        if nps_cost < current_cost:
                            break

                # Find the best direction
                bestc = None
                bestv = None
                for p in vcosts:
                    if bestc is None or bestc > p[1]:
                        bestv = p[0]
                        bestc = p[1]


                if bestv is not None and bestc < current_cost:
                    direction[k] = position_in_range(config.parameters[k], bestv) - position_in_range(config.parameters[k], current_value) # save the direction for the next step.
                    local_minimum=False
                    prev_value = current_value
                    prev_cost = current_cost
                    current_value = bestv
                    current_cost = bestc
                    
                    paramset[k] = bestv
                    print("BEST COST FOUND: %f" % bestc)

                    # Iterate on k while we can find a lower cost.
                    k_local_min=False
                    while not k_local_min:
                        k_local_min=True
                        # try linear prediction

                        # linear prediction iterator
                        # predict where the zero  cost is
                        #prediction = current_value + ( current_cost - bestc) * (bestv - current_value)
                        if type(current_value) is not str:
                            prediction = prev_value + prev_cost * (current_value - prev_value) / ( prev_cost - current_cost)
                            
                            # if the prediction is in the interval, use it
                            if in_interval(config.parameters[k], prediction):
                                nps = copy.deepcopy(paramset)
                                v = range_round(config.parameters[k], prediction).item()
                                nps[k] = v
                                res = runner.run(linearized_to_deep_dict(nps))
                                pred_cost = config.cost(res)
                                print("Cost: %f, %s == " % (pred_cost, k), nps[k])
                                if pred_cost < current_cost: # if it does not lower the cost, fallback to a step
                                    paramset[k] = v
                                    current_cost = pred_cost
                                    current_value = v
                                    print("BEST COST FOUND: %f" % pred_cost)
                                    k_local_min=False

                        if k_local_min:
                            nps = copy.deepcopy(paramset)

                            if direction[k] < 0:
                                nps[k] = prev_value_in_range(config.parameters[k], current_value)
                            else:
                                nps[k] = next_value_in_range(config.parameters[k], current_value)

                            if nps[k] is not None:
                                res = runner.run(linearized_to_deep_dict(nps))
                                step_cost = config.cost(res)
                                print("Cost: %f, %s == " % (step_cost, k), nps[k])
                                if step_cost < current_cost:
                                    paramset[k] = nps[k]
                                    current_cost = step_cost
                                    current_value = nps[k]
                                    print("BEST COST FOUND: %f" % step_cost)
                                    k_local_min=False

                            
'''
Parallel gradient descent strategy.
Minimise the cost function and try to stay in the givent constraints.

config:
  cost: lambda r: r['p1'] + 10 * r['p2']
  parameters:
    p1: 23.3
    p2: a starting point and a range  (parameter to optimize)
    p3: 1

constraint: lambda r: r['r1'] < 21

max_iteration: 200
iterator: step | linear_prediction
'''
def gradient_descent_parallel(runner, config):

    # build the initial paramset
    paramset = dict()
    direction = dict()
    for k in list(config.parameters.keys()):
        direction[k] = 1
        if type(config.parameters[k]) is not RV:
            paramset[k] = config.parameters[k];
        else:
            paramset[k] = config.parameters[k].value;

    # Test if it satisfies the constraint.    
    res = runner.run(paramset)
    current_cost = config.cost(res)
    if not config.constraint(res):
        print("Gradient descent error: The initial paramset does not satisfy the givent constraint.")
        return

    # iterate loop until a local minimum is found or max_iteration reached.
    local_minimum=False
    for iter in range(0, config.max_iterations):
        if local_minimum:
            break
        local_minimum=True
        for k in sorted(config.parameters.keys()):
            # For each non fixed parameter
            if type(config.parameters[k]) is  RV:
                print("=================== Optimize parameter %s" % k)
                current_value=paramset[k]
                value1 = prev_value_in_range(config.parameters[k].range, current_value)
                value2 = next_value_in_range(config.parameters[k].range, current_value)

                if direction[k] and direction[k] > 0:
                    value1,value2 = value2,value1

                vs=[value1, value2];
                vcosts=[];
                for v in vs:
                    if v is not None:
                        #   Fill the paramset with the next value
                        nps = copy.deepcopy(paramset)
                        nps[k] = v
                        #   Run the function
                        res = runner.run(nps)
                        nps_cost = config.cost(res)
                        print("Cost: %f, value: %f" % (nps_cost, v))
                        vcosts.append([v, nps_cost])
                        if nps_cost < current_cost:
                            break

                # Find the best direction
                bestc = None
                bestv = None
                for p in vcosts:
                    if bestc is None or bestc > p[1]:
                        bestv = p[0]
                        bestc = p[1]

                #   If their is a new minimum
                if bestv is not None and bestc < current_cost:
                    direction[k] = bestv - current_value # save the direction for the next step.
                    local_minimum=False
                    current_cost = bestc

                    print("BEST COST FOUND: %f" % bestc)
                    # Save it
                    if config.iterator == "step":
                        paramset[k] = bestv # step iterator
                    else:# if config.iterator == "linear_prediction": # linear prediction iterator
                        # predict where the zero  cost is
                        prediction = current_value + ( current_cost - bestc) * (bestv - current_value)

                        # if the prediction is in the interval, use it
                        if in_interval(config.parameters[k].range, prediction):
                            paramset[k] = range_round(config.parameters[k].range, prediction).item()
                            res = runner.run(paramset)
                            pred_cost = config.cost(res)
                            print("Cost: %f, value: %f" % (pred_cost, paramset[k]))
                            if pred_cost >= bestc: # if it does not lower the cost, fallback to a step
                                paramset[k] = bestv
                            else: # if it is better log it
                                current_cost = pred_cost
                                print("BEST COST FOUND: %f" % pred_cost)
                                
                        else: # if not, step
                            paramset[k] = bestv
                            
