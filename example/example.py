# This script is an example of how to use/invoke the engine to explore human mobility
from csv_readers.LogicGpsReader import LogicGpsReader
from pac.SmartPac import SmartPac as smart_pac
from pac.mobility_analyzer.WindowedGeoFencing import WindowedGeoFencing
from pac.stay_point_detectors.StreamedZhen import StreamedZhen
from visualization import trajectory_plotter

spd_time_parameter = 45 * 60
spd_distance_parameter = 500

gf_win_size = 3
gf_radio_distance = 250

sampling = 1  # one second


def execute_pac(gps_reader, spd_alg, win_gf, adaptive, seg, sep, base_sampling, cons_sampling):
    pac = smart_pac(spd_alg, win_gf, gps_reader,
                    spd_distance_parameter,
                    adapt_sampling=adaptive,
                    base_sampling=base_sampling,
                    late_departure_sampling=cons_sampling,
                    maximum_time_separations=sep,
                    sigmoid_segments=seg,
                    verbose=False)

    print('Starting main loop')
    pac.start_main_loop()
    print('Main loop ended')
    return pac


if __name__ == '__main__':
    sample_input_trajectory = '../sample_data/trajectory-2-base.csv'
    spd_algorithm = StreamedZhen(spd_time_parameter, spd_distance_parameter)
    gps_reader = LogicGpsReader(sample_input_trajectory)
    win_gf = WindowedGeoFencing(gf_radio_distance, gf_win_size)
    pac = execute_pac(gps_reader, spd_algorithm, win_gf,
                      adaptive=False, seg=None, sep=None, base_sampling=1, cons_sampling=-1)

    # The fixes, stay points, and visits can be extracted from the pac once it is finished.
    # Then they can be used to be plot in a 3d plot
    fixes = pac.fixes
    stay_points = pac.get_obtained_stay_points()
    visits = pac.get_obtained_visits()

    import matplotlib.pyplot as plt
    trajectory_plotter.plot_from_data(fixes, stay_points, visits)
    plt.show()
