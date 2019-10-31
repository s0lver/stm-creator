from typing import List, Tuple

import numpy as np

from pac.controller.SamplingPolicyCurve import SamplingPolicyCurve

TYPE_LINEAR = 0
TYPE_SIGMOID = 1
TYPE_SIGMOID_SLICED = 2


def linear_fun(x):
    y = x
    return y


def sigmoid_fun(x, **kwargs):
    alpha = kwargs["alpha"]
    y = 1.0 / (1 + np.math.exp(-alpha * x))
    # print('Evaluating with alpha {} and x {} = {}'.format(alpha, x, y))
    return y


def generate_function_linear(domain_start=0, domain_end=1, **kwargs):
    linear_function = linear_fun
    sampling_curve = SamplingPolicyCurve(domain_start, domain_end, linear_function, **kwargs)
    return sampling_curve


def generate_function_sigmoid(domain_start=-5, domain_end=5, **kwargs):
    sigmoid_function = sigmoid_fun
    sampling_curve = SamplingPolicyCurve(domain_start, domain_end, sigmoid_function, **kwargs)
    return sampling_curve


def generate_slices_for_sigmoid(total_length, sigmoid: SamplingPolicyCurve, maximum_separations: List[int],
                                sigmoid_segments: List[Tuple[float, float]]):
    fun_slices = len(sigmoid_segments)
    slices = []
    for i in range(0, fun_slices):
        x_min_i = sigmoid_segments[i][0]
        x_max_i = sigmoid_segments[i][1]
        sigmoid_at_min = sigmoid.evaluate(x_min_i)
        sigmoid_at_max = sigmoid.evaluate(x_max_i)

        if len(maximum_separations) > 1:
            cur_sep = maximum_separations[i]
        else:
            cur_sep = maximum_separations[0]

        # n = np.math.ceil(int(((total_length * sigmoid_at_max) - (total_length * sigmoid_at_min)) / minimum_separation))
        n = int(np.math.floor(((total_length * sigmoid_at_max) - (total_length * sigmoid_at_min)) / cur_sep))
        slots = n + 2
        x_this_slice = np.linspace(x_min_i, x_max_i, slots)
        # print('In slice {} n is {} bc {}'.format(i, n, x_this_slice))
        slices.append(x_this_slice)

    # flat lists
    flattened = []
    for sublist in slices:
        sublist_size = len(sublist)
        for i in range(0, sublist_size):
            if sublist[i] not in flattened:
                flattened.append(sublist[i])

    return flattened, slices
