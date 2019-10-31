from typing import List

from Utils import obtain_ordered_stay_points_from_visit_list
from entities.SimpleVisit import SimpleVisit
from entities.Visit import Visit
from stm.TransitionMatrix import TransitionMatrix
from stm.TransitionMatrixEntry import TransitionMatrixEntry


class TransitionMatrixBuilder(object):
    def __init__(self, visits: List[SimpleVisit]):
        self.visits = visits
        self.ordered_stay_points = obtain_ordered_stay_points_from_visit_list(visits)
        self.total_stay_points = len(self.ordered_stay_points)

    def build_matrix(self) -> TransitionMatrix:
        size = len(self.visits)
        if size == 0:
            print('No chance for building a visits matrix: the list of visits is empty')
            return None

        entries_visits_matrix = self.initialize_empty_matrix()

        for i in range(0, size - 1):
            origin = self.visits[i]
            dest = self.visits[i + 1]

            position_from = self.ordered_stay_points.index(origin.id_stay_point)
            position_to = self.ordered_stay_points.index(dest.id_stay_point)

            entry = TransitionMatrixEntry(origin.id_stay_point, dest.id_stay_point, origin.arrival_time,
                                          origin.departure_time, dest.arrival_time, dest.departure_time)
            current_cell = entries_visits_matrix[position_from][position_to]

            if current_cell is None:
                visits_list = [entry]
                entries_visits_matrix[position_from][position_to] = visits_list
            else:
                current_cell.append(entry)

        transition_matrix = TransitionMatrix(entries_visits_matrix, self.ordered_stay_points)
        return transition_matrix

    def initialize_empty_matrix(self):
        matrix_entries = []
        size = len(self.visits)

        for row in range(0, size):
            this_row_cells = []

            for col in range(0, size):
                this_row_cells.append(None)

            matrix_entries.append(this_row_cells)

        return matrix_entries
