from math import floor
from typing import Union, Tuple
from datetime import datetime
from entities.GpsFix import GpsFix
from pac.mobility_analyzer.GeoFencingOutcome import GeoFencingOutcome as gfo


class WindowedGeoFencing(object):
    """
    Analyzes windows of the GpsFixes stream for finding mobility changes.
    The window holds a pivot (centroid-medoid) that aids to determine what happened before and after it and determine 
    the mobility changes using several fixes instead of a single one as the BinaryGeoFencing does.
    The pivot is dynamic, it could be in other position than center.

    Attributes:
        radio_distance: The distance for considering a fix inside a stay point
        window_size: The size of the window to employ
        distances: The calculated distances to each stay point
        stay_points: The stay points considered during calculation of visits.
    """

    def __init__(self, radio_distance, window_size):
        """
        Basic constructor
        :param radio_distance: The distance for considering when a fix is inside a stay point 
        :param window_size: The size of the window to employ
        """
        self.radio_distance = radio_distance
        self.window_size = window_size
        self.fixes_window = []
        self.distances = {}
        self.distances_as_boolean = {}
        self.stay_points = []
        self.pivot = floor(window_size / 2.0)  # Ok, validated
        self.trimmed_once = False
        self.current_sp = None

    def analyze_location(self, gps_fix: GpsFix, pivot=-1):
        self.fixes_window.append(gps_fix)
        self.update_distances(gps_fix)
        self.trim_window_if_needed()
        return self.check_mobility_changes(gps_fix, self.pivot if pivot < 0 else pivot)

    def update_distances(self, gps_fix):
        for stay_point in self.stay_points:
            distance = stay_point.distance_to(gps_fix)
            distance_as_boolean = self.radio_distance > distance
            stay_point_distances = self.distances[stay_point.id_stay_point]
            stay_point_distances.append(distance)
            stay_point_distances_as_boolean = self.distances_as_boolean[stay_point.id_stay_point]
            stay_point_distances_as_boolean.append(distance_as_boolean)

    def trim_window_if_needed(self):
        if len(self.fixes_window) > self.window_size:
            self.trimmed_once = True
            self.fixes_window.pop(0)
            for stay_point in self.stay_points:
                stay_point_distances = self.distances[stay_point.id_stay_point]
                del stay_point_distances[0]
                stay_point_distances_as_boolean = self.distances_as_boolean[stay_point.id_stay_point]
                del stay_point_distances_as_boolean[0]

    def check_mobility_changes(self, gps_fix, pivot):
        decision = None
        if len(self.stay_points) > 0 and len(self.fixes_window) > pivot:
            decision = self.obtain_decision(gps_fix, pivot)
        return decision

    def obtain_decision(self, gps_fix, pivot):
        """
        Identifies the mobility change
        :type pivot: int
        :type gps_fix: GpsFix
        :param gps_fix: The latest received fix 
        :param pivot: The index of pivot in window
        :return: A GFO object or None if no changes are identified
        """
        # Count fixes inside stay point in oldest-newer sub-windows
        results = {}
        for sp in self.stay_points:
            distances_as_boolean = self.distances_as_boolean[sp.id_stay_point]
            results[sp.id_stay_point] = {
                # oldest stuff. Structure is: count of fixes inside, sub-window length
                "old_window": (sum(distances_as_boolean[:pivot]), pivot),
                # newer stuff
                "new_window": (sum(distances_as_boolean[(pivot + 1):]), len(distances_as_boolean[(pivot + 1):])),
                "pivot": (distances_as_boolean[pivot], 1)}

        is_user_arriving, metadata_arrival = self._check_for_arrival(gps_fix, results, pivot)
        is_user_leaving, metadata_departure = self._check_for_departure(gps_fix, results, pivot)
        if is_user_arriving and is_user_leaving:
            # Departure and arrival
            outcome = gfo(gfo.TYPE_LEAVING_AND_ARRIVING, metadata_departure.stay_point,
                          metadata_arrival.event_fix, metadata_arrival.stay_point,
                          metadata_arrival.detection_fix)
            self.current_sp = outcome.stay_point_2  # The arrived stay point
        elif is_user_arriving:
            outcome = metadata_arrival
            self.current_sp = outcome.stay_point
        elif is_user_leaving:
            outcome = metadata_departure
            self.current_sp = None
        else:
            # outcome = gfo(gfo.TYPE_NO_CHANGE, self.current_sp, gps_fix.timestamp, None, gps_fix.timestamp)
            # TODO the call to watchdog would be here, basically, it would try to ensure that if
            # TODO the distance to current stay point is way too large, then a leaving notification must be generated

            if self.current_sp is not None and self.distance_watchdog_barks(pivot):
                outcome = gfo(gfo.TYPE_LEAVING_STAY_POINT, self.current_sp, self.fixes_window[pivot], None, gps_fix)
                self.current_sp = None
            else:
                outcome = gfo(gfo.TYPE_NO_CHANGE, self.current_sp, self.fixes_window[pivot], None, gps_fix)

        return outcome

    def it_is_the_same_current_stay_point(self, stay_point) -> bool:
        """
        Finds out whether the specified stay point is the same current stay point where user is
        :param stay_point: The stay point to compare
        :return: True if it is the same stay point, false otherwise
        """
        return self.current_sp is not None and self.current_sp.id_stay_point == stay_point.id_stay_point

    def introduce_new_stay_point(self, stay_point):
        self.stay_points.append(stay_point)
        distances_new_stay_point = []
        distances_as_boolean_new_stay_point = []
        for fix in self.fixes_window:
            distance = stay_point.distance_to(fix)
            distances_new_stay_point.append(distance)

            distance_as_boolean = self.radio_distance > distance
            distances_as_boolean_new_stay_point.append(distance_as_boolean)

        self.distances[stay_point.id_stay_point] = distances_new_stay_point
        self.distances_as_boolean[stay_point.id_stay_point] = distances_as_boolean_new_stay_point

    def _check_for_arrival(self, fix, results, pivot) -> Tuple[bool, gfo]:
        for sp in self.stay_points:
            vote_value = results[sp.id_stay_point]
            inside_fixes_old_window, total_old_fixes = vote_value["old_window"]
            inside_fixes_new_window, total_new_fixes = vote_value["new_window"]
            pivot_inside, count = vote_value["pivot"]

            outside_fixes_old_window = total_old_fixes - inside_fixes_old_window
            voting_threshold = floor(self.window_size / 2.0)

            if pivot_inside:
                if outside_fixes_old_window >= voting_threshold and inside_fixes_new_window >= voting_threshold:
                    if not self.it_is_the_same_current_stay_point(sp):
                        metadata = gfo(gfo.TYPE_ARRIVING_STAY_POINT, sp, self.fixes_window[pivot], None, fix)
                        return True, metadata
                    else:
                        # Nothing to report, the stay point where user is arriving is the "same" where she is
                        pass

                elif inside_fixes_old_window >= voting_threshold and not self.trimmed_once:
                    # Case added for when testing PAC without SPD and trajectory starts right inside a know SP
                    if not self.it_is_the_same_current_stay_point(sp):
                        metadata = gfo(gfo.TYPE_ARRIVING_STAY_POINT, sp, self.fixes_window[0], None, fix)
                        return True, metadata
                    else:
                        # Nothing to report, the stay point where user is arriving is the "same" where she is
                        pass

        return False, None

    def _check_for_departure(self, fix, results, pivot) -> Tuple[bool, gfo]:
        for sp in self.stay_points:
            vote_value = results[sp.id_stay_point]
            inside_fixes_old_window, total_old_fixes = vote_value["old_window"]
            inside_fixes_new_window, total_new_fixes = vote_value["new_window"]
            pivot_inside, count = vote_value["pivot"]

            outside_fixes_new_window = total_new_fixes - inside_fixes_new_window
            voting_threshold = floor(self.window_size / 2.0)  # in winSize=5, 1 means a 50% of error tolerance

            if pivot_inside is False:
                if inside_fixes_old_window >= voting_threshold and outside_fixes_new_window >= voting_threshold:
                    if self.current_sp is not None:  # if not self.it_is_the_same_current_stay_point(sp):  # if self.current_sp is not None:
                        # Why? because there are orphan departures without arrival if user passes by quickly:
                        # For instance: FFTTF, FTTFF, and TTFFF
                        metadata = gfo(gfo.TYPE_LEAVING_STAY_POINT, sp, self.fixes_window[pivot], None, fix)
                        self.current_sp = None
                        return True, metadata

        return False, None

    def distance_watchdog_barks(self, pivot):
        distances_as_boolean = self.distances_as_boolean[self.current_sp.id_stay_point]
        if not distances_as_boolean[pivot]:
            votes, length = (sum(distances_as_boolean[(pivot + 1):]), len(distances_as_boolean[(pivot + 1):]))
            if votes == 0:
                if self.distances[self.current_sp.id_stay_point][-1] > self.radio_distance:
                    # Bark!
                    return True

        return False
