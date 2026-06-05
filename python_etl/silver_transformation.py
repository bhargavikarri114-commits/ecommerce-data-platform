import pandas as pd
# import logging
# from sqlalchemy import create_engine
# from urllib.parse import quote_plus
from sqlalchemy import text
from python_etl.config.db_config import engine
from python_etl.utils.logger import logger
from python_etl.utils.transformations import clean_dataframe
from python_etl.utils.data_quality import (
    check_nulls, 
    check_duplicates, 
    check_row_count, 
    check_referential_integrity
)

def run_silver_transformation():
    # Tables to Process

    tables = [
        "customers",
        "orders",
        "order_items",
        "products",
        "sellers",
        "order_payments",
        "order_reviews",
        "geolocation",
        "product_category_name_translation"
    ]

    for table in tables:
        try:
            if table == 'orders':
                logger.info(f"Processing table: {table}")

                watermark_query = """
                select last_loaded_timestamp
                from metadata.pipeline_watermark
                where pipeline_name = 'silver_orders_pipeline'
                """

                watermark_df = pd.read_sql(watermark_query, engine)

                if watermark_df.empty:
                    last_loaded_timestamp = pd.Timestamp("1900-01-01")
                else:
                    last_loaded_timestamp = watermark_df.iloc[0, 0]

                logger.info(f"Last loaded timestamp for orders: {last_loaded_timestamp}")

                orders_query = f"""
                select * from bronze.orders
                where order_purchase_timestamp > '{last_loaded_timestamp}'
                """
                orders_df = pd.read_sql(
                    orders_query,
                    engine,
                    parse_dates=["order_purchase_timestamp"]
                )

                logger.info(f"Loaded {len(orders_df)} new records from bronze.orders")

                orders_df = clean_dataframe(orders_df)

                logger.info(f"Rows after cleaning: {len(orders_df)}")

                if orders_df.empty:
                    logger.info("No records remaining after cleaning.")
                    continue
            
                check_row_count(orders_df)
                check_nulls(orders_df, "order_id")
                check_duplicates(orders_df, "order_id")
                customers_df = pd.read_sql(
                    """
                    select customer_id
                    from bronze.customers
                    """,
                    engine
                )

                logger.info(f"Rows after cleaning: {len(orders_df)}")

                check_referential_integrity(
                    child_df=orders_df,
                    parent_df=customers_df,
                    child_key="customer_id",
                    parent_key="customer_id"
                )

                orders_df.to_sql(
                    name="orders",
                    con=engine,
                    schema="silver",
                    if_exists="append",
                    index=False
                )

                logger.info("Loaded silver.orders")

                new_watermark = orders_df["order_purchase_timestamp"].max()

                update_query = text("""
                update metadata.pipeline_watermark
                set last_loaded_timestamp = :new_watermark
                where pipeline_name = 'silver_orders_pipeline'
                """)

                with engine.connect() as conn:
                    conn.execute(update_query, {"new_watermark": new_watermark})
                    conn.commit()

                logger.info(f"Updated watermark for orders to: {new_watermark}")
            else:
                logger.info(f"Processing table: {table}")
                # Read Bronze data
                query = f"SELECT * FROM bronze.{table}"
                df = pd.read_sql(query, engine)
                logger.info(f"Loaded {len(df)} records from bronze.{table}")

                # Cleaning
                # Remove duplicates
                df = clean_dataframe(df)
                logger.info(f"Rows after cleaning: {len(df)}")

                # Load into Silver
                df.to_sql(
                    name=table,
                    con=engine,
                    schema="silver",
                    if_exists="replace",
                    index=False
                )

                logger.info(f"Loaded silver.{table}")
        
        except Exception as e:

            logger.error(f"Error processing table {table}: {e}")
            logger.error(str(e))

if __name__ == "__main__":
    run_silver_transformation()