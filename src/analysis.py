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

def order_frequency_distribution(orders):
    """
    Distribution of total orders per user.
    Shows whether users are occasional or habitual shoppers.
    """
    orders_per_user = orders.groupby('user_id')['order_number'].max().reset_index()
    orders_per_user.columns = ['user_id', 'total_orders']

    distribution = orders_per_user['total_orders'].describe()

    buckets = pd.cut(
        orders_per_user['total_orders'],
        bins=[0, 5, 10, 20, 50, 100],
        labels=['1-5', '6-10', '11-20', '21-50', '51-100']
    )

    bucket_counts = buckets.value_counts().sort_index().reset_index()
    bucket_counts.columns = ['order_range', 'user_count']
    bucket_counts['pct'] = round(bucket_counts['user_count'] / len(orders_per_user) * 100, 2)

    return {
        'stats': distribution,
        'buckets': bucket_counts
    }

def peak_ordering_times(orders):
    """
    Analyze when customers place orders.
    By hour of day and day of week.
    """
    hourly = orders.groupby('order_hour_of_day').size().reset_index()
    hourly.columns = ['hour', 'order_count']
    hourly['pct'] = round(hourly['order_count'] / len(orders) * 100, 2)

    daily = orders.groupby('order_dow').size().reset_index()
    daily.columns = ['day', 'order_count']
    daily['pct'] = round(daily['order_count'] / len(orders) * 100, 2)

    # Map day numbers to names
    day_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday',
               3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    daily['day_name'] = daily['day'].map(day_map)

    return {
        'hourly': hourly,
        'daily': daily
    }

def ab_test_basket_size(orders, prior):
    """
    A/B test simulation: morning vs evening shoppers.
    Tests whether basket size differs significantly between groups.
    Group A: users who predominantly order 6am-12pm
    Group B: users who predominantly order 5pm-11pm
    Uses two-sample t-test. p < 0.05 = statistically significant.
    """
    # Classify each user as morning or evening based on their most common order hour
    user_peak_hour = orders.groupby('user_id')['order_hour_of_day'].agg(
        lambda x: x.mode()[0]
    ).reset_index()
    user_peak_hour.columns = ['user_id', 'peak_hour']

    morning_users = user_peak_hour[
        user_peak_hour['peak_hour'].between(6, 12)
    ]['user_id']

    evening_users = user_peak_hour[
        user_peak_hour['peak_hour'].between(17, 23)
    ]['user_id']

    # Calculate basket size per order
    basket_size = prior.groupby('order_id')['product_id'].count().reset_index()
    basket_size.columns = ['order_id', 'basket_size']

    # Merge with orders to get user_id
    orders_with_basket = orders[['order_id', 'user_id']].merge(basket_size, on='order_id')

    # Get basket sizes for each group
    morning_baskets = orders_with_basket[
        orders_with_basket['user_id'].isin(morning_users)
    ]['basket_size']

    evening_baskets = orders_with_basket[
        orders_with_basket['user_id'].isin(evening_users)
    ]['basket_size']

    # Run t-test
    t_stat, p_value = stats.ttest_ind(morning_baskets, evening_baskets)

    return {
    'morning_users': len(morning_users),
    'evening_users': len(evening_users),
    'morning_avg_basket': round(float(morning_baskets.mean()), 2),
    'evening_avg_basket': round(float(evening_baskets.mean()), 2),
    't_statistic': round(float(t_stat), 4),
    'p_value': float(p_value),
    'significant': bool(p_value < 0.05),
    'practical_significance': abs(float(morning_baskets.mean()) - float(evening_baskets.mean())) > 1.0
    }
