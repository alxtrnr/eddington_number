import getpass
import json
import os
import sys
import requests
from client import RWGPSClient
from config import API_KEY


def get_credentials():
    """Get user credentials with optional saving."""
    # First try to load saved credentials
    try:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
            return credentials['email'], credentials['password']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If no saved credentials or invalid file, prompt user
        while True:
            email = input("Enter your RWGPS email: ")
            password = getpass.getpass("Enter your RWGPS password: ")

            # Create temporary client to verify credentials
            try:
                client = RWGPSClient(API_KEY, email, password)
                # If we get here, authentication succeeded
                save = input("Authentication successful! Would you like to save your credentials? (y/n): ").lower()
                if save == 'y':
                    with open('credentials.json', 'w') as f:
                        json.dump({'email': email, 'password': password}, f)
                    print("Credentials saved successfully.")
                return email, password
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    print("\nAuthentication Failed!")
                    print("Error: Invalid email or password.")
                    if input("Would you like to try again? (y/n): ").lower() != 'y':
                        sys.exit(1)
                else:
                    raise


