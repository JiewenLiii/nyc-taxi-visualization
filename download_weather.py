"""
NYC Weather Data Downloader (2018)
Downloads weather data from NOAA NCDC for NYC Central Park station.
Requires: requests (already installed)

If download fails, run data_prep.py which will generate realistic fallback data.
"""
import os
import requests
import pandas as pd

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, 'nyc_weather_2018.csv')

# NOAA CDO API endpoint for station GHCND:USW00094728 (NYC Central Park)
# Free tier allows limited access. You need a token from: https://www.ncdc.noaa.gov/cdo-web/token
NOAA_TOKEN = None  # Set your token here or pass as env var

BASE_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"


def fetch_noaa_weather():
    """Try to fetch real weather from NOAA. Requires API token."""
    token = NOAA_TOKEN or os.environ.get('NOAA_TOKEN')
    if not token:
        print("No NOAA API token found.")
        print("Get a free token at: https://www.ncdc.noaa.gov/cdo-web/token")
        print("Then either:")
        print("  1. Set NOAA_TOKEN variable in this script")
        print("  2. Set environment variable: set NOAA_TOKEN=your_token")
        print("  3. Run data_prep.py which will generate realistic weather data")
        return False

    headers = {'token': token}
    params = {
        'datasetid': 'GHCND',
        'stationid': 'GHCND:USW00094728',
        'startdate': '2018-01-01',
        'enddate': '2018-12-31',
        'datatypeid': ['TMAX', 'TMIN', 'PRCP', 'SNOW'],
        'limit': 1000,
        'offset': 0,
    }

    all_data = []
    try:
        while True:
            resp = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if 'results' not in result or not result['results']:
                break
            all_data.extend(result['results'])
            params['offset'] += 1000
            if len(all_data) >= result.get('metadata', {}).get('resultset', {}).get('count', 0):
                break

        if not all_data:
            print("No data returned from NOAA API.")
            return False

        # Convert to DataFrame
        df = pd.DataFrame(all_data)
        print(f"Fetched {len(df)} weather records.")

        # Pivot to have one row per date
        pivot = df.pivot_table(
            index='date',
            columns='datatype',
            values='value',
            aggfunc='first'
        ).reset_index()

        pivot.columns.name = None
        pivot = pivot.rename(columns={
            'TMAX': 'temp_max_f',
            'TMIN': 'temp_min_f',
            'PRCP': 'precip_in',
            'SNOW': 'snow_in',
        })

        # Convert tenths of degrees F to F
        for col in ['temp_max_f', 'temp_min_f']:
            if col in pivot.columns:
                pivot[col] = pivot[col] / 10.0

        # Convert tenths of mm to inches
        if 'precip_in' in pivot.columns:
            pivot['precip_in'] = pivot['precip_in'] / 254.0

        # Convert mm to inches
        if 'snow_in' in pivot.columns:
            pivot['snow_in'] = pivot['snow_in'] / 25.4

        # Calculate average temperature
        if 'temp_max_f' in pivot.columns and 'temp_min_f' in pivot.columns:
            pivot['temp_avg_f'] = (pivot['temp_max_f'] + pivot['temp_min_f']) / 2

        pivot.to_csv(OUTPUT_FILE, index=False)
        print(f"Saved weather data to: {OUTPUT_FILE}")
        return True

    except Exception as e:
        print(f"Failed to fetch weather data: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("  NYC Weather Data Downloader (2018)")
    print("=" * 60)
    if os.path.exists(OUTPUT_FILE):
        print(f"Weather file already exists: {OUTPUT_FILE}")
        print("Delete it to re-download.")
    else:
        success = fetch_noaa_weather()
        if not success:
            print("\nFallback: data_prep.py will generate realistic weather data.")
