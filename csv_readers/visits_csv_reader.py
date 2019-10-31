import csv
from datetime import datetime
from typing import List, Iterator, Dict

from entities.GpsFix import GpsFix
from entities.Visit import Visit


def read(file_path: str) -> List[Visit]:
    """
    Returns a list of Visit read from the specified file path
    :param file_path: The path of file to read
    :return: A list of Visit
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    results = []
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        visit = build_visit_from_line(line)
        results.append(visit)

    return results


def read_line_by_line(file_path: str) -> Iterator[Visit]:
    """
    Reads a csv file of visits line by line
    :param file_path: The path of file to read
    :return: A Visit object usable in for each call
    """
    file = open(file_path, 'r', newline='', encoding='utf-8')
    reader = csv.DictReader(file, delimiter=',')
    for line in reader:
        current_visit = build_visit_from_line(line)
        yield current_visit


def build_visit_from_line(line: Dict) -> Visit:
    """
    Builds a Visit object parsing the specified line
    :param line: The line to parse
    :return: A Visit object
    """
    id_visit = int(line["_id"])
    id_stay_point = int(line["idStayPoint"])
    arrival_time = datetime.strptime(line["arrivalTime"], '%Y-%m-%d %H:%M:%S')
    fake_arrival_fix = GpsFix(0, 0, arrival_time, 0, 0, 0)
    departure_time = datetime.strptime(line["departureTime"], '%Y-%m-%d %H:%M:%S')
    fake_departure_fix = GpsFix(0, 0, departure_time, 0, 0, 0)
    # visit = Visit(id_visit, id_stay_point, arrival_time, departure_time)
    visit = Visit(id_visit, id_stay_point, fake_arrival_fix, fake_departure_fix, fake_arrival_fix, fake_departure_fix)
    return visit
