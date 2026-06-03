import pandas as pd
from sqlalchemy import text
from python_etl.config.db_config import engine
from python_etl.utils.logger import logger
from python_etl.utils.helpers import RAW_DATA_PATH
from datetime import datetime

def run_bronze_ingestion():

    # Get all CSV files

    csv_files = list(RAW_DATA_PATH.glob("*.csv"))

    logger.info(f"Found {len(csv_files)} CSV files")

    # Ingest each file

    for file in csv_files:
        try:

            start_time = datetime.now()

            table_name = file.stem.replace("olist_", "").replace("_dataset", "")

            logger.info(f"\nLoading file: {file.name}")
            logger.info(f"Target table: {table_name}")

            if table_name == "orders":
                # Convert order_purchase_timestamp to datetime
                watermark_query = """
                select last_loaded_timestamp
                from metadata.pipeline_watermark
                where pipeline_name = 'orders_pipeline'
                """

                last_loaded_timestamp = pd.read_sql(
                    watermark_query,
                    con=engine
                )

                if last_loaded_timestamp.empty:
                    last_loaded_timestamp = pd.to_datetime("1900-01-01")
                    logger.info("No existing watermark found. Starting from the beginning.")
                else:
                    last_loaded_timestamp = last_loaded_timestamp.iloc[0, 0]

                logger.info( f"Last loaded timestamp: {last_loaded_timestamp}" )

                df = pd.read_csv(
                    file,
                    parse_dates=["order_purchase_timestamp"]
                )

                df =df[df["order_purchase_timestamp"] > last_loaded_timestamp] 

                existing_orders_query = """
                select order_id
                from bronze.orders
                """

                try:
                    existing_orders = pd.read_sql(
                        existing_orders_query,
                        con=engine
                    )

                    df = df[
                        df["order_id"].isin(
                            existing_orders["order_id"]
                        )
                    ]

                    logger.info(
                        f"Records after deduplication: {len(df)}"
                    )
                except Exception as e:
                    logger.info("bronze.orders doesn't exist yet. "
                                "Skipping deduplication.")

                # logger.info( f"Incremental records found: {len(df)}" )

                # Add ingestion timestamp
                df["ingestion_timestamp"] = datetime.now()

                # Append incremental records

                df.to_sql(
                    name=table_name,
                    con=engine,
                    schema="bronze",
                    if_exists="append",
                    index=False
                )

                if not df.empty:
                    # Update watermark
                    new_watermark = df["order_purchase_timestamp"].max()

                    update_query = text("""
                    update metadata.pipeline_watermark
                    set last_loaded_timestamp = :new_watermark
                    where pipeline_name = 'orders_pipeline'
                    """)

                    with engine.connect() as conn:
                        conn.execute(update_query, {"new_watermark": new_watermark})
                        conn.commit()

                    logger.info(f"Updated watermark to: {new_watermark}")

            else:

                # Read CSV file
                df = pd.read_csv(file)

                # Add ingestion timestamp
                df["ingestion_timestamp"] = datetime.now()

                # Load to Bronze
                df.to_sql(
                    name=table_name,
                    con=engine,
                    schema="bronze",
                    if_exists="replace",
                    index=False
                )

            

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Successfully loaded {table_name} | Records: {len(df)} | Duration: {duration:.2f} seconds")
        except Exception as e:

            logger.error(f"Error processing {file.name}: {e}")
            logger.error(str(e))

    logger.info("\nBronze ingestion completed.")

if __name__ == "__main__":
    run_bronze_ingestion()