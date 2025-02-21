from typing import List, Dict, Any
import logging
import requests
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm


class RWGPSClient:
    """Client for interacting with the Ride With GPS API."""

    def __init__(self, api_key: str, email: str, password: str):
        """Initialize the RWGPS client with authentication credentials."""
        self.base_url = "https://ridewithgps.com/api/v1"
        self.api_key = api_key
        self.email = email
        self.password = password
        self._session = self._create_session()
        self.auth_token = self._get_auth_token()

    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
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
        """Authenticate with RWGPS and get auth token."""
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

    def get_all_trips(self) -> List[Dict[str, Any]]:
        """Fetch all trips from RWGPS with progress bar."""
        trips_url = f"{self.base_url}/trips.json"
        all_trips = []
        page = 1
        total_pages = None
        total_rides = None

        headers = {
            'x-rwgps-api-key': self.api_key,
            'x-rwgps-auth-token': self.auth_token
        }

        try:
            # Get first page to determine total pages
            response = self._session.get(
                trips_url,
                headers=headers,
                params={'page': 1, 'version': 2},
                timeout=30
            )
            data = response.json()
            total_pages = data['meta']['pagination']['page_count']
            total_rides = data['meta']['pagination']['record_count']

            with tqdm(total=total_rides, desc="Fetching rides") as pbar:
                while page <= total_pages:
                    params = {'page': page, 'version': 2}
                    response = self._session.get(
                        trips_url,
                        headers=headers,
                        params=params,
                        timeout=30
                    )
                    data = response.json()
                    trips = data['trips']
                    all_trips.extend(trips)
                    pbar.update(len(trips))
                    page += 1
                    time.sleep(1)  # Rate limiting

            return all_trips

        except Exception as e:
            logging.error(f"Failed to fetch trips: {str(e)}")
            raise
