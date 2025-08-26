from unittest.mock import patch, MagicMock
from model.raw_log import RawLog, LogLevel
from model.log_sources import LogSourceInDB, LogSourceStatus
from consumers.raw_log_to_db_consumer import RawLogToDBConsumer
from datetime import datetime, timezone
import json

CONSUMER_MODULE = 'consumers.raw_log_to_db_consumer'

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_processes_valid_log(mock_execute_query, mock_kafka_consumer, mock_raw_log_with_source_id):
    msg = MagicMock()
    msg.value.return_value = json.dumps(mock_raw_log_with_source_id).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    assert mock_execute_query.call_count == 2
    
    first_call_args = mock_execute_query.call_args_list[0]
    first_sql_query = first_call_args[0][0]
    first_params = first_call_args[0][1]
    
    assert "INSERT INTO raw_logs" in first_sql_query
    assert "source_id" in first_sql_query
    assert "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" in first_sql_query
    
    assert first_params[0] == mock_raw_log_with_source_id["source_id"]
    assert len(first_params) == 8
    
    second_call_args = mock_execute_query.call_args_list[1]
    second_sql_query = second_call_args[0][0]
    second_params = second_call_args[0][1]
    
    assert "UPDATE log_sources" in second_sql_query
    assert "log_count = log_count + 1" in second_sql_query
    assert "last_log_at" in second_sql_query

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_skips_log_without_source_id(mock_execute_query, mock_kafka_consumer, mock_raw_log_minimal):
    log_data_missing_source_id = mock_raw_log_minimal.copy()
    if "source_id" in log_data_missing_source_id:
        del log_data_missing_source_id["source_id"]
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(log_data_missing_source_id).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    mock_execute_query.assert_not_called()

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_skips_invalid_log(mock_execute_query, mock_kafka_consumer):
    invalid_log = {
        "source_id": 1,
        "level": "INVALID_LEVEL",
        "message": "test log"
    }
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(invalid_log).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    mock_execute_query.assert_not_called()

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_skips_kafka_error(mock_execute_query, mock_kafka_consumer):
    msg = MagicMock()
    msg.value.return_value = None
    msg.error.return_value = True

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    mock_execute_query.assert_not_called()

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query', side_effect=Exception("DB error"))
def test_consumer_handles_db_error(mock_execute_query, mock_kafka_consumer):
    log_data_with_source_id = {
        "source_id": 1,
        "level": "INFO",
        "message": "test log message",
        "data": {"key": "value"},
        "timestamp": "2023-07-25T10:30:00Z"
    }
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(log_data_with_source_id).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    mock_execute_query.assert_called_once()

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_processes_minimal_log(mock_execute_query, mock_kafka_consumer):
    minimal_log_data = {
        "source_id": 1,
        "message": "minimal log message"
    }
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(minimal_log_data).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    assert mock_execute_query.call_count == 2

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_processes_log_with_trace_ids(mock_execute_query, mock_kafka_consumer):
    traced_log_data = {
        "source_id": 1,
        "message": "traced log message",
        "trace_id": "trace-abc-123-def-456",
        "span_id": "span-xyz-789"
    }
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(traced_log_data).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    assert mock_execute_query.call_count == 2

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_handles_log_with_api_key_field(mock_execute_query, mock_kafka_consumer, mock_raw_log_with_source_id):
    log_data_with_api_key = mock_raw_log_with_source_id.copy()
    log_data_with_api_key["api_key"] = "dummy_api_key"
    
    msg = MagicMock()
    msg.value.return_value = json.dumps(log_data_with_api_key).encode('utf-8')
    msg.error.return_value = None

    consumer_instance = MagicMock()
    consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
    consumer_instance.subscribe.return_value = None
    mock_kafka_consumer.return_value = consumer_instance

    consumer = RawLogToDBConsumer()
    consumer._running = True
    try:
        consumer._consume_loop()
    except KeyboardInterrupt:
        pass

    assert mock_execute_query.call_count == 2
    
    # Check first call (INSERT into raw_logs)
    first_call_args = mock_execute_query.call_args_list[0]
    first_sql_query = first_call_args[0][0]
    first_params = first_call_args[0][1]
    
    assert "INSERT INTO raw_logs" in first_sql_query
    assert "source_id" in first_sql_query
    assert "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" in first_sql_query
    
    assert first_params[0] == mock_raw_log_with_source_id["source_id"]
    assert len(first_params) == 8
    
    # Check second call (UPDATE log_sources)
    second_call_args = mock_execute_query.call_args_list[1]
    second_sql_query = second_call_args[0][0]
    second_params = second_call_args[0][1]
    
    assert "UPDATE log_sources" in second_sql_query
    assert "log_count = log_count + 1" in second_sql_query
    assert "last_log_at" in second_sql_query