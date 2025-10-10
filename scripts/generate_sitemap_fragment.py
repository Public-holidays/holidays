#!/usr/bin/env python3
"""
Sitemap Fragment Generator for public-holidays/holidays repo
Generates sitemap entries for all ICS calendar files
This fragment can be included in the main sitemap.xml
"""

from datetime import datetime
import os
from pathlib import Path

# Configuration
BASE_URL = "https://public-holidays.github.io/holidays"  # CHANGE THIS to your actual domain
OUTPUT_DIR = "output"
SCHOOL_DIR = "output/school"


def get_last_modified(filepath):
    """Get the last modification time of a file"""
    try:
        timestamp = os.path.getmtime(filepath)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def get_ics_files(directory):
    """Get all ICS files in a directory"""
    path = Path(directory)
    if not path.exists():
        return []
    return sorted([f.name for f in path.glob('*.ics')])


def generate_sitemap_fragment():
    """Generate sitemap fragment with just ICS files"""

    print("=" * 60)
    print("Sitemap Fragment Generator (ICS Files Only)")
    print("=" * 60)
    print()

    current_date = datetime.now().strftime('%Y-%m-%d')

    sitemap_lines = [
        '<!-- Sitemap fragment for ICS calendar files -->',
        '<!-- Generated: ' + current_date + ' -->',
        '<!-- Include this in your main sitemap.xml -->',
        ''
    ]

    url_count = 0

    # German holidays ICS files
    german_bundeslaender = [
        'baden-wuerttemberg', 'bayern', 'berlin', 'brandenburg', 'bremen',
        'hamburg', 'hessen', 'mecklenburg-vorpommern', 'niedersachsen',
        'nordrhein-westfalen', 'rheinland-pfalz', 'saarland', 'sachsen',
        'sachsen-anhalt', 'schleswig-holstein', 'thueringen'
    ]

    sitemap_lines.append('  <!-- German Holidays ICS Files -->')
    for bundesland in german_bundeslaender:
        filename = f'german_holidays_{bundesland}.ics'
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            lastmod = get_last_modified(filepath)
            sitemap_lines.append('  <url>')
            sitemap_lines.append(f'    <loc>{BASE_URL}/{OUTPUT_DIR}/{filename}</loc>')
            sitemap_lines.append(f'    <lastmod>{lastmod}</lastmod>')
            sitemap_lines.append('    <changefreq>yearly</changefreq>')
            sitemap_lines.append('    <priority>0.7</priority>')
            sitemap_lines.append('  </url>')
            sitemap_lines.append('')
            url_count += 1
            print(f"✓ Added: {filename}")

    # Austrian holidays ICS files
    sitemap_lines.append('  <!-- Austrian Holidays ICS Files -->')

    # Rolling calendar (main one)
    rolling_file = 'austrian_holidays.ics'
    rolling_path = os.path.join(OUTPUT_DIR, rolling_file)
    if os.path.exists(rolling_path):
        lastmod = get_last_modified(rolling_path)
        sitemap_lines.append('  <url>')
        sitemap_lines.append(f'    <loc>{BASE_URL}/{OUTPUT_DIR}/{rolling_file}</loc>')
        sitemap_lines.append(f'    <lastmod>{lastmod}</lastmod>')
        sitemap_lines.append('    <changefreq>yearly</changefreq>')
        sitemap_lines.append('    <priority>0.8</priority>')
        sitemap_lines.append('  </url>')
        sitemap_lines.append('')
        url_count += 1
        print(f"✓ Added: {rolling_file}")

    # Year-specific Austrian calendars
    austrian_ics_files = get_ics_files(OUTPUT_DIR)
    for filename in austrian_ics_files:
        if filename.startswith('austrian_holidays_') and filename != 'austrian_holidays.ics':
            filepath = os.path.join(OUTPUT_DIR, filename)
            lastmod = get_last_modified(filepath)
            sitemap_lines.append('  <url>')
            sitemap_lines.append(f'    <loc>{BASE_URL}/{OUTPUT_DIR}/{filename}</loc>')
            sitemap_lines.append(f'    <lastmod>{lastmod}</lastmod>')
            sitemap_lines.append('    <changefreq>never</changefreq>')
            sitemap_lines.append('    <priority>0.5</priority>')
            sitemap_lines.append('  </url>')
            sitemap_lines.append('')
            url_count += 1
            print(f"✓ Added: {filename}")

    # Austrian school holidays ICS files
    sitemap_lines.append('  <!-- Austrian School Holidays ICS Files -->')

    austrian_bundeslaender = [
        'wien', 'niederoesterreich', 'burgenland', 'oberoesterreich',
        'steiermark', 'kaernten', 'salzburg', 'tirol', 'vorarlberg'
    ]

    for bundesland in austrian_bundeslaender:
        filename = f'school_holidays_{bundesland}.ics'
        filepath = os.path.join(SCHOOL_DIR, filename)

        if os.path.exists(filepath):
            lastmod = get_last_modified(filepath)
            sitemap_lines.append('  <url>')
            sitemap_lines.append(f'    <loc>{BASE_URL}/{SCHOOL_DIR}/{filename}</loc>')
            sitemap_lines.append(f'    <lastmod>{lastmod}</lastmod>')
            sitemap_lines.append('    <changefreq>yearly</changefreq>')
            sitemap_lines.append('    <priority>0.7</priority>')
            sitemap_lines.append('  </url>')
            sitemap_lines.append('')
            url_count += 1
            print(f"✓ Added: school/{filename}")

    # Write sitemap fragment
    sitemap_content = '\n'.join(sitemap_lines)

    with open('sitemap_fragment.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap_content)

    print()
    print("=" * 60)
    print(f"✓ Sitemap fragment generated: sitemap_fragment.xml")
    print(f"  Total ICS file URLs: {url_count}")
    print(f"  Last updated: {current_date}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Update BASE_URL in this script to your actual domain")
    print("2. Copy sitemap_fragment.xml content to your main sitemap.xml")
    print("3. Or use the content in your root repo's sitemap generator")


if __name__ == "__main__":
    print()
    print("🗓️  Feiertage & Schulferien - Sitemap Fragment Generator")
    print("   (For public-holidays/holidays repo)")
    print()

    # Check if BASE_URL needs to be updated
    if BASE_URL == "https://yourdomain.com":
        print("⚠️  WARNING: Please update BASE_URL in this script!")
        print("   Current: https://yourdomain.com")
        print("   Change to your actual domain name")
        print()

    # Generate fragment
    generate_sitemap_fragment()

    print()
    print("All done! 🎉")