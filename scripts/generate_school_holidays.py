#!/usr/bin/env python3
"""
Austrian School Holidays ICS Generator
Generates ICS calendar files for school holidays in each Bundesland
Based on Austrian school law (Schulzeitgesetz)
"""

from datetime import datetime, timedelta
import os
from holiday_utils import calculate_easter, generate_ics_header, create_ics_event, write_ics_file

def get_first_monday_of_month(year, month):
    """Get the first Monday of a given month"""
    first_day = datetime(year, month, 1)
    days_until_monday = (7 - first_day.weekday()) % 7
    if first_day.weekday() == 0:
        return first_day
    return first_day + timedelta(days=days_until_monday)


def get_nth_monday_of_month(year, month, n):
    """Get the nth Monday of a given month (n=1 for first, n=2 for second, etc.)"""
    first_monday = get_first_monday_of_month(year, month)
    return first_monday + timedelta(weeks=n - 1)


def get_first_saturday_in_range(year, month, start_day, end_day):
    """
    Get the first Saturday that falls within the date range
    Example: first Saturday between June 28 and July 4
    """
    start_date = datetime(year, month, start_day)

    days_until_saturday = (5 - start_date.weekday()) % 7
    if start_date.weekday() == 5:
        return start_date
    return start_date + timedelta(days=days_until_saturday)


def calculate_school_year_start(year, bundesland):
    """
    Calculate when the school year starts for a given Bundesland
    § 2 (1): Burgenland, Niederösterreich, Wien: first Monday in September
             Others: second Monday in September
    """
    group_1 = ['Burgenland', 'Niederösterreich', 'Wien']

    if bundesland in group_1:
        return get_nth_monday_of_month(year, 9, 1)
    else:
        return get_nth_monday_of_month(year, 9, 2)


def calculate_christmas_break(year):
    """
    Calculate Christmas break (Weihnachtsferien)
    § 2 (4) 3.: December 24 to January 6 (inclusive)
    """
    start = datetime(year, 12, 24)
    end = datetime(year + 1, 1, 6)
    return start, end


def calculate_semester_break(year, bundesland):
    """
    Calculate semester break (Semesterferien)
    § 2 (2) 1. b) and § 2 (4) 5.:
    - Niederösterreich, Wien: first Monday in February
    - Burgenland, Kärnten, Salzburg, Tirol, Vorarlberg: second Monday in February
    - Oberösterreich, Steiermark: third Monday in February
    Duration: Monday to Saturday (one week)
    """
    group_1 = ['Niederösterreich', 'Wien']
    group_2 = ['Burgenland', 'Kärnten', 'Salzburg', 'Tirol', 'Vorarlberg']
    group_3 = ['Oberösterreich', 'Steiermark']

    if bundesland in group_1:
        start = get_nth_monday_of_month(year, 2, 1)
    elif bundesland in group_2:
        start = get_nth_monday_of_month(year, 2, 2)
    elif bundesland in group_3:
        start = get_nth_monday_of_month(year, 2, 3)
    else:
        raise ValueError(f"Unknown Bundesland: {bundesland}")

    # Monday to Saturday (6 days)
    end = start + timedelta(days=5)
    return start, end


def calculate_easter_break(year):
    """
    Calculate Easter break (Osterferien)
    § 2 (4) 6.: Saturday before Palm Sunday to Easter Monday (inclusive)
    Palm Sunday is one week before Easter Sunday
    """
    easter = calculate_easter(year)
    palm_sunday = easter - timedelta(days=7)

    # Saturday before Palm Sunday
    saturday_before = palm_sunday - timedelta(days=1)

    # Easter Monday
    easter_monday = easter + timedelta(days=1)

    return saturday_before, easter_monday


def calculate_whit_break(year):
    """
    Calculate Whit/Pentecost break (Pfingstferien)
    § 2 (4) 7.: Saturday before Whit Sunday to Whit Monday (inclusive)
    Whit Sunday is 49 days after Easter
    """
    easter = calculate_easter(year)
    whit_sunday = easter + timedelta(days=49)

    # Saturday before Whit Sunday
    saturday_before = whit_sunday - timedelta(days=1)

    # Whit Monday
    whit_monday = whit_sunday + timedelta(days=1)

    return saturday_before, whit_monday


def calculate_autumn_break(year):
    """
    Calculate autumn break (Herbstferien)
    § 2 (4) 8.: October 27 to October 31 (inclusive)
    """
    start = datetime(year, 10, 27)
    end = datetime(year, 10, 31)
    return start, end


def calculate_summer_holidays(year, bundesland):
    """
    Calculate summer holidays (Hauptferien)
    § 2 (2) 2.:
    - Burgenland, Niederösterreich, Wien: Saturday between June 28 - July 4
    - Others: Saturday between July 5 - July 11
    Ends the day before the school year starts (in September of the SAME year)

    The school year that starts in September is named after that year
    (e.g., school year 2025/2026 starts in September 2025)
    """
    group_1 = ['Burgenland', 'Niederösterreich', 'Wien']

    if bundesland in group_1:
        start = get_first_saturday_in_range(year, 6, 28, 4)
        if start.month == 7 and start.day > 4:
            start = get_first_saturday_in_range(year, 6, 28, 30)
    else:
        start = get_first_saturday_in_range(year, 7, 5, 11)

    # End date is the Sunday before school year starts in September of the SAME year
    school_year_start = calculate_school_year_start(year, bundesland)
    end = school_year_start - timedelta(days=1)

    return start, end


def get_landespatron_day(year, bundesland):
    """
    Get the Landespatron (patron saint) day for a Bundesland
    § 2 (4) 2.: School-free on the day of the Landespatron
    Returns (date, name_de, name_en) or None if no patron day
    """
    landespatron_days = {
        'Kärnten': (datetime(year, 3, 19), "Hl. Josef", "St. Joseph"),
        'Steiermark': (datetime(year, 3, 19), "Hl. Josef", "St. Joseph"),
        'Tirol': (datetime(year, 3, 19), "Hl. Josef", "St. Joseph"),
        'Vorarlberg': (datetime(year, 3, 19), "Hl. Josef", "St. Joseph"),
        'Oberösterreich': (datetime(year, 5, 4), "Hl. Florian", "St. Florian"),
        'Salzburg': (datetime(year, 9, 24), "Hl. Rupert", "St. Rupert"),
        'Burgenland': (datetime(year, 11, 11), "Hl. Martin", "St. Martin"),
        'Wien': (datetime(year, 11, 15), "Hl. Leopold", "St. Leopold"),
        'Niederösterreich': (datetime(year, 11, 15), "Hl. Leopold", "St. Leopold"),
    }

    return landespatron_days.get(bundesland)


def get_landesfeiertag(year, bundesland):
    """
    Get additional Landesfeiertag (state holiday) if applicable
    Kärnten has an additional day: Tag der Volksabstimmung (October 10)
    Returns (date, name_de, name_en) or None
    """
    if bundesland == 'Kärnten':
        return (datetime(year, 10, 10), "Tag der Volksabstimmung", "Carinthian Plebiscite Day")
    return None


def get_school_holidays(year, bundesland):
    """
    Get all school holidays for a given year and Bundesland
    Returns list of (start_date, end_date, name_de, name_en)

    Note: Christmas break spans two years, so it appears in the year it starts
    """
    holidays = []

    # Landespatron day (single day, varies by Bundesland)
    landespatron = get_landespatron_day(year, bundesland)
    if landespatron:
        date, name_de, name_en = landespatron
        holidays.append((
            date,
            date,
            name_de,
            name_en
        ))

    # Additional Landesfeiertag (Kärnten only)
    landesfeiertag = get_landesfeiertag(year, bundesland)
    if landesfeiertag:
        date, name_de, name_en = landesfeiertag
        holidays.append((
            date,
            date,
            name_de,
            name_en
        ))

    # Semester break (February)
    sem_start, sem_end = calculate_semester_break(year, bundesland)
    holidays.append((
        sem_start,
        sem_end,
        "Semesterferien",
        "Semester Break"
    ))

    # Easter break (March/April)
    easter_start, easter_end = calculate_easter_break(year)
    holidays.append((
        easter_start,
        easter_end,
        "Osterferien",
        "Easter Break"
    ))

    # Whit/Pentecost break (May/June)
    whit_start, whit_end = calculate_whit_break(year)
    holidays.append((
        whit_start,
        whit_end,
        "Pfingstferien",
        "Whit Break"
    ))

    # Summer holidays (July-September)
    summer_start, summer_end = calculate_summer_holidays(year, bundesland)
    holidays.append((
        summer_start,
        summer_end,
        "Sommerferien",
        "Summer Holidays"
    ))

    # Autumn break (October)
    autumn_start, autumn_end = calculate_autumn_break(year)
    holidays.append((
        autumn_start,
        autumn_end,
        "Herbstferien",
        "Autumn Break"
    ))

    # Christmas break (December-January)
    christmas_start, christmas_end = calculate_christmas_break(year)
    holidays.append((
        christmas_start,
        christmas_end,
        "Weihnachtsferien",
        "Christmas Break"
    ))

    return holidays


def generate_school_holiday_ics(bundesland, start_year, end_year, output_dir="output/school"):
    """
    Generate ICS file for school holidays in a specific Bundesland
    """
    os.makedirs(output_dir, exist_ok=True)

    # Collect all holidays across years
    all_holidays = []
    for year in range(start_year, end_year + 1):
        all_holidays.extend(get_school_holidays(year, bundesland))

    # Sort by date
    all_holidays.sort(key=lambda x: x[0])

    # Generate ICS content
    ics_lines = generate_ics_header(bundesland, f"Schulferien in {bundesland}, Österreich ({start_year}-{end_year + 1})")

    for start_date, end_date, name_de, name_en in all_holidays:
        # ICS events are inclusive, but DTEND is exclusive, so add 1 day
        dtend = end_date + timedelta(days=1)

        uid = f"{start_date.strftime('%Y%m%d')}-{name_en.replace(' ', '-').lower()}-{bundesland.lower()}@austrian-school-holidays.local"

        ics_lines.extend(create_ics_event(start_date, dtend, name_de, f"{name_en} - Schulferien in {bundesland}", uid))

    ics_lines.append("END:VCALENDAR")

    # Write to file
    # Convert umlauts for filename
    bundesland_filename = (bundesland.lower()
                           .replace('ä', 'ae')
                           .replace('ö', 'oe')
                           .replace('ü', 'ue'))
    filename = f"{output_dir}/school_holidays_{bundesland_filename}.ics"

    write_ics_file(filename, ics_lines)

    return filename


def generate_all_bundeslaender(start_year, end_year):
    """
    Generate school holiday calendars for all Bundesländer
    """
    bundeslaender = [
        'Burgenland',
        'Kärnten',
        'Niederösterreich',
        'Oberösterreich',
        'Salzburg',
        'Steiermark',
        'Tirol',
        'Vorarlberg',
        'Wien'
    ]

    print("=" * 60)
    print(f"Austrian School Holidays Generator ({start_year}-{end_year + 1})")
    print("=" * 60)
    print()

    for bundesland in bundeslaender:
        filename = generate_school_holiday_ics(bundesland, start_year, end_year)
        print(f"✓ Generated: {filename}")

    print()
    print(f"All school holiday calendars generated in 'output/school/' directory")


if __name__ == "__main__":
    current_year = datetime.now().year

    # Generate for current year and next 5 years
    generate_all_bundeslaender(current_year, current_year + 5)

    # Print example for verification
    print()
    print("=" * 60)
    print(f"Example: Wien School Holidays {current_year}/{current_year + 1}")
    print("=" * 60)
    for start_date, end_date, name_de, name_en in get_school_holidays(current_year, 'Wien'):
        duration = (end_date - start_date).days + 1
        print(f"{name_de}:")
        print(f"  {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({duration} days)")