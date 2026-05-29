def clean_dataframe(df):

    # Remove duplicates
    df = df.drop_duplicates()

    # Standardize column names
    df.columns = [
        col.lower().strip()
        for col in df.columns
    ]

    # Handle nulls
    df = df.fillna("Unknown")

    return df