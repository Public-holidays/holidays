#!/usr/bin/env python3
"""
Shared utilities for generating holiday calendars
"""

from datetime import datetime, timedelta


def calculate_easter(year):
    """
    Calculate Easter Sunday using Gauss's Easter algorithm
    Returns datetime object for Easter Sunday
    """
    a = year % 19
    b = year % 4
    c = year % 7
    k = year // 100
    p = (13 + 8 * k) // 25
    q = k // 4
    M = (15 - p + k - q) % 30
    N = (4 + k - q) % 7
    d = (19 * a + M) % 30
    e = (2 * b + 4 * c + 6 * d + N) % 7

    if d + e < 10:
        day = d + e + 22
        month = 3
    else:
        day = d + e - 9
        month = 4

    if day == 26 and month == 4:
        day = 19
    if day == 25 and month == 4 and d == 28 and e == 6 and a > 10:
        day = 18

    return datetime(year, month, day)


def normalize_filename(text):
    """
    Convert text to filename-safe format
    Handles German and Austrian umlauts

    Args:
        text: String to normalize

    Returns:
        Filename-safe string
    """
    return (text.lower()
            .replace('ä', 'ae')
            .replace('ö', 'oe')
            .replace('ü', 'ue')
            .replace('ß', 'ss')
            .replace(' ', '-')
            .replace('/', '-'))

def generate_ics_header(cal_name, cal_desc):
    """Generate standard ICS header"""
    return [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Public Holidays//AT",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{cal_name}",
        "X-WR-TIMEZONE:Europe/Vienna",
        f"X-WR-CALDESC:{cal_desc}",
        f"X-GENERATION-TIME:{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}"
    ]


def create_ics_event(start_date, end_date, summary, description, uid_suffix):
    """Create a single ICS event"""
    end_date_exclusive = end_date + timedelta(days=1)

    return [
        "BEGIN:VEVENT",
        f"DTSTART;VALUE=DATE:{start_date.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{end_date_exclusive.strftime('%Y%m%d')}",
        f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
        f"UID:{uid_suffix}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{description}",
        "TRANSP:TRANSPARENT",
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "END:VEVENT"
    ]


def write_ics_file(filename, ics_lines):
    """Write ICS content to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\r\n'.join(ics_lines))