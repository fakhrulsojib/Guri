from unittest.mock import patch, MagicMock
import pytest
from database import db

@patch('database.db.psycopg2.connect')
def test_execute_query_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db.execute_query("SELECT 1;")
    mock_cursor.execute.assert_called_once_with("SELECT 1;")
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch('database.db.psycopg2.connect')
def test_execute_query_with_params_success(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    db.execute_query("INSERT INTO test (a, b) VALUES (%s, %s);", (1, 2))
    mock_cursor.execute.assert_called_once_with("INSERT INTO test (a, b) VALUES (%s, %s);", (1, 2))
    mock_conn.commit.assert_called_once()

@patch('database.db.psycopg2.connect')
def test_execute_query_param_count_mismatch(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    with pytest.raises(ValueError):
        db.execute_query("INSERT INTO test (a, b) VALUES (%s, %s);", (1,))

@patch('database.db.psycopg2.connect')
def test_execute_query_db_error(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("DB error")

    with pytest.raises(Exception):
        db.execute_query("SELECT 1;")
    mock_conn.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once() 