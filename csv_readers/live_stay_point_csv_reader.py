import csv
from datetime import datetime
from typing import List, Iterator, Dict

from entities.LiveStayPoint import LiveStayPoint


def read(file_path: str) -> List[LiveStayPoint]:
    """
    Returns a list of LiveStayPoint read from the specified file path
    :param file_path: The path of file to read
    :return: A list of LiveStayPoint
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    results = []
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        stay_point = build_stay_point_from_line(line)
        results.append(stay_point)

    return results


def read_line_by_line(file_path: str) -> Iterator[LiveStayPoint]:
    """
    Reads a csv file of live stay points (results of an SPD algorithm) line by line
    :param file_path: The path of file to read
    :return: A LiveStayPoint object usable in for each call
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_stay_point = build_stay_point_from_line(line)
        yield current_stay_point


def build_stay_point_from_line(line: Dict) -> LiveStayPoint:
    """
    Builds a StayPoint object parsing the specified line
    :param line: The line to parse
    :return: A StayPoint object
    """
    latitude = float(line["latitude"])
    longitude = float(line["longitude"])
    arrival_time = datetime.strptime(line["arrival_time"], '%Y-%m-%d %H:%M:%S')
    departure_time = datetime.strptime(line["departure_time"], '%Y-%m-%d %H:%M:%S')
    amount_of_fixes = int(line["amount_of_fixes"])
    stay_point = LiveStayPoint(latitude, longitude, arrival_time, departure_time, amount_of_fixes)

    return stay_point
