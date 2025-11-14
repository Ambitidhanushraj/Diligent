-- E-Commerce Report Query
-- Joins: customers → orders → order_items → products → payments
-- Returns: customer_name, email, order_id, order_date, product_name, quantity, price, total_amount_paid

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

