import pandas as pd
import numpy as np


def load_data():
    """Load all Instacart CSV files with optimized dtypes."""

    orders_dtypes = {
        'order_id': 'int32',
        'user_id': 'int32',
        'eval_set': 'category',
        'order_number': 'int8',
        'order_dow': 'int8',
        'order_hour_of_day': 'int8',
        'days_since_prior_order': 'float32'
    }

    prior_dtypes = {
        'order_id': 'int32',
        'product_id': 'int32',
        'add_to_cart_order': 'int8',
        'reordered': 'int8'
    }

    train_dtypes = {
        'order_id': 'int32',
        'product_id': 'int32',
        'add_to_cart_order': 'int8',
        'reordered': 'int8'
    }

    products_dtypes = {
        'product_id': 'int32',
        'aisle_id': 'int16',
        'department_id': 'int8'
    }

    departments_dtypes = {
        'department_id': 'int8'
    }

    aisles_dtypes = {
        'aisle_id': 'int16'
    }

    print("Loading orders...")
    orders = pd.read_csv('data/raw/orders.csv', dtype=orders_dtypes)

    print("Loading prior orders (large file)...")
    prior = pd.read_csv('data/raw/order_products__prior.csv', dtype=prior_dtypes)

    print("Loading train orders...")
    train = pd.read_csv('data/raw/order_products__train.csv', dtype=train_dtypes)

    print("Loading products...")
    products = pd.read_csv('data/raw/products.csv', dtype=products_dtypes)

    print("Loading departments...")
    departments = pd.read_csv('data/raw/departments.csv', dtype=departments_dtypes)

    print("Loading aisles...")
    aisles = pd.read_csv('data/raw/aisles.csv', dtype=aisles_dtypes)

    print("All files loaded.")

    return orders, prior, train, products, departments, aisles
