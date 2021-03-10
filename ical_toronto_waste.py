import csv
import logging
import sys
from collections import defaultdict
from datetime import datetime


logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

CALENDAR_OUTPUT_DIR = 'output/'
CSV_OUTPUT_DIR = 'csv/'
ICS_OUTPUT_DIR = 'ics/'

CSV_OUT_PATH = CALENDAR_OUTPUT_DIR + CSV_OUTPUT_DIR
ICS_OUT_PATH = CALENDAR_OUTPUT_DIR + ICS_OUTPUT_DIR

CALENDAR_INPUT_NAME = 'Calendars.csv'

INPUT_DATE_FORMAT = '%Y-%m-%d'
CSV_DATE_FORMAT = '%m-%d-%y'
ICS_DATE_FORMAT = '%Y%m%d'


def main():
    data = process_data()
    write_csv(data)
    write_ics(data)


def process_data():
    logging.info('Parsing City of Toronto Open Data')

    data = defaultdict(list)
    with open(CALENDAR_INPUT_NAME) as calendar_file:
        lines = csv.reader(calendar_file)

        # Skip header
        lines.__next__()

        for row in lines:
            pickup = Pickup(row)
            data[pickup.calendar].append(pickup)

    return data


def write_csv(data):
    logging.info('Writing CSV calendars')

    for calendar in data:
        pickups = data[calendar]
        logging.info('Writing %s CSV', calendar)

        with open(f'{CSV_OUT_PATH}{calendar}.csv', 'w') as csv_file:

            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(
                ["Subject", "Start Date", "All Day Event", "Description"])

            for pickup in pickups:
                start_date = datetime.strftime(pickup.day, CSV_DATE_FORMAT)
                csv_writer.writerow(
                    [pickup.subject(), start_date, 'TRUE',
                     f'{pickup.description()} - See {pickup.url()}'])

    logging.info('Finished writing CSV calendars')


def write_ics(data):
    logging.info('Writing ICS calendars')

    for calendar in data:
        pickups = data[calendar]

        logging.info('Writing %s ICS', calendar)

        with open(f'{ICS_OUT_PATH}{calendar}.ics', 'w') as ics_file:
            ics_file.write('BEGIN:VCALENDAR\n')
            ics_file.write('VERSION:2.0\n')
            ics_file.write('CALSCALE:GREGORIAN\n')
            ics_file.write('METHOD:PUBLISH\n')
            ics_file.write(f'X-WR-CALNAME:{calendar} Waste Pickup\n')
            ics_file.write('X-WR-TIMEZONE:America/Toronto\n')
            ics_file.write('X-WR-CALDESC:\n')

            for pickup in pickups:
                start_date = datetime.strftime(pickup.day, ICS_DATE_FORMAT)
                ics_file.write('BEGIN:VEVENT\n')
                ics_file.write(f'URL;VALUE=URI:{pickup.url()}\n')
                ics_file.write(f'SUMMARY:{pickup.subject()}\n')
                ics_file.write(f'DTSTART;VALUE=DATE:{start_date}\n')
                ics_file.write('DURATION;P1D\n')
                ics_file.write(f'DESCRIPTION:{pickup.description()}\n')
                ics_file.write('END:VEVENT\n')

            ics_file.write('END:VCALENDAR')

    logging.info('Finished writing ICS calendars')


SUBJECT_GARBAGE = '🗑 Garbage Day'
SUBJECT_RECYCLING = '♻️ Recycling Day'
SUBJECT_CHRISTMAS_TREE = '🎄 Christmas Tree/Garbage Day'

URL_GARBAGE = ('https://www.toronto.ca/services-payments/recycling-organics-garbage/'
               'houses/what-goes-in-my-green-bin/')
URL_RECYCLING = 'https://www.toronto.ca/services-payments/recycling-organics-garbage/waste-wizard/'


class Pickup:
    def __init__(self, row):
        [_, self.calendar, day, green_bin, garbage,
            recycling, yard_waste, christmas_tree] = row
        self.day = datetime.strptime(day, INPUT_DATE_FORMAT)
        self.green_bin = green_bin != '0'
        self.garbage = garbage != '0'
        self.recycling = recycling != '0'
        self.yard_waste = yard_waste != '0'
        self.christmas_tree = christmas_tree != '0'

    def subject(self):
        if self.christmas_tree:
            return SUBJECT_CHRISTMAS_TREE
        if self.recycling:
            return SUBJECT_RECYCLING

        return SUBJECT_GARBAGE

    def description(self):
        types = []
        if self.christmas_tree:
            types.append('Christmas Tree')
        if self.garbage:
            types.append('Garbage')
        if self.recycling:
            types.append('Recycling')
        if self.green_bin:
            types.append('Green Bin')
        if self.yard_waste:
            types.append('Yard Waste')
        return ('/').join(types)

    def url(self):
        if self.recycling:
            return URL_RECYCLING
        return URL_GARBAGE


if __name__ == "__main__":
    main()
