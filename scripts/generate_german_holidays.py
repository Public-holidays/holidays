#!/usr/bin/env python3
"""
German Public Holidays ICS Generator
Generates ICS calendar files for German public holidays by Bundesland
Based on German Feiertagsgesetze
"""

from datetime import datetime, timedelta
import os
from holiday_utils import (
    calculate_easter,
    create_ics_event,
    normalize_filename,
    generate_ics_header,
    write_ics_file,
)

bundeslaender = [
    'Baden-Württemberg',
    'Bayern',
    'Berlin',
    'Brandenburg',
    'Bremen',
    'Hamburg',
    'Hessen',
    'Mecklenburg-Vorpommern',
    'Niedersachsen',
    'Nordrhein-Westfalen',
    'Rheinland-Pfalz',
    'Saarland',
    'Sachsen',
    'Sachsen-Anhalt',
    'Schleswig-Holstein',
    'Thüringen'
]

def get_buss_und_bettag(year):
    """
    Calculate Buß- und Bettag (German Day of Repentance and Prayer)
    Wednesday before the last Sunday before the 1st Advent
    = Last Wednesday before November 23

    Args:
        year: Year

    Returns:
        datetime object
    """
    # Find first day of Advent: 4th Sunday before Dec 25
    dec_25 = datetime(year, 12, 25)
    days_from_sunday = (dec_25.weekday() + 1) % 7
    fourth_advent_sunday = dec_25 - timedelta(days=days_from_sunday)
    first_advent_sunday = fourth_advent_sunday - timedelta(days=21)

    # Buß- und Bettag is 11 days before 1st Advent (Wednesday)
    return first_advent_sunday - timedelta(days=11)


def get_german_holidays(year, bundesland):
    """
    Returns list of public holidays for a given year and Bundesland
    Based on Wikipedia: https://de.wikipedia.org/wiki/Feiertag_(Deutschland)
    """
    easter = calculate_easter(year)

    # Nationwide holidays (all 16 Bundesländer)
    holidays = [
        (datetime(year, 1, 1), "Neujahr", "New Year's Day", "bundesweit"),
        (easter - timedelta(days=2), "Karfreitag", "Good Friday", "bundesweit"),
        (easter + timedelta(days=1), "Ostermontag", "Easter Monday", "bundesweit"),
        (datetime(year, 5, 1), "Tag der Arbeit", "Labour Day", "bundesweit"),
        (easter + timedelta(days=39), "Christi Himmelfahrt", "Ascension Day", "bundesweit"),
        (easter + timedelta(days=50), "Pfingstmontag", "Whit Monday", "bundesweit"),
        (datetime(year, 10, 3), "Tag der Deutschen Einheit", "German Unity Day", "bundesweit"),
        (datetime(year, 12, 25), "1. Weihnachtsfeiertag", "Christmas Day", "bundesweit"),
        (datetime(year, 12, 26), "2. Weihnachtsfeiertag", "St. Stephen's Day", "bundesweit"),
    ]

    # Heilige Drei Könige (Epiphany) - Jan 6
    # BW, BY, ST
    if bundesland in ['Baden-Württemberg', 'Bayern', 'Sachsen-Anhalt']:
        holidays.append((datetime(year, 1, 6), "Heilige Drei Könige", "Epiphany", "regional"))

    # Internationaler Frauentag - March 8
    # BE, MV (since 2023)
    if bundesland in ['Berlin', 'Mecklenburg-Vorpommern']:
        holidays.append((datetime(year, 3, 8), "Internationaler Frauentag", "International Women's Day", "regional"))

    # Fronleichnam - 60 days after Easter
    # BW, BY, HE, NW, RP, SL
    # Also in parts of SN and TH
    if bundesland in ['Baden-Württemberg', 'Bayern', 'Hessen', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland']:
        holidays.append((easter + timedelta(days=60), "Fronleichnam", "Corpus Christi", "regional"))

    # Augsburger Friedensfest - August 8 (only city of Augsburg, Bavaria)
    # Note: Only in Augsburg city, not all of Bavaria
    if bundesland == 'Bayern':
        holidays.append(
            (datetime(year, 8, 8), "Augsburger Friedensfest", "Augsburg Peace Festival", "nur Stadt Augsburg"))

    # Mariä Himmelfahrt - August 15
    # SL, BY (only in predominantly Catholic municipalities)
    if bundesland == 'Saarland':
        holidays.append((datetime(year, 8, 15), "Mariä Himmelfahrt", "Assumption of Mary", "regional"))
    elif bundesland == 'Bayern':
        holidays.append((datetime(year, 8, 15), "Mariä Himmelfahrt", "Assumption of Mary",
                         "nur in überwiegend katholischen Gemeinden"))

    # Weltkindertag - September 20
    # TH (since 2019)
    if bundesland == 'Thüringen':
        holidays.append((datetime(year, 9, 20), "Weltkindertag", "World Children's Day", "regional"))

    # Reformationstag - October 31
    # BB, MV, SN, ST, TH, HB, HH, NI, SH (since 2018)
    if bundesland in ['Brandenburg', 'Mecklenburg-Vorpommern', 'Sachsen', 'Sachsen-Anhalt', 'Thüringen',
                      'Bremen', 'Hamburg', 'Niedersachsen', 'Schleswig-Holstein']:
        holidays.append((datetime(year, 10, 31), "Reformationstag", "Reformation Day", "regional"))

    # Allerheiligen - November 1
    # BW, BY, NW, RP, SL
    if bundesland in ['Baden-Württemberg', 'Bayern', 'Nordrhein-Westfalen', 'Rheinland-Pfalz', 'Saarland']:
        holidays.append((datetime(year, 11, 1), "Allerheiligen", "All Saints' Day", "regional"))

    # Buß- und Bettag - Wednesday before the last Sunday before 1st Advent
    # SN only
    if bundesland == 'Sachsen':
        holidays.append((get_buss_und_bettag(year), "Buß- und Bettag", "Day of Repentance and Prayer", "regional"))

    # Sort by date
    holidays.sort(key=lambda x: x[0])

    return holidays

def create_ics_content(holidays, bundesland, description):
    """
    Create ICS content from a list of holidays

    Args:
        holidays: List of (date, name_de, name_en, scope) tuples
        bundesland: Name of the Bundesland
        description: Calendar description

    Returns:
        List of ICS content lines
    """
    ics_lines = generate_ics_header(f"Feiertage {bundesland}", description)

    for date, name_de, name_en, scope in holidays:
        uid = f"{date.strftime('%Y%m%d')}-{name_en.replace(' ', '-').lower()}-{bundesland.lower().replace(' ', '-')}@german-holidays.local"
        ics_lines.extend(create_ics_event(date, date, name_de, f"{name_en} - {scope}", uid))

    ics_lines.append("END:VCALENDAR")
    return ics_lines

def generate_ics(year, bundesland, output_dir="output"):
    """
    Generate ICS file for German holidays for a specific Bundesland
    """
    holidays = get_german_holidays(year, bundesland)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate ICS content
    ics_lines = create_ics_content(holidays, bundesland, f"Gesetzliche Feiertage in {bundesland}, Deutschland")

    # Convert Bundesland name to filename-safe format
    bundesland_filename = normalize_filename(bundesland.lower())

    filename = f"{output_dir}/german_holidays_{bundesland_filename}.ics"
    write_ics_file(filename, ics_lines)

    print(f"✓ Generated: {filename}")
    return filename


def generate_rolling_calendar(bundesland, output_dir="output"):
    """Generate a rolling calendar with current - 1 to current + 5 years"""
    current_year = datetime.now().year
    start_year = current_year - 1
    end_year = current_year + 5

    print(f"Generating rolling calendar for {bundesland} ({start_year}-{end_year})...")

    all_holidays = []
    for year in range(start_year, end_year + 1):
        all_holidays.extend(get_german_holidays(year, bundesland))

    all_holidays.sort(key=lambda x: x[0])

    os.makedirs(output_dir, exist_ok=True)

    # Generate ICS content
    ics_lines = create_ics_content(all_holidays, bundesland, f"Gesetzliche Feiertage in {bundesland}, Deutschland ({start_year}-{end_year})")


    bundesland_filename = normalize_filename(bundesland.lower())

    filename = f"{output_dir}/german_holidays_{bundesland_filename}.ics"
    write_ics_file(filename, ics_lines)

    print(f"✓ Generated rolling calendar: {filename}")
    print(f"  └─ Contains {len(all_holidays)} holidays from {start_year} to {end_year}")
    return filename


def generate_all_bundeslaender(start_year, end_year):
    """Generate ICS files for all 16 Bundesländer"""

    print("=" * 60)
    print(f"German Public Holidays Generator ({start_year}-{end_year})")
    print("=" * 60)
    print()

    for bundesland in bundeslaender:
        for year in range(start_year, end_year + 1):
            generate_ics(year, bundesland)

    print()
    print(f"All calendars generated in 'output/' directory")


def generate_all_rolling():
    """Generate rolling calendars for all Bundesländer"""

    print("=" * 60)
    print("German Public Holidays - Rolling Calendars")
    print("=" * 60)
    print()

    for bundesland in bundeslaender:
        generate_rolling_calendar(bundesland)

    print()
    print("All rolling calendars generated!")


if __name__ == "__main__":
    current_year = datetime.now().year

    # Generate rolling calendars (recommended)
    generate_all_rolling()

    # Optionally generate individual years
    # generate_all_bundeslaender(current_year, current_year + 2)

    # Print example for verification
    print()
    print("=" * 60)
    print(f"Example: Bayern Holidays {current_year}")
    print("=" * 60)
    for date, name_de, name_en, scope in get_german_holidays(current_year, 'Bayern'):
        print(f"{date.strftime('%Y-%m-%d')} - {name_de} ({scope})")
