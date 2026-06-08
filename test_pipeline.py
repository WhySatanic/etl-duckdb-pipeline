import pytest
import pandas as pd
import os
import duckdb
from pipeline import transform_data, load_data

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'transaction_id': [1, 2, 3, 4],
        'transaction_amount': [100.0, -20.0, 0.0, 50.5]
    })

def test_transform_data_filters_negatives(sample_data):
    res = transform_data(sample_data)
    assert (res['transaction_amount'] > 0).all()
    assert len(res) == 2  # Должны остаться только 100.0 и 50.5

def test_transform_empty_dataset():
    df = pd.DataFrame({'transaction_id': [], 'transaction_amount': []})
    res = transform_data(df)
    assert len(res) == 0

def test_load_data_creates_table(tmp_path):
    # Создаем временную БД в изолированной папке для теста
    test_db = os.path.join(tmp_path, "test_analytics.db")
    df = pd.DataFrame({'transaction_id': [99], 'transaction_amount': [999.9]})
    
    load_data(df, test_db)
    
    # Проверяем, что данные физически записались
    con = duckdb.connect(database=test_db)
    res = con.execute("SELECT * FROM processed_transactions").fetchall()
    con.close()
    
    assert len(res) == 1
    assert res[0][0] == 99
    assert res[0][1] == 999.9