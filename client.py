from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import logging
import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm


class RWGPSClient:
    """Client for interacting with the Ride With GPS API."""

    def __init__(self, api_key: str, email: str, password: str):
        self.base_url = "https://ridewithgps.com/api/v1"
        self.api_key = api_key
        self.email = email
        self.password = password
        self._session = self._create_session()
        self.auth_token = self._get_auth_token()

    def _create_session(self) -> requests.Session:
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("https://", adapter)
        return session

    def _get_auth_token(self) -> str:
        auth_url = f"{self.base_url}/auth_tokens.json"
        headers = {
            'x-rwgps-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'user': {
                'email': self.email,
                'password': self.password
            }
        }
        try:
            response = self._session.post(
                auth_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            if 'auth_token' in data and 'auth_token' in data['auth_token']:
                return data['auth_token']['auth_token']
            raise Exception("Invalid authentication response format")
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            raise

    def get_latest_trip(self) -> dict:
        """Fetch the most recent trip from RWGPS."""
        trips_url = f"{self.base_url}/trips.json"
        headers = {
            'x-rwgps-api-key': self.api_key,
            'x-rwgps-auth-token': self.auth_token
        }
        try:
            response = self._session.get(
                trips_url,
                headers=headers,
                params={'page': 1, 'version': 2, 'per_page': 1},
                timeout=30
            )
            data = response.json()
            return data['trips'][0] if data['trips'] else None
        except Exception as e:
            logging.error(f"Failed to fetch latest trip: {str(e)}")
            raise

    def get_trips_page(self, page: int) -> List[dict]:
        """Fetch a single page of trips."""
        trips_url = f"{self.base_url}/trips.json"
        headers = {
            'x-rwgps-api-key': self.api_key,
            'x-rwgps-auth-token': self.auth_token
        }
        try:
            logging.info(f"Fetching page {page} from RWGPS API")
            response = self._session.get(
                trips_url,
                headers=headers,
                params={'page': page, 'version': 2, 'per_page': 50},
                timeout=30
            )
            data = response.json()
            logging.info(f"Got {len(data['trips'])} trips from page {page}")

            # Add detailed logging for February 2025 rides
            for trip in data['trips']:
                date = datetime.strptime(trip['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                if date.year == 2025 and date.month == 2:
                    distance_miles = trip['distance'] * 0.000621371
                    logging.info(f"Feb 2025 ride: {trip['distance']} meters = {distance_miles:.2f} miles")
                    logging.info(f"Ride details - Date: {date}, ID: {trip['id']}")

            return data['trips']
        except Exception as e:
            logging.error(f"Failed to fetch trips page {page}: {str(e)}")
            raise

    def get_missing_trips(self, cached_trips: List[dict], latest_trip: dict) -> List[dict]:
        """Fetch only the trips that aren't in the cache."""
        if not cached_trips:
            return self.get_all_trips()

        latest_cached_id = max(trip['id'] for trip in cached_trips)
        missing_trips = []

        if latest_trip['id'] > latest_cached_id:
            page = 1
            with tqdm(desc="Fetching new rides") as pbar:
                while True:
                    time.sleep(1)  # Rate limiting
                    new_trips = self.get_trips_page(page)
                    if not new_trips:
                        break

                    # Only keep trips that are newer than our latest cached
                    new_trips = [trip for trip in new_trips if trip['id'] > latest_cached_id]
                    if not new_trips:
                        break

                    missing_trips.extend(new_trips)
                    pbar.update(len(new_trips))
                    page += 1

        return missing_trips

    def get_all_trips(self) -> List[Dict[str, Any]]:
        """Fetch all trips from RWGPS with enhanced validation and logging."""
        trips_url = f"{self.base_url}/trips.json"
        all_trips = []
        page = 1
        total_meters = Decimal('0')
        earliest_date = None
        latest_date = None

        try:
            # Get first page to determine total pages
            response = self._session.get(
                trips_url,
                headers={
                    'x-rwgps-api-key': self.api_key,
                    'x-rwgps-auth-token': self.auth_token
                },
                params={'page': 1, 'version': 2, 'limit': 100},
                timeout=30
            )

            data = response.json()
            total_pages = data['meta']['pagination']['page_count']
            total_rides = data['meta']['pagination']['record_count']
            logging.info(f"RWGPS reports total rides: {total_rides}")

            with tqdm(total=total_rides, desc="Fetching all rides") as pbar:
                while page <= total_pages:
                    try:
                        trips = self.get_trips_page(page)

                        # Track running total and date range
                        for trip in trips:
                            meters = Decimal(str(trip.get('distance', 0)))
                            total_meters += meters

                            date = datetime.strptime(trip['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                            if earliest_date is None or date < earliest_date:
                                earliest_date = date
                            if latest_date is None or date > latest_date:
                                latest_date = date

                        # Log detailed page info
                        logging.info(f"Page {page}/{total_pages}:")
                        logging.info(f"- Retrieved {len(trips)} rides")
                        logging.info(f"- Running total: {total_meters / 1000:.1f}km")

                        # Log first/last ride IDs and dates on page
                        if trips:
                            first_trip = trips[0]
                            last_trip = trips[-1]
                            logging.info(f"- First ride: ID {first_trip['id']}, Date: {first_trip['created_at']}")
                            logging.info(f"- Last ride: ID {last_trip['id']}, Date: {last_trip['created_at']}")

                        all_trips.extend(trips)
                        pbar.update(len(trips))
                        page += 1
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        logging.error(f"Error on page {page}: {str(e)}")
                        time.sleep(5)
                        continue

            # Final validation
            actual_rides = len(all_trips)
            logging.info(f"\nFinal Statistics:")
            logging.info(f"Total rides retrieved: {actual_rides}/{total_rides}")
            logging.info(f"Total distance: {total_meters / 1000:.1f}km")
            logging.info(f"Date range: {earliest_date} to {latest_date}")

            if actual_rides < total_rides:
                logging.warning(f"Missing {total_rides - actual_rides} rides!")

            # Log ride ID ranges
            ride_ids = [trip.get('id') for trip in all_trips]
            logging.info(f"Ride ID range: {min(ride_ids)} to {max(ride_ids)}")

            # Check for gaps in ride IDs
            sorted_ids = sorted(ride_ids)
            gaps = []
            for i in range(len(sorted_ids) - 1):
                if sorted_ids[i + 1] - sorted_ids[i] > 1:
                    gaps.append((sorted_ids[i], sorted_ids[i + 1]))
            if gaps:
                logging.warning(f"Found gaps in ride IDs: {gaps}")

            return all_trips

        except Exception as e:
            logging.error(f"Failed to fetch trips: {str(e)}")
            raise
