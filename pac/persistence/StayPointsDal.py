from typing import List

from entities.StayPoint import StayPoint


class StayPointsDal(object):
    """
    Manages access to the stay points repository

    Attributes:
        stay_points: The global list of stay points learned by the engine
        distance_radio: The distance in meters for considering two stay points as equivalent
    """

    def __init__(self, distance_radio):
        """
        Basic constructor
        :param distance_radio: The distance radio for considering two stay points equivalent
        """
        self.stay_points = []  # type List[StayPoint]
        self.distance_radio = distance_radio

    def add(self, stay_point: StayPoint) -> StayPoint:
        """
        Adds a stay point to repository
        :param stay_point: The stay point to add
        :return: The stay point if could be added, None otherwise
        """
        if self.stay_point_already_exists(stay_point):
            return None

        self.stay_points.append(stay_point)
        self.stay_points[-1].id_stay_point = len(self.stay_points)
        return self.stay_points[-1]

    def stay_point_already_exists(self, stay_point) -> bool:
        """
        Determines whether the specified stay point already exists in the repository
        :param stay_point: The stay point to check for.
        :return: True if the stay point already exists, False otherwise
        """
        distances = list(map(lambda x: stay_point.distance_to(x), self.stay_points))

        if len(distances) > 0:
            min_distance = min(distances)

            if min_distance < self.distance_radio:
                # index_of_min = distances.index(min_distance)
                # closest_stay_point = self.stay_points[index_of_min]
                # return closest_stay_point
                return True

        return False

    def get_all(self) -> List[StayPoint]:
        """
        Obtains the list of stay points in the repository
        :return: The list of existing stay points
        """
        return self.stay_points
