from typing import List

from entities.GpsFix import GpsFix
from entities.LiveStayPoint import LiveStayPoint


class StreamedZhen(object):
    """
    Zhen live algorithm for stay points detection. It works buffering fixes,
    as the accumulation of coordinates might lead to overflow of values.

    Attributes:
        time_threshold: time threshold parameter (value is kept in milliseconds)
        distance_threshold: distance threshold parameter
        verbose: print internal states-task details
    """

    def __init__(self, time_threshold, distance_threshold, verbose=False):
        """
        Basic constructor
        :param time_threshold: Time threshold to employ (in seconds)
        :param distance_threshold:  Distance threshold to employ
        :param verbose: print task details
        """
        self.list_of_fixes = []  # type List[StayPointInAlgorithm]
        self.time_threshold = time_threshold * 1000
        self.distance_threshold = distance_threshold
        self.verbose = verbose

    def analyze_location(self, gps_fix: GpsFix) -> (LiveStayPoint, List[GpsFix]):
        """
        Process the given GpsFix
        :param gps_fix: The fix to analyze
        :return: A StayPoint if found with the current GpsFix, and the list of involved fixes
        """
        self.list_of_fixes.append(gps_fix)
        if len(self.list_of_fixes) == 1:
            return None, None
        else:
            return self._process_live()

    def _process_live(self) -> (LiveStayPoint, List[GpsFix]):
        """
        Live processing of specified fix
        :return: A StayPointInAlgorithm object if found
        """
        pi = self.list_of_fixes[0]
        pj = self.list_of_fixes[-1]

        distance = pi.distance_to(pj)

        if distance > self.distance_threshold:
            time_difference = pi.time_difference(pj)

            if time_difference > self.time_threshold:
                stay_point = LiveStayPoint.create_from_list(self.list_of_fixes)
                if self.verbose:
                    print('Stay point {} created, involved fixes are'.format(stay_point))
                    for x in self.list_of_fixes:
                        print(x)
                copy_of_list = self.list_of_fixes
                self.clean_list(pj)
                return stay_point, copy_of_list

            self.clean_list(pj)

        return None, None

    def analyze_last_part(self) -> (LiveStayPoint, List[GpsFix]):
        """
        Process the remaining part of the trajectory.
        Should be called when there are not going to be more fixes anymore
        :return: A StayPointInAlgorithm object if found
        """
        if len(self.list_of_fixes) == 0 or len(self.list_of_fixes) == 1:
            return None, None

        if self.verbose:
            print('Building a stay point in last part with ', len(self.list_of_fixes), ' fixes.')

        stay_point = LiveStayPoint.create_from_list(self.list_of_fixes)
        copy_of_list = self.list_of_fixes
        self.list_of_fixes = []
        return stay_point, copy_of_list

    def clean_list(self, gps_fix: GpsFix) -> None:
        """
        Resets the list and appends the given fix
        :param gps_fix: The GpsFix to append
        """
        self.list_of_fixes = []
        self.list_of_fixes.append(gps_fix)
        if self.verbose:
            print("Cleaning the list and adding", gps_fix)
