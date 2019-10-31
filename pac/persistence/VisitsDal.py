from typing import List

from entities.GpsFix import GpsFix
from entities.Visit import Visit


class VisitsDal(object):
    """
    Holds visits information to each stay point

    Attributes:
        visits: The list of visits performed
    """

    def __init__(self):
        self.visits = []  # type: List[Visit]

    def add(self, visit: Visit) -> Visit:
        """
        Adds a visit to memory
        :param visit: The visit to add
        :return: The visit with updated id
        """
        self.visits.append(visit)
        self.visits[-1].id_visit = len(self.visits)
        return self.visits[-1]

    def get_all(self) -> List[Visit]:
        return self.visits

    def update_last(self, pivot_departure_fix: GpsFix, detection_departure_fix: GpsFix):
        last_visit = self.visits[-1]  # type: Visit
        last_visit.pivot_departure_fix = pivot_departure_fix
        last_visit.detection_departure_fix = detection_departure_fix
        last_visit.update_stay_time()

    def update_visit(self, idx, pivot_departure_fix: GpsFix, detection_departure_fix: GpsFix):
        visit = self.visits[idx]
        visit.pivot_departure_fix = pivot_departure_fix
        visit.detection_departure_fix = detection_departure_fix
        visit.update_stay_time()
