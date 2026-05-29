import pandas as pd
# import logging
# from sqlalchemy import create_engine
# from urllib.parse import quote_plus
from config.db_config import engine
from utils.logger import logger
from utils.transformations import clean_dataframe

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
    "product_category"
]

for table in tables:
    try:

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