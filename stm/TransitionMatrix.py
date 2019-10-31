from typing import List

from stm.TransitionMatrixEntry import TransitionMatrixEntry


class TransitionMatrix(object):
    def __init__(self, visit_entries: List[List[TransitionMatrixEntry]], ordered_stay_points: List[int]):
        super().__init__()
        self.visit_entries = visit_entries
        self.ordered_stay_points = ordered_stay_points

    def flat_visits(self) -> List[TransitionMatrixEntry]:
        flatten_visits = []

        length = len(self.ordered_stay_points)
        for row in range(0, length):
            for col in range(0, length):
                if self.visit_entries[row][col] is not None and len(self.visit_entries[row][col]) > 0:
                    for visit_entry in self.visit_entries[row][col]:
                        flatten_visits.append(visit_entry)

        return flatten_visits
