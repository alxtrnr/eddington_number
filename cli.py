# cli.py

import argparse
import os
from datetime import datetime
from typing import List, Dict
from decimal import Decimal

from main import update_cache, process_trips, RWGPSClient
from calculations import (
    calculate_statistics, calculate_yearly_eddington,
    analyze_ride_distribution, analyze_ride_metrics,
    calculate_overall_e_progress, get_ride_titles,
    calculate_next_yearly_e
)
from config import API_KEY, CACHE_FILE, DEFAULT_UNIT
from auth import get_credentials


def get_preferred_unit():
    """Load the user's preferred unit from file."""
    try:
        with open('.unit_preference', 'r') as f:
            unit = f.read().strip()
            if unit in ['miles', 'km']:
                return unit
    except FileNotFoundError:
        pass
    return DEFAULT_UNIT


def save_preferred_unit(unit: str):
    """Save the user's preferred unit to file."""
    with open('.unit_preference', 'w') as f:
        f.write(unit)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Cycling Statistics Analysis')

    # Add unit option to the main parser so it applies to all commands
    parser.add_argument('--unit', choices=['miles', 'km'], default=None,
                        help='Distance unit (miles or km)')

    # Add refresh flag to force fresh data
    parser.add_argument('--refresh', action='store_true',
                        help='Force refresh data instead of using cache')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Full summary command
    subparsers.add_parser('summary', help='Display full statistics summary')

    # Individual section commands
    subparsers.add_parser('eddington', help='Show Eddington number progress')
    subparsers.add_parser('ytd', help='Show year-to-date statistics')
    subparsers.add_parser('yearly', help='Show yearly Eddington numbers')
    subparsers.add_parser('metrics', help='Show ride metrics')
    subparsers.add_parser('distribution', help='Show ride distribution')
    subparsers.add_parser('distance', help='Show distance achievements')
    subparsers.add_parser('longest', help='Show top 5 longest rides')
    subparsers.add_parser('monthly', help='Show monthly statistics')

    # Unit command
    unit_parser = subparsers.add_parser('unit', help='Set or toggle distance unit')
    unit_parser.add_argument('value', nargs='?', choices=['miles', 'km', 'toggle'],
                             default='toggle', help='Unit to use (miles, km) or toggle between them')

    # Status command
    subparsers.add_parser('status', help='Show current unit setting and stats')

    return parser


def display_eddington(trips: List[dict], distances: List[Decimal], unit: str = 'miles') -> None:
    current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext = \
        calculate_overall_e_progress(distances, unit)

    print("\n=== OVERALL EDDINGTON PROGRESS ===")
    print(f"Current overall Eddington: {current_e}")
    print(f"In progress: E={current_e + 1} ({rides_at_next} rides of {current_e + 1}+ {unit})")
    print(f"Need {rides_needed_next} more rides of {current_e + 1}+ {unit} for E={current_e + 1}")
    print(f"Next goal after that: E={current_e + 2} ({rides_at_nextnext} rides of {current_e + 2}+ {unit})")
    print(f"Will need {rides_needed_nextnext} more rides of {current_e + 2}+ {unit} for E={current_e + 2}")


def display_ytd(trips: List[dict], yearly_eddington: Dict[int, int], unit: str = 'miles') -> None:
    current_year = datetime.now().year
    if current_year in yearly_eddington:
        ytd_rides = []
        for trip in trips:
            date_str = trip.get('departed_at')
            if date_str:
                try:
                    date_str = date_str.split('+')[0].rstrip('Z')
                    trip_date = datetime.fromisoformat(date_str)
                    if trip_date.year == current_year:
                        ytd_rides.append(trip)
                except ValueError:
                    continue

        ytd_distances = process_trips(ytd_rides, unit)
        ytd_stats = calculate_statistics(ytd_distances, unit)
        next_e, rides_at_target, rides_needed = calculate_next_yearly_e(trips, current_year, unit)

        print(f"\n=== EDDINGTON YEAR TO DATE ({current_year}) ===")
        print(f"Rides this year: {len(ytd_rides)}")
        print(f"Distance this year: {ytd_stats['total_distance']:,.1f} {unit}")
        print(f"Current year Eddington: {yearly_eddington[current_year]}")
        print(f"In progress: E={next_e} ({rides_at_target} rides of {next_e}+ {unit})")
        print(f"Need {rides_needed} more rides of {next_e}+ {unit} for E={next_e}")


def display_yearly(yearly_eddington: Dict[int, int]) -> None:
    print("\n=== YEARLY EDDINGTON NUMBERS ===")
    highest_e = max(yearly_eddington.values()) if yearly_eddington else 0
    for year in sorted(yearly_eddington.keys(), reverse=True):
        if yearly_eddington[year] == highest_e:
            print(f"{year}: {yearly_eddington[year]} *Highest*")
        else:
            print(f"{year}: {yearly_eddington[year]}")


def display_metrics(stats: Dict[str, Decimal], unit: str = 'miles') -> None:
    print("\n=== RIDE METRICS ===")
    print(f"Longest ride: {stats['longest_ride']:.1f} {unit}")
    print(f"Average ride: {stats['average_ride']:.1f} {unit}")
    print(f"Total distance: {stats['total_distance']:.1f} {unit}")


def display_distribution(distances: List[Decimal], unit: str = 'miles') -> None:
    print(f"\n=== RIDE DISTRIBUTION ===")
    distribution = analyze_ride_distribution(distances, unit)

    # Create range buckets (e.g., 0-20, 20-40, 40-60, etc.)
    buckets = {}
    bucket_size = 50  # Adjust bucket size as needed
    max_distance = max(distances) if distances else 0

    for i in range(0, int(max_distance) + bucket_size, bucket_size):
        lower = i
        upper = i + bucket_size

        # Count rides in this range
        count = sum(1 for d in distances if lower <= d < upper)
        if count > 0:
            buckets[f"{lower}-{upper}"] = count

    # Display as table with percentages
    total = len(distances)
    print(f"{'Range':<15} | {'Count':<6} | {'Percentage':<10}")
    print(f"{'-' * 15}-|{'-' * 8}|{'-' * 10}")

    for range_label, count in buckets.items():
        percentage = (count / total) * 100
        print(f"{range_label: <15} | {count: <6} | {percentage:.2f}%")


def display_milestones(metrics: Dict, unit: str = 'miles') -> None:
    print("\n=== DISTANCE ACHIEVEMENTS ===")
    milestones = metrics['milestone_rides']
    if unit == 'miles':
        print(f"Century rides (100+ {unit}): {milestones['centuries']}")
        print(f"Double centuries (200+ {unit}): {milestones['double_centuries']}")
        print(f"Triple centuries (300+ {unit}): {milestones['triple_centuries']}")
        print(f"Quad centuries (400+ {unit}): {milestones['quad_centuries']}")
    else:  # kilometers - display new distance ranges
        print(f"Randonneur 50 {unit}: {milestones['range_50_to_99']}")
        print(f"Randonneur 100 {unit}: {milestones['range_100_to_149']}")
        print(f"Randonneur 150 {unit}: {milestones['range_150_to_199']}")
        print(f"Randonneur 200 {unit}: {milestones['range_200_to_299']}")
        print(f"Randonneur 300 {unit}: {milestones['range_300_to_399']}")
        print(f"Randonneur 400 {unit}: {milestones['range_400_to_599']}")
        print(f"Randonneur 600 {unit}: {milestones['range_600_to_999']}")
        print(f"Randonneur 1000 {unit}: {milestones['range_1000_plus']}")


def display_longest(trips: List[dict], distances: List[Decimal], unit: str = 'miles') -> None:
    print("\n=== TOP 5 LONGEST RIDES ===")
    distance_titles = get_ride_titles(trips, distances, unit)
    for i, (distance, title) in enumerate(distance_titles, 1):
        print(f"{i}. {distance:.1f} {unit} - {title}")


def display_monthly(metrics: Dict, unit: str = 'miles') -> None:
    print("\n=== MONTHLY STATISTICS ===")
    current_date = datetime.now()
    month_tuples = []
    for month in metrics['monthly_totals'].keys():
        year, month_num = map(int, month.split('-'))
        month_tuples.append((datetime(year, month_num, 1), month))
    sorted_months = [month for _, month in sorted(month_tuples, reverse=True)][:12]
    for month in sorted_months:
        rides = metrics['monthly_counts'][month]
        distance = metrics['monthly_totals'][month]
        print(f"{month}: {rides} rides, {distance:.1f} {unit}")


def display_status(unit: str = 'miles'):
    print(f"\n=== CURRENT SETTINGS ===")
    print(f"Distance unit: {unit}")
    cache_file = f"{CACHE_FILE.split('.')[0]}_{unit}.pkl"
    print(f"Cache file: {cache_file}")
    # Show if cache exists
    if os.path.exists(cache_file):
        print("Cache status: Available")
    else:
        print("Cache status: Not available")


def handle_unit_command(args):
    current_unit = args.unit if args.unit else get_preferred_unit()
    new_unit = args.value

    if new_unit == 'toggle':
        new_unit = 'km' if current_unit == 'miles' else 'miles'

    # Save preference to config
    save_preferred_unit(new_unit)
    print(f"Unit changed to: {new_unit}")
    return new_unit


def display_header(unit: str = 'miles'):
    print(f"\n=== CYCLING STATISTICS (distances in {unit}) ===")
    print(f"Current unit: {unit} (use --unit option to change)")


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Get the unit from args or saved preference
    if args.unit:
        unit = args.unit
        # Save the unit preference when specified via command line
        save_preferred_unit(unit)
    else:
        unit = get_preferred_unit()

    # Handle unit command
    if args.command == 'unit':
        unit = handle_unit_command(args)
        # Show current status after changing unit
        display_status(unit)
        return

    # Handle status command
    if args.command == 'status':
        display_status(unit)
        return

    # First get user credentials
    from auth import get_credentials
    email, password = get_credentials()

    # Create client with user credentials
    client = RWGPSClient(API_KEY, email, password)

    # Handle cache - use by default, only refresh if flag is set
    cache_file = f"{CACHE_FILE.split('.')[0]}_{unit}.pkl"

    if args.refresh and os.path.exists(cache_file):
        os.remove(cache_file)
        print("Cache cleared. Fetching fresh data...")

    trips = update_cache(CACHE_FILE, client, unit)
    distances = process_trips(trips, unit)
    yearly_eddington = calculate_yearly_eddington(trips, unit)
    stats = calculate_statistics(distances, unit)
    metrics = analyze_ride_metrics(trips, unit)

    # Display header with current unit
    display_header(unit)

    if args.command == 'summary':
        print(f"Total rides analyzed: {len(distances)}")
        display_eddington(trips, distances, unit)
        display_ytd(trips, yearly_eddington, unit)
        display_yearly(yearly_eddington)
        display_metrics(stats, unit)
        display_distribution(distances, unit)
        display_milestones(metrics, unit)
        display_longest(trips, distances, unit)
        display_monthly(metrics, unit)
    elif args.command == 'eddington':
        display_eddington(trips, distances, unit)
    elif args.command == 'ytd':
        display_ytd(trips, yearly_eddington, unit)
    elif args.command == 'yearly':
        display_yearly(yearly_eddington)
    elif args.command == 'metrics':
        display_metrics(stats, unit)
    elif args.command == 'distribution':
        display_distribution(distances, unit)
    elif args.command == 'distance':
        display_milestones(metrics, unit)
    elif args.command == 'longest':
        display_longest(trips, distances, unit)
    elif args.command == 'monthly':
        display_monthly(metrics, unit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
