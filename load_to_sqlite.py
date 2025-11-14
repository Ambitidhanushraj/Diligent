"""
Load CSV files into SQLite database.
Creates tables with appropriate data types and loads data from CSV files.
"""

import sqlite3
import pandas as pd
import os

# Database name
DB_NAME = 'ecommerce.db'
CSV_DIR = 'csv_data'

print("="*60)
print("Creating SQLite Database and Loading CSV Data")
print("="*60)

# Remove existing database if it exists
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Removed existing database: {DB_NAME}")

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(DB_NAME)
# Enable foreign key constraints
conn.execute('PRAGMA foreign_keys = ON')
cursor = conn.cursor()

print(f"\nCreated database: {DB_NAME}\n")

# ============================================================================
# CREATE TABLES WITH APPROPRIATE SCHEMAS
# ============================================================================

print("Creating tables...")

# 1. CUSTOMERS TABLE
cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT,
    date_registered TEXT,
    is_active INTEGER
)
""")
print("✓ Created table: customers")

# 2. PRODUCTS TABLE
cursor.execute("""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    price REAL NOT NULL,
    cost REAL,
    stock_quantity INTEGER,
    sku TEXT UNIQUE,
    brand TEXT,
    created_date TEXT,
    is_active INTEGER
)
""")
print("✓ Created table: products")

# 3. ORDERS TABLE
cursor.execute("""
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT,
    shipping_address TEXT,
    shipping_city TEXT,
    shipping_state TEXT,
    shipping_zip TEXT,
    shipping_country TEXT,
    shipping_cost REAL,
    tax_amount REAL,
    subtotal REAL,
    total_amount REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")
print("✓ Created table: orders")

# 4. ORDER_ITEMS TABLE
cursor.execute("""
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount REAL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")
print("✓ Created table: order_items")

# 5. PAYMENTS TABLE
cursor.execute("""
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    payment_method TEXT,
    amount REAL NOT NULL,
    status TEXT,
    transaction_id TEXT UNIQUE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
)
""")
print("✓ Created table: payments")

conn.commit()
print("\nAll tables created successfully!\n")

# ============================================================================
# LOAD DATA FROM CSV FILES
# ============================================================================

print("="*60)
print("Loading data from CSV files...")
print("="*60)

# 1. LOAD CUSTOMERS
print("\n[1/5] Loading customers.csv...")
df_customers = pd.read_csv(f'{CSV_DIR}/customers.csv')
# Convert boolean to integer (True -> 1, False -> 0)
df_customers['is_active'] = df_customers['is_active'].astype(int)
df_customers.to_sql('customers', conn, if_exists='append', index=False)
print(f"   ✓ Inserted {len(df_customers)} customers")

# 2. LOAD PRODUCTS
print("\n[2/5] Loading products.csv...")
df_products = pd.read_csv(f'{CSV_DIR}/products.csv')
# Convert boolean to integer
df_products['is_active'] = df_products['is_active'].astype(int)
df_products.to_sql('products', conn, if_exists='append', index=False)
print(f"   ✓ Inserted {len(df_products)} products")

# 3. LOAD ORDERS
print("\n[3/5] Loading orders.csv...")
df_orders = pd.read_csv(f'{CSV_DIR}/orders.csv')
df_orders.to_sql('orders', conn, if_exists='append', index=False)
print(f"   ✓ Inserted {len(df_orders)} orders")

# 4. LOAD ORDER_ITEMS
print("\n[4/5] Loading order_items.csv...")
df_order_items = pd.read_csv(f'{CSV_DIR}/order_items.csv')
df_order_items.to_sql('order_items', conn, if_exists='append', index=False)
print(f"   ✓ Inserted {len(df_order_items)} order items")

# 5. LOAD PAYMENTS
print("\n[5/5] Loading payments.csv...")
df_payments = pd.read_csv(f'{CSV_DIR}/payments.csv')
df_payments.to_sql('payments', conn, if_exists='append', index=False)
print(f"   ✓ Inserted {len(df_payments)} payments")

# ============================================================================
# VERIFICATION
# ============================================================================

print("\n" + "="*60)
print("Verification - Record counts:")
print("="*60)

tables = ['customers', 'products', 'orders', 'order_items', 'payments']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  {table:15} : {count:4} records")

# Verify foreign key constraints
print("\n" + "="*60)
print("Foreign Key Verification:")
print("="*60)

# Check for orphaned orders (orders without valid customers)
cursor.execute("""
    SELECT COUNT(*) FROM orders 
    WHERE customer_id NOT IN (SELECT customer_id FROM customers)
""")
orphaned_orders = cursor.fetchone()[0]
print(f"  Orphaned orders: {orphaned_orders}")

# Check for orphaned order_items (items without valid orders)
cursor.execute("""
    SELECT COUNT(*) FROM order_items 
    WHERE order_id NOT IN (SELECT order_id FROM orders)
""")
orphaned_items = cursor.fetchone()[0]
print(f"  Orphaned order items: {orphaned_items}")

# Check for orphaned order_items (items without valid products)
cursor.execute("""
    SELECT COUNT(*) FROM order_items 
    WHERE product_id NOT IN (SELECT product_id FROM products)
""")
orphaned_product_items = cursor.fetchone()[0]
print(f"  Order items with invalid products: {orphaned_product_items}")

# Check for orphaned payments (payments without valid orders)
cursor.execute("""
    SELECT COUNT(*) FROM payments 
    WHERE order_id NOT IN (SELECT order_id FROM orders)
""")
orphaned_payments = cursor.fetchone()[0]
print(f"  Orphaned payments: {orphaned_payments}")

# Close connection
conn.close()

print("\n" + "="*60)
print("✓ Database creation and data loading completed successfully!")
print(f"✓ Database saved as: {DB_NAME}")
print("="*60)

