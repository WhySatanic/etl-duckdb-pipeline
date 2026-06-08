import os
from typing import List, Dict, Any
import pandas as pd
import duckdb
import loguru
from config import DUMMY_DATA_PATH, LOGS_PATH, CONNECTION_STRING

log = loguru.logger
log.add(LOGS_PATH, rotation="10 MB")

def extract_data(source: str) -> pd.DataFrame:
    try:
        if source.startswith("http"):
            raise NotImplementedError("API extraction is not implemented yet.")
        else:
            if not os.path.exists(source):
                # Создаем фейковый CSV, если его еще нет, чтобы скрипт не падал при первом запуске
                df_init = pd.DataFrame({
                    'transaction_id': [1, 2, 3, 4],
                    'transaction_amount': [100.50, -50.00, 250.00, 0.00]
                })
                df_init.to_csv(source, index=False)
                log.info(f"Created dummy source file at {source}")
            
            df = pd.read_csv(source)
            log.info(f"Data extracted successfully from {source}. Rows: {len(df)}")
            return df
    except Exception as e:
        log.error(f"Error extracting data from {source}: {str(e)}")
        raise

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Фильтруем только положительные транзакции (как просил QA)
        filtered_df = df[df['transaction_amount'] > 0].copy()
        log.info(f"Data transformation completed. Filtered rows: {len(filtered_df)}")
        return filtered_df
    except Exception as e:
        log.error(f"Error transforming data: {str(e)}")
        raise

def load_data(df: pd.DataFrame, db_path: str):
    try:
        # Подключаемся к DuckDB и загружаем Pandas DataFrame напрямую
        con = duckdb.connect(database=db_path)
        
        # Создаем таблицу или перезаписываем её данными из DataFrame
        con.execute("CREATE OR REPLACE TABLE processed_transactions AS SELECT * FROM df")
        con.close()
        
        log.info(f"Data loaded into DuckDB successfully at {db_path}")
    except Exception as e:
        log.error(f"Error loading data to database: {str(e)}")
        raise

if __name__ == '__main__':
    log.info("Starting ETL Pipeline...")
    raw_data = extract_data(DUMMY_DATA_PATH)
    cleaned_data = transform_data(raw_data)
    load_data(cleaned_data, CONNECTION_STRING)
    log.info("ETL Pipeline completed successfully!")