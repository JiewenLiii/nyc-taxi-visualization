"""Verify cleaned data — check all anomalies have been resolved."""
import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
TIDY_DIR = os.path.join(DATA_DIR, "tidy")


def verify_dataset(color):
    folder = os.path.join(TIDY_DIR, color)
    files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])

    print(f"\n{'='*70}")
    print(f"  VERIFY: {color} Taxi ({len(files)} files)")
    print(f"{'='*70}")

    total_rows = 0
    issues_found = []

    for f in files:
        filepath = os.path.join(folder, f)
        df = pd.read_parquet(filepath)
        n = len(df)
        total_rows += n
        month = f.rsplit('-', 1)[-1].replace('_clean.parquet', '')
        if len(month) == 1:
            month = f.split('-')[-2]
        month = month.replace('_clean', '')

        file_issues = []

        # 1. Check year (all should be 2018)
        pickup_col = next((c for c in df.columns if 'pickup' in c.lower() and 'datetime' in c.lower()), None)
        dropoff_col = next((c for c in df.columns if 'dropoff' in c.lower() and 'datetime' in c.lower()), None)
        if pickup_col:
            pu = pd.to_datetime(df[pickup_col], errors='coerce')
            non_2018 = (pu.dt.year != 2018).sum()
            if non_2018 > 0:
                file_issues.append(f"Non-2018 pickup: {non_2018}")

            if dropoff_col:
                do = pd.to_datetime(df[dropoff_col], errors='coerce')
                # 2. Time logic
                swapped = (do < pu).sum()
                zero_dur = (do == pu).sum()
                dur_sec = (do - pu).dt.total_seconds()
                too_short = ((dur_sec > 0) & (dur_sec < 30)).sum()
                too_long = (dur_sec > 21600).sum()

                if swapped > 0:
                    file_issues.append(f"Dropoff<Pickup: {swapped}")
                if zero_dur > 0:
                    file_issues.append(f"Zero duration: {zero_dur}")
                if too_short > 0:
                    file_issues.append(f"Duration<30s: {too_short}")
                if too_long > 0:
                    file_issues.append(f"Duration>6h: {too_long}")

        # 3. Passenger count
        if 'passenger_count' in df.columns:
            pc_invalid = df['passenger_count'].isna() | (df['passenger_count'] < 1) | (df['passenger_count'] > 6)
            if pc_invalid.sum() > 0:
                file_issues.append(f"Passenger invalid: {pc_invalid.sum()}")

        # 4. Trip distance
        if 'trip_distance' in df.columns:
            td_invalid = df['trip_distance'].isna() | (df['trip_distance'] <= 0) | (df['trip_distance'] > 200)
            if td_invalid.sum() > 0:
                file_issues.append(f"Distance invalid: {td_invalid.sum()}")

        # 5. Fare amount
        if 'fare_amount' in df.columns:
            fa_invalid = df['fare_amount'].isna() | (df['fare_amount'] <= 0) | (df['fare_amount'] > 500)
            if fa_invalid.sum() > 0:
                file_issues.append(f"Fare invalid: {fa_invalid.sum()}")

        # 6. Total amount
        if 'total_amount' in df.columns:
            ta_invalid = df['total_amount'].isna() | (df['total_amount'] <= 0)
            if ta_invalid.sum() > 0:
                file_issues.append(f"Total_amount<=0: {ta_invalid.sum()}")

        # 7. Payment type
        if 'payment_type' in df.columns:
            pt_invalid = df['payment_type'].isna() | ~df['payment_type'].isin([1.0, 2.0])
            if pt_invalid.sum() > 0:
                file_issues.append(f"Payment invalid: {pt_invalid.sum()}")

        # 8. RatecodeID
        if 'RatecodeID' in df.columns:
            rc_invalid = df['RatecodeID'].isna() | ~df['RatecodeID'].isin([1, 2, 3, 4, 5, 6])
            if rc_invalid.sum() > 0:
                file_issues.append(f"RatecodeID invalid: {rc_invalid.sum()}")

        # 9. Negative amounts
        for col in ['extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge']:
            if col in df.columns:
                neg = (df[col] < 0).sum()
                if neg > 0:
                    file_issues.append(f"{col}<0: {neg}")

        # 10. Fixed surcharges
        if 'mta_tax' in df.columns:
            mta_bad = (df['mta_tax'].notna() & (df['mta_tax'] != 0.50)).sum()
            if mta_bad > 0:
                file_issues.append(f"mta_tax!=0.50: {mta_bad}")
        if 'improvement_surcharge' in df.columns:
            imp_bad = (df['improvement_surcharge'].notna() & (df['improvement_surcharge'] != 0.30)).sum()
            if imp_bad > 0:
                file_issues.append(f"improvement_surcharge!=0.30: {imp_bad}")

        # 11. Extra
        if 'extra' in df.columns:
            extra_bad = (df['extra'].notna() & ~df['extra'].isin([0.0, 0.50, 1.0])).sum()
            if extra_bad > 0:
                file_issues.append(f"extra invalid: {extra_bad}")

        # 12. Tip ratio
        if 'tip_amount' in df.columns and 'fare_amount' in df.columns:
            mask = (df['tip_amount'] > 0) & (df['fare_amount'] > 0)
            tip_bad = mask & (df['tip_amount'] / df['fare_amount'] > 1.0)
            if tip_bad.sum() > 0:
                file_issues.append(f"Tip>100% fare: {tip_bad.sum()}")

        # 13. Tolls
        if 'tolls_amount' in df.columns:
            tolls_bad = (df['tolls_amount'] > 100).sum()
            if tolls_bad > 0:
                file_issues.append(f"Tolls>$100: {tolls_bad}")

        # 14. Duplicates
        dup_n = df.duplicated().sum()
        if dup_n > 0:
            file_issues.append(f"Duplicates: {dup_n}")

        if file_issues:
            print(f"  Month {month}: {n:,} rows — {len(file_issues)} ISSUES")
            for iss in file_issues:
                print(f"    WARN: {iss}")
        else:
            print(f"  Month {month}: {n:,} rows — CLEAN")

        issues_found.extend([f"[{color}] Month {month}: {i}" for i in file_issues])

    print(f"\n  TOTAL: {total_rows:,} rows")
    if not issues_found:
        print(f"  Result: ALL CLEAN - No anomalies detected")
    else:
        print(f"  Result: {len(issues_found)} issues found across all months")

    return issues_found


green_issues = verify_dataset("Green")
yellow_issues = verify_dataset("Yellow")

print(f"\n{'='*70}")
print(f"  FINAL VERDICT")
print(f"{'='*70}")
all_issues = green_issues + yellow_issues
if all_issues:
    print(f"  {len(all_issues)} issue(s) still present:")
    for i in all_issues:
        print(f"    - {i}")
else:
    print(f"  Data is fully clean. No anomalies remain.")
print()
