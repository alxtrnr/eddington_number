import pickle
from typing import Any, Optional
import logging
import os


def cache_data(data: Any, filename: str) -> None:
    """Cache data to a file."""
    try:
        with open(filename, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        logging.error(f"Failed to cache data: {str(e)}")


def load_cached_data(filename: str) -> Optional[Any]:
    """Load cached data from a file."""
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(f"Failed to load cached data: {str(e)}")
        return None


def save_token(token: str) -> None:
    token_file = os.path.expanduser('~/.rwgps/token')
    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    with open(token_file, 'w') as f:
        f.write(token)


def load_token() -> str:
    token_file = os.path.expanduser('~/.rwgps/token')
    try:
        with open(token_file, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
