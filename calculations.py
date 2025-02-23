# calculations.py
import logging
from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, getcontext

getcontext().prec = 28  # Adjust precision as needed
METERS_TO_MILES = Decimal("0.000621371192237334")


def calculate_eddington(distances: List[Decimal]) -> int:
    """
    Calculate the Eddington number from a list of ride distances.
    The Eddington number E is the number where you have done E rides of at least E miles.
    """
    if not distances:
        return 0
    max_possible_e = int(max(distances)) + 1
    rides_above_threshold = [0] * (max_possible_e + 1)
    for distance in distances:
        for e in range(1, int(distance) + 1):
            rides_above_threshold[e] += 1
    E = 0
    for i in range(1, max_possible_e + 1):
        if rides_above_threshold[i] >= i:
            E = i
    return E


def calculate_statistics(distances: List[Decimal]) -> Dict[str, Decimal]:
    """Calculate various statistics from ride distances."""
    if not distances:
        return {
            'longest_ride': Decimal('0'),
            'average_ride': Decimal('0'),
            'total_distance': Decimal('0')
        }

    # Keep full precision throughout calculations
    total_distance = sum(distances)

    return {
        'longest_ride': max(distances),
        'average_ride': total_distance / Decimal(len(distances)),
        'total_distance': total_distance  # No rounding here
    }


def calculate_yearly_eddington(trips: List[Dict]) -> Dict[int, int]:
    """
    Calculate Eddington numbers per year.
    Returns a dictionary with years as keys and Eddington numbers as values.
    """
    yearly_distances = defaultdict(list)
    current_year = datetime.now().year
    for trip in trips:
        if 'distance' in trip:
            for date_field in ['departed_at', 'start_date', 'scheduled_date', 'created_at']:
                if date_field in trip and trip[date_field]:
                    try:
                        date_str = trip[date_field].split('+')[0].rstrip('Z')
                        trip_date = datetime.fromisoformat(date_str)
                        if trip_date.year <= current_year:
                            distance = Decimal(str(trip['distance'])) * Decimal("0.000621371")
                            yearly_distances[trip_date.year].append(distance)
                            break
                    except ValueError:
                        continue
    return {year: calculate_eddington(yearly_distances[year])
            for year in yearly_distances.keys()}


def calculate_overall_e_progress(distances: List[Decimal]) -> Tuple[int, int, int, int, int]:
    """
    Calculate current E and progress towards next E numbers.
    Returns (current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext)
    """
    current_e = calculate_eddington(distances)
    next_e = current_e + 1
    nextnext_e = next_e + 1

    rides_at_next = sum(1 for d in distances if d >= next_e)
    rides_needed_next = next_e - rides_at_next

    rides_at_nextnext = sum(1 for d in distances if d >= nextnext_e)
    rides_needed_nextnext = nextnext_e - rides_at_nextnext

    return current_e, rides_at_next, rides_needed_next, rides_at_nextnext, rides_needed_nextnext


def get_highest_yearly_eddington(yearly_eddington: Dict[int, int]) -> Tuple[int, int]:
    """
    Return the year and value of highest Eddington number.
    Returns tuple of (year, eddington_number)
    """
    if not yearly_eddington:
        return (0, 0)
    return max(yearly_eddington.items(), key=lambda x: x[1])


def analyze_ride_distribution(distances: List[Decimal]) -> Dict[int, int]:
    """
    Analyze distribution of rides by distance thresholds.
    Returns dictionary with mile thresholds as keys and number of rides above that threshold as values.
    """
    thresholds = {}
    for threshold in range(0, int(max(distances)) + 10, 10):
        rides_above = sum(1 for d in distances if d >= threshold)
        if rides_above > 0:
            thresholds[threshold] = rides_above
    return thresholds


def verify_eddington(distances: List[Decimal], e_number: int) -> str:
    """
    Verify Eddington number calculation with detailed breakdown.
    Returns a string with verification details.
    """
    rides_at_e = sum(1 for d in distances if d >= e_number)
    return f"\nEddington verification (E={e_number}):\n" \
           f"Number of rides >= {e_number} miles: {rides_at_e}"


def get_milestone_rides(distances: List[Decimal]) -> Dict[str, List[Decimal]]:
    """
    Identify milestone rides (longest, shortest, etc.).
    Returns dictionary with milestone categories and corresponding distances.
    """
    if not distances:
        return {}

    sorted_distances = sorted(distances)

    centuries = sum(1 for d in distances if d >= 100)
    double_centuries = sum(1 for d in distances if d >= 200)
    triple_centuries = sum(1 for d in distances if d >= 300)
    quad_centuries = sum(1 for d in distances if d >= 400)

    longest_rides = sorted(distances, reverse=True)[:5]

    return {
        'total_rides': len(distances),
        'longest': sorted_distances[-1],
        'shortest': sorted_distances[0],
        'median': sorted_distances[len(sorted_distances) // 2],
        'centuries': centuries,
        'double_centuries': double_centuries,
        'triple_centuries': triple_centuries,
        'quad_centuries': quad_centuries,
        'longest_rides': longest_rides
    }


def get_ride_titles(trips: List[Dict], distances: List[Decimal]) -> List[Tuple[Decimal, str]]:
    """Get distances paired with their ride titles, sorted by distance."""
    distance_title_pairs = []

    for trip in trips:
        if 'distance' in trip and 'name' in trip and trip['name']:
            try:
                distance_miles = Decimal(str(trip['distance'])) * METERS_TO_MILES
                distance_title_pairs.append((distance_miles, trip['name']))
            except (ValueError, TypeError) as e:
                logging.error(f"Error processing ride {trip.get('id', 'unknown')}: {e}")

    return sorted(distance_title_pairs, key=lambda x: x[0], reverse=True)[:5]


def analyze_ride_metrics(trips: List[Dict]) -> Dict:
    """Calculate advanced riding metrics."""
    monthly_totals = defaultdict(Decimal)
    monthly_counts = defaultdict(int)
    processed_ids = set()

    for trip in trips:
        if 'distance' in trip and trip['id'] not in processed_ids:
            processed_ids.add(trip['id'])

            date_str = trip.get('departed_at', trip.get('created_at'))
            if not date_str:
                continue

            date_str = date_str.split('+')[0].rstrip('Z')
            date = datetime.fromisoformat(date_str)

            distance_miles = Decimal(str(trip['distance'])) * Decimal("0.000621371")

            month_key = f"{date.year}-{date.month:02d}"
            monthly_totals[month_key] += distance_miles
            monthly_counts[month_key] += 1

            logging.debug(f"Ride {trip['id']}: {trip['distance']}m = {distance_miles:.2f} miles")
            logging.debug(f"Month {month_key} total: {monthly_totals[month_key]:.2f} miles")

    current_e = calculate_eddington([
        Decimal(str(trip['distance'])) * Decimal("0.000621371")
        for trip in trips
        if 'distance' in trip
    ])

    return {
        'monthly_totals': dict(monthly_totals),
        'monthly_counts': dict(monthly_counts),
        'rides_needed_next_e': calculate_rides_needed_next([
            Decimal(str(trip['distance'])) * Decimal("0.000621371")
            for trip in trips
            if 'distance' in trip
        ]),
        'milestone_rides': get_milestone_rides([
            Decimal(str(trip['distance'])) * Decimal("0.000621371")
            for trip in trips
            if 'distance' in trip
        ]),
        'next_e_target': current_e + 1
    }


def calculate_rides_needed_next(distances: List[Decimal]) -> int:
    """Calculate rides needed for next Eddington number."""
    current_e = calculate_eddington(distances)
    target = current_e + 1
    current_qualifying = sum(1 for d in distances if d >= target)
    return target - current_qualifying


def calculate_next_yearly_e(trips: List[Dict], year: int) -> Tuple[int, int, int]:
    """
    Calculate the next E number goal for the specified year and rides needed.
    Returns (next_e, rides_at_target, rides_needed)
    """
    yearly_distances = [
        Decimal(str(trip['distance'])) * Decimal("0.000621371")
        for trip in trips
        if 'distance' in trip and 'created_at' in trip
        and datetime.strptime(trip['created_at'], "%Y-%m-%dT%H:%M:%SZ").year == year
    ]

    current_e = calculate_eddington(yearly_distances)
    next_e = current_e + 1
    rides_at_next_e = sum(1 for d in yearly_distances if d >= next_e)
    rides_needed = next_e - rides_at_next_e
    return next_e, rides_at_next_e, rides_needed
