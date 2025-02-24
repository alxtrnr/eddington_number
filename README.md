# Cycling Statistics Analyzer

A comprehensive Python application that analyzes cycling data from Ride with GPS, providing detailed statistics, Eddington numbers, and ride metrics.

## Features

- Overall and yearly Eddington number calculations
- Monthly and yearly statistics tracking
- Detailed ride distribution analysis
- Progress tracking towards next achievement levels
- Milestone achievements (centuries, double centuries, etc.)
- Data caching system for efficient API usage
- Secure credential management

## Requirements

- Python 3.x
- Ride with GPS account
- Environment Variables:
  - RWGPS_API_KEY

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install requests python-dotenv tqdm
```
3. Create a `.env` file with your API key:
```bash
RWGPS_API_KEY=your_api_key
```

## Usage

Run the main application:
```bash
python main.py
```

Or use specific commands:
```bash
python cli.py summary
python cli.py eddington
python cli.py ytd
python cli.py yearly
python cli.py metrics
python cli.py distribution
python cli.py milestones
python cli.py longest
python cli.py monthly
```

## Project Structure

```
cycling-stats/
├── main.py         # Main application entry point
├── cli.py          # Command-line interface
├── client.py       # RWGPS API client
├── auth.py         # Authentication handling
├── config.py       # Configuration settings
├── calculations.py # Statistical calculations
└── utils.py        # Utility functions
```

## Features in Detail

**Authentication**
- Secure credential handling
- Optional credential saving
- Token-based authentication

**Data Management**
- Efficient API rate limiting
- Smart caching system
- Incremental updates

**Statistical Analysis**
- Overall Eddington number
- Yearly Eddington numbers
- Monthly distance totals
- Ride distribution analysis
- Milestone tracking

**Progress Tracking**
- Current achievement levels
- Progress towards next goals
- Detailed breakdowns of rides needed

## Command Options

- `summary`: Display complete statistics overview
- `eddington`: Show Eddington number progress
- `ytd`: Display year-to-date statistics
- `yearly`: Show yearly Eddington numbers
- `metrics`: Display ride metrics
- `distribution`: Show ride distribution
- `milestones`: Display milestone achievements
- `longest`: Show top 5 longest rides
- `monthly`: Display monthly statistics

## Security

- Secure credential storage
- Environment variable configuration
- Token-based API authentication

## Data Processing

- Precise decimal calculations
- Comprehensive error handling
- Efficient data caching
- Smart update system that only fetches new rides

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss proposed changes.

## License

This project is licensed under the MIT License.
