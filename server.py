"""
NYC Taxi Dashboard — Flask Server
Serves the dashboard HTML and data APIs.
"""
import os
import json
import pandas as pd
import numpy as np
from flask import Flask, send_file, jsonify, request
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DATA = os.path.join(DATA_DIR, 'dashboard_data')


@app.route('/')
def index():
    """Serve the main dashboard page."""
    response = send_file(os.path.join(DATA_DIR, 'dashboard.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/dashboard_data/<path:filename>')
def serve_data(filename):
    """Serve pre-computed JSON data files and other assets."""
    filepath = os.path.join(DASHBOARD_DATA, filename)
    if os.path.exists(filepath):
        # Set correct MIME type for different file types
        if filename.endswith('.glb'):
            return send_file(filepath, mimetype='model/gltf-binary')
        elif filename.endswith('.gltf'):
            return send_file(filepath, mimetype='model/gltf+json')
        elif filename.endswith('.geojson'):
            return send_file(filepath, mimetype='application/json')
        else:
            return send_file(filepath, mimetype='application/json')
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/monthly_detail')
def monthly_detail():
    """Return detailed monthly data with day-level aggregation."""
    month = request.args.get('month', '1', type=int)
    company = request.args.get('company', 'all', type=str)

    cache_file = os.path.join(DASHBOARD_DATA, f'_monthly_detail_{month}_{company}.json')
    if os.path.exists(cache_file):
        return send_file(cache_file, mimetype='application/json')

    data = {'days': [], 'hourly': [], 'company': company, 'month': month}

    colors = ['Yellow', 'Green'] if company == 'all' else [company]
    for color in colors:
        folder = os.path.join(DATA_DIR, f"{color}_清洗后")
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        target_file = next((f for f in files if f"-{month:02d}" in f), None)
        if target_file is None:
            continue

        df = pd.read_parquet(os.path.join(folder, target_file))
        pu_col = next((c for c in df.columns if 'pickup' in c.lower() and 'datetime' in c.lower()), None)

        if pu_col:
            df['_pu'] = pd.to_datetime(df[pu_col])
            df['_day'] = df['_pu'].dt.day
            df['_hour'] = df['_pu'].dt.hour

            # Daily counts
            daily = df.groupby('_day').size().reset_index(name='count')
            for _, row in daily.iterrows():
                data['days'].append({
                    'day': int(row['_day']),
                    'count': int(row['count']),
                    'company': color,
                })

            # Hourly distribution
            hourly = df.groupby('_hour').size().reset_index(name='count')
            for _, row in hourly.iterrows():
                data['hourly'].append({
                    'hour': int(row['_hour']),
                    'count': int(row['count']),
                    'company': color,
                })

    with open(cache_file, 'w') as f:
        json.dump(data, f)
    return jsonify(data)


@app.route('/api/time_range')
def time_range_data():
    """Return trip data aggregated for a specific time range (for dynamic slider)."""
    start_month = request.args.get('start_month', '1', type=int)
    end_month = request.args.get('end_month', '12', type=int)
    group_by = request.args.get('group_by', 'month')  # month, day, hour

    cache_file = os.path.join(DASHBOARD_DATA,
                              f'_timerange_{start_month}_{end_month}_{group_by}.json')
    if os.path.exists(cache_file):
        return send_file(cache_file, mimetype='application/json')

    data = []
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files:
            month_num = int(f.split('-')[-1].replace('_clean.parquet', ''))
            if month_num < start_month or month_num > end_month:
                continue

            df = pd.read_parquet(os.path.join(folder, f))
            pu_col = next((c for c in df.columns
                          if 'pickup' in c.lower() and 'datetime' in c.lower()), None)
            if pu_col:
                df['_pu'] = pd.to_datetime(df[pu_col])

                if group_by == 'month':
                    grp_col = df['_pu'].dt.month
                elif group_by == 'hour':
                    grp_col = df['_pu'].dt.hour
                else:  # day of week
                    grp_col = df['_pu'].dt.dayofweek

                counts = grp_col.value_counts()
                for k, v in counts.items():
                    data.append({
                        'group': int(k),
                        'count': int(v),
                        'company': color,
                    })

    with open(cache_file, 'w') as f:
        json.dump(data, f)
    return jsonify(data)


@app.route('/api/top_routes')
def top_routes():
    """Return top OD routes with details."""
    limit = request.args.get('limit', '20', type=int)
    month = request.args.get('month', '0', type=int)

    zones = pd.read_csv(os.path.join(DATA_DIR, 'taxi_zone_lookup.csv')).dropna(subset=['LocationID'])
    zones['Borough'] = zones['Borough'].fillna('Unknown')
    zones['Zone'] = zones['Zone'].fillna('Unknown')
    zone_name = dict(zip(zones['LocationID'], zones['Zone']))

    od_counts = {}
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files:
            if month > 0 and f"-{month:02d}" not in f:
                continue
            df = pd.read_parquet(os.path.join(folder, f))
            for _, row in df.iterrows():
                key = (int(row['PULocationID']), int(row['DOLocationID']))
                od_counts[key] = od_counts.get(key, 0) + 1

    top = sorted(od_counts.items(), key=lambda x: -x[1])[:limit]
    result = [{
        'pickup_zone': zone_name.get(pu, f'Zone {pu}'),
        'dropoff_zone': zone_name.get(do, f'Zone {do}'),
        'count': cnt,
    } for (pu, do), cnt in top]

    return jsonify(result)


@app.route('/api/month_stats')
def month_stats():
    """Return detailed statistics for a specific month (from pre-computed cache)."""
    month = request.args.get('month', '1', type=int)
    if month < 1 or month > 12:
        return jsonify({'error': 'month must be between 1 and 12'}), 400

    cache_file = os.path.join(DASHBOARD_DATA, f'_month_stats_{month}.json')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))

    return jsonify({'error': f'month {month} cache not found'}), 404


@app.route('/api/summary')
def api_summary():
    """Return overall summary statistics."""
    with open(os.path.join(DASHBOARD_DATA, '_summary.json'), 'r') as f:
        return jsonify(json.load(f))


if __name__ == '__main__':
    print("=" * 50)
    print("  NYC Taxi Dashboard Server")
    print("=" * 50)
    print(f"  Data directory: {DATA_DIR}")
    print(f"  Dashboard data: {DASHBOARD_DATA}")
    print(f"  Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
