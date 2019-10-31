import csv
from typing import List, Iterator, Dict

from entities.StayPoint import StayPoint


def read(file_path: str) -> List[StayPoint]:
    """
    Returns a list of StayPoint read from the specified file path
    :param file_path: The path of file to read
    :return: A list of StayPoint
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    results = []
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        stay_point = build_stay_point_from_line(line)
        results.append(stay_point)

    return results


def read_line_by_line(file_path: str) -> Iterator[StayPoint]:
    """
    Reads a csv file of stay points line by line
    :param file_path: The path of file to read
    :return: A StayPoint object usable in for each call
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_stay_point = build_stay_point_from_line(line)
        yield current_stay_point


def build_stay_point_from_line(line: Dict) -> StayPoint:
    """
    Builds a StayPoint object parsing the specified line
    :param line: The line to parse
    :return: A StayPoint object
    """
    id_stay_point = int(line["_id"])
    latitude = float(line["latitude"])
    longitude = float(line["longitude"])
    visit_count = int(line["visitCount"])
    stay_point = StayPoint(id_stay_point, latitude, longitude, visit_count)

    return stay_point

