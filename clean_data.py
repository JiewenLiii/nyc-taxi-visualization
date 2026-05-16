"""
NYC Taxi Trip Data (2018) — Comprehensive Cleaning Script
Handles all anomalies identified in the analysis phase.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(DATA_DIR, "tidy")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Cleaning Parameters ──────────────────────────────────────────────
MAX_FARE = 500          # max reasonable fare
MAX_DISTANCE = 200      # max reasonable trip distance (miles)
MAX_DURATION_SEC = 6 * 3600   # 6 hours
MIN_DURATION_SEC = 30          # 30 seconds
MAX_PASSENGERS = 6
MIN_PASSENGERS = 1
VALID_PAYMENT_TYPES = {1.0, 2.0}
VALID_RATECODES = {1, 2, 3, 4, 5, 6}
# Fixed surcharges in NYC 2018
EXPECTED_MTA_TAX = 0.50
EXPECTED_IMPROVEMENT_SURCHARGE = 0.30
ALLOWED_EXTRAS = {0.0, 0.50, 1.00}
MAX_TIP_RATIO = 1.0    # tip <= 100% of fare
MAX_TOLLS = 100         # generous max toll


def clean_dataset(color):
    """Clean Green or Yellow taxi data."""
    folder = os.path.join(DATA_DIR, color)
    files = sorted([f for f in os.listdir(folder) if f.endswith('.parquet')])

    # Determine which columns exist
    sample = pd.read_parquet(os.path.join(folder, files[0]))
    has_trip_type = 'trip_type' in sample.columns
    has_ehail_fee = 'ehail_fee' in sample.columns
    pickup_col = next((c for c in sample.columns if 'pickup' in c.lower() and 'datetime' in c.lower()), None)
    dropoff_col = next((c for c in sample.columns if 'dropoff' in c.lower() and 'datetime' in c.lower()), None)

    all_stats = {
        'total': 0, 'dup_removed': 0, 'year_filtered': 0,
        'time_logic': 0, 'duration_too_short': 0, 'duration_too_long': 0,
        'passenger_invalid': 0, 'distance_invalid': 0,
        'fare_negative_or_zero': 0, 'fare_extreme': 0,
        'total_amount_invalid': 0, 'payment_invalid': 0,
        'ratecode_invalid': 0, 'amount_negative': 0,
        'surcharge_wrong': 0, 'extra_invalid': 0,
        'tip_ratio_extreme': 0, 'tolls_extreme': 0,
        'systematic_nulls': 0, 'kept': 0,
    }

    for f in files:
        filepath = os.path.join(folder, f)
        month = f.rsplit('-', 1)[-1].replace('.parquet', '')
        df = pd.read_parquet(filepath)
        n_before = len(df)
        all_stats['total'] += n_before

        # Track reason for each removal
        df['_clean_flag'] = 'keep'
        df['_clean_reason'] = ''

        def flag(reason, mask, df_local):
            df_local.loc[mask & (df_local['_clean_flag'] == 'keep'), '_clean_flag'] = 'remove'
            df_local.loc[mask & (df_local['_clean_flag'] == 'remove'), '_clean_reason'] += reason + ';'

        # 1. Remove duplicates (keep first occurrence)
        raw_cols = [c for c in df.columns if not c.startswith('_clean')]
        dup_mask = df[raw_cols].duplicated(keep='first')
        n_dup = dup_mask.sum()
        all_stats['dup_removed'] += n_dup
        df = df[~dup_mask]
        # Recalc flag columns after dropping
        df['_clean_flag'] = 'keep'
        df['_clean_reason'] = ''

        # 2. Filter to 2018 pickup dates only
        if pickup_col:
            pu = pd.to_datetime(df[pickup_col], errors='coerce')
            bad_year = pu.dt.year != 2018
            all_stats['year_filtered'] += bad_year.sum()
            flag('bad_year', bad_year, df)

        # 3. Time logic: dropoff must be after pickup
        if pickup_col and dropoff_col:
            pu = pd.to_datetime(df[pickup_col], errors='coerce')
            do = pd.to_datetime(df[dropoff_col], errors='coerce')
            dur_sec = (do - pu).dt.total_seconds()

            time_logic = dur_sec <= 0
            too_short = (dur_sec > 0) & (dur_sec < MIN_DURATION_SEC)
            too_long = dur_sec > MAX_DURATION_SEC

            all_stats['time_logic'] += time_logic.sum()
            all_stats['duration_too_short'] += too_short.sum()
            all_stats['duration_too_long'] += too_long.sum()

            flag('time_logic', time_logic, df)
            flag('duration_too_short', too_short, df)
            flag('duration_too_long', too_long, df)

        # 4. Passenger count: 1-6
        if 'passenger_count' in df.columns:
            pc_invalid = df['passenger_count'].isna() | \
                         (df['passenger_count'] < MIN_PASSENGERS) | \
                         (df['passenger_count'] > MAX_PASSENGERS)
            all_stats['passenger_invalid'] += pc_invalid.sum()
            flag('passenger_invalid', pc_invalid, df)

        # 5. Trip distance: 0 < d < MAX_DISTANCE
        if 'trip_distance' in df.columns:
            dist_invalid = df['trip_distance'].isna() | \
                           (df['trip_distance'] <= 0) | \
                           (df['trip_distance'] > MAX_DISTANCE)
            all_stats['distance_invalid'] += dist_invalid.sum()
            flag('distance_invalid', dist_invalid, df)

        # 6. Fare amount: 0 < fare < MAX_FARE
        if 'fare_amount' in df.columns:
            fare_neg_zero = df['fare_amount'].isna() | (df['fare_amount'] <= 0)
            fare_extreme = (df['fare_amount'] > MAX_FARE)
            all_stats['fare_negative_or_zero'] += fare_neg_zero.sum()
            all_stats['fare_extreme'] += fare_extreme.sum()
            flag('fare_neg_zero', fare_neg_zero, df)
            flag('fare_extreme', fare_extreme, df)

        # 7. Total amount: > 0
        if 'total_amount' in df.columns:
            ta_invalid = df['total_amount'].isna() | (df['total_amount'] <= 0)
            all_stats['total_amount_invalid'] += ta_invalid.sum()
            flag('total_invalid', ta_invalid, df)

        # 8. Payment type: 1 or 2 only
        if 'payment_type' in df.columns:
            pay_invalid = df['payment_type'].isna() | \
                          ~df['payment_type'].isin(VALID_PAYMENT_TYPES)
            all_stats['payment_invalid'] += pay_invalid.sum()
            flag('payment_invalid', pay_invalid, df)

        # 9. RatecodeID: 1-6
        if 'RatecodeID' in df.columns:
            rc_invalid = df['RatecodeID'].isna() | \
                         ~df['RatecodeID'].isin(VALID_RATECODES)
            all_stats['ratecode_invalid'] += rc_invalid.sum()
            flag('ratecode_invalid', rc_invalid, df)

        # 10. No negative values in any amount column
        amount_cols = [c for c in ['extra', 'mta_tax', 'tip_amount', 'tolls_amount',
                                    'improvement_surcharge', 'congestion_surcharge']
                       if c in df.columns]
        for ac in amount_cols:
            if ac == 'congestion_surcharge':
                continue  # not applicable in 2018, expected null/0
            neg_mask = df[ac] < 0
            if neg_mask.sum() > 0:
                all_stats['amount_negative'] += neg_mask.sum()
                flag(f'{ac}_negative', neg_mask, df)

        # 11. Fixed surcharges: mta_tax == 0.50, improvement_surcharge == 0.30
        if 'mta_tax' in df.columns:
            mta_wrong = (df['mta_tax'] != EXPECTED_MTA_TAX) & \
                        (df['_clean_flag'] == 'keep')
            all_stats['surcharge_wrong'] += mta_wrong.sum()
            flag('mta_tax_wrong', mta_wrong, df)

        if 'improvement_surcharge' in df.columns:
            imp_wrong = (df['improvement_surcharge'] != EXPECTED_IMPROVEMENT_SURCHARGE) & \
                        (df['_clean_flag'] == 'keep')
            all_stats['surcharge_wrong'] += imp_wrong.sum()
            flag('improvement_surcharge_wrong', imp_wrong, df)

        # 12. Extra should be 0, 0.50, or 1.00
        if 'extra' in df.columns:
            extra_invalid = (df['extra'].notna()) & \
                            (~df['extra'].isin(ALLOWED_EXTRAS)) & \
                            (df['_clean_flag'] == 'keep')
            all_stats['extra_invalid'] += extra_invalid.sum()
            flag('extra_invalid', extra_invalid, df)

        # 13. Tip amount should not exceed fare amount (tip > 100% is suspicious)
        if 'tip_amount' in df.columns and 'fare_amount' in df.columns:
            tip_extreme = (df['tip_amount'] > 0) & (df['fare_amount'] > 0) & \
                          (df['tip_amount'] / df['fare_amount'] > MAX_TIP_RATIO) & \
                          (df['_clean_flag'] == 'keep')
            all_stats['tip_ratio_extreme'] += tip_extreme.sum()
            flag('tip_ratio_extreme', tip_extreme, df)

        # 14. Tolls extreme
        if 'tolls_amount' in df.columns:
            tolls_ext = (df['tolls_amount'] > MAX_TOLLS) & \
                        (df['_clean_flag'] == 'keep')
            all_stats['tolls_extreme'] += tolls_ext.sum()
            flag('tolls_extreme', tolls_ext, df)

        # 15. Remove rows with systematic nulls in key fields (3+ of these null)
        key_cols = [c for c in ['store_and_fwd_flag', 'RatecodeID', 'passenger_count',
                                 'payment_type', 'trip_type'] if c in df.columns]
        if key_cols:
            null_count_key = df[key_cols].isnull().sum(axis=1)
            systematic = (null_count_key >= 3) & (df['_clean_flag'] == 'keep')
            all_stats['systematic_nulls'] += systematic.sum()
            flag('systematic_nulls', systematic, df)

        # ── Apply filtering ──
        kept = df[df['_clean_flag'] == 'keep'].copy()
        removed = df[df['_clean_flag'] == 'remove']
        all_stats['kept'] += len(kept)

        # Drop helper columns
        kept = kept.drop(columns=['_clean_flag', '_clean_reason'])
        # Also drop columns that are 100% null and not applicable for 2018
        for col in kept.columns:
            if kept[col].isnull().all():
                # Only drop if it's expected: congestion_surcharge, ehail_fee, airport_fee
                if col in ['congestion_surcharge', 'ehail_fee', 'airport_fee']:
                    kept = kept.drop(columns=[col])

        # ── Save ──
        out_subdir = os.path.join(OUT_DIR, color)
        os.makedirs(out_subdir, exist_ok=True)
        out_name = f.replace('.parquet', '_clean.parquet')
        kept.to_parquet(os.path.join(out_subdir, out_name), index=False)

        rm_summary = removed['_clean_reason'].value_counts().to_dict() if len(removed) > 0 else {}
        pct_removed = len(removed) / n_before * 100
        print(f"  {f}: {n_before:,} → {len(kept):,} kept, "
              f"{len(removed):,} removed ({pct_removed:.1f}%)")
        if rm_summary:
            top_reasons = sorted(rm_summary.items(), key=lambda x: -x[1])[:5]
            for reason, cnt in top_reasons:
                print(f"         {reason}: {cnt:,}")

    # ── Total summary ──
    print(f"\n{'='*70}")
    print(f"  {color} Taxi - OVERALL CLEANING SUMMARY")
    print(f"{'='*70}")
    print(f"  Total original:     {all_stats['total']:>12,}")
    print(f"  Duplicates:         {all_stats['dup_removed']:>12,}")
    print(f"  Bad year:           {all_stats['year_filtered']:>12,}")
    print(f"  Time logic:         {all_stats['time_logic']:>12,}")
    print(f"  Duration too short: {all_stats['duration_too_short']:>12,}")
    print(f"  Duration too long:  {all_stats['duration_too_long']:>12,}")
    print(f"  Passenger invalid:  {all_stats['passenger_invalid']:>12,}")
    print(f"  Distance invalid:   {all_stats['distance_invalid']:>12,}")
    print(f"  Fare <= 0:          {all_stats['fare_negative_or_zero']:>12,}")
    print(f"  Fare > ${MAX_FARE}:      {all_stats['fare_extreme']:>12,}")
    print(f"  Total amount <= 0:  {all_stats['total_amount_invalid']:>12,}")
    print(f"  Payment invalid:    {all_stats['payment_invalid']:>12,}")
    print(f"  Ratecode invalid:   {all_stats['ratecode_invalid']:>12,}")
    print(f"  Negative amounts:   {all_stats['amount_negative']:>12,}")
    print(f"  Wrong surcharges:   {all_stats['surcharge_wrong']:>12,}")
    print(f"  Extra invalid:      {all_stats['extra_invalid']:>12,}")
    print(f"  Tip ratio extreme:  {all_stats['tip_ratio_extreme']:>12,}")
    print(f"  Tolls extreme:      {all_stats['tolls_extreme']:>12,}")
    print(f"  Systematic nulls:   {all_stats['systematic_nulls']:>12,}")
    print(f"  {'─'*50}")
    print(f"  FINAL KEPT:         {all_stats['kept']:>12,}")
    keep_pct = all_stats['kept'] / all_stats['total'] * 100
    print(f"  Retention rate:     {keep_pct:>11.1f}%")

    return all_stats


# ── Run ──
print("Cleaning Green Taxi data...\n")
green_stats = clean_dataset("Green")

print("\n\nCleaning Yellow Taxi data...\n")
yellow_stats = clean_dataset("Yellow")

print(f"\n\n{'='*70}")
print(f"  GRAND TOTAL")
print(f"{'='*70}")
total_orig = green_stats['total'] + yellow_stats['total']
total_kept = green_stats['kept'] + yellow_stats['kept']
print(f"  Original: {total_orig:,}")
print(f"  Kept:     {total_kept:,}")
print(f"  Removed:  {total_orig - total_kept:,} ({(1-total_kept/total_orig)*100:.1f}%)")
print(f"\nCleaned data saved to: {OUT_DIR}")
print("Done.")
