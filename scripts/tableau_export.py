"""
Generate clean CSV files from Instacart data for Tableau dashboard.
Reuses existing analysis functions from src/analysis.py.

Usage: python3 scripts/tableau_export.py
Output: data/processed/
"""

import sys, os
import pandas as pd

sys.path.append('.')
from src.data_loader import load_data
from src.analysis import (
    cohort_retention,
    reorder_rate_by_department,
    order_frequency_distribution,
    peak_ordering_times,
    ab_test_basket_size
)

os.makedirs('data/processed', exist_ok=True)

print("Loading data...")
orders, prior, train, products, departments, aisles = load_data()


# 1. RETENTION — days to second order per user (row per user)
print("Generating retention.csv...")
second_orders = orders[orders['order_number'] == 2][['user_id', 'days_since_prior_order']]
second_orders = second_orders[second_orders['days_since_prior_order'] < 30].copy()
second_orders.columns = ['user_id', 'days_to_second_order']

def retention_bucket(days):
    if days <= 7:
        return 'Within 7 days'
    elif days <= 14:
        return 'Within 14 days'
    elif days <= 28:
        return 'Within 28 days'
    else:
        return 'Over 28 days'

second_orders['retention_bucket'] = second_orders['days_to_second_order'].apply(retention_bucket)
second_orders.to_csv('data/processed/retention.csv', index=False)
print(f"  {len(second_orders)} rows")


# 2. DEPARTMENT LOYALTY — reorder rate per department
print("Generating department_loyalty.csv...")
dept_stats = reorder_rate_by_department(prior, products, departments)
dept_stats.to_csv('data/processed/department_loyalty.csv', index=False)
print(f"  {len(dept_stats)} rows")


# 3. CUSTOMER SEGMENTS — total orders per user with segment label
print("Generating customer_segments.csv...")
orders_per_user = orders.groupby('user_id')['order_number'].max().reset_index()
orders_per_user.columns = ['user_id', 'total_orders']

def segment_label(n):
    if n <= 5:
        return '1-5 orders'
    elif n <= 10:
        return '6-10 orders'
    elif n <= 20:
        return '11-20 orders'
    elif n <= 50:
        return '21-50 orders'
    else:
        return '51-100 orders'

orders_per_user['segment'] = orders_per_user['total_orders'].apply(segment_label)
orders_per_user.to_csv('data/processed/customer_segments.csv', index=False)
print(f"  {len(orders_per_user)} rows")


# 4. PEAK TIMES — hourly and daily order counts (two sheets in one CSV)
print("Generating peak_times_hourly.csv and peak_times_daily.csv...")
time_data = peak_ordering_times(orders)
time_data['hourly'].to_csv('data/processed/peak_times_hourly.csv', index=False)
time_data['daily'].to_csv('data/processed/peak_times_daily.csv', index=False)
print(f"  hourly: {len(time_data['hourly'])} rows, daily: {len(time_data['daily'])} rows")


# 5. AB TEST — per-user basket size with group label
print("Generating ab_test.csv...")
user_peak_hour = orders.groupby('user_id')['order_hour_of_day'].agg(
    lambda x: x.mode()[0]
).reset_index()
user_peak_hour.columns = ['user_id', 'peak_hour']

morning_ids = user_peak_hour[user_peak_hour['peak_hour'].between(6, 12)]['user_id']
evening_ids = user_peak_hour[user_peak_hour['peak_hour'].between(17, 23)]['user_id']

basket_size = prior.groupby('order_id')['product_id'].count().reset_index()
basket_size.columns = ['order_id', 'basket_size']

orders_with_basket = orders[['order_id', 'user_id']].merge(basket_size, on='order_id')

morning_df = orders_with_basket[orders_with_basket['user_id'].isin(morning_ids)].copy()
morning_df['group'] = 'Morning (6am-12pm)'

evening_df = orders_with_basket[orders_with_basket['user_id'].isin(evening_ids)].copy()
evening_df['group'] = 'Evening (5pm-11pm)'

ab_df = pd.concat([morning_df, evening_df], ignore_index=True)
ab_df.to_csv('data/processed/ab_test.csv', index=False)
print(f"  {len(ab_df)} rows")


print("\nDone. Files in data/processed/:")
for f in sorted(os.listdir('data/processed/')):
    size_kb = os.path.getsize(f'data/processed/{f}') // 1024
    print(f"  {f} ({size_kb} KB)")
