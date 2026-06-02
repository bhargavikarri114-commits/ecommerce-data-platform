import pandas as pd
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
            # read csv
            df = pd.read_csv(file)

            # Add ingestion timestamp
            df["ingestion_timestamp"] = datetime.now()

            table_name = file.stem.replace("olist_", "").replace("_dataset", "")

            logger.info(f"\nLoading file: {file.name}")
            logger.info(f"Target table: {table_name}")

            # Load to Postgres
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