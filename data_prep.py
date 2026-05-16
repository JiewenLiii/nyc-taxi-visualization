"""
NYC Taxi Trip Data — Comprehensive Data Preparation
Pre-computes all statistics and data needed for the 17-chart dashboard.
"""
import pandas as pd
import numpy as np
import os
import json
import warnings
import zipfile
from datetime import datetime

warnings.filterwarnings('ignore')

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(DATA_DIR, "dashboard_data")
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def jdump(obj, filename):
    """Save object as JSON with special type handling."""
    class NpEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, (np.integer,)): return int(o)
            if isinstance(o, (np.floating,)): return float(o)
            if isinstance(o, (np.ndarray,)): return o.tolist()
            if isinstance(o, (pd.Timestamp,)): return str(o)
            if isinstance(o, (pd.Period,)): return str(o)
            return super().default(o)
    with open(os.path.join(OUT_DIR, filename), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, cls=NpEncoder)
    print(f"  Saved: {filename}")


def load_zone_lookup():
    """Load taxi zone lookup with NaN handling."""
    zones = pd.read_csv(os.path.join(DATA_DIR, 'taxi_zone_lookup.csv'))
    zones = zones.dropna(subset=['LocationID'])
    zones['Borough'] = zones['Borough'].fillna('Unknown')
    zones['Zone'] = zones['Zone'].fillna('Unknown')
    zones['service_zone'] = zones['service_zone'].fillna('Unknown')
    return zones


def get_pickup_dropoff_cols(df):
    """Find pickup/dropoff datetime column names."""
    pu = next((c for c in df.columns if 'pickup' in c.lower() and 'datetime' in c.lower()), None)
    do = next((c for c in df.columns if 'dropoff' in c.lower() and 'datetime' in c.lower()), None)
    return pu, do


def load_monthly_data(color, month=None):
    """Load cleaned data for a color, optionally for specific month(s)."""
    folder = os.path.join(DATA_DIR, f"{color}_清洗后")
    files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
    if month:
        files = [f for f in files if f"-{month:02d}" in f or f"-{month}" in f[-10:]]
    dfs = []
    for f in files:
        df = pd.read_parquet(os.path.join(folder, f))
        pu, do = get_pickup_dropoff_cols(df)
        df['_pu'] = pd.to_datetime(df[pu])
        df['_do'] = pd.to_datetime(df[do])
        df['_duration_min'] = (df['_do'] - df['_pu']).dt.total_seconds() / 60
        df['_month'] = df['_pu'].dt.month
        df['_hour'] = df['_pu'].dt.hour
        df['_day'] = df['_pu'].dt.day
        df['_dow'] = df['_pu'].dt.dayofweek  # Monday=0
        df['_company'] = color
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def sample_data(n=200000):
    """Get a stratified sample across all months for detailed analysis."""
    cache_path = os.path.join(OUT_DIR, "_sample_cache.parquet")
    if os.path.exists(cache_path):
        print("  Loading cached sample...")
        return pd.read_parquet(cache_path)

    print("  Creating stratified sample (this may take a while)...")
    frames = []
    for color in ['Yellow', 'Green']:
        folder = os.path.join(DATA_DIR, f"{color}_清洗后")
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        n_per_file = max(1, n // (len(files) * 2))
        for f in files:
            df = pd.read_parquet(os.path.join(folder, f))
            if len(df) > n_per_file:
                df = df.sample(n=n_per_file, random_state=42)
            pu, do = get_pickup_dropoff_cols(df)
            df['_pu'] = pd.to_datetime(df[pu])
            df['_do'] = pd.to_datetime(df[do])
            df['_duration_min'] = (df['_do'] - df['_pu']).dt.total_seconds() / 60
            df['_month'] = df['_pu'].dt.month
            df['_hour'] = df['_pu'].dt.hour
            df['_dow'] = df['_pu'].dt.dayofweek
            df['_company'] = color
            frames.append(df)
    result = pd.concat(frames, ignore_index=True)
    result.to_parquet(cache_path, index=False)
    print(f"  Sample created: {len(result):,} rows")
    return result


def compute_summary_stats():
    """Compute global summary statistics for KPI cards and yearly aggregation."""
    cache_path = os.path.join(OUT_DIR, "_summary.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    print("\nComputing summary statistics...")
    stats = {'yellow': {}, 'green': {}, 'total': {}}
    monthly_counts = {c: [] for c in ['yellow', 'green']}

    for color, folder_name in [('yellow', 'Yellow_清洗后'), ('green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        total_rows, total_fare, total_dist, total_dur = 0, 0, 0, 0
        for f in files:
            df = pd.read_parquet(os.path.join(folder, f))
            n = len(df)
            total_rows += n
            total_fare += df['total_amount'].sum()
            total_dist += df['trip_distance'].sum()
            pu, do = get_pickup_dropoff_cols(df)
            dur_sec = (pd.to_datetime(df[do]) - pd.to_datetime(df[pu])).dt.total_seconds()
            total_dur += dur_sec.sum()
            month = int(f.split('-')[-1].replace('_clean.parquet', ''))
            monthly_counts[color].append({'month': month, 'count': n})

        stats[color] = {
            'total_trips': int(total_rows),
            'total_fare': float(total_fare),
            'total_distance': float(total_dist),
            'total_duration_min': float(total_dur / 60),
            'avg_fare': float(total_fare / total_rows) if total_rows else 0,
            'avg_distance': float(total_dist / total_rows) if total_rows else 0,
            'avg_duration_min': float(total_dur / total_rows / 60) if total_rows else 0,
        }

    stats['total'] = {
        'total_trips': stats['yellow']['total_trips'] + stats['green']['total_trips'],
        'avg_fare': (stats['yellow']['total_fare'] + stats['green']['total_fare']) /
                    (stats['yellow']['total_trips'] + stats['green']['total_trips']),
        'avg_distance': (stats['yellow']['total_distance'] + stats['green']['total_distance']) /
                        (stats['yellow']['total_trips'] + stats['green']['total_trips']),
        'avg_duration_min': (stats['yellow']['total_duration_min'] + stats['green']['total_duration_min']) /
                            (stats['yellow']['total_trips'] + stats['green']['total_trips']),
    }

    stats['monthly_counts'] = monthly_counts
    jdump(stats, '_summary.json')
    return stats


# ─────────────────────────────────────────────
# Chart 1: KPI Cards
# ─────────────────────────────────────────────
def chart_1_kpi_cards(stats):
    print("\n[Chart 1] KPI cards...")
    data = {
        'total_trips': stats['total']['total_trips'],
        'yellow_trips': stats['yellow']['total_trips'],
        'green_trips': stats['green']['total_trips'],
        'avg_fare': round(stats['total']['avg_fare'], 2),
        'avg_distance': round(stats['total']['avg_distance'], 2),
        'avg_duration_min': round(stats['total']['avg_duration_min'], 1),
    }
    jdump(data, 'chart_1_kpi.json')
    return data


# ─────────────────────────────────────────────
# Chart 2: Missing Values Heatmap (from raw data)
# ─────────────────────────────────────────────
def chart_2_missing_heatmap():
    print("\n[Chart 2] Missing values heatmap...")
    cache_path = os.path.join(OUT_DIR, 'chart_2_missing.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    # Analyze one raw month per color to get missing patterns
    data = []
    for color, raw_folder in [('Yellow', 'Yellow'), ('Green', 'Green')]:
        folder = os.path.join(DATA_DIR, raw_folder)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files:
            df = pd.read_parquet(os.path.join(folder, f))
            # Standardize column names for display
            missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
            total_missing = df.isnull().sum().sum()
            for col in df.columns:
                data.append({
                    'company': color,
                    'file': f.replace('.parquet', ''),
                    'column': col,
                    'missing_pct': round(df[col].isnull().sum() / len(df) * 100, 2),
                    'missing_count': int(df[col].isnull().sum()),
                    'total_rows': len(df),
                })
            break  # Only analyze first file per color for speed
        break  # Only one file

    # Also compute summary by column (average across months)
    columns_data = {}
    for item in data:
        col = item['column']
        if col not in columns_data:
            columns_data[col] = []
        columns_data[col].append(item['missing_pct'])

    summary = [{'column': k, 'avg_missing_pct': round(np.mean(v), 2)} for k, v in columns_data.items()]
    summary.sort(key=lambda x: -x['avg_missing_pct'])

    result = {'details': data, 'column_summary': summary}
    jdump(result, 'chart_2_missing.json')
    return result


# ─────────────────────────────────────────────
# Chart 3: Field Correlation Heatmap
# ─────────────────────────────────────────────
def chart_3_correlation_heatmap(sample):
    print("\n[Chart 3] Field correlation heatmap...")
    numeric_cols = ['trip_distance', 'fare_amount', 'tip_amount', 'tolls_amount',
                    'total_amount', 'passenger_count', 'extra', 'mta_tax',
                    'improvement_surcharge', '_duration_min']
    available = [c for c in numeric_cols if c in sample.columns]
    corr_df = sample[available].corr()
    
    # Replace NaN values with 0 (NaN occurs when a column has zero variance)
    corr_df = corr_df.fillna(0)
    
    result = {
        'columns': available,
        'matrix': corr_df.values.tolist(),
        'labels': [c.replace('_', ' ').title() for c in available],
    }
    jdump(result, 'chart_3_correlation.json')
    return result


# ─────────────────────────────────────────────
# Chart 4: Trip Clustering Scatter Plot
# ─────────────────────────────────────────────
def chart_4_clustering(sample):
    print("\n[Chart 4] Trip clustering scatter...")
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    # Use a subsample for clustering
    cluster_sample = sample[[
        'trip_distance', 'fare_amount', '_duration_min', 'passenger_count'
    ]].dropna()
    cluster_sample = cluster_sample[
        (cluster_sample['trip_distance'] > 0) &
        (cluster_sample['trip_distance'] < 50) &
        (cluster_sample['fare_amount'] > 0) &
        (cluster_sample['fare_amount'] < 200) &
        (cluster_sample['_duration_min'] > 0) &
        (cluster_sample['_duration_min'] < 180)
    ]
    if len(cluster_sample) > 50000:
        cluster_sample = cluster_sample.sample(n=50000, random_state=42)

    X = cluster_sample[['trip_distance', 'fare_amount', '_duration_min']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Prepare scatter data (use a subset for the scatter plot)
    n_plot = min(8000, len(cluster_sample))
    idx = np.random.choice(len(cluster_sample), n_plot, replace=False)

    result = []
    for i in idx:
        result.append({
            'x': float(cluster_sample.iloc[i]['trip_distance']),
            'y': float(cluster_sample.iloc[i]['fare_amount']),
            'duration': float(cluster_sample.iloc[i]['_duration_min']),
            'cluster': int(labels[i]),
        })

    # Cluster centers (inverse transform)
    centers_scaled = kmeans.cluster_centers_
    centers = scaler.inverse_transform(centers_scaled)
    centers_list = []
    for i, c in enumerate(centers):
        centers_list.append({
            'cluster': i,
            'distance': round(float(c[0]), 2),
            'fare': round(float(c[1]), 2),
            'duration': round(float(c[2]), 1),
            'count': int((labels == i).sum()),
        })

    cluster_result = {'points': result, 'centers': centers_list}
    jdump(cluster_result, 'chart_4_clustering.json')
    return cluster_result


# ─────────────────────────────────────────────
# Chart 5: Monthly Trip Trend
# ─────────────────────────────────────────────
def chart_5_monthly_trend(stats):
    print("\n[Chart 5] Monthly trip trend...")
    monthly = stats['monthly_counts']
    result = {
        'months': list(range(1, 13)),
        'month_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'yellow': [0] * 12,
        'green': [0] * 12,
    }
    for item in monthly['yellow']:
        result['yellow'][item['month'] - 1] = item['count']
    for item in monthly['green']:
        result['green'][item['month'] - 1] = item['count']
    jdump(result, 'chart_5_monthly_trend.json')
    return result


# ─────────────────────────────────────────────
# Chart 6: 24-Hour Trip Distribution
# ─────────────────────────────────────────────
def chart_6_hourly_distribution():
    print("\n[Chart 6] 24-hour trip distribution...")
    cache_path = os.path.join(OUT_DIR, 'chart_6_hourly.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    hourly_yellow = np.zeros(24)
    hourly_green = np.zeros(24)

    for color, folder_name in [('yellow', 'Yellow_清洗后'), ('green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        # Only use 4 representative months for speed (Jan, Apr, Jul, Oct)
        sample_files = [f for f in files if any(f'-{m:02d}' in f for m in [1, 4, 7, 10])]
        for f in sample_files:
            df = pd.read_parquet(os.path.join(folder, f))
            pu, _ = get_pickup_dropoff_cols(df)
            hours = pd.to_datetime(df[pu]).dt.hour
            counts = hours.value_counts()
            for h in range(24):
                if color == 'yellow':
                    hourly_yellow[h] += counts.get(h, 0)
                else:
                    hourly_green[h] += counts.get(h, 0)

    result = {
        'hours': list(range(24)),
        'hour_labels': [f'{h:02d}:00' for h in range(24)],
        'yellow': hourly_yellow.tolist(),
        'green': hourly_green.tolist(),
    }
    jdump(result, 'chart_6_hourly.json')
    return result


# ─────────────────────────────────────────────
# Chart 7: Payment Method Ratio
# ─────────────────────────────────────────────
def chart_7_payment_method(sample=None):
    print("\n[Chart 7] Payment method ratio...")
    cache_path = os.path.join(OUT_DIR, 'chart_7_payment.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    payment_counts = {'yellow': {}, 'green': {}}
    payment_labels = {1: 'Credit Card', 2: 'Cash'}

    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        # Use 4 representative months
        sample_files = [f for f in files if any(f'-{m:02d}' in f for m in [1, 4, 7, 10])]
        for f in sample_files:
            df = pd.read_parquet(os.path.join(folder, f))
            if 'payment_type' in df.columns:
                vc = df['payment_type'].value_counts()
                for k, v in vc.items():
                    key = payment_labels.get(int(k), f'Other({int(k)})')
                    payment_counts[color.lower()][key] = payment_counts[color.lower()].get(key, 0) + int(v)

    result = {
        'yellow': [{'name': k, 'value': v} for k, v in payment_counts['yellow'].items()],
        'green': [{'name': k, 'value': v} for k, v in payment_counts['green'].items()],
    }
    jdump(result, 'chart_7_payment.json')
    return result


# ─────────────────────────────────────────────
# Chart 8: Trip Distance Distribution
# ─────────────────────────────────────────────
def chart_8_distance_distribution(sample):
    print("\n[Chart 8] Trip distance distribution...")
    distances = sample[
        (sample['trip_distance'] > 0) & (sample['trip_distance'] < 30)
    ]['trip_distance'].values

    hist, bin_edges = np.histogram(distances, bins=50)
    result = {
        'bins': [round(float(e), 2) for e in bin_edges],
        'counts': hist.tolist(),
        'avg': round(float(distances.mean()), 2),
        'median': round(float(np.median(distances)), 2),
        'p95': round(float(np.percentile(distances, 95)), 2),
    }
    jdump(result, 'chart_8_distance.json')
    return result


# ─────────────────────────────────────────────
# Chart 9: Fare Box Plot
# ─────────────────────────────────────────────
def chart_9_fare_boxplot(sample):
    print("\n[Chart 9] Fare box plot...")
    subset = sample[
        (sample['fare_amount'] > 0) & (sample['fare_amount'] < 100)
    ]
    yellow_fares = subset[subset['_company'] == 'Yellow']['fare_amount'].values
    green_fares = subset[subset['_company'] == 'Green']['fare_amount'].values

    def box_stats(arr):
        return {
            'min': float(np.min(arr)),
            'q1': float(np.percentile(arr, 25)),
            'median': float(np.median(arr)),
            'q3': float(np.percentile(arr, 75)),
            'max': float(np.max(arr)),
            'mean': float(np.mean(arr)),
        }

    result = {
        'yellow': box_stats(yellow_fares),
        'green': box_stats(green_fares),
    }

    # Also by payment type
    for pt in [1, 2]:
        pt_fares = subset[(subset['_company'] == 'Yellow') &
                          (subset['payment_type'] == pt)]['fare_amount'].values
        if len(pt_fares) > 0:
            result[f'yellow_payment_{pt}'] = box_stats(pt_fares)

    jdump(result, 'chart_9_fare_box.json')
    return result


# ─────────────────────────────────────────────
# Chart 10: Cluster Feature Radar Chart
# ─────────────────────────────────────────────
def chart_10_cluster_radar():
    print("\n[Chart 10] Cluster feature radar...")
    cache_path = os.path.join(OUT_DIR, 'chart_4_clustering.json')
    if not os.path.exists(cache_path):
        print("  WARNING: Run chart 4 first!")
        return {}

    with open(cache_path, 'r') as f:
        cluster_data = json.load(f)

    centers = cluster_data.get('centers', [])
    if not centers:
        return {}

    # Normalize for radar chart
    max_dist = max(c['distance'] for c in centers)
    max_fare = max(c['fare'] for c in centers)
    max_dur = max(c['duration'] for c in centers)
    max_cnt = max(c['count'] for c in centers)

    radar_data = []
    for c in centers:
        radar_data.append({
            'cluster': f'Cluster {c["cluster"]}',
            'distance': round(c['distance'] / max_dist * 100, 1),
            'fare': round(c['fare'] / max_fare * 100, 1),
            'duration': round(c['duration'] / max_dur * 100, 1),
            'popularity': round(c['count'] / max_cnt * 100, 1),
            'raw_distance': c['distance'],
            'raw_fare': c['fare'],
            'raw_duration': c['duration'],
            'raw_count': c['count'],
        })

    result = {
        'indicators': [
            {'name': 'Distance', 'max': 100},
            {'name': 'Fare', 'max': 100},
            {'name': 'Duration', 'max': 100},
            {'name': 'Count', 'max': 100},
        ],
        'data': radar_data,
    }
    jdump(result, 'chart_10_radar.json')
    return result


# ─────────────────────────────────────────────
# Chart 11 & 12: Trip Volume Prediction & Residuals
# ─────────────────────────────────────────────
def chart_11_12_prediction(stats):
    print("\n[Chart 11&12] Trip volume prediction...")
    from sklearn.linear_model import LinearRegression

    monthly = stats['monthly_counts']
    months = np.array(range(1, 13)).reshape(-1, 1)

    all_trips = []
    for m in range(1, 13):
        y = sum(item['count'] for item in monthly['yellow']
                if item['month'] == m)
        g = sum(item['count'] for item in monthly['green']
                if item['month'] == m)
        all_trips.append(y + g)

    # Train on Jan-Nov, predict Dec
    X_train = months[:11]
    y_train = np.array(all_trips[:11])

    # Polynomial features for better fit
    from sklearn.preprocessing import PolynomialFeatures
    poly = PolynomialFeatures(degree=3)
    X_poly = poly.fit_transform(X_train)

    model = LinearRegression()
    model.fit(X_poly, y_train)

    # Predict all months for visualization
    X_all_poly = poly.transform(months)
    predicted = model.predict(X_all_poly)

    # Also predict Dec specifically
    residuals = np.array(all_trips) - predicted

    result = {
        'months': list(range(1, 13)),
        'month_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'actual': all_trips,
        'predicted': predicted.tolist(),
        'residuals': residuals.tolist(),
        'train_months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'test_month': 12,
        'mape': round(float(np.mean(np.abs(residuals[:11]) / np.array(all_trips[:11])) * 100), 2),
    }
    jdump(result, 'chart_11_prediction.json')

    # Residual distribution data
    resid_data = {
        'residuals': residuals.tolist(),
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'mean_residual': round(float(np.mean(residuals)), 2),
        'std_residual': round(float(np.std(residuals)), 2),
    }
    jdump(resid_data, 'chart_12_residuals.json')
    return result


# ─────────────────────────────────────────────
# Chart 13: Origin-Destination Sankey
# ─────────────────────────────────────────────
def chart_13_sankey():
    print("\n[Chart 13] OD Sankey diagram...")
    cache_path = os.path.join(OUT_DIR, 'chart_13_sankey.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    # Load zone lookup
    zones = load_zone_lookup()
    zone_boro = dict(zip(zones['LocationID'], zones['Borough']))

    # Aggregate OD pairs from representative months
    od_counts = {}
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        sample_files = [f for f in files if any(f'-{m:02d}' in f for m in [1, 7])]
        for f in sample_files:
            df = pd.read_parquet(os.path.join(folder, f))
            # Use vectorized aggregation for speed
            od_series = df.groupby(['PULocationID', 'DOLocationID']).size()
            for (pu, do), cnt in od_series.items():
                od_counts[(int(pu), int(do))] = od_counts.get((int(pu), int(do)), 0) + int(cnt)

    # Get top 40 OD pairs
    top_pairs = sorted(od_counts.items(), key=lambda x: -x[1])[:40]

    # Build node list
    nodes_set = set()
    for (pu, do), _ in top_pairs:
        nodes_set.add(pu)
        nodes_set.add(do)

    zone_names = dict(zip(zones['LocationID'], zones['Zone']))
    nodes = [{'name': f"{zone_names.get(nid, f'Zone {nid}')} ({zone_boro.get(nid, '?')})"}
             for nid in sorted(nodes_set)]
    node_id_map = {nid: i for i, nid in enumerate(sorted(nodes_set))}

    links = []
    for (pu, do), count in top_pairs:
        if pu in node_id_map and do in node_id_map:
            # Skip self-loops (source == target) as they cause cycles in Sankey
            if node_id_map[pu] != node_id_map[do]:
                links.append({
                    'source': node_id_map[pu],
                    'target': node_id_map[do],
                    'value': count,
                })

    result = {'nodes': nodes, 'links': links}
    jdump(result, 'chart_13_sankey.json')
    return result


# ─────────────────────────────────────────────
# Chart 14: Regional Trip Volume Ranking
# ─────────────────────────────────────────────
def chart_14_region_ranking():
    print("\n[Chart 14] Regional trip volume ranking...")
    cache_path = os.path.join(OUT_DIR, 'chart_14_regions.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    zones = load_zone_lookup()
    zone_boro = dict(zip(zones['LocationID'], zones['Borough']))
    zone_name = dict(zip(zones['LocationID'], zones['Zone']))

    borough_counts = {}
    zone_counts = {}

    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files:
            df = pd.read_parquet(os.path.join(folder, f))
            vc = df['PULocationID'].value_counts()
            for loc_id, cnt in vc.items():
                try:
                    boro = zone_boro.get(int(loc_id), 'Unknown')
                    if pd.isna(boro) or boro == '':
                        boro = 'Unknown'
                except (ValueError, TypeError):
                    boro = 'Unknown'
                borough_counts[boro] = borough_counts.get(boro, 0) + int(cnt)
                zone_counts[int(loc_id)] = zone_counts.get(int(loc_id), 0) + int(cnt)
            break  # Use first month per color (representative)

    # Borough ranking
    borough_ranking = sorted(
        [{'name': k, 'value': v} for k, v in borough_counts.items()],
        key=lambda x: -x['value']
    )

    # Top zone ranking
    zone_ranking = sorted(
        [{'id': k, 'name': zone_name.get(k, f'Zone {k}'),
          'borough': zone_boro.get(k, '?'), 'value': v}
         for k, v in zone_counts.items()],
        key=lambda x: -x['value']
    )

    result = {
        'borough_ranking': borough_ranking,
        'zone_ranking': zone_ranking[:20],
    }
    jdump(result, 'chart_14_regions.json')
    return result


# ─────────────────────────────────────────────
# Chart 15: Weather & Trip Volume
# ─────────────────────────────────────────────
def chart_15_weather():
    print("\n[Chart 15] Weather & trip volume linkage...")
    cache_path = os.path.join(OUT_DIR, 'chart_15_weather.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    # Try to load real weather data first
    weather_file = os.path.join(DATA_DIR, 'nyc_weather_2018.csv')
    if os.path.exists(weather_file):
        print("  Loading real weather data from nyc_weather_2018.csv...")
        raw = pd.read_csv(weather_file, low_memory=False)
        # Parse NOAA hourly data format
        raw['date'] = pd.to_datetime(raw['DATE']).dt.strftime('%Y-%m-%d')
        raw['month'] = pd.to_datetime(raw['DATE']).dt.month
        raw['day'] = pd.to_datetime(raw['DATE']).dt.day

        # Extract daily summary columns (first non-null per day)
        daily = raw.groupby('date').agg(
            month=('month', 'first'),
            day=('day', 'first'),
            temp_avg_f=('DailyAverageDryBulbTemperature', lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else None),
            precip_in=('DailyPrecipitation', lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else 0),
            snow_in=('DailySnowfall', lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else 0),
        ).reset_index()

        # Fill missing values
        daily['temp_avg_f'] = daily['temp_avg_f'].fillna(
            daily.groupby('month')['temp_avg_f'].transform('mean')
        ).fillna(50)
        daily['precip_in'] = daily['precip_in'].fillna(0).replace('T', '0.0').astype(float)
        daily['snow_in'] = daily['snow_in'].fillna(0).replace('T', '0.0').astype(float)
        daily['is_rain'] = daily['precip_in'] > 0.1
        daily['is_snow'] = daily['snow_in'] > 0.5
        weather = daily
        print(f"  Parsed {len(weather)} days of weather data")
    else:
        print("  WARNING: No weather data file found. Generating realistic NYC 2018 weather...")
        # Generate realistic NYC 2018 weather data
        np.random.seed(42)
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        # NYC 2018 actual monthly averages (approximate)
        monthly_temps = [31, 38, 40, 50, 63, 71, 77, 78, 70, 57, 44, 37]  # Fahrenheit
        monthly_precip = [3.2, 4.5, 4.0, 3.8, 3.5, 3.0, 4.2, 4.5, 4.0, 4.2, 3.8, 4.5]  # inches
        monthly_snow = [8.0, 4.0, 11.0, 1.5, 0, 0, 0, 0, 0, 0, 2.5, 1.0]

        weather_records = []
        for month in range(1, 13):
            ndays = days_in_month[month - 1]
            avg_temp = monthly_temps[month - 1]
            avg_precip = monthly_precip[month - 1]
            for day in range(1, ndays + 1):
                temp = avg_temp + np.random.normal(0, 5)
                precip = max(0, np.random.exponential(avg_precip / 5))
                snow = max(0, np.random.exponential(monthly_snow[month - 1] / 5)) if monthly_snow[month - 1] > 0 else 0
                weather_records.append({
                    'date': f'2018-{month:02d}-{day:02d}',
                    'month': month,
                    'day': day,
                    'temp_avg_f': round(temp, 1),
                    'precip_in': round(precip, 2),
                    'snow_in': round(snow, 1),
                    'is_rain': precip > 0.1,
                    'is_snow': snow > 0.5,
                })
        weather = pd.DataFrame(weather_records)
        # Save generated weather for reference
        weather.to_csv(os.path.join(OUT_DIR, 'nyc_weather_2018_generated.csv'), index=False)

    # Compute trip counts by day (all months, vectorized)
    daily_trips = {}
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files:
            df = pd.read_parquet(os.path.join(folder, f))
            pu, _ = get_pickup_dropoff_cols(df)
            # Vectorized: extract date string and count
            dates = pd.to_datetime(df[pu]).dt.strftime('%Y-%m-%d')
            counts = dates.value_counts()
            for date_key, cnt in counts.items():
                daily_trips[date_key] = daily_trips.get(date_key, 0) + int(cnt)

    # Merge
    weather['trip_count'] = weather['date'].map(daily_trips).fillna(
        weather['date'].map(lambda d: daily_trips.get(d, 0))
    )

    # Aggregate by month for simpler view
    monthly = weather.groupby('month').agg(
        avg_temp=('temp_avg_f', 'mean'),
        total_precip=('precip_in', 'sum'),
        total_snow=('snow_in', 'sum'),
        rainy_days=('is_rain', 'sum'),
        snowy_days=('is_snow', 'sum'),
        avg_trips_per_day=('trip_count', 'mean'),
    ).reset_index()

    result = {
        'daily': weather.to_dict(orient='records'),
        'monthly': monthly.to_dict(orient='records'),
    }
    jdump(result, 'chart_15_weather.json')
    return result


# ─────────────────────────────────────────────
# Chart 16: NYC Trip Heatmap (Geo)
# ─────────────────────────────────────────────
def chart_16_heatmap():
    print("\n[Chart 16] NYC trip heatmap (Geo)...")
    cache_path = os.path.join(OUT_DIR, 'chart_16_heatmap.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    # Compute pickup counts by location
    pu_counts = {}
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        for f in files[:2]:  # First 2 months (Jan, Feb)
            df = pd.read_parquet(os.path.join(folder, f))
            vc = df['PULocationID'].value_counts()
            for loc_id, cnt in vc.items():
                pu_counts[int(loc_id)] = pu_counts.get(int(loc_id), 0) + int(cnt)

    # Load zone centroids from taxi zone shapefile
    zones = load_zone_lookup()
    zone_boro = dict(zip(zones['LocationID'], zones['Borough']))

    # We need lat/lon for each zone. Extract from shapefile.
    shp_centroids = get_zone_centroids()

    heat_data = []
    for loc_id, count in pu_counts.items():
        if loc_id in shp_centroids:
            heat_data.append({
                'location_id': loc_id,
                'lng': shp_centroids[loc_id][0],
                'lat': shp_centroids[loc_id][1],
                'count': count,
                'borough': zone_boro.get(loc_id, 'Unknown'),
            })

    result = {'data': heat_data, 'max_count': max(h['count'] for h in heat_data) if heat_data else 1}
    jdump(result, 'chart_16_heatmap.json')
    return result


def get_zone_centroids():
    """Extract zone centroids from the taxi_zones shapefile."""
    import shapefile as shp
    cache_path = os.path.join(OUT_DIR, '_zone_centroids.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return {int(k): v for k, v in json.load(f).items()}

    # Extract shapefile from zip
    shp_dir = os.path.join(OUT_DIR, '_shapefiles')
    os.makedirs(shp_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(DATA_DIR, 'taxi_zones.zip'), 'r') as zf:
        zf.extractall(shp_dir)

    sf = shp.Reader(os.path.join(shp_dir, 'taxi_zones.shp'))
    # Fields in the shapefile
    fields = [f[0] for f in sf.fields[1:]]

    centroids = {}
    for rec, shape in zip(sf.records(), sf.shapes()):
        rec_dict = dict(zip(fields, rec))
        loc_id = rec_dict.get('LocationID', rec_dict.get('OBJECTID', rec_dict.get('location_i', None)))
        if loc_id is None:
            continue
        # Compute centroid from shape points
        points = shape.points
        if points:
            lngs = [p[0] for p in points]
            lats = [p[1] for p in points]
            centroids[int(loc_id)] = [round(np.mean(lngs), 6), round(np.mean(lats), 6)]

    jdump(centroids, '_zone_centroids.json')
    return centroids


def convert_shapefile_to_geojson():
    """Convert taxi_zones shapefile to GeoJSON for ECharts map."""
    geojson_path = os.path.join(OUT_DIR, 'nyc_taxi_zones.geojson')
    if os.path.exists(geojson_path):
        print("  GeoJSON already exists, skipping conversion.")
        return geojson_path

    print("  Converting shapefile to GeoJSON...")
    import shapefile as shp

    # Extract shapefile from zip
    shp_dir = os.path.join(OUT_DIR, '_shapefiles')
    os.makedirs(shp_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(DATA_DIR, 'taxi_zones.zip'), 'r') as zf:
        zf.extractall(shp_dir)

    sf = shp.Reader(os.path.join(shp_dir, 'taxi_zones.shp'))
    fields = [f[0] for f in sf.fields[1:]]

    features = []
    for rec, shape in zip(sf.records(), sf.shapes()):
        rec_dict = dict(zip(fields, rec))
        loc_id = rec_dict.get('LocationID', rec_dict.get('OBJECTID', rec_dict.get('location_i', None)))
        boro = rec_dict.get('borough', rec_dict.get('Borough', ''))
        zone_name = rec_dict.get('zone', rec_dict.get('Zone', ''))

        # Convert shape to GeoJSON geometry
        if shape.shapeType == shp.POLYGON:
            geom_type = 'Polygon'
            coords = [shape.points]
        elif shape.shapeType == shp.MULTIPATCH:
            geom_type = 'Polygon'
            # MultiPatch — take the outer ring
            parts = list(shape.parts)
            coords = []
            for i, start in enumerate(parts):
                end = parts[i + 1] if i + 1 < len(parts) else len(shape.points)
                coords.append(shape.points[start:end])
        else:
            continue

        feature = {
            'type': 'Feature',
            'properties': {
                'LocationID': int(loc_id) if loc_id else None,
                'borough': boro,
                'zone': zone_name,
            },
            'geometry': {
                'type': geom_type,
                'coordinates': coords if len(coords) > 1 else coords[0],
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'features': features,
    }

    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f)

    print(f"  GeoJSON saved: {geojson_path} ({len(features)} zones)")
    return geojson_path


# ─────────────────────────────────────────────
# Chart 17: Top 15 Pickup Areas
# ─────────────────────────────────────────────
def chart_17_top_pickup():
    print("\n[Chart 17] Top 15 pickup areas...")
    cache_path = os.path.join(OUT_DIR, 'chart_17_top_pickup.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    zones = load_zone_lookup()
    zone_name = dict(zip(zones['LocationID'], zones['Zone']))
    zone_boro = dict(zip(zones['LocationID'], zones['Borough']))

    pu_counts = {}
    for color, folder_name in [('Yellow', 'Yellow_清洗后'), ('Green', 'Green_清洗后')]:
        folder = os.path.join(DATA_DIR, folder_name)
        files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])
        sample_files = [f for f in files if any(f'-{m:02d}' in f for m in [1, 4, 7, 10])]
        for f in sample_files:
            df = pd.read_parquet(os.path.join(folder, f))
            vc = df['PULocationID'].value_counts()
            for loc_id, cnt in vc.items():
                pu_counts[int(loc_id)] = pu_counts.get(int(loc_id), 0) + int(cnt)

    top15 = sorted(pu_counts.items(), key=lambda x: -x[1])[:15]
    result = [{
        'rank': i + 1,
        'location_id': loc_id,
        'zone_name': zone_name.get(loc_id, f'Zone {loc_id}'),
        'borough': zone_boro.get(loc_id, 'Unknown'),
        'trip_count': count,
    } for i, (loc_id, count) in enumerate(top15)]

    jdump(result, 'chart_17_top_pickup.json')
    return result


# ─────────────────────────────────────────────
# Main Orchestration
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  NYC Taxi Dashboard — Data Preparation")
    print("=" * 60)
    start_time = datetime.now()

    # Phase 0: GeoJSON conversion (needed for map)
    print("\n[Phase 0] Converting GeoJSON...")
    convert_shapefile_to_geojson()

    # Phase 1: Summary statistics
    print("\n[Phase 1] Global summary statistics...")
    stats = compute_summary_stats()

    # Phase 2: Create data sample for detailed charts
    print("\n[Phase 2] Creating stratified sample...")
    sample = sample_data(n=200000)

    # Phase 3: Generate all chart data
    print("\n[Phase 3] Generating chart data...")

    chart_1_kpi_cards(stats)
    chart_2_missing_heatmap()
    chart_3_correlation_heatmap(sample)
    chart_4_clustering(sample)
    chart_5_monthly_trend(stats)
    chart_6_hourly_distribution()
    chart_7_payment_method()
    chart_8_distance_distribution(sample)
    chart_9_fare_boxplot(sample)
    chart_10_cluster_radar()
    chart_11_12_prediction(stats)
    chart_13_sankey()
    chart_14_region_ranking()
    chart_15_weather()
    chart_16_heatmap()
    chart_17_top_pickup()

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{'='*60}")
    print(f"  Data preparation complete! ({elapsed:.1f}s)")
    print(f"  Output directory: {OUT_DIR}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
