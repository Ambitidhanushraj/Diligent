"""
Generate a comprehensive e-commerce report by joining all tables.
Shows customer information, order details, products, and payment totals.
"""

import sqlite3
import pandas as pd

# Database name
DB_NAME = 'ecommerce.db'

# SQL Query to join all tables and generate the report
SQL_QUERY = """
SELECT 
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    o.order_id,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.unit_price AS price,
    COALESCE(payment_totals.total_amount_paid, 0) AS total_amount_paid
FROM 
    order_items oi
    INNER JOIN orders o ON oi.order_id = o.order_id
    INNER JOIN customers c ON o.customer_id = c.customer_id
    INNER JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN (
        SELECT 
            order_id,
            SUM(amount) AS total_amount_paid
        FROM payments
        WHERE status = 'Completed'
        GROUP BY order_id
    ) payment_totals ON o.order_id = payment_totals.order_id
ORDER BY 
    o.order_date DESC
"""

print("="*100)
print("E-Commerce Report: Customer Orders with Products and Payments")
print("="*100)
print()

# Connect to database
conn = sqlite3.connect(DB_NAME)

try:
    # Execute query and load into DataFrame
    df = pd.read_sql_query(SQL_QUERY, conn)
    
    # Display results
    print(f"Total records: {len(df)}")
    print()
    print("Report Preview (first 20 rows):")
    print("-"*100)
    
    # Format the DataFrame for better display
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 30)
    
    print(df.head(20).to_string(index=False))
    
    print()
    print("-"*100)
    print(f"\nFull report contains {len(df)} rows.")
    print()
    
    # Display summary statistics
    print("Summary Statistics:")
    print("-"*100)
    print(f"Total unique customers: {df['customer_name'].nunique()}")
    print(f"Total unique orders: {df['order_id'].nunique()}")
    print(f"Total unique products: {df['product_name'].nunique()}")
    print(f"Total quantity sold: {df['quantity'].sum()}")
    print(f"Total revenue (from payments): ${df['total_amount_paid'].sum():,.2f}")
    print(f"Average order value: ${df.groupby('order_id')['total_amount_paid'].first().mean():,.2f}")
    
    # Optionally save to CSV
    output_file = 'ecommerce_report.csv'
    df.to_csv(output_file, index=False)
    print()
    print(f"✓ Report saved to: {output_file}")
    
except Exception as e:
    print(f"Error executing query: {e}")
    raise

finally:
    conn.close()

print()
print("="*100)

