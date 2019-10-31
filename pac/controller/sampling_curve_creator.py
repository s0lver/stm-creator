# Discarded! Gaussian is not the way!
# Tener la curva tal y como se define, con parámetros "perfectos".
# Luego escalarla de acuerdo a lo que las necesidades indiquen,
# por ejemplo hacerla más alta o alargarla y demás.
import math

import matplotlib.pyplot as plt
import numpy as np

def_a_height = 1.0
def_b_center = 0.0
def_c_width = 1.0
def_base_width = 8.0
def_x_length = 100


def max_height_in_base_gaussian(a_height=def_a_height, b_center=def_b_center, c_width=def_c_width):
    return a_height * math.exp(-((b_center - b_center) ** 2) / (2 * (c_width ** 2)))


def obtain_base_gaussian_with_center(base_width=def_base_width, a_height=def_a_height, b_center=def_b_center,
                                     c_width=def_c_width,
                                     x_granularity=def_x_length, padding_left=0, padding_right=0):
    # c_width = 1.0  # as variances, 1 variance gives around 8 of width
    bell_start = -base_width / 2.0
    bell_end = base_width / 2.0
    x_values = np.linspace(bell_start - padding_left + b_center, bell_end + padding_right + b_center, x_granularity)
    y_values = []
    for x_val in x_values:
        y_values.append(a_height * math.exp(-((x_val - b_center) ** 2) / (2 * (c_width ** 2))))

    return x_values, y_values


def obtain_base_gaussian(curve_width, bell_center_position, height, x_granularity, bell_width, exponent=2):
    """
    Generates a gaussian curve with the given parameters. The starting point of the gaussian is 0
    :param curve_width: The width of the full curve
    :param bell_width: The width of bell's only
    :param bell_center_position: Where the highest point of the gaussian is put. 
    If the center is not 0 < bell_bell_center_position < curve_width, then it might not be described by y values
    :param height: The maximum height of the gaussian
    :param x_granularity: The amount of x values to calculate. The higher, the more resolution
    :return: A tuple of float arrays, one for x, one for y values
    """
    y_values = []
    x_values = np.linspace(0, curve_width, x_granularity)
    gauss_bell_width = bell_width / 8.0

    corresponding_frequency = []
    max_freq = 30
    min_freq = 3600
    freq_diff = min_freq - max_freq
    for x_val in x_values:
        y_values.append(
            height * math.exp(-((x_val - bell_center_position) ** exponent) / (2 * (gauss_bell_width ** exponent))))
        corresponding_frequency.append(
            max_freq + (
                freq_diff * math.exp(
                    -((x_val - bell_center_position) ** exponent) / (2 * (gauss_bell_width ** exponent)))))

    return x_values, y_values, corresponding_frequency


def generate_and_plot_base_gaussian():
    """
    Intermediate function, not needed
    :return: None
    """
    x, y = obtain_base_gaussian_with_center()
    plt.plot(x, y, label='Normal distribution (BASE)')


def generate_and_plot_scaled_gaussian(base_width=def_base_width):
    """
    Intermediate function, not needed
    :param base_width: 
    :return: None
    """
    scaled_x, scaled_y = obtain_base_gaussian_with_center()
    desired_width = 8.0
    x_factor = desired_width / base_width
    for i in range(0, len(scaled_x)):
        scaled_x[i] = scaled_x[i] * x_factor
    desired_height = 2.0
    y_factor = desired_height / max_height_in_base_gaussian()
    for i in range(0, len(scaled_y)):
        scaled_y[i] = scaled_y[i] * y_factor
    plt.plot(scaled_x, scaled_y, label='Normal distribution scaled width')


def generate_and_plot_shifted_gaussian(base_width=def_base_width):
    """
    Intermediate function, not needed
    :param base_width: 
    :return: 
    """
    shifted_x, shifted_y = obtain_base_gaussian_with_center()
    shift_distance = base_width / 2.0
    shifted_x = np.add(shifted_x, shift_distance)
    plt.plot(shifted_x, shifted_y, label='Normal distribution shifted')


def generate_and_plot_shifted_scaled_gaussian(base_width=def_base_width):
    """
    Intermediate function, not needed
    :param base_width: 
    :return: None
    """
    shifted_scaled_x, shifted_scaled_y = obtain_base_gaussian_with_center()
    desired_width = 16.0
    x_factor = desired_width / base_width
    for i in range(0, len(shifted_scaled_x)):
        shifted_scaled_x[i] = shifted_scaled_x[i] * x_factor
    desired_height = 0.5
    y_factor = desired_height / max_height_in_base_gaussian()

    for i in range(0, len(shifted_scaled_y)):
        shifted_scaled_y[i] = shifted_scaled_y[i] * y_factor
    shift_distance = -1
    shifted_scaled_x = np.add(shifted_scaled_x, shift_distance)
    plt.plot(shifted_scaled_x, shifted_scaled_y, label='Normal distribution shifted and scaled')


def generate_and_plot_schedule_curve():
    """
    Intermediate function, not needed
    :return: None
    """
    amount_schedules = 11
    x_for_schedules, y_for_schedules = obtain_base_gaussian_with_center(x_granularity=amount_schedules)
    plt.plot(x_for_schedules, y_for_schedules, marker='o', label='Selected schedules')


def generate_gaussian(width, height, center=0, granularity=10, padding_left=0, padding_right=0):
    """
    Intermediate function, not needed. It creates a padded gaussian, but parameters are hard to implement.
    :param width: 
    :param height: 
    :param center: 
    :param granularity: 
    :param padding_left: 
    :param padding_right: 
    :return: 
    """
    x, y = obtain_base_gaussian_with_center(base_width=width, a_height=height, b_center=center,
                                            x_granularity=granularity,
                                            padding_left=padding_left,
                                            padding_right=padding_right)
    return x, y


def generate_and_plot_parametrized_gaussian():
    for i in range(0, 10):
        x, y, other = obtain_base_gaussian(curve_width=4 + i, bell_center_position=i, height=i * 1.25,
                                           x_granularity=1800,
                                           bell_width=2)
        plt.plot(x, y, label='Curve center {}, curve width {}, bell width {}, height {}'.format(i, 4 + i, 2, i * 1.25))

# generate_and_plot_base_gaussian()
# generate_and_plot_shifted_gaussian()
# generate_and_plot_scaled_gaussian()
# generate_and_plot_shifted_scaled_gaussian()
# generate_and_plot_schedule_curve()
# generate_and_plot_parametrized_gaussian()
#
# plt.legend()
# plt.show()
#
# x, y, other_y = obtain_base_gaussian(3600, 1800, height=1, x_granularity=200, bell_width=3400, exponent=8)
# print(other_y)
# plt.plot(x, other_y, label='Tobi')
# plt.legend()
# plt.show()
