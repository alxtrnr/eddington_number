# main.py

import getpass
import logging
import os
from collections import defaultdict
from typing import List
from auth import get_credentials
from client import RWGPSClient
from config import API_KEY, DEFAULT_UNIT
import time
from datetime import datetime
from client import RWGPSClient
from decimal import Decimal, getcontext
from calculations import (
    calculate_eddington,
    calculate_statistics,
    calculate_yearly_eddington,
    get_highest_yearly_eddington,
    analyze_ride_distribution,
    analyze_ride_metrics,
    calculate_next_yearly_e,
    calculate_overall_e_progress,
    get_ride_titles,
    METERS_TO_MILES,
    METERS_TO_KM
)
from utils import cache_data, load_cached_data
from config import API_KEY, CACHE_FILE, CACHE_DURATION
from log_rate_limit import StreamRateLimitFilter, RateLimit

getcontext().prec = 28  # Adjust precision as needed


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Add rate limiting to root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(StreamRateLimitFilter(
        period_sec=1,  # Limit similar logs to once per second
        default_stream_id=None  # Don't rate limit by default
    ))
    # Disable verbose HTTP logging
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def update_cache(cache_file: str, client: RWGPSClient, unit: str = 'miles') -> List[dict]:
    """Update cache with only new rides if needed."""
    cached_data = load_cached_data(cache_file, unit)

    if not cached_data:
        logging.info("No cache found. Fetching all trips...")
        trips = client.get_all_trips()
        cache_data({
            'trips': trips,
            'timestamp': time.time()
        }, cache_file, unit)
        return trips

    cached_trips = cached_data.get('trips', [])

    # Check if cache is expired
    if time.time() - cached_data.get('timestamp', 0) > CACHE_DURATION:
        logging.info("Cache expired. Fetching all trips...")
        trips = client.get_all_trips()
        cache_data({
            'trips': trips,
            'timestamp': time.time()
        }, cache_file, unit)
        return trips

    # Check for new trips
    latest_trip = client.get_latest_trip()
    if not latest_trip:
        return cached_trips

    latest_cached_id = max(trip['id'] for trip in cached_trips) if cached_trips else 0

    if latest_trip['id'] > latest_cached_id:
        logging.info("Fetching new trips since last cache update...")
        new_trips = client.get_missing_trips(cached_trips, latest_trip)
        if new_trips:
            all_trips = cached_trips + new_trips
            all_trips.sort(key=lambda x: x['id'])
            cache_data({
                'trips': all_trips,
                'timestamp': time.time()
            }, cache_file, unit)
            logging.info(f"Added {len(new_trips)} new trips to cache")
            return all_trips

    return cached_trips


def process_trips(trips: List[dict], unit: str = 'miles') -> List[Decimal]:
    """
    Process trips with detailed API data analysis.
    """
    # Select the appropriate conversion factor
    conversion_factor = METERS_TO_MILES if unit == 'miles' else METERS_TO_KM

    total_meters = Decimal('0')
    api_total = 0.0  # Float for raw API comparison
    yearly_totals = defaultdict(Decimal)

    for trip in trips:
        if 'distance' in trip:
            # Store both raw API value and Decimal conversion
            raw_distance = float(trip['distance'])
            api_total += raw_distance
            meters = Decimal(str(trip['distance']))
            total_meters += meters
            # Track by year for pattern analysis
            year = datetime.fromisoformat(trip['created_at'].split('Z')[0]).year
            yearly_totals[year] += meters

    return [Decimal(str(trip['distance'])) * conversion_factor for trip in trips if 'distance' in trip]


def main(unit: str = DEFAULT_UNIT, refresh_cache: bool = False):
    """Main execution function."""
    setup_logging()
    logging.info("Starting Eddington number calculation...")

    # Check for API key
    if not API_KEY:
        raise ValueError("Missing required RWGPS_API_KEY environment variable")

    try:
        from auth import get_credentials
        email, password = get_credentials()
        if not email or not password:
            raise ValueError("Email and password are required")

        client = RWGPSClient(API_KEY, email, password)

        # Handle cache with respect to refresh flag
        cache_file = f"{CACHE_FILE.split('.')[0]}_{unit}.pkl"

        if refresh_cache and os.path.exists(cache_file):
            os.remove(cache_file)
            logging.info("Cache cleared. Fetching fresh data...")

        trips = update_cache(CACHE_FILE, client, unit)
        distances = process_trips(trips, unit)
        trips = update_cache(CACHE_FILE, client)
        distances = process_trips(trips, unit)
        yearly_eddington = calculate_yearly_eddington(trips, unit)
        stats = calculate_statistics(distances, unit)
        highest_year, highest_e = get_highest_yearly_eddington(yearly_eddington)
        advanced_metrics = analyze_ride_metrics(trips, unit)
        current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext = \
            calculate_overall_e_progress(distances, unit)

        print("\n=== RIDE STATISTICS ===")
        print(f"Total rides analyzed: {len(distances)}")
        print("\n=== OVERALL EDDINGTON PROGRESS ===")
        print(f"Current overall Eddington: {current_e}")
        print(f"In progress: E={current_e + 1} ({rides_at_next} rides of {current_e + 1}+ {unit})")
        print(f"Need {rides_needed_next} more rides of {current_e + 1}+ {unit} for E={current_e + 1}")
        print(f"Next goal after that: E={current_e + 2} ({rides_at_nextnext} rides of {current_e + 2}+ {unit})")
        print(f"Will need {rides_needed_nextnext} more rides of {current_e + 2}+ {unit} for E={current_e + 2}")

        current_year = datetime.now().year
        if current_year in yearly_eddington:
            print(f"\n=== EDDINGTON YEAR TO DATE ({current_year}) ===")
            ytd_rides = [trip for trip in trips
                         if datetime.strptime(trip['created_at'],
                                              "%Y-%m-%dT%H:%M:%SZ").year == current_year]
            ytd_distances = process_trips(ytd_rides, unit)
            ytd_stats = calculate_statistics(ytd_distances, unit)
            next_e, rides_at_target, rides_needed = calculate_next_yearly_e(trips, current_year, unit)
            print(f"Rides this year: {len(ytd_rides)}")
            print(f"Distance this year: {ytd_stats['total_distance']:,.1f} {unit}")
            print(f"Current year Eddington: {yearly_eddington[current_year]}")
            print(f"In progress: E={next_e} ({rides_at_target} rides of {next_e}+ {unit})")
            print(f"Need {rides_needed} more rides of {next_e}+ {unit} for E={next_e}")

        print("\n=== YEARLY EDDINGTON NUMBERS === ")
        for year in sorted(yearly_eddington.keys(), reverse=True):
            current_e = yearly_eddington[year]
            if year == highest_year:
                print(f"{year}: {current_e} *Highest*")
            else:
                print(f"{year}: {current_e}")

        print("\n=== RIDE METRICS ===")
        print(f"Longest ride: {stats['longest_ride']:.1f} {unit}")
        print(f"Average ride: {stats['average_ride']:.1f} {unit}")
        print(f"Total distance: {stats['total_distance']:.1f} {unit}")

        print("\n=== RIDE DISTRIBUTION ===")
        distribution = analyze_ride_distribution(distances, unit)
        for distance_threshold in sorted(distribution.keys()):
            if distance_threshold % 20 == 0:
                print(f">= {distance_threshold} {unit}: {distribution[distance_threshold]} rides")

        print("\n=== MILESTONE ACHIEVEMENTS ===")
        milestones = advanced_metrics['milestone_rides']
        print(f"Century rides (100+ {unit}): {milestones['centuries']}")
        print(f"Double centuries (200+ {unit}): {milestones['double_centuries']}")
        print(f"Triple centuries (300+ {unit}): {milestones['triple_centuries']}")
        print(f"Quad centuries (400+ {unit}): {milestones['quad_centuries']}")

        print("\n=== TOP 5 LONGEST RIDES === ")
        distance_titles = get_ride_titles(trips, distances, unit)
        for i, (distance, title) in enumerate(distance_titles, 1):
            print(f"{i}. {distance:.1f} {unit} - {title}")

        print("\n=== MONTHLY STATISTICS ===")
        current_date = datetime.now()
        month_tuples = []
        for month in advanced_metrics['monthly_totals'].keys():
            year, month_num = map(int, month.split('-'))
            month_tuples.append((datetime(year, month_num, 1), month))
        sorted_months = [month for _, month in sorted(month_tuples, reverse=True)][:12]
        for month in sorted_months:
            rides = advanced_metrics['monthly_counts'][month]
            distance = advanced_metrics['monthly_totals'][month]
            print(f"{month}: {rides} rides, {distance:.1f} {unit}")

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        raise


def display_statistics(stats: dict[str, Decimal], unit: str = 'miles') -> None:
    """Display statistics with appropriate rounding only at display time."""
    print(f"Longest ride: {stats['longest_ride']:.1f} {unit}")
    print(f"Average ride: {stats['average_ride']:.1f} {unit}")
    print(f"Total distance: {stats['total_distance']:.1f} {unit}")


if __name__ == "__main__":
    main()
