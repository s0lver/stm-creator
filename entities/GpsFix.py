import math
from datetime import timedelta


class GpsFix(object):
    """
    A GpsFix, which represents the basic level of mobility information

    Attributes:
        is_valid: whether fix was obtained or caused by timeout
        latitude: float latitude of fix
        longitude: float longitude of fix
        timestamp: datetime of fix
        altitude: the altitude of fix
        accuracy: the accuracy of fix
        speed: speed of fix
        battery_level: the battery level when fix was collected
        detected_activity: the activity of user when fix was collected.
    """

    def __init__(self, latitude, longitude, timestamp, altitude=0, accuracy=0, speed=0, battery_level=None,
                 detected_activity=None):
        """
        :param latitude: latitude to assign
        :param longitude: latitude to assign
        :param timestamp: timestamp structure to assign
        :param altitude: altitude to assign
        :param accuracy: accuracy to assign
        :param speed: speed to assign
        :param battery_level: battery level when fix was collected
        :param detected_activity: activity identified when fix was collected
        """
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.altitude = altitude
        self.accuracy = accuracy
        self.speed = speed
        self.detected_activity = detected_activity

        self.is_valid = False if latitude == 0 and longitude == 0 and accuracy == 0 and speed == 0 and altitude == 0 \
            else True

        self.battery_level = 0 if battery_level is None else battery_level

    def distance_to(self, other_fix: 'GpsFix') -> float:
        """
        Calculates the distance to other GpsFix (ported from Android source code)
        :param other_fix: The fix to measure distance to
        :return: The distance to other fix, in meters
        """
        max_iterations = 20

        lat1 = self.latitude
        lon1 = self.longitude
        lat2 = other_fix.latitude
        lon2 = other_fix.longitude

        lat1 *= math.pi / 180.0
        lat2 *= math.pi / 180.0
        lon1 *= math.pi / 180.0
        lon2 *= math.pi / 180.0

        a_axis = 6378137.0  # WGS84 major axis double
        b_axis = 6356752.3142  # WGS84 semi - major axis double
        f = (a_axis - b_axis) / a_axis
        a_sq_minus_bsq_over_bsq = (a_axis * a_axis - b_axis * b_axis) / (b_axis * b_axis)

        l = lon2 - lon1
        a_axis = 0.0
        u1 = math.atan((1.0 - f) * math.tan(lat1))
        u2 = math.atan((1.0 - f) * math.tan(lat2))

        cos_u1 = math.cos(u1)
        cos_u2 = math.cos(u2)
        sin_u1 = math.sin(u1)
        sin_u2 = math.sin(u2)
        cos_u1_cos_u2 = cos_u1 * cos_u2
        sin_u1_sin_u2 = sin_u1 * sin_u2

        sigma = 0.0
        delta_sigma = 0.0

        lambda_var = l
        for i in range(0, max_iterations):
            lambda_orig = lambda_var
            cos_lambda = math.cos(lambda_var)
            sin_lambda = math.sin(lambda_var)

            t1 = cos_u2 * sin_lambda
            t2 = cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda

            sin_sq_sigma = t1 * t1 + t2 * t2
            sin_sigma = math.sqrt(sin_sq_sigma)
            cos_sigma = sin_u1_sin_u2 + cos_u1_cos_u2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = 0.0 if sin_sigma == 0 else cos_u1_cos_u2 * sin_lambda / sin_sigma
            cos_sq_alpha = 1.0 - sin_alpha * sin_alpha
            cos_2_sm = 0.0 if cos_sq_alpha == 0 else cos_sigma - 2.0 * sin_u1_sin_u2 / cos_sq_alpha
            u_squared = cos_sq_alpha * a_sq_minus_bsq_over_bsq

            a_axis = 1 + (u_squared / 16384.0) * (
                4096.0 + u_squared * (-768 + u_squared * (320.0 - 175.0 * u_squared)))
            b = (u_squared / 1024.0) * (256.0 + u_squared * (-128.0 + u_squared * (74.0 - 47.0 * u_squared)))
            c = (f / 16.0) * cos_sq_alpha * (4.0 + f * (4.0 - 3.0 * cos_sq_alpha))

            cos2_s_m_sq = cos_2_sm * cos_2_sm
            delta_sigma = b * sin_sigma * (cos_2_sm + (b / 4.0) * (
                cos_sigma * (-1.0 + 2.0 * cos2_s_m_sq) - (b / 6.0) * cos_2_sm * (-3.0 + 4.0 * sin_sigma * sin_sigma) * (
                    -3.0 + 4.0 * cos2_s_m_sq)))

            lambda_var = l + (1.0 - c) * f * sin_alpha * (
                sigma + c * sin_sigma * (cos_2_sm + c * cos_sigma * (-1.0 + 2.0 * cos_2_sm * cos_2_sm)))

            delta = (lambda_var - lambda_orig) / lambda_var if lambda_var != 0 else 0.0

            if math.fabs(delta) < 1.0e-12:
                break

        distance = b_axis * a_axis * (sigma - delta_sigma)
        return distance

    def time_difference(self, other_fix: 'GpsFix'):
        """
        Calculates the absolute time difference of the fix to the specified one
        :param other_fix: The GpsFix to compare with
        :return: The time difference in milliseconds
        """
        if self.timestamp > other_fix.timestamp:
            recent_date, old_date = self.timestamp, other_fix.timestamp
        else:
            recent_date, old_date = other_fix.timestamp, self.timestamp

        time_delta = recent_date - old_date
        difference = (time_delta.days * 3600 * 24 * 1000) + (time_delta.seconds * 1000) + (
            time_delta.microseconds / 1000)

        return math.fabs(difference)

    def __eq__(self, other):
        if not isinstance(other, GpsFix):
            return False

        if self.latitude != other.latitude:
            return False
        if self.longitude != other.longitude:
            return False
        if (self.timestamp - other.timestamp) != timedelta(0):
            return False

        return True

    def __str__(self, *args, **kwargs):
        date_format = '%Y-%m-%d %H:%M:%S'

        return '{},{},{}'.format(self.latitude, self.longitude, self.timestamp.strftime(date_format))
