from typing import List, Dict, Tuple
from collections import defaultdict
from datetime import datetime


def calculate_eddington(distances: List[float]) -> int:
    """
    Calculate the Eddington number from a list of ride distances.
    The Eddington number E is the number where you have done E rides of at least E miles.
    """
    if not distances:
        return 0

    days_count = defaultdict(int)
    for distance in distances:
        days_count[distance] += 1

    E = 0
    while True:
        days_above_E = sum(count for dist, count in days_count.items() if dist >= E + 1)
        if days_above_E >= E + 1:
            E += 1
        else:
            break
    return E


def calculate_statistics(distances: List[float]) -> Dict[str, float]:
    """Calculate various statistics from ride distances."""
    if not distances:
        return {
            'longest_ride': 0,
            'average_ride': 0,
            'total_distance': 0
        }

    return {
        'longest_ride': max(distances),
        'average_ride': sum(distances) / len(distances),
        'total_distance': sum(distances)
    }


def calculate_yearly_eddington(trips: List[Dict]) -> Dict[int, int]:
    """
    Calculate Eddington numbers per year.
    Returns a dictionary with years as keys and Eddington numbers as values.
    """
    yearly_distances = defaultdict(list)

    for trip in trips:
        if 'distance' in trip and 'created_at' in trip:
            year = datetime.strptime(trip['created_at'], "%Y-%m-%dT%H:%M:%SZ").year
            distance = trip['distance'] * 0.000621371  # Convert to miles
            yearly_distances[year].append(distance)

    return {year: calculate_eddington(distances)
            for year, distances in yearly_distances.items()}


def get_highest_yearly_eddington(yearly_eddington: Dict[int, int]) -> Tuple[int, int]:
    """
    Return the year and value of highest Eddington number.
    Returns tuple of (year, eddington_number)
    """
    if not yearly_eddington:
        return (0, 0)
    return max(yearly_eddington.items(), key=lambda x: x[1])


def analyze_ride_distribution(distances: List[float]) -> Dict[int, int]:
    """
    Analyze distribution of rides by distance thresholds.
    Returns dictionary with mile thresholds as keys and number of rides above that threshold as values.
    """
    thresholds = {}
    for threshold in range(0, int(max(distances)) + 10, 10):  # Check every 10 mile increment
        rides_above = sum(1 for d in distances if d >= threshold)
        if rides_above > 0:  # Only include thresholds with rides
            thresholds[threshold] = rides_above
    return thresholds


def verify_eddington(distances: List[float], e_number: int) -> str:
    """
    Verify Eddington number calculation with detailed breakdown.
    Returns a string with verification details.
    """
    rides_at_e = sum(1 for d in distances if d >= e_number)
    return f"\nEddington verification (E={e_number}):\n" \
           f"Number of rides >= {e_number} miles: {rides_at_e}"


def get_milestone_rides(distances: List[float]) -> Dict[str, List[float]]:
    """
    Identify milestone rides (longest, shortest, etc.).
    Returns dictionary with milestone categories and corresponding distances.
    """
    if not distances:
        return {}

    sorted_distances = sorted(distances)
    return {
        'total_rides': len(distances),
        'longest': sorted_distances[-1],
        'shortest': sorted_distances[0],
        'median': sorted_distances[len(sorted_distances)//2],
        'centuries': len([d for d in distances if d >= 100]),
        'double_centuries': len([d for d in distances if d >= 200]),
        'triple_centuries': len([d for d in distances if d >= 300]),
        'quad_centuries': len([d for d in distances if d >= 400]),
        'longest_rides': sorted(distances, reverse=True)[:5]
    }


def analyze_ride_metrics(trips: List[Dict]) -> Dict:
    """Calculate advanced riding metrics."""
    distances = [trip['distance'] * 0.000621371 for trip in trips if 'distance' in trip]
    dates = [trip['created_at'] for trip in trips if 'created_at' in trip]

    monthly_totals = defaultdict(float)
    monthly_counts = defaultdict(int)

    for trip in trips:
        if 'distance' and 'created_at' in trip:
            date = datetime.strptime(trip['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            month_key = f"{date.year}-{date.month:02d}"
            monthly_totals[month_key] += trip['distance'] * 0.000621371
            monthly_counts[month_key] += 1

    current_e = calculate_eddington(distances)

    return {
        'monthly_totals': dict(monthly_totals),
        'monthly_counts': dict(monthly_counts),
        'rides_needed_next_e': calculate_rides_needed_next(distances),
        'milestone_rides': get_milestone_rides(distances),
        'next_e_target': current_e + 1
    }


def calculate_rides_needed_next(distances: List[float]) -> int:
    """Calculate rides needed for next Eddington number."""
    current_e = calculate_eddington(distances)
    target = current_e + 1
    current_qualifying = sum(1 for d in distances if d >= target)
    return target - current_qualifying

