#!/usr/bin/env python3
"""
Austrian Public Holidays ICS Generator
Generates ICS calendar files for Austrian national holidays
"""

from datetime import datetime, timedelta
import os
from holiday_utils import calculate_easter, generate_ics_header, create_ics_event, write_ics_file

def get_austrian_holidays(year):
    """
    Returns list of all 13 Austrian national public holidays for given year
    """
    easter = calculate_easter(year)

    holidays = [
        # Fixed holidays
        (datetime(year, 1, 1), "Neujahr", "New Year's Day"),
        (datetime(year, 1, 6), "Heilige Drei Könige", "Epiphany"),
        (datetime(year, 5, 1), "Staatsfeiertag", "Labour Day"),
        (datetime(year, 8, 15), "Mariä Himmelfahrt", "Assumption of Mary"),
        (datetime(year, 10, 26), "Nationalfeiertag", "National Day"),
        (datetime(year, 11, 1), "Allerheiligen", "All Saints' Day"),
        (datetime(year, 12, 8), "Mariä Empfängnis", "Immaculate Conception"),
        (datetime(year, 12, 25), "Christtag", "Christmas Day"),
        (datetime(year, 12, 26), "Stefanitag", "St. Stephen's Day"),

        # Easter-dependent holidays
        (easter + timedelta(days=1), "Ostermontag", "Easter Monday"),
        (easter + timedelta(days=39), "Christi Himmelfahrt", "Ascension Day"),
        (easter + timedelta(days=50), "Pfingstmontag", "Whit Monday"),
        (easter + timedelta(days=60), "Fronleichnam", "Corpus Christi"),
    ]

    # Sort by date
    holidays.sort(key=lambda x: x[0])

    return holidays


def generate_ics(year, output_dir="output"):
    """
    Generate ICS file for Austrian holidays
    """
    holidays = get_austrian_holidays(year)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate ICS content
    ics_lines = generate_ics_header("Österreichische Feiertage", "Gesetzliche Feiertage in Österreich")

    for date, name_de, name_en in holidays:
        # Create unique ID
        uid = f"{date.strftime('%Y%m%d')}-{name_en.replace(' ', '-').lower()}@austrian-holidays.local"

        ics_lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{date.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{(date + timedelta(days=1)).strftime('%Y%m%d')}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"UID:{uid}",
            f"SUMMARY:{name_de}",
            f"DESCRIPTION:{name_en} - Gesetzlicher Feiertag in Österreich",
            "TRANSP:TRANSPARENT",
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "END:VEVENT"
        ])

    ics_lines.append("END:VCALENDAR")

    # Write to file

    filename = f"{output_dir}/austrian_holidays_{year}.ics"
    write_ics_file(filename, ics_lines)

    print(f"✓ Generated: {filename}")
    return filename


def generate_rolling_calendar(output_dir="output"):
    """
    Generate a rolling calendar with extended time range
    (current year - 1 to current year + 5)
    """
    current_year = datetime.now().year
    start_year = current_year - 1
    end_year = current_year + 5

    print(f"Generating rolling calendar ({start_year}-{end_year})...")

    # Collect all holidays across the date range
    all_holidays = []
    for year in range(start_year, end_year + 1):
        all_holidays.extend(get_austrian_holidays(year))

    # Sort by date
    all_holidays.sort(key=lambda x: x[0])

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate ICS content
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Austrian Holidays//AT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Österreichische Feiertage",
        "X-WR-TIMEZONE:Europe/Vienna",
        f"X-WR-CALDESC:Gesetzliche Feiertage in Österreich ({start_year}-{end_year})",
        f"X-GENERATION-TIME:{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}"
    ]

    for date, name_de, name_en in all_holidays:
        # Create unique ID
        uid = f"{date.strftime('%Y%m%d')}-{name_en.replace(' ', '-').lower()}@austrian-holidays.local"

        ics_lines.extend(create_ics_event(date, date, name_de, f"{name_en} - Gesetzlicher Feiertag in Österreich", uid))

    ics_lines.append("END:VCALENDAR")

    # Write to file
    filename = f"{output_dir}/austrian_holidays.ics"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\r\n'.join(ics_lines))

    print(f"✓ Generated rolling calendar: {filename}")
    print(f"  └─ Contains {len(all_holidays)} holidays from {start_year} to {end_year}")
    return filename


def generate_multi_year(start_year, end_year, output_dir="output"):
    """
    Generate individual ICS files for multiple years
    """
    print(f"\nGenerating individual year calendars ({start_year}-{end_year})...")

    for year in range(start_year, end_year + 1):
        generate_ics(year, output_dir)

    print(f"\nAll files generated in '{output_dir}/' directory")


if __name__ == "__main__":
    current_year = datetime.now().year

    print("=" * 60)
    print("Austrian Holiday Calendar Generator")
    print("=" * 60)
    print()

    # Generate rolling calendar (primary use case)
    generate_rolling_calendar()

    # Generate individual year files (for reference)
    generate_multi_year(current_year, current_year + 2)

    # Optional: Print holidays for verification
    print("\n" + "=" * 60)
    print(f"Austrian Holidays {current_year}:")
    print("=" * 60)
    for date, name_de, name_en in get_austrian_holidays(current_year):
        print(f"{date.strftime('%Y-%m-%d')} ({date.strftime('%A'):>9}) - {name_de}")