from time import strftime


class TransitionMatrixEntry(object):
    def __init__(self, id_sp_origin, id_sp_destination, arrival_time_sp_origin, departure_time_sp_origin,
                 arrival_time_sp_dest, departure_time_sp_dest):
        self.id_sp_origin = id_sp_origin
        self.id_sp_destination = id_sp_destination
        self.arrival_time_sp_origin = arrival_time_sp_origin
        self.departure_time_sp_origin = departure_time_sp_origin
        self.arrival_time_sp_dest = arrival_time_sp_dest
        self.departure_time_sp_dest = departure_time_sp_dest

    def __str__(self):
        date_format = '%Y-%m-%d %H:%M:%S'

        return 'From: {} [{}, {}] To: [{}, {}]', \
               self.id_sp_origin, strftime(date_format, self.arrival_time_sp_origin), \
               strftime(date_format, self.departure_time_sp_origin), \
               self.id_sp_destination, strftime(date_format, self.arrival_time_sp_dest), \
               strftime(date_format, self.departure_time_sp_dest)
