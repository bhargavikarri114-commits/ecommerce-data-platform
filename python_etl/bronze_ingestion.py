import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# PostgreSQL connection details
username = "postgres"
password = quote_plus("Pmnbvcxz@1")
host = "localhost"
port = "5432"
database = "ecommerce_db"

# Create database connection
engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)

# Read CSV file
# customers_df = pd.read_csv(
#     "../data/raw/olist_customers_dataset.csv"
# )
customers_df = pd.read_csv(
    r"C:\Users\HP\Data_Engineering_projects\ecommerce-data-platform\data\raw\olist_customers_dataset.csv"
)

# Load into PostgreSQL bronze schema
customers_df.to_sql(
    name="customers",
    con=engine,
    schema="bronze",
    if_exists="replace",
    index=False
)

print("Customers data loaded successfully!")