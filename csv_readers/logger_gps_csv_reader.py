import csv
from datetime import datetime, timedelta
from typing import List, Iterator, Dict

from entities.GpsFix import GpsFix


def read(file_path: str, date_format='%Y/%m/%d %H:%M:%S') -> List[GpsFix]:
    """
    Returns a list of GpsFix read from the specified file path
    :param file_path: The path of file to read
    :param date_format: The date format to use
    :return: A list of GpsFix
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    results = []
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_fix = build_fix_from_line(line, date_format)

        results.append(current_fix)

    return results


def read_line_by_line(file_path: str) -> Iterator[GpsFix]:
    """
    Reads a csv file of fixes line by line
    :param file_path:
    :return: A GpsFix object usable in for each call
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_fix = build_fix_from_line(line)
        yield current_fix


def _is_summer_time(date: datetime):
    summer_time_start_month = 4  # april
    summer_time_start_day = 3  # april 3rd

    summer_time_end_month = 10  # october
    summer_time_end_day = 30 # october 30th

    if summer_time_start_month <= date.month <= summer_time_end_month:
        if date.month == summer_time_start_month:
            # within start month
            if date.day >= summer_time_start_day:
                return True
        elif date.month == summer_time_end_month:
            # within end month
            if date.day <= summer_time_end_day:
                return True
        else:
            # for any of other inside-months
            return True

    return False


def build_fix_from_line(line: Dict, date_format) -> GpsFix:
    """
    Builds a GpsFix parsing the specified line
    :param line: The line to parse
    :param date_format: The date format to use
    :return: A GpsFix object
    """
    str_datetime = line["UTC DATE"] + ' ' + line["UTC TIME"]
    date = datetime.strptime(str_datetime, date_format)

    if _is_summer_time(date):
        date = date - timedelta(hours=5)
    else:
        date = date - timedelta(hours=6)

    latitude = float(line["LATITUDE"])
    if line["N/S"] == "S":
        latitude *= -1

    longitude = float(line["LONGITUDE"])
    if line["E/W"] == "W":
        longitude *= -1

    battery_level = 0
    speed = float(line["SPEED"])
    altitude = float(line["ALTITUDE"])
    accuracy = 0
    detected_activity = 0
    fix = GpsFix(latitude=latitude, longitude=longitude, timestamp=date, altitude=altitude,
                 accuracy=accuracy, speed=speed, battery_level=battery_level,
                 detected_activity=detected_activity)
    return fix
