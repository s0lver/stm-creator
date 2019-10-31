from entities.GpsFix import GpsFix


class Visit(object):
    """
    A Visit, which represents an arrival-departure to a stay point

    Attributes:
            id_visit: the id of the visit itself
            id_stay_point: the id of the stay point
            pivot_arrival_fix: the GpsFix that corresponds to real world arrival
            pivot_departure_fix: the GpsFix that corresponds to real world departure
            detection_arrival_fix: the GpsFix that triggered the arrival by the platform
            detection_departure_fix: the GpsFix that triggered the departure by the platform
            stay_time: stay time of the visit in seconds
    """

    def __init__(self, id_visit, id_stay_point, pivot_arrival_fix: GpsFix, pivot_departure_fix: GpsFix,
                 detection_arrival_fix: GpsFix,
                 detection_departure_fix: GpsFix):
        """
        Builds a Visit object
        :param id_visit: the id of the visit
        :param id_stay_point: the id of the stay point
        :param pivot_arrival_fix: the GpsFix that corresponds to real world arrival
        :param pivot_departure_fix: the GpsFix that corresponds to real world departure
        :param detection_arrival_fix: the GpsFix that triggered the arrival by the platform
        :param detection_departure_fix: the GpsFix that triggered the departure by the platform
        """
        self.id_visit = id_visit
        self.id_stay_point = id_stay_point
        self.pivot_arrival_fix = pivot_arrival_fix
        self.pivot_departure_fix = pivot_departure_fix
        self.detection_arrival_fix = detection_arrival_fix
        self.detection_departure_fix = detection_departure_fix
        self.stay_time = None
        self.update_stay_time()

    def update_stay_time(self):
        """
        Updates the stay time of visit
        :return: None
        """
        # It would not be better to simply self.stay_time = self.get_length() ??
        self.stay_time = self.get_length()

    def get_length(self) -> int:
        """
        Gets the length of visit in seconds
        :return: The length of visit in seconds
        """
        return (self.pivot_departure_fix.timestamp - self.pivot_arrival_fix.timestamp).total_seconds()

    def __str__(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        return '{},{},{},{},{}'.format(self.id_visit, self.id_stay_point,
                                       self.pivot_arrival_fix.timestamp.strftime(date_format),
                                       self.pivot_departure_fix.timestamp.strftime(date_format), self.get_length())
