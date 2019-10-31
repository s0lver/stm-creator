from copy import deepcopy
from datetime import timedelta

from typing import List, Union

from csv_readers import logger_gps_csv_reader
from entities.GpsFix import GpsFix


class LogicGpsReader(object):
    """
    This class tries to read a file of gps fixes according to specifications of time in each reading.
    All file content is put on RAM, so, proceed with caution
    """

    def __init__(self, csv_file_path: str):
        self._fixes = []  # type: List[GpsFix]
        self._read_logger_file(csv_file_path)
        self.first_fix = None
        self.last_fix = None
        self.time_length = -1
        self.amount_fixes = -1
        self._time_pointer = None
        self._index_pointer = -1

        self._reset_attribute_values()

    def _reset_attribute_values(self):
        self.first_fix = self._fixes[0]
        self.last_fix = self._fixes[-1]
        self.time_length = (self.last_fix.timestamp - self.first_fix.timestamp).total_seconds()
        self.amount_fixes = len(self._fixes)
        self._time_pointer = self.first_fix.timestamp
        self._index_pointer = 0

    def get_fix_in_n_seconds(self, n_seconds: int) -> Union[GpsFix, None]:
        """
        Note, call it when you need future dates, otherwise it will behave weird, W-E-I-R-D
        :param n_seconds: the seconds in the future of the desired GpsFix
        :return: The GpsFix collected @ n_seconds from previous delivered fix
        """
        if self._index_pointer == self.amount_fixes:
            return None

        target_time = self._time_pointer + timedelta(seconds=n_seconds)

        # Need to advance until we reach 'that' time
        while self._fixes[self._index_pointer].timestamp < target_time:
            self._index_pointer += 1
            if self._index_pointer == self.amount_fixes:
                return None

        self._time_pointer = target_time
        if (self._fixes[self._index_pointer].timestamp - target_time).total_seconds() == 0:
            # this is the one!
            return self._fixes[self._index_pointer]
        else:
            # need to report the previous fix (spatial information) but with the requested timestamp
            previous_fix = deepcopy(self._fixes[self._index_pointer - 1])
            previous_fix.timestamp = target_time
            return previous_fix

    def read_whole_file_with_one_second(self):
        fix = self.get_fix_in_n_seconds(0)
        fixes_one_hert = []
        while fix is not None:
            fixes_one_hert.append(fix)
            fix = self.get_fix_in_n_seconds(1)

        return fixes_one_hert

    def _read_logger_file(self, csv_file_path):
        self._fixes = logger_gps_csv_reader.read(csv_file_path)

    def get_read_fixes(self) -> List[GpsFix]:
        return self._fixes

    def reset_position(self):
        self._reset_attribute_values()
