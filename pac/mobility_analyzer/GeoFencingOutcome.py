from datetime import datetime
from typing import List, Tuple

from entities.GpsFix import GpsFix
from entities.StayPoint import StayPoint


class GeoFencingOutcome(object):
    """
    Represents the outcome of GeoFencing after analyzing each GpsFix.

    Attributes:
        event_type: The type of the event being reported. For convention:
        -1 = No event detected
        0 (off) = Leaving stay point,
        1 (on) = Arriving stay point,
        2 (off-on) = Leaving and appearing into a new stay point
        stay_point: The stay point causing the event
        event_fix: The timestamp of the occurring event, (it should be extracted from the fix)
        stay_point_2: The second stay point involved in the leaving-arriving case
    """

    TYPE_NO_CHANGE = -1
    TYPE_LEAVING_STAY_POINT = 0
    TYPE_ARRIVING_STAY_POINT = 1
    TYPE_LEAVING_AND_ARRIVING = 2

    def __init__(self, event_type: int, stay_point: Tuple[StayPoint, None], event_fix: GpsFix,
                 stay_point_2: StayPoint = None, detection_fix: GpsFix = None):
        """
        Basic constructor
        :param event_type: The type of the event
        :param stay_point: The causing stay point
        :param event_fix: The gps fix that caused the event in real world
        :param stay_point_2: The second stay point involved (if apply)
        :param detection_fix: The fix that caused the detection of the event, it has a latency with respect of time of event
        """

        self.event_type = event_type
        self.stay_point = stay_point
        self.event_fix = event_fix
        self.stay_point_2 = stay_point_2
        self.detection_fix = detection_fix

    def __str__(self):
        date_format = '%Y-%m-%d %H:%M:%S'
        timestamp_as_string = self.event_fix.timestamp.strftime(date_format)

        if self.event_type == GeoFencingOutcome.TYPE_NO_CHANGE:
            event_type_as_string = "No event change"
        elif self.event_type == GeoFencingOutcome.TYPE_LEAVING_STAY_POINT:
            event_type_as_string = "Leaving stay point"
        elif self.event_type == GeoFencingOutcome.TYPE_ARRIVING_STAY_POINT:
            event_type_as_string = "Arriving to a stay point"
        elif self.event_type == GeoFencingOutcome.TYPE_LEAVING_AND_ARRIVING:
            event_type_as_string = "Leaving and then arriving to a new stay point"
        else:
            raise ValueError('Dunno what event type this is')

        if self.event_type == GeoFencingOutcome.TYPE_NO_CHANGE:
            if self.stay_point is None:
                full_event_as_string = event_type_as_string + ', user is still on trajectory, detected @' \
                                       + timestamp_as_string
            else:
                full_event_as_string = event_type_as_string + ', user is still inside stay point ' + str(
                    self.stay_point) + ', detected @' + timestamp_as_string
        elif self.event_type == GeoFencingOutcome.TYPE_LEAVING_AND_ARRIVING:
            full_event_as_string = event_type_as_string + ' ' + str(self.stay_point) + ', and ' + str(
                self.stay_point_2) + ' @' + timestamp_as_string
        else:
            detection_time_as_string = self.detection_fix.timestamp.strftime(date_format)
            full_event_as_string = '{} {}, @{}, detected @{}'.format(event_type_as_string, self.stay_point,
                                                                     timestamp_as_string,
                                                                     detection_time_as_string)

        return full_event_as_string
