from typing import List

from entities.GpsFix import GpsFix


class Trajectory(object):
    def __init__(self, fixes: List[GpsFix]):
        self._fixes = fixes

    def get_fix(self, index):
        return self._fixes[index]

    def get_first(self):
        return self._fixes[0]

    def get_last(self):
        return self._fixes[-1]

    def get_size(self):
        return len(self._fixes)

    def get_time_closest_fix_index(self, fix: GpsFix, start_index: int):
        size = self.get_size()
        # i = 0
        for i in range(start_index, size):
            if fix.timestamp < self._fixes[i].timestamp:
                break

        previous_fix_index = i - 1
        next_fix_index = i

        if self.is_out_of_bounds(next_fix_index):
            return i - 1

        previous_fix = self.get_fix(previous_fix_index)
        next_fix = self.get_fix(next_fix_index)

        time_difference_previous = (fix.timestamp - previous_fix.timestamp).total_seconds()
        time_difference_next = (next_fix.timestamp - fix.timestamp).total_seconds()

        if time_difference_previous < time_difference_next:
            return previous_fix_index

        return next_fix_index

    def is_out_of_bounds(self, requested_index):
        if self.get_size() <= requested_index:  # Not sure if >, maye it is working bc the = sign
            return True
        return False

    def get_time_closest_fix(self, fix: GpsFix, start_index):
        fix_index = self.get_time_closest_fix_index(fix, start_index)
        return self.get_fix(fix_index)

    def get_sub_trajectory(self, start_index, end_index):
        portion_of_fixes = self._fixes[start_index: end_index + 1]
        # Risky
        return Trajectory(portion_of_fixes)

    def get_internal_distance(self):
        distance_sum = 0
        size = self.get_size()
        for i in range(0, size - 1):
            distance_sum += self._fixes[i].distance_to(self._fixes[i + 1])

        return distance_sum
