# cli.py
import argparse
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
from config import API_KEY, EMAIL, PASSWORD, CACHE_FILE


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Cycling Statistics Analysis')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Full summary command
    subparsers.add_parser('summary', help='Display full statistics summary')

    # Individual section commands
    subparsers.add_parser('eddington', help='Show Eddington number progress')
    subparsers.add_parser('ytd', help='Show year-to-date statistics')
    subparsers.add_parser('yearly', help='Show yearly Eddington numbers')
    subparsers.add_parser('metrics', help='Show ride metrics')
    subparsers.add_parser('distribution', help='Show ride distribution')
    subparsers.add_parser('milestones', help='Show milestone achievements')
    subparsers.add_parser('longest', help='Show top 5 longest rides')
    subparsers.add_parser('monthly', help='Show monthly statistics')

    return parser


def display_eddington(trips: List[dict], distances: List[Decimal]) -> None:
    current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext = \
        calculate_overall_e_progress(distances)

    print("\n=== OVERALL EDDINGTON PROGRESS ===")
    print(f"Current overall Eddington: {current_e}")
    print(f"In progress: E={current_e + 1} ({rides_at_next} rides of {current_e + 1}+ miles)")
    print(f"Need {rides_needed_next} more rides of {current_e + 1}+ miles for E={current_e + 1}")
    print(f"Next goal after that: E={current_e + 2} ({rides_at_nextnext} rides of {current_e + 2}+ miles)")
    print(f"Will need {rides_needed_nextnext} more rides of {current_e + 2}+ miles for E={current_e + 2}")


def display_ytd(trips: List[dict], yearly_eddington: Dict[int, int]) -> None:
    current_year = datetime.now().year
    if current_year in yearly_eddington:
        ytd_rides = [trip for trip in trips
                     if datetime.strptime(trip['created_at'],
                                          "%Y-%m-%dT%H:%M:%SZ").year == current_year]
        ytd_distances = [Decimal(str(trip['distance'])) * Decimal("0.000621371")
                         for trip in ytd_rides]
        ytd_stats = calculate_statistics(ytd_distances)
        next_e, rides_at_target, rides_needed = calculate_next_yearly_e(trips, current_year)

        print(f"\n=== EDDINGTON YEAR TO DATE ({current_year}) ===")
        print(f"Rides this year: {len(ytd_rides)}")
        print(f"Distance this year: {ytd_stats['total_distance']:,.1f} miles")
        print(f"Current year Eddington: {yearly_eddington[current_year]}")
        print(f"In progress: E={next_e} ({rides_at_target} rides of {next_e}+ miles)")
        print(f"Need {rides_needed} more rides of {next_e}+ miles for E={next_e}")


def display_yearly(yearly_eddington: Dict[int, int]) -> None:
    print("\n=== YEARLY EDDINGTON NUMBERS ===")
    highest_e = max(yearly_eddington.values())
    for year in sorted(yearly_eddington.keys(), reverse=True):
        if yearly_eddington[year] == highest_e:
            print(f"{year}: {yearly_eddington[year]} *Highest*")
        else:
            print(f"{year}: {yearly_eddington[year]}")


def display_metrics(stats: Dict[str, Decimal]) -> None:
    print("\n=== RIDE METRICS ===")
    print(f"Longest ride: {stats['longest_ride']:.1f} miles")
    print(f"Average ride: {stats['average_ride']:.1f} miles")
    print(f"Total distance: {stats['total_distance']:.1f} miles")


def display_distribution(distances: List[Decimal]) -> None:
    print("\n=== RIDE DISTRIBUTION ===")
    distribution = analyze_ride_distribution(distances)
    for miles in sorted(distribution.keys()):
        if miles % 20 == 0:
            print(f">= {miles} miles: {distribution[miles]} rides")


def display_milestones(metrics: Dict) -> None:
    print("\n=== MILESTONE ACHIEVEMENTS ===")
    milestones = metrics['milestone_rides']
    print(f"Century rides (100+ miles): {milestones['centuries']}")
    print(f"Double centuries (200+ miles): {milestones['double_centuries']}")
    print(f"Triple centuries (300+ miles): {milestones['triple_centuries']}")
    print(f"Quad centuries (400+ miles): {milestones['quad_centuries']}")


def display_longest(trips: List[dict], distances: List[Decimal]) -> None:
    print("\n=== TOP 5 LONGEST RIDES ===")
    distance_titles = get_ride_titles(trips, distances)
    for i, (distance, title) in enumerate(distance_titles, 1):
        print(f"{i}. {distance:.1f} miles - {title}")


def display_monthly(metrics: Dict) -> None:
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
        print(f"{month}: {rides} rides, {distance:.1f} miles")


def main():
    parser = create_parser()
    args = parser.parse_args()

    client = RWGPSClient(API_KEY, EMAIL, PASSWORD)
    trips = update_cache(CACHE_FILE, client)
    distances = process_trips(trips)
    yearly_eddington = calculate_yearly_eddington(trips)
    stats = calculate_statistics(distances)
    metrics = analyze_ride_metrics(trips)

    if args.command == 'summary':
        print(f"\n=== RIDE STATISTICS ===")
        print(f"Total rides analyzed: {len(distances)}")
        display_eddington(trips, distances)
        display_ytd(trips, yearly_eddington)
        display_yearly(yearly_eddington)
        display_metrics(stats)
        display_distribution(distances)
        display_milestones(metrics)
        display_longest(trips, distances)
        display_monthly(metrics)
    elif args.command == 'eddington':
        display_eddington(trips, distances)
    elif args.command == 'ytd':
        display_ytd(trips, yearly_eddington)
    elif args.command == 'yearly':
        display_yearly(yearly_eddington)
    elif args.command == 'metrics':
        display_metrics(stats)
    elif args.command == 'distribution':
        display_distribution(distances)
    elif args.command == 'milestones':
        display_milestones(metrics)
    elif args.command == 'longest':
        display_longest(trips, distances)
    elif args.command == 'monthly':
        display_monthly(metrics)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
