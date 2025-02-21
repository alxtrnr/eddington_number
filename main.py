import logging
from typing import List
import time
from datetime import datetime
from client import RWGPSClient
from calculations import (
    calculate_eddington,
    calculate_statistics,
    calculate_yearly_eddington,
    get_highest_yearly_eddington,
    analyze_ride_distribution,
    verify_eddington, analyze_ride_metrics
)
from utils import cache_data, load_cached_data
from config import API_KEY, EMAIL, PASSWORD, CACHE_FILE, CACHE_DURATION

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def process_trips(trips: List[dict]) -> List[float]:
    """Process trips and convert distances to miles."""
    distances = []
    for trip in trips:
        if 'distance' in trip:
            distances.append(trip['distance'] * 0.000621371)  # Convert to miles
        else:
            logging.warning(f"Trip {trip.get('id', 'Unknown ID')} missing distance data.")
    return distances


def should_refresh_cache(cache_file: str) -> bool:
    """Check if cache should be refreshed based on age."""
    try:
        cached_data = load_cached_data(cache_file)
        if not cached_data:
            return True
        cache_time = cached_data.get('timestamp', 0)
        return time.time() - cache_time > CACHE_DURATION
    except Exception:
        return True


def main():
    """Main execution function."""
    logging.info("Starting Eddington number calculation...")

    if not all([API_KEY, EMAIL, PASSWORD]):
        raise ValueError("Missing required environment variables. Please set RWGPS_API_KEY, RWGPS_EMAIL, and RWGPS_PASSWORD")

    try:
        # Check if we should use cached data
        if should_refresh_cache(CACHE_FILE):
            logging.info("Fetching fresh data from RWGPS...")
            client = RWGPSClient(API_KEY, EMAIL, PASSWORD)
            trips = client.get_all_trips()
            cache_data({
                'trips': trips,
                'timestamp': time.time()
            }, CACHE_FILE)
        else:
            logging.info("Using cached trip data")
            cached_data = load_cached_data(CACHE_FILE)
            trips = cached_data['trips']

        # Process all trips
        distances = process_trips(trips)

        # Calculate various metrics
        overall_eddington = calculate_eddington(distances)
        yearly_eddington = calculate_yearly_eddington(trips)
        stats = calculate_statistics(distances)
        highest_year, highest_e = get_highest_yearly_eddington(yearly_eddington)
        advanced_metrics = analyze_ride_metrics(trips)

        # Display results
        print("\n=== RIDE STATISTICS ===")
        print(f"Total rides analyzed: {len(distances)}")

        print("\n=== EDDINGTON NUMBERS ===")
        print(f"Overall Eddington number: {overall_eddington}")
        print(verify_eddington(distances, overall_eddington))

        print("\nYearly Eddington numbers:")
        print("-" * 30)
        for year in sorted(yearly_eddington.keys(), reverse=True):
            current_e = yearly_eddington[year]
            if year == highest_year:
                print(f"{year}: {current_e} *Highest*")
            else:
                print(f"{year}: {current_e}")

        print("\n=== RIDE METRICS ===")
        print(f"Longest ride: {stats['longest_ride']:.1f} miles")
        print(f"Average ride: {stats['average_ride']:.1f} miles")
        print(f"Total distance: {stats['total_distance']:,.1f} miles")

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

        print("\nTop 5 longest rides:")
        for i, distance in enumerate(milestones['longest_rides'], 1):
            print(f"{i}. {distance:.1f} miles")

        print("\n=== NEXT MILESTONE ===")
        print(f"Rides needed for E={advanced_metrics['next_e_target']}: "
              f"{advanced_metrics['rides_needed_next_e']}")

        print("\n=== MONTHLY STATISTICS ===")
        sorted_months = sorted(advanced_metrics['monthly_totals'].keys())[-12:]
        for month in sorted_months:
            rides = advanced_metrics['monthly_counts'][month]
            distance = advanced_metrics['monthly_totals'][month]
            print(f"{month}: {rides} rides, {distance:.1f} miles")

        # Calculate and display year-to-date statistics
        current_year = datetime.now().year
        if current_year in yearly_eddington:
            print(f"\n=== YEAR TO DATE ({current_year}) ===")
            ytd_rides = [trip for trip in trips
                        if datetime.strptime(trip['created_at'],
                        "%Y-%m-%dT%H:%M:%SZ").year == current_year]
            ytd_distances = process_trips(ytd_rides)
            ytd_stats = calculate_statistics(ytd_distances)
            print(f"Rides this year: {len(ytd_rides)}")
            print(f"Distance this year: {ytd_stats['total_distance']:,.1f} miles")
            print(f"Current year Eddington: {yearly_eddington[current_year]}")

        logging.info("Calculation completed successfully")

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()

