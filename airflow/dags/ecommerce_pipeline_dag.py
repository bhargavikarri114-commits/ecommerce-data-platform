from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# importing pipeline functions
from python_etl.bronze_ingestion import run_bronze_ingestion
from python_etl.silver_transformation import run_silver_transformation
from python_etl.gold_layer import run_gold_layer

default_args = {
    "owner": "bhargavi",
    "retries": 2
}
# Dag defination
with DAG(
    dag_id = "ecommerce_pipeline",
    description="End-to-end ecommerce ELT pipeline",
    start_date = datetime(2026, 1, 1),
    schedule_interval = None,
    catchup = False,
    tags = ["data_engineering"],
    default_args=default_args
) as dag:
    
    # Bronze task

    bronze_task = PythonOperator(
        task_id = "bronze_ingestion",
        python_callable = run_bronze_ingestion
    )

    # Silver task

    silver_task = PythonOperator(
        task_id = "silver_transformation",
        python_callable = run_silver_transformation
    )

    # Gold task

    gold_task = PythonOperator(
        task_id = "gold_layer",
        python_callable = run_gold_layer
    )

    bronze_task >> silver_task >> gold_task