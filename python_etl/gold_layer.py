import pandas as pd
from sqlalchemy import text
# import logging
# from sqlalchemy import create_engine
# from urllib.parse import quote_plus
from python_etl.config.db_config import engine
from python_etl.utils.logger import logger

def run_gold_layer():

    watermark_query = """
    select last_loaded_timestamp
    from metadata.pipeline_watermark
    where pipeline_name = 'gold_orders_pipeline'
    """

    watermark_df = pd.read_sql(watermark_query, engine)

    if watermark_df.empty:
        last_loaded_timestamp = pd.Timestamp("1900-01-01")
    else:
        last_loaded_timestamp = watermark_df.iloc[0, 0]

    logger.info(f"Last loaded timestamp for gold layer: {last_loaded_timestamp}")

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

    #  Dim_products

    products_query = """
    Select
        product_id,
        product_category_name,
        product_weight_g,
        product_length_cm,
        product_height_cm,
        product_width_cm
    from silver.products
    """
    dim_products = pd.read_sql(products_query, engine)

    dim_products = dim_products.drop_duplicates()

    dim_products.to_sql(
        name="dim_products",
        con=engine,
        schema="gold",
        if_exists="replace",
        index=False
    )

    logger.info("Loaded gold.dim_products")

    # dim_sellers
    sellers_query = """
    select 
        seller_id,
        seller_city,
        seller_state
    from silver.sellers
    """

    dim_sellers = pd.read_sql(sellers_query, engine)

    dim_sellers = dim_sellers.drop_duplicates()

    dim_sellers.to_sql(
        name="dim_sellers",
        con=engine,
        schema="gold",
        if_exists="replace",
        index=False
    )

    logger.info("Loaded gold.dim_sellers")

    # dim_dates

    dates_query = """
    select distinct
        date(order_purchase_timestamp) as order_date
    from silver.orders
    """

    dim_dates = pd.read_sql(dates_query, engine)
    
    dim_dates["year"] = pd.to_datetime(dim_dates["order_date"]).dt.year
    dim_dates["month"] = pd.to_datetime(dim_dates["order_date"]).dt.month
    dim_dates["month_name"] = pd.to_datetime(dim_dates["order_date"]).dt.month_name()
    dim_dates["quarter"] = pd.to_datetime(dim_dates["order_date"]).dt.quarter
    dim_dates["day_of_week"] = pd.to_datetime(dim_dates["order_date"]).dt.day_name()

    dim_dates.to_sql(
        name="dim_dates",
        con=engine,
        schema="gold",
        if_exists="replace",
        index=False
    )

    logger.info("Loaded gold.dim_dates")

    # Fact__orders

    fact_query = f"""
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
    where o.order_purchase_timestamp > '{last_loaded_timestamp}'
    """

    fact_orders = pd.read_sql(fact_query, engine)

    if fact_orders.empty:
        logger.info(
            "No new records found for gold layer."
        )
        return

    # Load fact table
    fact_orders.to_sql(
        name="fact_orders",
        con=engine,
        schema="gold",
        if_exists="append",
        index=False
    )

    logger.info("Loaded gold.fact_orders")

    new_watermark = fact_orders["order_purchase_timestamp"].max()

    update_query = text("""
    update metadata.pipeline_watermark
    set last_loaded_timestamp = :new_watermark
    where pipeline_name = 'gold_orders_pipeline'
    """)

    with engine.connect() as conn:
        conn.execute(update_query, {"new_watermark": new_watermark})
        conn.commit()

if __name__ == "__main__":
    run_gold_layer()