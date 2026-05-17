import pandas as pd
import numpy as np
from scipy import stats

def cohort_retention(orders):
    """
    Reorder frequency analysis.
    Since dataset excludes one-time buyers, we measure how quickly
    returning customers place their second order.
    Note: days_since_prior_order is capped at 30 in this dataset.
    We exclude the capped values (30) to avoid skewed metrics.
    """
    second_orders = orders[orders['order_number'] == 2][['user_id', 'days_since_prior_order']]

    # Exclude capped values — 30 means 30+ days, not exactly 30
    second_orders = second_orders[second_orders['days_since_prior_order'] < 30]

    total_users = orders['user_id'].nunique()

    d7 = second_orders[second_orders['days_since_prior_order'] <= 7].shape[0]
    d14 = second_orders[second_orders['days_since_prior_order'] <= 14].shape[0]
    d28 = second_orders[second_orders['days_since_prior_order'] <= 28].shape[0]
    median_days = float(second_orders['days_since_prior_order'].median())

    return {
        'total_users': total_users,
        'reorder_within_7_days_pct': round(d7 / total_users * 100, 2),
        'reorder_within_14_days_pct': round(d14 / total_users * 100, 2),
        'reorder_within_28_days_pct': round(d28 / total_users * 100, 2),
        'median_days_between_orders': median_days
    }

def reorder_rate_by_department(prior, products, departments):
    """
    Calculate reorder rate per department.
    Reorder rate = % of order lines that are reorders vs first time purchases.
    """
    # Merge prior orders with product and department info
    merged = prior.merge(products[['product_id', 'department_id']], on='product_id')
    merged = merged.merge(departments, on='department_id')

    # Calculate reorder rate per department
    dept_stats = merged.groupby('department').agg(
        total_orders=('reordered', 'count'),
        total_reorders=('reordered', 'sum')
    ).reset_index()

    dept_stats['reorder_rate'] = round(
        dept_stats['total_reorders'] / dept_stats['total_orders'] * 100, 2
    )

    return dept_stats.sort_values('reorder_rate', ascending=False)

