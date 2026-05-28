import pandas as pd
import logging
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Logging configuration

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

# read bronze data

query = "select * from bronze.customers"

customers_df = pd.read_sql(query, engine)

logging.info(f"Read {len(customers_df)} records from bronze.customers")

# Data Cleaning

# Remove duplicates
customers_df = customers_df.drop_duplicates()
logging.info(f"Removed duplicates, {len(customers_df)} records remaining")

# Handle null values
customers_df = customers_df.fillna("unknown")

# Standardize column names
customers_df.columns = [
    col.lower().strip()
    for col in customers_df.columns
]

# Load to silver layer

customers_df.to_sql(
    name="customers",
    con=engine,
    schema="silver",
    if_exists="replace",
    index=False
)

logging.info(f"Successfully loaded {len(customers_df)} records into silver.customers")