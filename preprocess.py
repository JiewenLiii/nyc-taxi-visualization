# -*- coding: utf-8 -*-
"""
纽约出租车数据可视化大作业 - 数据预处理与聚合
加载2018年全年Yellow/Green数据，进行清洗、聚合，生成分析用数据
"""
import pandas as pd
import numpy as np
import os
import gc
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = r'd:\数据可视化大作业\题目及数据\材料'
OUTPUT_DIR = r'D:\数据可视化大作业\出租车\data'
ZONE_CSV = os.path.join(DATA_DIR, 'taxi_zone_lookup.csv')

def load_monthly_data(company, month):
    fname = f'{company}_tripdata_2018-{month:02d}.parquet'
    subdir = 'Yellow' if company == 'yellow' else 'Green'
    fpath = os.path.join(DATA_DIR, subdir, fname)
    if not os.path.exists(fpath):
        print(f"  文件不存在: {fpath}")
        return None
    df = pd.read_parquet(fpath)
    return df

def standardize_columns(df, company):
    if company == 'yellow':
        df = df.rename(columns={
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime'
        })
    else:
        df = df.rename(columns={
            'lpep_pickup_datetime': 'pickup_datetime',
            'lpep_dropoff_datetime': 'dropoff_datetime'
        })
    df['company'] = company
    return df

def clean_data(df, company):
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
    df['trip_duration'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60.0
    df = df[(df['trip_duration'] > 1) & (df['trip_duration'] < 600)]
    df = df[(df['trip_distance'] > 0) & (df['trip_distance'] < 200)]
    df = df[(df['fare_amount'] > 0) & (df['fare_amount'] < 1000)]
    df = df[(df['total_amount'] > 0) & (df['total_amount'] < 1000)]
    df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 9)]
    df = df[(df['pickup_datetime'] >= '2018-01-01') & (df['pickup_datetime'] < '2019-01-01')]
    df['pickup_hour'] = df['pickup_datetime'].dt.hour
    df['pickup_day'] = df['pickup_datetime'].dt.day
    df['pickup_month'] = df['pickup_datetime'].dt.month
    df['pickup_dayofweek'] = df['pickup_datetime'].dt.dayofweek
    df['pickup_date'] = df['pickup_datetime'].dt.date
    return df

def process_all_data():
    zone_df = pd.read_csv(ZONE_CSV)
    zone_df.to_csv(os.path.join(OUTPUT_DIR, 'zone_lookup.csv'), index=False, encoding='utf-8-sig')

    monthly_company_stats = []
    hourly_patterns = []
    dow_patterns = []
    payment_patterns = []
    borough_patterns = []
    top_routes = []
    missing_stats = []

    for company in ['yellow', 'green']:
        print(f"\n{'='*60}")
        print(f"处理 {company.upper()} 出租车数据")
        print(f"{'='*60}")

        for month in range(1, 13):
            print(f"  处理 {month}月...", end=' ', flush=True)
            df = load_monthly_data(company, month)
            if df is None:
                continue

            original_count = len(df)
            df = standardize_columns(df, company)

            for col in df.columns:
                if col in ['pickup_datetime', 'dropoff_datetime', 'company']:
                    continue
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    missing_stats.append({
                        'company': company, 'month': month, 'column': col,
                        'null_count': int(null_count),
                        'null_pct': round(null_count / original_count * 100, 2),
                        'total_rows': original_count
                    })

            df = clean_data(df, company)
            cleaned_count = len(df)
            print(f"原始{original_count:,} -> 清洗后{cleaned_count:,}")

            if cleaned_count == 0:
                continue

            monthly_company_stats.append({
                'company': company, 'month': month, 'trip_count': cleaned_count,
                'avg_fare': round(df['fare_amount'].mean(), 2),
                'avg_distance': round(df['trip_distance'].mean(), 2),
                'avg_duration': round(df['trip_duration'].mean(), 2),
                'avg_passengers': round(df['passenger_count'].mean(), 2),
                'avg_tip': round(df['tip_amount'].mean(), 2),
                'avg_total': round(df['total_amount'].mean(), 2),
                'median_fare': round(df['fare_amount'].median(), 2),
                'total_revenue': round(df['total_amount'].sum(), 2)
            })

            sample = df if len(df) < 500000 else df.sample(n=500000, random_state=42)

            hourly = sample.groupby('pickup_hour').agg(
                trip_count=('trip_duration', 'count'),
                avg_fare=('fare_amount', 'mean'),
                avg_distance=('trip_distance', 'mean'),
                avg_duration=('trip_duration', 'mean')
            ).reset_index()
            hourly['company'] = company
            hourly['month'] = month
            hourly_patterns.append(hourly)

            dow = sample.groupby('pickup_dayofweek').agg(
                trip_count=('trip_duration', 'count'),
                avg_fare=('fare_amount', 'mean'),
                avg_distance=('trip_distance', 'mean')
            ).reset_index()
            dow['company'] = company
            dow['month'] = month
            dow_patterns.append(dow)

            pay_map = {1: '信用卡', 2: '现金', 3: '免费', 4: '争议', 5: '未知', 6: '作废'}
            if 'payment_type' in sample.columns:
                pay = sample['payment_type'].value_counts().reset_index()
                pay.columns = ['payment_type', 'count']
                pay['payment_type'] = pay['payment_type'].map(pay_map).fillna(pay['payment_type'].astype(str))
                pay['company'] = company
                pay['month'] = month
                payment_patterns.append(pay)

            sample_zone = sample.merge(zone_df, left_on='PULocationID', right_on='LocationID', how='left')
            if 'Borough' in sample_zone.columns:
                borough = sample_zone.groupby('Borough').agg(
                    trip_count=('trip_duration', 'count'),
                    avg_fare=('fare_amount', 'mean'),
                    avg_distance=('trip_distance', 'mean')
                ).reset_index()
                borough['company'] = company
                borough['month'] = month
                borough_patterns.append(borough)

            routes = sample.groupby(['PULocationID', 'DOLocationID']).size().reset_index(name='count')
            routes = routes.nlargest(20, 'count')
            routes = routes.merge(zone_df[['LocationID', 'Zone']], left_on='PULocationID', right_on='LocationID', how='left')
            routes = routes.rename(columns={'Zone': 'PU_Zone'}).drop(columns=['LocationID'])
            routes = routes.merge(zone_df[['LocationID', 'Zone']], left_on='DOLocationID', right_on='LocationID', how='left')
            routes = routes.rename(columns={'Zone': 'DO_Zone'}).drop(columns=['LocationID'])
            routes['company'] = company
            routes['month'] = month
            top_routes.append(routes)

            del df, sample
            gc.collect()

    print("\n保存聚合数据...")
    pd.DataFrame(monthly_company_stats).to_csv(os.path.join(OUTPUT_DIR, 'monthly_stats.csv'), index=False, encoding='utf-8-sig')
    pd.DataFrame(missing_stats).to_csv(os.path.join(OUTPUT_DIR, 'missing_values.csv'), index=False, encoding='utf-8-sig')
    pd.concat(hourly_patterns, ignore_index=True).to_csv(os.path.join(OUTPUT_DIR, 'hourly_patterns.csv'), index=False, encoding='utf-8-sig')
    pd.concat(dow_patterns, ignore_index=True).to_csv(os.path.join(OUTPUT_DIR, 'dow_patterns.csv'), index=False, encoding='utf-8-sig')
    if payment_patterns:
        pd.concat(payment_patterns, ignore_index=True).to_csv(os.path.join(OUTPUT_DIR, 'payment_patterns.csv'), index=False, encoding='utf-8-sig')
    if borough_patterns:
        pd.concat(borough_patterns, ignore_index=True).to_csv(os.path.join(OUTPUT_DIR, 'borough_patterns.csv'), index=False, encoding='utf-8-sig')
    if top_routes:
        pd.concat(top_routes, ignore_index=True).to_csv(os.path.join(OUTPUT_DIR, 'top_routes.csv'), index=False, encoding='utf-8-sig')
    print("数据预处理完成！")

if __name__ == '__main__':
    process_all_data()
