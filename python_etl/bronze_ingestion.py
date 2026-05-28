import pandas as pd
import logging
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from pathlib import Path
from datetime import datetime

# Logging configration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Database Connection

username = "postgres"
password = quote_plus("Pmnbvcxz@1")
host = "localhost"
port = "5432"
database = "ecommerce_db"

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)

# Project root directory

BASE_DIR = Path(__file__).resolve().parent.parent

# Raw Data Directory

raw_data_dir = BASE_DIR / "data" / "raw"

# Get all CSV files

csv_files = list(raw_data_dir.glob("*.csv"))

logging.info(f"Found {len(csv_files)} CSV files")

# Ingest each file

for file in csv_files:
    try:

        start_time = datetime.now()
        # read csv
        df = pd.read_csv(file)

        # Add ingestion timestamp
        df["ingestion_timestamp"] = datetime.now()

        table_name = file.stem.replace("olist_", "").replace("_dataset", "")

        logging.info(f"\nLoading file: {file.name}")
        logging.info(f"Target table: {table_name}")

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
        logging.info(f"Successfully loaded {table_name} | Records: {len(df)} | Duration: {duration:.2f} seconds")
    except Exception as e:

        logging.error(f"Error processing {file.name}: {e}")
        logging.error(str(e))

logging.info("\nBronze ingestion completed.")