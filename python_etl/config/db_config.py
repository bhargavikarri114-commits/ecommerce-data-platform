from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Database credentials

username = "postgres"
password = quote_plus("Pmnbvcxz@1")

host = "localhost"
port = "5432"
database = "ecommerce_db"

# Create engine

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
)