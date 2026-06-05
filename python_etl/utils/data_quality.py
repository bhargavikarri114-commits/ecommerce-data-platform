from python_etl.utils.logger import logger

def check_nulls(df, column_name):
    null_count = df[column_name].isnull().sum()

    if null_count > 0:
        raise ValueError(f"Column '{column_name}' contains {null_count} null values.")
    
    logger.info(f"Column '{column_name}' has no null values.")

def check_duplicates(df, column_name):

    duplicate_count = df[column_name].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(f"Column '{column_name}' contains {duplicate_count} duplicate values.")
    
    logger.info(f"Column '{column_name}' has no duplicate values.")

def check_row_count(df):

    if len(df) == 0:
        raise ValueError("DataFrame is empty.")
    
    logger.info(f"DataFrame contains {len(df)} rows.")

def check_referential_integrity(
        child_df,
        parent_df,
        child_key,
        parent_key
):
    
    invalid_records = child_df(
        ~child_df[child_key].isin(parent_df[parent_key])
    )

    if not invalid_records.empty:
        raise ValueError(
            f"Found {len(invalid_records)} records "
            f"violating referential integrity."
        )
    logger.info(
        f"Referential integrity passed for "
        f"{child_key} -> {parent_key}"
    )