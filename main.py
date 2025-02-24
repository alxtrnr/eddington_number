# main.py
import getpass
import logging
from collections import defaultdict
from typing import List
from auth import get_credentials
from client import RWGPSClient
from config import API_KEY

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
    calculate_next_yearly_e, calculate_overall_e_progress, get_ride_titles
)
from utils import cache_data, load_cached_data
from config import API_KEY, CACHE_FILE, CACHE_DURATION
from log_rate_limit import StreamRateLimitFilter, RateLimit

METERS_TO_MILES = Decimal("0.000621371192237334")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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


def update_cache(cache_file: str, client: RWGPSClient) -> List[dict]:
    """Update cache with only new rides if needed."""
    cached_data = load_cached_data(cache_file)
    if not cached_data:
        logging.info("No cache found. Fetching all trips...")
        trips = client.get_all_trips()
        cache_data({
            'trips': trips,
            'timestamp': time.time()
        }, cache_file)
        return trips

    cached_trips = cached_data.get('trips', [])
    if time.time() - cached_data.get('timestamp', 0) > CACHE_DURATION:
        logging.info("Cache expired. Fetching all trips...")
        trips = client.get_all_trips()
        cache_data({
            'trips': trips,
            'timestamp': time.time()
        }, cache_file)
        return trips

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
            }, cache_file)
            logging.info(f"Added {len(new_trips)} new trips to cache")
            return all_trips

    return cached_trips


def process_trips(trips: List[dict]) -> List[Decimal]:
    """
    Process trips with detailed API data analysis.
    """
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

    return [Decimal(str(trip['distance'])) * METERS_TO_MILES for trip in trips if 'distance' in trip]


def main():
    """Main execution function."""
    setup_logging()
    logging.info("Starting Eddington number calculation...")

    # Check for API key
    if not API_KEY:
        raise ValueError("Missing required RWGPS_API_KEY environment variable")

    try:
        # Get user credentials
        from auth import get_credentials
        email, password = get_credentials()

        if not email or not password:
            raise ValueError("Email and password are required")

        client = RWGPSClient(API_KEY, email, password)
        trips = update_cache(CACHE_FILE, client)
        distances = process_trips(trips)
        yearly_eddington = calculate_yearly_eddington(trips)
        stats = calculate_statistics(distances)
        highest_year, highest_e = get_highest_yearly_eddington(yearly_eddington)
        advanced_metrics = analyze_ride_metrics(trips)

        current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext = \
            calculate_overall_e_progress(distances)

        print("\n=== RIDE STATISTICS ===")
        print(f"Total rides analyzed: {len(distances)}")

        print("\n=== OVERALL EDDINGTON PROGRESS ===")
        print(f"Current overall Eddington: {current_e}")
        print(f"In progress: E={current_e + 1} ({rides_at_next} rides of {current_e + 1}+ miles)")
        print(f"Need {rides_needed_next} more rides of {current_e + 1}+ miles for E={current_e + 1}")
        print(f"Next goal after that: E={current_e + 2} ({rides_at_nextnext} rides of {current_e + 2}+ miles)")
        print(f"Will need {rides_needed_nextnext} more rides of {current_e + 2}+ miles for E={current_e + 2}")

        current_year = datetime.now().year
        if current_year in yearly_eddington:
            print(f"\n=== EDDINGTON YEAR TO DATE ({current_year}) ===")
            ytd_rides = [trip for trip in trips
                        if datetime.strptime(trip['created_at'],
                                          "%Y-%m-%dT%H:%M:%SZ").year == current_year]
            ytd_distances = [Decimal(str(trip['distance'])) * Decimal("0.000621371") for trip in ytd_rides]
            ytd_stats = calculate_statistics(ytd_distances)
            next_e, rides_at_target, rides_needed = calculate_next_yearly_e(trips, current_year)

            print(f"Rides this year: {len(ytd_rides)}")
            print(f"Distance this year: {ytd_stats['total_distance']:,.1f} miles")
            print(f"Current year Eddington: {yearly_eddington[current_year]}")
            print(f"In progress: E={next_e - 1} ({rides_at_target} rides of {next_e - 1}+ miles)")
            print(f"Need {next_e - 1 - rides_at_target} more rides of {next_e - 1}+ miles for E={next_e - 1}")
            print(f"Next goal after that: E={next_e} ({rides_at_target} rides of {next_e}+ miles)")
            print(f"Will need {rides_needed} more rides of {next_e}+ miles for E={next_e}")

        print("\n=== YEARLY EDDINGTON NUMBERS === ")
        for year in sorted(yearly_eddington.keys(), reverse=True):
            current_e = yearly_eddington[year]
            if year == highest_year:
                print(f"{year}: {current_e} *Highest*")
            else:
                print(f"{year}: {current_e}")

        print("\n=== RIDE METRICS ===")
        print(f"Longest ride: {stats['longest_ride']:.1f} miles")
        print(f"Average ride: {stats['average_ride']:.1f} miles")
        print(f"Total distance: {stats['total_distance']:.1f} miles")

        print("\n=== RIDE DISTRIBUTION ===")
        distribution = analyze_ride_distribution(distances)
        for miles in sorted(distribution.keys()):
            if miles % 20 == 0:
                print(f">= {miles} miles: {distribution[miles]} rides")

        print("\n=== MILESTONE ACHIEVEMENTS ===")
        milestones = advanced_metrics['milestone_rides']
        print(f"Century rides (100+ miles): {milestones['centuries']}")
        print(f"Double centuries (200+ miles): {milestones['double_centuries']}")
        print(f"Triple centuries (300+ miles): {milestones['triple_centuries']}")
        print(f"Quad centuries (400+ miles): {milestones['quad_centuries']}")

        print("\n=== TOP 5 LONGEST RIDES === ")
        distance_titles = get_ride_titles(trips, distances)
        for i, (distance, title) in enumerate(distance_titles, 1):
            print(f"{i}. {distance:.1f} miles - {title}")

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
            print(f"{month}: {rides} rides, {distance:.1f} miles")

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        raise




def display_statistics(stats: dict[str, Decimal]) -> None:
    """Display statistics with appropriate rounding only at display time."""
    print(f"Longest ride: {stats['longest_ride']:.1f} miles")
    print(f"Average ride: {stats['average_ride']:.1f} miles")
    print(f"Total distance: {stats['total_distance']:.1f} miles")


if __name__ == "__main__":
    main()
