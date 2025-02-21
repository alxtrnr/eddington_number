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

2025-02-21 14:11:54,640 - INFO - Starting Eddington number calculation...
2025-02-21 14:11:54,660 - INFO - Using cached trip data

=== RIDE STATISTICS ===

Total rides analyzed: 4106

=== EDDINGTON NUMBERS ===

Overall Eddington number: 100

Eddington verification (E=100):

Number of rides >= 100 miles: 100

Yearly Eddington numbers:
------------------------------
2025: 26
2024: 43
2023: 31
2022: 32
2021: 36
2020: 31
2019: 38
2018: 76 *Highest*

=== RIDE METRICS ===
Longest ride: 909.5 miles
Average ride: 23.2 miles
Total distance: 95,221.5 miles

=== RIDE DISTRIBUTION ===
* 	\>= 0 miles: 4106 rides
* 	\>= 20 miles: 1839 rides
* 	\>= 40 miles: 387 rides
* 	\>= 60 miles: 201 rides
* 	\>= 80 miles: 132 rides
* 	\>= 100 miles: 100 rides
* 	\>= 120 miles: 80 rides
* 	\>= 140 miles: 40 rides
* 	\>= 160 miles: 36 rides
* 	\>= 180 miles: 33 rides
* 	\>= 200 miles: 15 rides
* 	\>= 220 miles: 14 rides
* 	\>= 240 miles: 14 rides
* 	\>= 260 miles: 12 rides
* 	\>= 280 miles: 9 rides
* 	\>= 300 miles: 9 rides
* 	\>= 320 miles: 9 rides
* 	\>= 340 miles: 9 rides
* 	\>= 360 miles: 9 rides
* 	\>= 380 miles: 7 rides
* 	\>= 400 miles: 3 rides
* 	\>= 420 miles: 3 rides
* 	\>= 440 miles: 3 rides
* 	\>= 460 miles: 3 rides
* 	\>= 480 miles: 3 rides
* 	\>= 500 miles: 3 rides
* 	\>= 520 miles: 3 rides
* 	\>= 540 miles: 3 rides
* 	\>= 560 miles: 3 rides
* 	\>= 580 miles: 3 rides
* 	\>= 600 miles: 3 rides
* 	\>= 620 miles: 3 rides
* 	\>= 640 miles: 3 rides
* 	\>= 660 miles: 3 rides
* 	\>= 680 miles: 3 rides
* 	\>= 700 miles: 3 rides
* 	\>= 720 miles: 3 rides
* 	\>= 740 miles: 3 rides
* 	\>= 760 miles: 3 rides
* 	\>= 780 miles: 2 rides
* 	\>= 800 miles: 2 rides
* 	\>= 820 miles: 2 rides
* 	\>= 840 miles: 2 rides
* 	\>= 860 miles: 2 rides
* 	\>= 880 miles: 1 rides
* 	\>= 900 miles: 1 rides

=== MILESTONE ACHIEVEMENTS ===
* Century rides (100+ miles): 100
* Double centuries (200+ miles): 15
* Triple centuries (300+ miles): 9
* Quad centuries (400+ miles): 3

Top 5 longest rides:
1. 909.5 miles
2. 876.9 miles
3. 761.6 miles
4. 387.7 miles
5. 387.0 miles

=== NEXT MILESTONE ===
* Rides needed for E=101: 2

=== MONTHLY STATISTICS ===
* 2024-03: 30 rides, 716.2 miles
* 2024-04: 30 rides, 637.8 miles
* 2024-05: 50 rides, 1513.7 miles
* 2024-06: 19 rides, 724.8 miles
* 2024-07: 19 rides, 805.4 miles
* 2024-08: 20 rides, 924.7 miles
* 2024-09: 27 rides, 628.0 miles
* 2024-10: 22 rides, 808.3 miles
* 2024-11: 21 rides, 952.2 miles
* 2024-12: 31 rides, 1020.5 miles
* 2025-01: 23 rides, 825.9 miles
* 2025-02: 13 rides, 846.3 miles

=== YEAR TO DATE (2025) ===

2025-02-21 14:11:54,834 - INFO - Calculation completed successfully
* Rides this year: 36
* Distance this year: 1,672.2 miles
* Current year Eddington: 26

Process finished with exit code 0


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.



