from unittest.mock import patch, MagicMock
from model.raw_log import RawLog
from consumers.raw_log_to_db_consumer import RawLogToDBConsumer

CONSUMER_MODULE = 'consumers.raw_log_to_db_consumer'

valid_log = RawLog(provider="test", data="test log", timestamp="2023-07-25T10:30:00Z")

@patch(f'{CONSUMER_MODULE}.Consumer')
@patch(f'{CONSUMER_MODULE}.execute_query')
def test_consumer_processes_valid_log(mock_execute_query, mock_kafka_consumer):
    msg = MagicMock()
    msg.value.return_value = valid_log.model_dump_json().encode('utf-8')
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
def test_consumer_skips_invalid_log(mock_execute_query, mock_kafka_consumer):
    invalid_log = b'{"provider": "test", "data": "test log", "timestamp": "invalid-timestamp"}'
    msg = MagicMock()
    msg.value.return_value = invalid_log
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
    msg = MagicMock()
    msg.value.return_value = valid_log.model_dump_json().encode('utf-8')
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