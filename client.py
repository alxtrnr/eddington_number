from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
import logging
import requests
import json
import time
import sys  # Add this for sys.exit()
from log_rate_limit import RateLimit
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
from config import API_KEY
import getpass

from utils import load_token, save_token


class RWGPSClient:
    """Client for interacting with the Ride With GPS API."""

    def __init__(self, api_key: str, email: str = None, password: str = None):
        self.base_url = "https://ridewithgps.com/api/v1"
        self.api_key = api_key
        self._session = self._create_session()

        # Try to load existing token first
        self.auth_token = load_token()
        if not self.auth_token and email and password:
            self.email = email
            self.password = password
            self.auth_token = self._get_auth_token()
            if self.auth_token:
                save_token(self.auth_token)

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

    def _get_auth_token(self, max_retries=3) -> str:
        """Get authentication token with limited retries."""
        retry_count = 0

        while retry_count < max_retries:
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
                # Basic email format validation
                if '@' not in self.email or '.' not in self.email:
                    raise ValueError("Invalid email format")

                response = self._session.post(
                    auth_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                response.raise_for_status()
                data = response.json()

                if 'auth_token' in data and 'auth_token' in data['auth_token']:
                    auth_token = data['auth_token']['auth_token']
                    # Return immediately on success
                    return auth_token

                raise ValueError("Invalid response format from API")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    print("\nAuthentication Failed: Invalid credentials")
                else:
                    print(f"\nHTTP Error: {e.response.status_code}")
            except ValueError as e:
                print(f"\nValidation Error: {str(e)}")
            except Exception as e:
                print(f"\nUnexpected Error: {str(e)}")

            retry_count += 1
            if retry_count < max_retries:
                retry = input("\nWould you like to retry? (y/n): ").lower()
                if retry != 'y':
                    break
                self.email = input("Enter your RWGPS email: ")
                self.password = getpass.getpass("Enter your RWGPS password: ")

        raise Exception("Authentication failed after maximum retries")

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

        try:
            response = self._session.get(
                trips_url,
                headers={
                    'x-rwgps-api-key': self.api_key,
                    'x-rwgps-auth-token': self.auth_token
                },
                params={'page': page, 'version': 2, 'per_page': 50},
                timeout=30
            )
            data = response.json()
            return data['trips']
        except Exception as e:
            logging.error(f"Failed to fetch page {page}: {str(e)}")
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
        """Fetch all trips from RWGPS with simplified progress tracking."""
        trips_url = f"{self.base_url}/trips.json"
        all_trips = []

        try:
            # Get first page to determine total counts
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

            start_time = time.time()
            logging.info(f"Fetching {total_rides} rides across {total_pages} pages")

            with tqdm(total=total_rides, desc="Retrieving rides", unit=" rides per") as pbar:
                for page in range(1, total_pages + 1):
                    try:
                        trips = self.get_trips_page(page)
                        all_trips.extend(trips)
                        pbar.update(len(trips))
                        time.sleep(1)  # Rate limiting
                    except Exception as e:
                        logging.error(f"Error on page {page}: {str(e)}")
                        time.sleep(5)
                        continue

            elapsed_time = time.time() - start_time
            logging.info(f"Retrieved {len(all_trips)} rides in {elapsed_time:.1f} seconds")

            return all_trips

        except Exception as e:
            logging.error(f"Failed to fetch trips: {str(e)}")
            raise
