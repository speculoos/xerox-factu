
import sys
import requests
import io
import csv
from pathlib import Path

KEYS = [
    'Job Index ',  # 0
    'Protocol',
    ' User Name',
    ' Host Name',
    ' File Name',
    ' Job Name',  # 5
    ' Pages(Sheets) Printed',
    ' Pages(Sides) Printed',
    ' Start Time',
    ' End Time',
    ' Interpreter Duration',  # 10
    ' Paper Type',
    ' Custom Name',
    ' Paper Size',
    ' Standard Capacity Cyan Used',
    ' Standard Capacity Magenta Used',  # 15
    ' Standard Capacity Yellow Used',
    ' Standard Capacity Black Used',
    ' High Capacity Cyan Used',
    ' High Capacity Magenta Used',
    ' High Capacity Yellow Used',  # 20
    ' High Capacity Black Used',
    'Printer Model Number',
]


def main():
    current_path = Path(sys.argv[1])
    password = sys.argv[2]
    req = requests.get('http://xerox.speculoos/jobacct.dat',
                       auth=('admin', password))
    #  a
    sio = io.StringIO()
    sio.write(req.text)
    sio.seek(0)

    if len(sys.argv) > 3:
        sio = open(sys.argv[3], 'r')

    current_path.touch()
    with current_path.open('r+') as current:
        check_db = dict()
        current_reader = csv.DictReader(current)
        has_headers = False
        for row in current_reader:
            has_headers = True
            start_time = row[KEYS[8]]
            check_db[start_time] = True

        current_writer = csv.DictWriter(current, KEYS)
        new_reader = csv.DictReader(sio, delimiter='\t')

        if not has_headers:
            current_writer.writeheader()
        for row in new_reader:
            start_time = row[KEYS[8]]
            if start_time not in check_db:
                current_writer.writerow(row)


if __name__ == '__main__':
    main()
