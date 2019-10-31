from datetime import datetime, timedelta
from typing import List

from csv_readers.LogicGpsReaderSparse import LogicGpsReaderSparse
from entities.GpsFix import GpsFix
from entities.LiveStayPoint import LiveStayPoint
from entities.StayPoint import StayPoint
from entities.Visit import Visit
from pac.controller import pool_policies
from pac.controller.SamplingCurveGenerator import SamplingCurveGenerator
from pac.controller.SamplingCurveGenerator import SamplingCurveGenerator as Scg
from pac.mobility_analyzer.GeoFencingOutcome import GeoFencingOutcome
from pac.mobility_analyzer.GeoFencingOutcome import GeoFencingOutcome as Gfo
from pac.mobility_analyzer.WindowedGeoFencing import WindowedGeoFencing
from pac.persistence.StayPointsDal import StayPointsDal
from pac.persistence.VisitsDal import VisitsDal
from pac.stay_point_detectors.StreamedZhen import StreamedZhen


class SmartPacSparseInput(object):
    """
    This class represents the PAC using all of its features: SPD, GF, PRM.
    For this class, the input can be a non 1Hz sampling file, the reader delivers the closest next fix to the request.
    """

    def __init__(self, spd_algorithm: StreamedZhen, gf: WindowedGeoFencing,
                 file_enumerator: LogicGpsReaderSparse, stay_points_dal_distance: float,
                 adapt_sampling=True, base_sampling=30, late_departure_sampling=30,
                 maximum_time_separations=None, sigmoid_segments=None, verbose=False):
        self._file_enumerator = file_enumerator
        self._spd_algorithm = spd_algorithm
        self._geo_fencing = gf
        self._verbose = verbose
        self._adapt_sampling = adapt_sampling
        self._base_sampling = base_sampling
        self._stay_points_dal = StayPointsDal(stay_points_dal_distance)
        self._visits_dal = VisitsDal()
        self._mobility_status = {"mobility_mode": "trajectory"}
        self._curve_generator = None  # type: SamplingCurveGenerator
        self._late_departure_sampling = late_departure_sampling
        self._maximum_time_separations = maximum_time_separations
        self._sigmoid_segments = sigmoid_segments
        self.fixes_read = 0
        self.fixes = []  # type: List[GpsFix]
        self._pre_loaded = False
        self._minor_allowed_sampling = 30
        self._live_stay_points = []
        self.accuracy_factor = 2500

    def _append_stay_point_to_memory(self, live_stay_point: LiveStayPoint, list_of_fixes: List[GpsFix]) -> StayPoint:
        self._live_stay_points.append((live_stay_point, list_of_fixes))
        stay_point_to_add = StayPoint(0, live_stay_point.latitude, live_stay_point.longitude,
                                      live_stay_point.amount_of_fixes)
        stay_point_added = self._stay_points_dal.add(stay_point_to_add)

        if stay_point_added is None and self._verbose:
            print('Stay point {} already exists'.format(live_stay_point))
        elif stay_point_added is not None and self._verbose:
            print('Stay point {} is added'.format(live_stay_point))

        return stay_point_added

    def _insert_visit_from_new_stay_point(self, stay_point_id, live_stay_point: LiveStayPoint) -> Visit:
        self.is_last_visit_because_new_stay_point = True
        fake_arrival_fix = GpsFix(live_stay_point.latitude, live_stay_point.longitude, live_stay_point.arrival_time)
        fake_departure_fix = GpsFix(live_stay_point.latitude, live_stay_point.longitude, live_stay_point.departure_time)

        visit = Visit(0, stay_point_id,
                      pivot_arrival_fix=fake_arrival_fix,
                      pivot_departure_fix=fake_departure_fix,
                      detection_arrival_fix=fake_arrival_fix,
                      detection_departure_fix=fake_departure_fix)
        added_visit = self._visits_dal.add(visit)
        return added_visit

    @staticmethod
    def _live_stay_point_could_be_added(stay_point: StayPoint) -> bool:
        return stay_point is not None

    def start_main_loop(self):
        aux_stop_time = datetime.strptime('2017-01-29 21:37:00', '%Y-%m-%d %H:%M:%S')
        next_time = 0
        fix = self._file_enumerator.get_fix_in_n_seconds(next_time)
        self.fixes_read = 1
        time_percentage = 0
        start_timestamp = fix.timestamp
        total_time = (self._file_enumerator.last_fix.timestamp - start_timestamp).total_seconds()
        previous_fix = None

        while fix is not None:
            if fix != previous_fix:
                self.fixes_read += 1

            cur_timestamp = fix.timestamp
            new_time_percentage = int((cur_timestamp - start_timestamp).total_seconds() * 100 / total_time)
            if new_time_percentage != time_percentage:
                time_percentage = new_time_percentage
                print('{}%'.format(time_percentage), end='')

            # is_valid_fix = self.validate_fix(fix, factor=self.accuracy_factor)
            # if is_valid_fix is not True:
            #     fix.is_valid = False
            if fix.accuracy >= 250:  # TODO warning here, when gf is none I am hardcoding this... self._geo_fencing.radio_distance:
                fix.is_valid = False

            if fix.is_valid:
                self.fixes.append(fix)

            if self._spd_algorithm is not None:
                self._evaluate_fix_in_spd(fix)

            if self._curve_generator is not None and self._curve_generator.is_done is False and self._verbose:
                print('Sigmoid reading {}, after {} seconds'.format(fix, next_time))

            if self._geo_fencing is not None:
                outcome = self._evaluate_fix_in_gf(fix)

            if self._adapt_sampling:
                next_time = self._calculate_next_scheduling(outcome)
            else:
                next_time = self._base_sampling

            previous_fix = fix
            fix = self._file_enumerator.get_fix_in_n_seconds(next_time)

        self._process_last_part()

    def _process_last_part(self):
        if self._spd_algorithm is not None:
            live_stay_point, list_of_fixes = self._spd_algorithm.analyze_last_part()
            self.detect_sp_and_try_to_append_visit(live_stay_point, list_of_fixes)

        if self._geo_fencing is not None:
            last_visit = self.get_obtained_visits()[-1]
            if last_visit is not None and last_visit.pivot_arrival_fix.timestamp == last_visit.pivot_departure_fix.timestamp:
                last_fix = self._file_enumerator.last_fix
                last_visit.pivot_departure_fix = last_fix
                last_visit.detection_departure_fix = last_fix
                last_visit.update_stay_time()

                if last_fix != self.fixes[-1]:
                    self.fixes.append(last_fix)

    def detect_sp_and_try_to_append_visit(self, live_stay_point, list_of_fixes):
        if live_stay_point is not None:
            stay_point = self._append_stay_point_to_memory(live_stay_point, list_of_fixes)
            if self._live_stay_point_could_be_added(stay_point):
                if self._verbose:
                    print()
                    print('Stay point added, now storing visit')
                self._insert_visit_from_new_stay_point(stay_point.id_stay_point, live_stay_point)
                if self._geo_fencing is not None:
                    self._notify_geo_fencing(stay_point)

    def _evaluate_fix_in_spd(self, fix):
        if fix.is_valid:
            live_stay_point, list_of_fixes = self._spd_algorithm.analyze_location(fix)
            self.detect_sp_and_try_to_append_visit(live_stay_point, list_of_fixes)
        else:
            if self._verbose:
                print('Invalid fix received, continuing to next one')

    def _evaluate_fix_in_gf(self, fix):
        outcome = None

        if fix.is_valid:
            outcome = self._geo_fencing.analyze_location(fix)
            if outcome is not None:
                if outcome.event_type == GeoFencingOutcome.TYPE_ARRIVING_STAY_POINT:
                    if self._verbose:
                        print()
                    self._append_visit_to_memory(outcome)

                    self._mobility_status["mobility_mode"] = 'stay_point'

                    if self._adapt_sampling:
                        self._mobility_status["is_sigmoid_done"] = False
                        oracle_visit = self.get_visit_smartly(outcome)
                        self._mobility_status["curve_offset"] = 0
                        self.generate_sigmoid(oracle_visit, outcome.detection_fix.timestamp)

                elif outcome.event_type == GeoFencingOutcome.TYPE_LEAVING_STAY_POINT:
                    self._mark_end_of_visit(outcome)
                    self._mobility_status["mobility_mode"] = 'trajectory'
                    if self._adapt_sampling:
                        self._curve_generator = None
                        self._mobility_status["curve_offset"] = 0

                elif outcome.event_type == GeoFencingOutcome.TYPE_LEAVING_AND_ARRIVING:
                    self._mark_end_of_visit(outcome)
                    self._append_visit_to_memory(outcome)
                    # Hard to happen but shruggie
                    if self._adapt_sampling:
                        self._mobility_status["is_sigmoid_done"] = False
                        oracle_visit = self.get_visit_smartly(outcome)
                        self._mobility_status["curve_offset"] = 0
                        self.generate_sigmoid(oracle_visit, outcome.detection_fix.timestamp)
                elif outcome.event_type == GeoFencingOutcome.TYPE_NO_CHANGE:
                    pass
                else:
                    raise RuntimeError('That is not the type of outcome you are looking for')

                if self._verbose and outcome.event_type is not outcome.TYPE_NO_CHANGE:
                    print(outcome)
        else:
            if self._verbose:
                print('Invalid fix received')
        return outcome

    def _append_visit_to_memory(self, outcome):
        id_stay_point = 0
        if outcome.event_type == GeoFencingOutcome.TYPE_ARRIVING_STAY_POINT:
            id_stay_point = outcome.stay_point.id_stay_point
        elif outcome.event_type == GeoFencingOutcome.TYPE_LEAVING_AND_ARRIVING:
            id_stay_point = outcome.stay_point_2.id_stay_point

        visit = Visit(0, id_stay_point,
                      pivot_arrival_fix=outcome.event_fix,
                      pivot_departure_fix=outcome.event_fix,
                      detection_arrival_fix=outcome.detection_fix,
                      detection_departure_fix=outcome.detection_fix)
        self._visits_dal.add(visit)

    def _mark_end_of_visit(self, outcome: Gfo):
        visits = self._visits_dal.visits
        for i, v in reversed(list(enumerate(visits))):
            if v.id_stay_point == outcome.stay_point.id_stay_point:
                self._visits_dal.update_visit(i, outcome.event_fix, outcome.detection_fix)
                return
        raise ValueError('No visit found for the outcome\'s stay point given')

    def get_obtained_stay_points(self) -> List[StayPoint]:
        return self._stay_points_dal.get_all()

    def get_obtained_visits(self):
        return self._visits_dal.get_all()

    def _notify_geo_fencing(self, stay_point):
        self._geo_fencing.introduce_new_stay_point(stay_point)

    def _calculate_next_scheduling(self, outcome):
        if outcome is None:
            return self._base_sampling

        if self._mobility_status["mobility_mode"] == 'stay_point':
            if self._curve_generator.is_done:
                if self._verbose and not self._sigmoid_done_message_has_been_shown:
                    print('Sigmoid is done')
                    self._sigmoid_done_message_has_been_shown = True

                return self._late_departure_sampling
            else:
                next_curve_value = int(self._curve_generator.get_next_schedule())
                if self._mobility_status["curve_offset"] == 0:
                    self._mobility_status["curve_offset"] = next_curve_value
                    return next_curve_value
                else:
                    next_schedule = next_curve_value - self._mobility_status["curve_offset"]
                    if self._watchdog_barks_at_next_schedule(next_schedule):
                        next_curve_value = self._mobility_status["curve_offset"] + self._minor_allowed_sampling
                        next_schedule = 30

                    self._mobility_status["curve_offset"] = next_curve_value
                    return next_schedule
        elif self._mobility_status["mobility_mode"] == 'trajectory':
            return self._base_sampling
        else:
            raise NotImplementedError(
                'Outcome is not none and the mobility mode is not recognized' + self._mobility_status["mobility_mode"])

    def generate_sigmoid(self, oracle_visit: Visit, now_time: datetime):
        oracle_visit_length = (
                oracle_visit.pivot_departure_fix.timestamp - oracle_visit.pivot_arrival_fix.timestamp).total_seconds()
        self._curve_generator = Scg(now_time, now_time + timedelta(seconds=oracle_visit_length), total_schedules=-1,
                                    curve_type=pool_policies.TYPE_SIGMOID_SLICED,
                                    **{"alpha": 1,
                                       "maximum_time_separations": self._maximum_time_separations,
                                       "sigmoid_segments": self._sigmoid_segments})
        self._sigmoid_done_message_has_been_shown = False
        if self._verbose:
            print('Generating sigmoid from {} to {}, {} seconds, {} max time sep (secs)'
                  .format(now_time,
                          now_time + timedelta(seconds=oracle_visit_length),
                          oracle_visit_length,
                          self._maximum_time_separations))

    def get_visit_smartly(self, outcome):
        for v in self._visits_dal.visits:
            if v.id_stay_point == outcome.stay_point.id_stay_point:
                return v
        raise NotImplementedError('I could not find a visit for that stay point')

    def preload_stay_points(self, live_sps):
        self._pre_loaded = True
        for lsp in live_sps:
            new_sp = self._append_stay_point_to_memory(lsp, None)
            self._insert_visit_from_new_stay_point(new_sp.id_stay_point, lsp)
            self._notify_geo_fencing(new_sp)

    def _watchdog_barks_at_next_schedule(self, value):
        if value < self._minor_allowed_sampling:
            return True
        return False

    def get_calculated_live_stay_points(self):
        return self._live_stay_points

    def validate_fix(self, fix: GpsFix, factor: float) -> bool:
        if fix.accuracy >= self._geo_fencing.radio_distance:
            return False
        if len(self.fixes) > 0:
            if self.fixes[-1].distance_to(fix) > factor:
                return False
        return True
