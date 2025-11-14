"""
Simple version: Execute SQL query and display results as DataFrame.
"""

import sqlite3
import pandas as pd

# Database name
DB_NAME = 'ecommerce.db'

# SQL Query
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

# Connect and execute
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query(SQL_QUERY, conn)
conn.close()

# Display results
print(df)
print(f"\nTotal rows: {len(df)}")

