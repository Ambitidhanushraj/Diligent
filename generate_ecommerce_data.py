"""
Generate synthetic e-commerce CSV files with realistic data.
Uses pandas and faker to create customers, products, orders, order_items, and payments.
"""

import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)

# Configuration
NUM_CUSTOMERS = 150
NUM_PRODUCTS = 100
NUM_ORDERS = 180
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5
MIN_PAYMENT_AMOUNT = 10.0
MAX_PAYMENT_AMOUNT = 5000.0

# Product categories
CATEGORIES = [
    'Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports & Outdoors',
    'Toys & Games', 'Health & Beauty', 'Automotive', 'Food & Beverages', 'Pet Supplies'
]

# Payment methods
PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']

# Order statuses
ORDER_STATUSES = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned']

# Payment statuses
PAYMENT_STATUSES = ['Pending', 'Completed', 'Failed', 'Refunded']

print("Generating synthetic e-commerce data...")

# ============================================================================
# 1. CUSTOMERS
# ============================================================================
print("Generating customers...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        'customer_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.street_address(),
        'city': fake.city(),
        'state': fake.state(),
        'zip_code': fake.zipcode(),
        'country': fake.country(),
        'date_registered': fake.date_between(start_date='-2y', end_date='today').isoformat(),
        'is_active': random.choice([True, True, True, False])  # 75% active
    })

df_customers = pd.DataFrame(customers)
print(f"Generated {len(df_customers)} customers")

# ============================================================================
# 2. PRODUCTS
# ============================================================================
print("Generating products...")
products = []
for i in range(1, NUM_PRODUCTS + 1):
    base_price = round(random.uniform(5.99, 999.99), 2)
    products.append({
        'product_id': i,
        'product_name': fake.catch_phrase() + ' ' + random.choice(['Pro', 'Premium', 'Deluxe', 'Standard', 'Basic']),
        'category': random.choice(CATEGORIES),
        'description': fake.text(max_nb_chars=200),
        'price': base_price,
        'cost': round(base_price * random.uniform(0.3, 0.7), 2),  # Cost is 30-70% of price
        'stock_quantity': random.randint(0, 500),
        'sku': fake.bothify(text='SKU-####-???', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'brand': fake.company(),
        'created_date': fake.date_between(start_date='-1y', end_date='today').isoformat(),
        'is_active': random.choice([True, True, True, False])  # 75% active
    })

df_products = pd.DataFrame(products)
print(f"Generated {len(df_products)} products")

# ============================================================================
# 3. ORDERS
# ============================================================================
print("Generating orders...")
orders = []
order_id = 1
start_date = datetime.now() - timedelta(days=365)

for _ in range(NUM_ORDERS):
    customer_id = random.randint(1, NUM_CUSTOMERS)
    order_date = fake.date_time_between(start_date=start_date, end_date='now')
    
    orders.append({
        'order_id': order_id,
        'customer_id': customer_id,
        'order_date': order_date.isoformat(),
        'status': random.choice(ORDER_STATUSES),
        'shipping_address': fake.street_address(),
        'shipping_city': fake.city(),
        'shipping_state': fake.state(),
        'shipping_zip': fake.zipcode(),
        'shipping_country': fake.country(),
        'shipping_cost': round(random.uniform(0, 25.99), 2),
        'tax_amount': round(random.uniform(0, 50.00), 2)
    })
    order_id += 1

df_orders = pd.DataFrame(orders)
print(f"Generated {len(df_orders)} orders")

# ============================================================================
# 4. ORDER ITEMS
# ============================================================================
print("Generating order items...")
order_items = []
item_id = 1

for order in orders:
    order_id = order['order_id']
    num_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
    
    # Select unique products for this order
    selected_products = random.sample(range(1, NUM_PRODUCTS + 1), min(num_items, NUM_PRODUCTS))
    
    for product_id in selected_products:
        product = df_products[df_products['product_id'] == product_id].iloc[0]
        quantity = random.randint(1, 5)
        unit_price = product['price']
        # Apply occasional discounts
        discount = random.choice([0, 0, 0, 0, 0.1, 0.15, 0.2, 0.25])  # 50% chance of discount
        discounted_price = round(unit_price * (1 - discount), 2)
        
        order_items.append({
            'item_id': item_id,
            'order_id': order_id,
            'product_id': product_id,
            'quantity': quantity,
            'unit_price': discounted_price,
            'discount': round(discount * 100, 2),  # As percentage
            'subtotal': round(discounted_price * quantity, 2)
        })
        item_id += 1

df_order_items = pd.DataFrame(order_items)
print(f"Generated {len(df_order_items)} order items")

# Calculate order totals and update orders
print("Calculating order totals...")
order_totals = df_order_items.groupby('order_id')['subtotal'].sum().reset_index()
order_totals.columns = ['order_id', 'subtotal']
df_orders = df_orders.merge(order_totals, on='order_id', how='left')
df_orders['subtotal'] = df_orders['subtotal'].fillna(0)
df_orders['total_amount'] = df_orders['subtotal'] + df_orders['shipping_cost'] + df_orders['tax_amount']
df_orders['total_amount'] = df_orders['total_amount'].round(2)

# ============================================================================
# 5. PAYMENTS
# ============================================================================
print("Generating payments...")
payments = []
payment_id = 1

for order in orders:
    order_id = order['order_id']
    order_total = df_orders[df_orders['order_id'] == order_id]['total_amount'].iloc[0]
    
    # Some orders might have multiple payments (partial payments, refunds)
    num_payments = random.choice([1, 1, 1, 2])  # Mostly single payment, sometimes 2
    
    if num_payments == 1:
        # Single payment
        payment_date = fake.date_time_between(
            start_date=datetime.fromisoformat(order['order_date']),
            end_date=datetime.fromisoformat(order['order_date']) + timedelta(days=7)
        )
        payments.append({
            'payment_id': payment_id,
            'order_id': order_id,
            'payment_date': payment_date.isoformat(),
            'payment_method': random.choice(PAYMENT_METHODS),
            'amount': round(order_total, 2),
            'status': random.choice(PAYMENT_STATUSES),
            'transaction_id': fake.bothify(text='TXN-##########', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        })
        payment_id += 1
    else:
        # Split payment (e.g., partial payment + remainder)
        payment1_amount = round(order_total * 0.6, 2)
        payment2_amount = round(order_total - payment1_amount, 2)
        
        payment_date1 = fake.date_time_between(
            start_date=datetime.fromisoformat(order['order_date']),
            end_date=datetime.fromisoformat(order['order_date']) + timedelta(days=3)
        )
        payment_date2 = fake.date_time_between(
            start_date=payment_date1,
            end_date=datetime.fromisoformat(order['order_date']) + timedelta(days=7)
        )
        
        payments.append({
            'payment_id': payment_id,
            'order_id': order_id,
            'payment_date': payment_date1.isoformat(),
            'payment_method': random.choice(PAYMENT_METHODS),
            'amount': payment1_amount,
            'status': 'Completed',
            'transaction_id': fake.bothify(text='TXN-##########', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        })
        payment_id += 1
        
        payments.append({
            'payment_id': payment_id,
            'order_id': order_id,
            'payment_date': payment_date2.isoformat(),
            'payment_method': random.choice(PAYMENT_METHODS),
            'amount': payment2_amount,
            'status': 'Completed',
            'transaction_id': fake.bothify(text='TXN-##########', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        })
        payment_id += 1

df_payments = pd.DataFrame(payments)
print(f"Generated {len(df_payments)} payments")

# ============================================================================
# SAVE TO CSV FILES
# ============================================================================
print("\nSaving CSV files...")

# Create output directory if it doesn't exist
output_dir = 'csv_data'
os.makedirs(output_dir, exist_ok=True)

# Save each dataframe to CSV
df_customers.to_csv(f'{output_dir}/customers.csv', index=False)
print(f"✓ Saved {output_dir}/customers.csv ({len(df_customers)} rows)")

df_products.to_csv(f'{output_dir}/products.csv', index=False)
print(f"✓ Saved {output_dir}/products.csv ({len(df_products)} rows)")

df_orders.to_csv(f'{output_dir}/orders.csv', index=False)
print(f"✓ Saved {output_dir}/orders.csv ({len(df_orders)} rows)")

df_order_items.to_csv(f'{output_dir}/order_items.csv', index=False)
print(f"✓ Saved {output_dir}/order_items.csv ({len(df_order_items)} rows)")

df_payments.to_csv(f'{output_dir}/payments.csv', index=False)
print(f"✓ Saved {output_dir}/payments.csv ({len(df_payments)} rows)")

print("\n" + "="*60)
print("Data generation complete!")
print("="*60)
print(f"\nSummary:")
print(f"  Customers: {len(df_customers)}")
print(f"  Products: {len(df_products)}")
print(f"  Orders: {len(df_orders)}")
print(f"  Order Items: {len(df_order_items)}")
print(f"  Payments: {len(df_payments)}")
print(f"\nAll files saved to '{output_dir}/' directory")

