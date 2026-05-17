"""
Run this script locally to regenerate precomputed analysis results.
Requires the full Instacart dataset in data/raw/.

Usage: python3 scripts/precompute.py
Output: assets/precomputed.json
"""
import sys, json, os
sys.path.append('.')
from src.data_loader import load_data
from src.analysis import (
    cohort_retention, reorder_rate_by_department,
    order_frequency_distribution, peak_ordering_times, ab_test_basket_size
)

orders, prior, train, products, departments, aisles = load_data()

results = {
    'retention': cohort_retention(orders),
    'dept_data': reorder_rate_by_department(prior, products, departments).to_dict(orient='records'),
    'freq_data': {
        'stats': order_frequency_distribution(orders)['stats'].to_dict(),
        'buckets': order_frequency_distribution(orders)['buckets'].to_dict(orient='records')
    },
    'time_data': {
        'hourly': peak_ordering_times(orders)['hourly'].to_dict(orient='records'),
        'daily': peak_ordering_times(orders)['daily'].to_dict(orient='records')
    },
    'ab_data': ab_test_basket_size(orders, prior)
}

os.makedirs('assets', exist_ok=True)
with open('assets/precomputed.json', 'w') as f:
    json.dump(results, f)

print('Saved to assets/precomputed.json')
