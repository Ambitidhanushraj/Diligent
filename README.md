# Diligent - E-Commerce Data Generation and Analysis

A Python-based project for generating synthetic e-commerce data, creating SQLite databases, and generating comprehensive reports.

## Overview

This project provides tools to:
- Generate realistic synthetic e-commerce CSV data (customers, products, orders, order items, payments)
- Load data into a SQLite database with proper schema and foreign key constraints
- Generate comprehensive reports by joining all tables

## Features

- **Synthetic Data Generation**: Creates realistic e-commerce data using Faker library
- **Database Management**: SQLite database with proper schema, foreign keys, and data integrity
- **Reporting**: SQL queries and Python scripts for generating detailed reports
- **Data Integrity**: Ensures all foreign key relationships are valid

## Project Structure

```
Diligent_task/
├── generate_ecommerce_data.py  # Generate synthetic CSV files
├── load_to_sqlite.py            # Load CSV data into SQLite database
├── generate_report.py           # Generate comprehensive reports
├── simple_report.py             # Simple report version
├── report_query.sql             # SQL query for reports
├── requirements.txt             # Python dependencies
├── csv_data/                    # Generated CSV files
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── payments.csv
├── ecommerce.db                 # SQLite database
└── README.md                    # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ambitidhanushraj/Diligent.git
cd Diligent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Generate Synthetic E-Commerce Data

Generate CSV files with synthetic data:

```bash
python generate_ecommerce_data.py
```

This creates 5 CSV files in the `csv_data/` directory:
- **customers.csv** (150 customers)
- **products.csv** (100 products)
- **orders.csv** (180 orders)
- **order_items.csv** (541 order items)
- **payments.csv** (223 payments)

**Configuration**: You can modify the number of records by editing the constants at the top of `generate_ecommerce_data.py`:
- `NUM_CUSTOMERS = 150`
- `NUM_PRODUCTS = 100`
- `NUM_ORDERS = 180`

### 2. Load Data into SQLite Database

Create the database and load CSV files:

```bash
python load_to_sqlite.py
```

This script:
- Creates `ecommerce.db` SQLite database
- Creates 5 tables with appropriate schemas
- Loads all CSV data into the database
- Enables foreign key constraints
- Verifies data integrity

**Database Schema**:
- `customers` - Customer information
- `products` - Product catalog
- `orders` - Order headers
- `order_items` - Order line items
- `payments` - Payment transactions

### 3. Generate Reports

Generate a comprehensive report joining all tables:

```bash
python generate_report.py
```

Or use the simple version:

```bash
python simple_report.py
```

The report includes:
- Customer name and email
- Order ID and date
- Product name
- Quantity and price
- Total amount paid
- Results sorted by order date (newest first)

The report is also saved as `ecommerce_report.csv`.

## Database Schema

### Tables and Relationships

```
customers (1) ──< (many) orders (1) ──< (many) order_items (many) >── (1) products
                                 │
                                 └──< (many) payments
```

### Key Fields

**customers**
- `customer_id` (PRIMARY KEY)
- `first_name`, `last_name`, `email`
- `address`, `city`, `state`, `zip_code`, `country`
- `date_registered`, `is_active`

**products**
- `product_id` (PRIMARY KEY)
- `product_name`, `category`, `description`
- `price`, `cost`, `stock_quantity`
- `sku`, `brand`, `created_date`, `is_active`

**orders**
- `order_id` (PRIMARY KEY)
- `customer_id` (FOREIGN KEY → customers)
- `order_date`, `status`
- `shipping_address`, `shipping_city`, `shipping_state`, `shipping_zip`, `shipping_country`
- `shipping_cost`, `tax_amount`, `subtotal`, `total_amount`

**order_items**
- `item_id` (PRIMARY KEY)
- `order_id` (FOREIGN KEY → orders)
- `product_id` (FOREIGN KEY → products)
- `quantity`, `unit_price`, `discount`, `subtotal`

**payments**
- `payment_id` (PRIMARY KEY)
- `order_id` (FOREIGN KEY → orders)
- `payment_date`, `payment_method`, `amount`, `status`
- `transaction_id`

## SQL Query Example

The main report query joins all tables:

```sql
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
    o.order_date DESC;
```

## Sample Output

The report generates output like:

```
customer_name          email                    order_id  order_date           product_name              quantity  price    total_amount_paid
Michael Smith          bgross@example.net       123       2025-11-11T19:28:23  Configurable multi-state  5         83.01    7357.66
Joseph Perry           yjones@example.org       119       2025-11-11T04:34:02  Public-key content-based  4         332.28   0.00
...
```

## Dependencies

- **pandas** >= 2.0.0 - Data manipulation and CSV handling
- **faker** >= 19.0.0 - Synthetic data generation

## Data Characteristics

- **Realistic Data**: Uses Faker library for realistic names, addresses, emails, etc.
- **Referential Integrity**: All foreign keys are validated
- **Varied Scenarios**: Includes discounts, multiple payment methods, different order statuses
- **Calculated Fields**: Order totals include subtotals, shipping, and tax

## Notes

- The data generation uses seeded random values for reproducibility
- Foreign key constraints are enabled in SQLite
- The database is recreated each time `load_to_sqlite.py` is run
- CSV files are preserved unless regenerated

## Author

**Ambitidhanushraj**
- Email: ambitidhanush@gmail.com
- GitHub: [@Ambitidhanushraj](https://github.com/Ambitidhanushraj)

## License

This project is open source and available for use.
