import csv
from datetime import datetime
from typing import List, Iterator, Dict

from entities.GpsFix import GpsFix


def read(file_path: str) -> List[GpsFix]:
    """
    Returns a list of GpsFix read from the specified file path
    :param file_path: The path of file to read
    :return: A list of GpsFix
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    results = []
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_fix = build_fix_from_line(line)

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


def build_fix_from_line(line: Dict) -> GpsFix:
    """
    Builds a GpsFix parsing the specified line
    :param line: The line to parse
    :return: A GpsFix object
    """
    date = datetime.strptime(line["timestamp"], '%Y-%m-%d %H:%M:%S')
    latitude = float(line["latitude"])
    longitude = float(line["longitude"])
    battery_level = float(line["batteryLevel"])
    speed = float(line["speed"])
    altitude = float(line["altitude"])
    accuracy = float(line["accuracy"])
    detected_activity = int(line["detectedActivity"])
    fix = GpsFix(latitude=latitude, longitude=longitude, timestamp=date, altitude=altitude,
                 accuracy=accuracy, speed=speed, battery_level=battery_level,
                 detected_activity=detected_activity)
    return fix
