from datetime import datetime

from entities.GpsFix import GpsFix


class StayPoint(object):
    """
    Represents a stay point as a spatial object. In conjunction with Visit, it would represent the full spatial time
    relevance in user mobility

    Attributes:
        id_stay_point: The stay point identifier
        latitude: the latitude coordinate of stay point
        longitude: the longitude coordinate of stay point
        visit_count: the visit count of stay point
    """

    def __init__(self, id_stay_point, latitude, longitude, visit_count=0):
        """
        Creates a new StayPoint object
        :param id_stay_point: The identifier of stay point
        :param latitude: The latitude to assign to stay point
        :param longitude: The longitude to assign to stay point
        :param visit_count: The visit count to assign (if apply...)
        """
        self.id_stay_point = id_stay_point
        self.latitude = latitude
        self.longitude = longitude
        self.visit_count = visit_count

    def distance_to(self, other: 'StayPoint'):
        """
        Calculates the distance to other StayPoint object.
        :param other: The StayPoint object to find the distance to
        :return: The distance between the stay points, in meters
        """
        self_as_fix = GpsFix(self.latitude, self.longitude, datetime.now(), altitude=0, speed=0, battery_level=0,
                             detected_activity=0)
        other_as_fix = GpsFix(other.latitude, other.longitude, datetime.now(), altitude=0, speed=0, battery_level=0,
                              detected_activity=0)

        return self_as_fix.distance_to(other_as_fix)

    def __eq__(self, other):
        """
        Checks whether the specified value represents the same spatial stay point (only coordinates are evaluated)
        :param other: The other stay point to check against
        :return: True if it is the same stay point, False otherwise
        """

        return self.latitude == other.latitude and self.longitude == other.longitude

    def __str__(self, *args, **kwargs):
        return '{},{},{},{}'.format(self.id_stay_point, self.latitude, self.longitude, self.visit_count)
