from datetime import datetime, timedelta

import numpy as np

from pac.controller.pool_policies import TYPE_LINEAR, generate_function_sigmoid, TYPE_SIGMOID, generate_function_linear, \
    TYPE_SIGMOID_SLICED, generate_slices_for_sigmoid


class SamplingCurveGenerator(object):
    def __init__(self, prediction_start: datetime, prediction_end: datetime, total_schedules: int, curve_type: int,
                 **kwargs):
        self.length_seconds = (prediction_end - prediction_start).total_seconds()
        self.total_schedules = total_schedules
        self.index_in_curve = 0
        self.is_done = False
        self.fun = None
        self._curve_type = curve_type
        self.generate_fun(**kwargs)
        self.x = []
        self.x_list = []
        self.generate_tks_in_function_domain(**kwargs)
        self.y = []
        self.evaluate_tks()

        self.mapped_x = []
        self.mapped_y = []
        self.map_to_real_time()
        self.map_to_sampling_interventions()
        # self.print_real_times(prediction_start)
        self._current_segment = 0

    def generate_tks_in_function_domain(self, **kwargs):
        if self._curve_type == TYPE_SIGMOID_SLICED:
            maximum_separations = kwargs["maximum_time_separations"]
            sigmoid_segments = kwargs["sigmoid_segments"]
            self.x, self.x_list = generate_slices_for_sigmoid(self.length_seconds, self.fun, maximum_separations,
                                                              sigmoid_segments)
        else:
            self.x = np.linspace(self.fun.function_domain_start, self.fun.function_domain_end, self.total_schedules)

    def evaluate_tks(self):
        for x_val in self.x:
            self.y.append(self.fun.evaluate(x_val))

    def generate_fun(self, **kwargs):
        if self._curve_type == TYPE_LINEAR:
            self.fun = generate_function_linear(**kwargs)
        elif self._curve_type == TYPE_SIGMOID:
            self.fun = generate_function_sigmoid(**kwargs)
        elif self._curve_type == TYPE_SIGMOID_SLICED:
            self.fun = generate_function_sigmoid(**kwargs)

    def map_to_real_time(self):
        absolute_start_time = 0
        absolute_end_time = self.length_seconds
        for y_val in self.y:
            mapped_value = absolute_start_time + (absolute_end_time - absolute_start_time) * y_val
            self.mapped_y.append(mapped_value)

            # Regardless of the values, we assign 1 to be the absolute end time
            # self.mapped_y[0] = absolute_start_time
            # self.mapped_y[-1] = absolute_end_time

    def map_to_sampling_interventions(self):
        self.mapped_x = [x for x in range(0, len(self.x))]

    def plot_real_world_values(self):
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(self.mapped_x, self.mapped_y, marker='o', label='Scheduled RT')
        plt.legend()

    def plot_function_domain_values(self):
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(self.x, self.y, marker='o', label='Function (co-)domain values')
        plt.legend()

    def get_next_schedule(self):
        if self.is_done:
            return None
        else:
            value = self.mapped_y[self.index_in_curve]
            self.index_in_curve += 1

            self.update_current_segment()

            if self.index_in_curve == len(self.mapped_y):
                self._current_segment = -1
                self.is_done = True

            return value

    def print_real_times(self, start_time: datetime):
        print('Times would be')
        for y_val in self.mapped_y:
            print('{}, after {}'.format(start_time + timedelta(seconds=y_val), y_val))

    def update_current_segment(self):
        upper_threshold_current_slice = 0

        for s in range(self._current_segment + 1):
            upper_threshold_current_slice += len(self.x_list[s])

        if self.index_in_curve >= upper_threshold_current_slice:
            self._current_segment += 1

    def get_current_segment(self):
        return self._current_segment
