from datetime import datetime, timedelta

from pac.controller import pool_policies
from pac.controller.SamplingCurveGenerator import SamplingCurveGenerator
from pac.mobility_analyzer.GeoFencingOutcome import GeoFencingOutcome as Gfo


class SamplingDecisionMaker(object):
    def __init__(self):
        self.current_curve_generator = None
        self.current_prediction_start_time = None
        self.current_prediction_end_time = None

    def receive_notification(self, event_type, prediction_start_time, prediction_end_time):
        self.current_prediction_start_time = prediction_start_time
        self.current_prediction_end_time = prediction_end_time
        self.current_curve_generator = None
        if event_type == Gfo.TYPE_ARRIVING_STAY_POINT:
            self.generate_curve_for_stay_point()
        elif event_type == Gfo.TYPE_LEAVING_STAY_POINT:
            self.generate_curve_for_trajectory()

    def generate_curve_for_trajectory(self):
        if self.current_prediction_start_time is not None and self.current_prediction_end_time is not None:
            time_difference = (self.current_prediction_end_time - self.current_prediction_start_time).total_seconds()
            total_schedules = 60 * int(time_difference / 3600)  # 60 schedules per hour (1 per minute)
            self.current_curve_generator = SamplingCurveGenerator(prediction_start=self.current_prediction_start_time,
                                                                  prediction_end=self.current_prediction_end_time,
                                                                  total_schedules=total_schedules,
                                                                  curve_type=pool_policies.TYPE_LINEAR)
            self.current_curve_generator.plot_real_world_values()
        else:
            # No prediction available
            print('No prediction available, decide something good!')
            # curve_generator = something good
            pass

    def generate_curve_for_stay_point(self):
        if self.current_prediction_start_time is not None and self.current_prediction_end_time is not None:
            time_difference = (self.current_prediction_end_time - self.current_prediction_start_time).total_seconds()
            total_schedules = 6 * int(time_difference / 3600)  # 6 schedules per hour
            self.current_curve_generator = SamplingCurveGenerator(prediction_start=self.current_prediction_start_time,
                                                                  prediction_end=self.current_prediction_end_time,
                                                                  total_schedules=total_schedules,
                                                                  curve_type=pool_policies.TYPE_SIGMOID,
                                                                  **{"alpha": 1})
            self.current_curve_generator.plot_real_world_values()
        else:
            # No prediction available
            print('No prediction available, decide something good!')
            # curve_generator = something good
            pass

    def generate_cognitive_action(self) -> datetime:
        next_schedule = self.current_curve_generator.get_next_schedule()
        if next_schedule is None:
            print('I don\'t have more schedules, but it is not my job to detect mismatches and decide what to do!')
            return None
        else:
            next_schedule_timestamp = self.current_prediction_start_time + timedelta(seconds=next_schedule)
            return next_schedule_timestamp
