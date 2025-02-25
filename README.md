# Cycling Statistics App

A Python application that interfaces with the Ride With GPS (RWGPS) API to analyse cycling data and calculate various metrics, with a particular focus on the Eddington number.

## What is the Eddington Number?

The Eddington number (E) for cycling is the maximum number such that you have completed E rides of at least E distance units (miles or kilometers). For example, an Eddington number of 70 means you have completed at least 70 rides that were each at least 70 miles long.

## Features

- Calculate your overall Eddington number
- Track yearly Eddington numbers
- Monitor progress toward your next Eddington milestone
- View year-to-date statistics
- Analyse ride distribution by distance
- Track milestone achievements (century rides, etc.)
- View your top 5 longest rides
- Examine monthly riding statistics
- Support for both miles and kilometers

## Prerequisites

Before you begin, ensure you have:

- Python 3.7 or higher installed
- A Ride With GPS account
- An API key from Ride With GPS

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/cycling-statistics.git
   cd cycling-statistics
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your RWGPS API key:
   ```
   RWGPS_API_KEY=your_api_key_here
   RWGPS_DEFAULT_UNIT=miles  # or km
   ```

## Usage

The application provides a command-line interface with various subcommands:

```bash
# Display full statistics summary
python cli.py summary

# Show Eddington number progress
python cli.py eddington

# Show year-to-date statistics
python cli.py ytd

# Show yearly Eddington numbers
python cli.py yearly

# Show ride metrics
python cli.py metrics

# Show ride distribution
python cli.py distribution

# Show milestone achievements
python cli.py milestones

# Show top 5 longest rides
python cli.py longest

# Show monthly statistics
python cli.py monthly

# Change distance unit
python cli.py unit km  # or miles

# Show current settings
python cli.py status
```

### Command Options

- `--unit {miles,km}`: Set the distance unit for the current command
- `--refresh`: Force refresh data instead of using cache

## Configuration

The application stores your preferred unit (miles or km) and caches ride data to minimise API calls. You can view your current settings with:

```bash
python cli.py status
```

## Authentication

On first run, you'll be prompted to enter your Ride With GPS email and password. You can choose to save these credentials locally for future use.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

