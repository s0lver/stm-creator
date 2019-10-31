from datetime import datetime, timedelta
from typing import List

import Utils
from entities.SimpleVisit import SimpleVisit


class VisitsStreamSplitter(object):
    def __init__(self, start_hour: int, end_hour: int, day: int, visits: List[SimpleVisit]):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.day = day
        self.visits = visits

    def _project_from_single_day(self):
        start_projection = datetime.now()

        departure_calendar = self.visits[0].departure_time  # type: datetime
        # monday is 0 and sunday is 6 in python!!
        departure_day = departure_calendar.weekday()
        days_to_go_back = self._get_amount_of_days_back_to_start_parameter(departure_day)

        if departure_day == self.day:
            start_projection = start_projection.replace(year=departure_calendar.year,
                                                        month=departure_calendar.month,
                                                        day=departure_calendar.day,
                                                        hour=self.start_hour,
                                                        minute=0,
                                                        second=0,
                                                        microsecond=0)
        else:
            start_projection = departure_calendar
            start_projection = start_projection + timedelta(days=-1 * days_to_go_back)
            start_projection = start_projection.replace(hour=self.start_hour, minute=0, second=0, microsecond=0)

        end_projection = self._generate_end_projection_for_day_interval(start_projection)
        return start_projection, end_projection

    def _get_amount_of_days_back_to_start_parameter(self, departure_day):
        return Utils.calculate_days_difference(self.day, departure_day)

    def _generate_end_projection_for_day_interval(self, start_projection):
        """
        Calculates the end projection from the projected start, targeted at day interval queries.
        It adds the days difference between the start and end query parameters
        :param start_projection: The start projection to which time will be added
        :return: A datetime with the projected end.
        """
        end_projection = start_projection

        if Utils.trespassing_day(self.start_hour, self.end_hour):
            end_projection += end_projection + timedelta(days=1)

        end_projection = end_projection.replace(hour=self.end_hour, minute=59, second=59)
        return end_projection

    def _belongs_to_new_window(self, visit: SimpleVisit, projected_end: datetime):
        """
        Finds out whether the specified visit belongs to the next window. This is done by comparing the arrival of the
        visit against the timestamp of the projected end.
        [No null check is done here]
        :param visit: The visit to analyze
        :param projected_end: The projected end
        :return:  True if the visit belongs to the next window, False otherwise
        """
        return visit.arrival_time > projected_end

    def split_visits(self) -> List[List[SimpleVisit]]:
        visit_windows_list = []  # type: List[List[SimpleVisit]]

        if self.visits is None or len(self.visits) == 0:
            return None

        start_projection, end_projection = self._project_from_single_day()

        current_window = []
        for i in range(0, len(self.visits)):
            current_window.append(self.visits[i])

            if (i + 1) == len(self.visits):
                break

            next_visit = self.visits[i + 1]

            if self._belongs_to_new_window(next_visit, end_projection):
                if len(current_window) != 0:
                    visit_windows_list.append(current_window)
                current_window = []

                start_projection = start_projection + timedelta(days=7)
                end_projection = end_projection + timedelta(days=7)

        if len(current_window) != 0:
            visit_windows_list.append(current_window)

        return visit_windows_list
