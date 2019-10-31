from datetime import datetime


class SimpleVisit(object):
    def __init__(self, id_visit, id_stay_point, arrival_time, departure_time):
        self.id_visit = id_visit  # type: int
        self.id_stay_point = id_stay_point  # type:  int
        self.arrival_time = arrival_time  # type: datetime
        self.departure_time = departure_time  # type: datetime

    def get_length(self):
        return (self.departure_time - self.arrival_time).total_seconds()

    def __str__(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        return '{},{},{},{},{}'.format(self.id_visit, self.id_stay_point, self.arrival_time.strftime(date_format),
                                       self.departure_time.strftime(date_format), self.get_length())
