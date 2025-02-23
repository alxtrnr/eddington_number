# Cycling Eddington Number Calculator

A Python application that calculates your cycling Eddington number (E) and provides detailed riding statistics using the Ride with GPS API.

## Description

The Eddington number (E) for cycling is the maximum number where a cyclist has ridden E miles on E distinct days. For example, an E-number of 100 means you have cycled at least 100 miles on 100 different days.

This application:
- Fetches your ride data from Ride with GPS
- Calculates your overall and yearly Eddington numbers
- Provides detailed ride statistics and distributions
- Shows progress towards your next Eddington milestone
- Tracks century, double century, and longer rides

## Features

- Overall Eddington number calculation
- Yearly Eddington number breakdown
- Ride distribution analysis
- Monthly statistics
- Year-to-date tracking
- Milestone achievements tracking
- Progress tracking towards next E-number
- Data caching to minimize API calls

## Requirements

- Python 3.x
- Ride with GPS account
- Ride with GPS API credentials

## Installation

1. Clone the repository: git clone https://github.com/yourusername/eddington-calculator.git

2. Install required packages: pip install requests python-dotenv tqdm


3. Create a .env file with your Ride with GPS credentials:
	RWGPS_API_KEY=your_api_key
	RWGPS_EMAIL=your_email
	RWGPS_PASSWORD=your_password

## Usage

Run the main script: python main.py

The application will display:
- Your current Eddington number and verification
- Yearly Eddington numbers
- Detailed ride metrics
- Ride distribution
- Milestone achievements
- Monthly statistics
- Year-to-date progress

## Project Structure
	eddington/
	├── init.py
	├── client.py # RWGPS API client
	├── calculations.py # Eddington calculations
	├── utils.py # Utility functions
	├── config.py # Configuration
	└── main.py # Main execution


## Sample Output

**=== RIDE STATISTICS ===**
Total rides analyzed: 4106

=== OVERALL EDDINGTON PROGRESS ===

Current overall Eddington: 98

In progress: E=99 (98 rides of 99+ miles)

Need 1 more rides of 99+ miles for E=99

Next goal after that: E=100 (98 rides of 100+ miles)

Will need 2 more rides of 100+ miles for E=100

**=== EDDINGTON YEAR TO DATE (2025) ===**

Rides this year: 38

Distance this year: 1,762.3 miles

Current year Eddington: 27

In progress: E=28 (25 rides of 28+ miles)

Need 3 more rides of 28+ miles for E=28

Next goal after that: E=29 (25 rides of 29+ miles)

Will need 4 more rides of 29+ miles for E=29

**=== YEARLY EDDINGTON NUMBERS ===**

2025: 27

2024: 42

2023: 31

2022: 33

2021: 33

2020: 31

2019: 39

2018: 34

2017: 35

2016: 43

2015: 44 *Highest*

2014: 39

2013: 38

2012: 20

**=== RIDE METRICS ===**

Longest ride: 909.5 miles

Average ride: 23.1 miles

Total distance: 94927.7 miles

**=== RIDE DISTRIBUTION ===**

\>= 0 miles: 4106 rides

\>= 20 miles: 1839 rides

\>= 40 miles: 386 rides

\>= 60 miles: 199 rides

\>= 80 miles: 130 rides

\>= 100 miles: 98 rides

\>= 120 miles: 78 rides

\>= 140 miles: 38 rides

\>= 160 miles: 34 rides

\>= 180 miles: 31 rides

\>= 200 miles: 15 rides

\>= 220 miles: 14 rides

\>= 240 miles: 14 rides

\>= 260 miles: 12 rides

\>= 280 miles: 9 rides

\>= 300 miles: 9 rides

\>= 320 miles: 9 rides

\>= 340 miles: 9 rides

\>= 360 miles: 9 rides

\>= 380 miles: 7 rides

\>= 400 miles: 3 rides

\>= 420 miles: 3 rides

\>= 440 miles: 3 rides

\>= 460 miles: 3 rides

\>= 480 miles: 3 rides

\>= 500 miles: 3 rides

\>= 520 miles: 3 rides

\>= 540 miles: 3 rides

\>= 560 miles: 3 rides

\>= 580 miles: 3 rides

\>= 600 miles: 3 rides

\>= 620 miles: 3 rides

\>= 640 miles: 3 rides

\>= 660 miles: 3 rides

\>= 680 miles: 3 rides

\>= 700 miles: 3 rides

\>= 720 miles: 3 rides

\>= 740 miles: 3 rides

\>= 760 miles: 3 rides

\>= 780 miles: 2 rides

\>= 800 miles: 2 rides

\>= 820 miles: 2 rides

\>= 840 miles: 2 rides

\>= 860 miles: 2 rides

\>= 880 miles: 1 rides

\>= 900 miles: 1 rides

**=== MILESTONE ACHIEVEMENTS ===**

Century rides (100+ miles): 98

Double centuries (200+ miles): 15

Triple centuries (300+ miles): 9

Quad centuries (400+ miles): 3

**=== TOP 5 LONGEST RIDES ===**
1. 909.5 miles - audax: LEL
2. 876.9 miles - audax: LEJOG
3. 761.6 miles - audax: PBP
4. 387.7 miles - audax: Willesden's Last Gasp
5. 387.0 miles - audax: Orbit London 600k DIY

**=== MONTHLY STATISTICS ===**

2025-02: 14 rides, 549.4 miles

2025-01: 23 rides, 825.9 miles

2024-12: 31 rides, 1020.5 miles

2024-11: 20 rides, 955.2 miles

2024-10: 22 rides, 808.3 miles

2024-09: 12 rides, 447.8 miles

2024-08: 21 rides, 960.8 miles

2024-07: 19 rides, 805.4 miles

2024-06: 19 rides, 724.8 miles

2024-05: 49 rides, 1505.0 miles

2024-04: 31 rides, 646.4 miles

2024-03: 34 rides, 751.2 miles

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
