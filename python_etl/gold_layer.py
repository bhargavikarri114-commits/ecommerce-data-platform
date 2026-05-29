import pandas as pd
# import logging
# from sqlalchemy import create_engine
# from urllib.parse import quote_plus
from config.db_config import engine
from utils.logger import logger

customers_query = """
Select
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state
from silver.customers
"""

dim_customers = pd.read_sql(customers_query, engine)

# Remove Duplicates
dim_customers = dim_customers.drop_duplicates()

# Load dimension table
dim_customers.to_sql(
    name="dim_customers",
    con=engine,
    schema="gold",
    if_exists="replace",
    index=False
)

logger.info("Loaded gold.customers")

# Fact__orders

fact_query = """
Select
    oi.order_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    op.payment_type,
    o.order_purchase_timestamp
from silver.order_items oi
join silver.orders o
    on oi.order_id = o.order_id
join silver.order_payments op
    on o.order_id = op.order_id
"""

fact_orders = pd.read_sql(fact_query, engine)

# Load fact table
fact_orders.to_sql(
    name="fact_orders",
    con=engine,
    schema="gold",
    if_exists="replace",
    index=False
)

logger.info("Loaded gold.fact_orders")