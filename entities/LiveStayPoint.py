from datetime import datetime, timedelta
from typing import List

from entities.GpsFix import GpsFix


class LiveStayPoint(object):
    """
    Represents a stay point as a spatial object. In conjunction with Visit, it would represent the full spatial time
    relevance in user mobility

    Attributes:
        latitude: the latitude coordinate of stay point
        longitude: the longitude coordinate of stay point
        arrival_time: the arrival time to the stay point
        departure_time: the departure time to the stay point
        visit_count: the visit count of stay point
        amount_of_fixes: amount of GpsFixes used to calculate this stay point
    """

    def __init__(self, latitude, longitude, arrival_time: datetime, departure_time: datetime,
                 visit_count=0,
                 amount_of_fixes=0):
        """
        Creates a new StayPoint object
        :param latitude: The latitude to assign to stay point
        :param longitude: The longitude to assign to stay point
        :param arrival_time: The arrival time to the stay point
        :param departure_time: the departure time to the stay point
        :param visit_count: The visit count to assign (if apply...)
        :param amount_of_fixes: The amount of GpsFixes used to calculate this stay point
        """
        self.latitude = latitude
        self.longitude = longitude
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.visit_count = visit_count
        self.amount_of_fixes = amount_of_fixes

    @staticmethod
    def create_from_sublist(gps_fixes: List[GpsFix], start_index, end_index) -> 'LiveStayPoint':
        """
        Creates a StayPoint from the specified arguments
        :param gps_fixes: A list of GpsFix
        :param start_index: The start index for sublist
        :param end_index: The end index for sublist
        :return: A LiveStayPoint object
        """
        size_of_portion = end_index - start_index + 1

        sum_latitude = 0.0
        sum_longitude = 0.0
        for x in range(start_index, end_index + 1):
            sum_latitude += gps_fixes[x].latitude
            sum_longitude += gps_fixes[x].longitude

        latitude = sum_latitude / size_of_portion
        longitude = sum_longitude / size_of_portion
        arrival_time = gps_fixes[start_index].timestamp
        departure_time = gps_fixes[end_index].timestamp
        amount_of_fixes = size_of_portion

        return LiveStayPoint(latitude, longitude, arrival_time, departure_time, 0, amount_of_fixes)

    @staticmethod
    def create_from_list(gps_fixes: List[GpsFix]) -> 'LiveStayPoint':
        return LiveStayPoint.create_from_sublist(gps_fixes, 0, len(gps_fixes) - 1)

    def distance_to(self, other: 'LiveStayPoint'):
        """
        Calculates the distance to other LiveStayPoint object.
        :param other: The LiveStayPoint object to find the distance to
        :return: The distance between the stay points, in meters
        """
        self_as_fix = GpsFix(self.latitude, self.longitude, datetime.now(), altitude=0, speed=0, battery_level=0,
                             detected_activity=0)
        other_as_fix = GpsFix(other.latitude, other.longitude, datetime.now(), altitude=0, speed=0, battery_level=0,
                              detected_activity=0)

        return self_as_fix.distance_to(other_as_fix)

    def __str__(self, *args, **kwargs):
        date_format = '%Y-%m-%d %H:%M:%S'

        return '{},{},{},{},{}'.format(self.latitude, self.longitude, self.arrival_time.strftime(date_format),
                                       self.departure_time.strftime(date_format),
                                       self.amount_of_fixes)

    def __eq__(self, other):
        if not isinstance(other, LiveStayPoint):
            return False

        if self.latitude != other.latitude:
            return False
        if self.longitude != other.longitude:
            return False
        if (self.arrival_time - other.arrival_time) != timedelta(0):
            return False
        if (self.departure_time - other.departure_time) != timedelta(0):
            return False

        return True
