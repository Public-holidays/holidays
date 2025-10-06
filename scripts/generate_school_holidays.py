#!/usr/bin/env python3
"""
Austrian School Holidays ICS Generator
Generates ICS calendar files for school holidays in each Bundesland
Based on Austrian school law (Schulzeitgesetz)
"""

from datetime import datetime, timedelta
import os

def get_first_monday_of_month(year, month):
    """Get the first Monday of a given month"""
    first_day = datetime(year, month, 1)
    days_until_monday = (7 - first_day.weekday()) % 7
    if first_day.weekday() == 0:  # If first day is already Monday
        return first_day
    return first_day + timedelta(days=days_until_monday)

def get_nth_monday_of_month(year, month, n):
    """Get the nth Monday of a given month (n=1 for first, n=2 for second, etc.)"""
    first_monday = get_first_monday_of_month(year, month)
    return first_monday + timedelta(weeks=n-1)

def get_first_saturday_in_range(year, month, start_day, end_day):
    """
    Get the first Saturday that falls within the date range
    Example: first Saturday between June 28 and July 4
    """
    start_date = datetime(year, month, start_day)
    
    # Find the first Saturday from start_date
    days_until_saturday = (5 - start_date.weekday()) % 7
    if start_date.weekday() == 5:  # Already Saturday
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
        return get_nth_monday_of_month(year, 9, 1)  # First Monday
    else:
        return get_nth_monday_of_month(year, 9, 2)  # Second Monday

def calculate_semester_break(year, bundesland):
    """
    Calculate semester break for a given Bundesland
    § 2 (2) 1. b): 
    - Niederösterreich, Wien: first Monday in February
    - Burgenland, Kärnten, Salzburg, Tirol, Vorarlberg: second Monday in February
    - Oberösterreich, Steiermark: third Monday in February
    Duration: 1 week
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
    
    end = start + timedelta(days=6)  # One week (Monday to Sunday)
    return start, end

def calculate_summer_holidays(year, bundesland):
    """
    Calculate summer holidays (Hauptferien)
    § 2 (2) 2.:
    - Burgenland, Niederösterreich, Wien: Saturday between June 28 - July 4
    - Others: Saturday between July 5 - July 11
    Ends with the beginning of the next school year
    """
    group_1 = ['Burgenland', 'Niederösterreich', 'Wien']
    
    if bundesland in group_1:
        # First Saturday between June 28 and July 4
        start = get_first_saturday_in_range(year, 6, 28, 4)
        if start.month == 7 and start.day > 4:
            # Fallback: find Saturday in June 28-30 range
            start = get_first_saturday_in_range(year, 6, 28, 30)
    else:
        # First Saturday between July 5 and July 11
        start = get_first_saturday_in_range(year, 7, 5, 11)
    
    # End date is the day before next school year starts
    next_school_year = calculate_school_year_start(year + 1, bundesland)
    end = next_school_year - timedelta(days=1)
    
    return start, end

def get_school_holidays(year, bundesland):
    """
    Get all school holidays for a given year and Bundesland
    Returns list of (start_date, end_date, name_de, name_en)
    """
    holidays = []
    
    # Semester break
    sem_start, sem_end = calculate_semester_break(year, bundesland)
    holidays.append((
        sem_start,
        sem_end,
        "Semesterferien",
        "Semester Break"
    ))
    
    # Summer holidays
    summer_start, summer_end = calculate_summer_holidays(year, bundesland)
    holidays.append((
        summer_start,
        summer_end,
        "Sommerferien",
        "Summer Holidays"
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
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Austrian School Holidays//AT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Schulferien {bundesland}",
        "X-WR-TIMEZONE:Europe/Vienna",
        f"X-WR-CALDESC:Schulferien in {bundesland}, Österreich ({start_year}-{end_year})"
    ]
    
    for start_date, end_date, name_de, name_en in all_holidays:
        # ICS events are inclusive, but DTEND is exclusive, so add 1 day
        dtend = end_date + timedelta(days=1)
        
        uid = f"{start_date.strftime('%Y%m%d')}-{name_en.replace(' ', '-').lower()}-{bundesland.lower()}@austrian-school-holidays.local"
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{start_date.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{dtend.strftime('%Y%m%d')}",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"UID:{uid}",
            f"SUMMARY:{name_de}",
            f"DESCRIPTION:{name_en} - Schulferien in {bundesland}",
            "TRANSP:TRANSPARENT",
            "STATUS:CONFIRMED",
            "SEQUENCE:0",
            "END:VEVENT"
        ])
    
    ics_lines.append("END:VCALENDAR")
    
    # Write to file
    filename = f"{output_dir}/school_holidays_{bundesland.lower().replace('ö', 'oe').replace('ü', 'ue')}.ics"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\r\n'.join(ics_lines))
    
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
    
    print("="*60)
    print(f"Austrian School Holidays Generator ({start_year}-{end_year})")
    print("="*60)
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
    print("="*60)
    print(f"Example: Wien School Holidays {current_year}")
    print("="*60)
    for start_date, end_date, name_de, name_en in get_school_holidays(current_year, 'Wien'):
        duration = (end_date - start_date).days + 1
        print(f"{name_de}:")
        print(f"  {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({duration} days)")