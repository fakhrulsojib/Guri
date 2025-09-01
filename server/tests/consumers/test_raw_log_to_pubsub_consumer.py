from unittest.mock import patch, MagicMock
from model.raw_log import RawLog, LogLevel
from consumers.raw_log_to_pubsub_consumer import RawLogToPubSubConsumer
from datetime import datetime, timezone
import json

CONSUMER_MODULE = 'consumers.raw_log_to_pubsub_consumer'

class TestRawLogToPubSubConsumer:
    
    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_publishes_when_subscribers_exist(self, mock_redis_service, mock_kafka_consumer, mock_raw_log_with_source_id):
        mock_redis_instance = MagicMock()
        mock_redis_instance.client.pubsub_numsub.return_value = [(f"logs:source:{mock_raw_log_with_source_id['source_id']}", 2)]
        mock_redis_instance.client.publish.return_value = 2
        mock_redis_service.return_value = mock_redis_instance
        
        msg = MagicMock()
        msg.value.return_value = json.dumps(mock_raw_log_with_source_id).encode('utf-8')
        msg.error.return_value = None

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_instance.client.pubsub_numsub.assert_called_once_with(f"logs:source:{mock_raw_log_with_source_id['source_id']}")
        mock_redis_instance.client.publish.assert_called_once()
        
        publish_call = mock_redis_instance.client.publish.call_args
        assert publish_call[0][0] == f"logs:source:{mock_raw_log_with_source_id['source_id']}"
        assert json.loads(publish_call[0][1]) == mock_raw_log_with_source_id

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_skips_when_no_subscribers(self, mock_redis_service, mock_kafka_consumer, mock_raw_log_with_source_id):
        mock_redis_instance = MagicMock()
        mock_redis_instance.client.pubsub_numsub.return_value = [(f"logs:source:{mock_raw_log_with_source_id['source_id']}", 0)]
        mock_redis_service.return_value = mock_redis_instance
        
        msg = MagicMock()
        msg.value.return_value = json.dumps(mock_raw_log_with_source_id).encode('utf-8')
        msg.error.return_value = None

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_instance.client.pubsub_numsub.assert_called_once_with(f"logs:source:{mock_raw_log_with_source_id['source_id']}")
        mock_redis_instance.client.publish.assert_not_called()

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_skips_log_without_source_id(self, mock_redis_service, mock_kafka_consumer, mock_raw_log_minimal):
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

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_service.return_value.pubsub_numsub.assert_not_called()
        mock_redis_service.return_value.publish.assert_not_called()

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_handles_redis_subscriber_check_error(self, mock_redis_service, mock_kafka_consumer, mock_raw_log_with_source_id):
        mock_redis_instance = MagicMock()
        mock_redis_instance.client.pubsub_numsub.side_effect = Exception("Redis connection error")
        mock_redis_service.return_value = mock_redis_instance
        
        msg = MagicMock()
        msg.value.return_value = json.dumps(mock_raw_log_with_source_id).encode('utf-8')
        msg.error.return_value = None

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_instance.client.pubsub_numsub.assert_called_once()
        mock_redis_instance.client.publish.assert_not_called()

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_handles_redis_publish_error(self, mock_redis_service, mock_kafka_consumer, mock_raw_log_with_source_id):
        mock_redis_instance = MagicMock()
        mock_redis_instance.client.pubsub_numsub.return_value = [(f"logs:source:{mock_raw_log_with_source_id['source_id']}", 1)]
        mock_redis_instance.client.publish.side_effect = Exception("Redis publish error")
        mock_redis_service.return_value = mock_redis_instance
        
        msg = MagicMock()
        msg.value.return_value = json.dumps(mock_raw_log_with_source_id).encode('utf-8')
        msg.error.return_value = None

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_instance.client.pubsub_numsub.assert_called_once()
        mock_redis_instance.client.publish.assert_called_once()

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_handles_invalid_json(self, mock_redis_service, mock_kafka_consumer):
        msg = MagicMock()
        msg.value.return_value = b"invalid json"
        msg.error.return_value = None

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_service.return_value.pubsub_numsub.assert_not_called()
        mock_redis_service.return_value.publish.assert_not_called()

    @patch(f'{CONSUMER_MODULE}.Consumer')
    @patch(f'{CONSUMER_MODULE}.BaseRedisService')
    def test_consumer_handles_kafka_error(self, mock_redis_service, mock_kafka_consumer):
        msg = MagicMock()
        msg.error.return_value = "Kafka error"

        consumer_instance = MagicMock()
        consumer_instance.poll.side_effect = [msg, KeyboardInterrupt()]
        consumer_instance.subscribe.return_value = None
        mock_kafka_consumer.return_value = consumer_instance

        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        try:
            consumer._consume_loop()
        except KeyboardInterrupt:
            pass

        mock_redis_service.return_value.pubsub_numsub.assert_not_called()
        mock_redis_service.return_value.publish.assert_not_called()

    def test_has_active_subscribers_returns_true_when_subscribers_exist(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.pubsub_numsub.return_value = [("logs:source:123", 3)]
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            result = consumer._has_active_subscribers("123")
            
            assert result is True
            mock_redis_instance.client.pubsub_numsub.assert_called_once_with("logs:source:123")

    def test_has_active_subscribers_returns_false_when_no_subscribers(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.pubsub_numsub.return_value = [("logs:source:123", 0)]
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            result = consumer._has_active_subscribers("123")
            
            assert result is False

    def test_has_active_subscribers_returns_false_on_redis_error(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.pubsub_numsub.side_effect = Exception("Redis error")
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            result = consumer._has_active_subscribers("123")
            
            assert result is False

    def test_publish_to_channel_returns_true_on_success(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.publish.return_value = 1
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            log_data = {"source_id": 123, "message": "test"}
            result = consumer._publish_to_channel("123", log_data)
            
            assert result is True
            mock_redis_instance.client.publish.assert_called_once_with("logs:source:123", json.dumps(log_data))

    def test_publish_to_channel_returns_false_on_redis_error(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.publish.side_effect = Exception("Redis error")
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            log_data = {"source_id": 123, "message": "test"}
            result = consumer._publish_to_channel("123", log_data)
            
            assert result is False

    def test_publish_to_channel_returns_false_when_no_receivers(self):
        with patch(f'{CONSUMER_MODULE}.BaseRedisService') as mock_redis_service:
            mock_redis_instance = MagicMock()
            mock_redis_instance.client.publish.return_value = 0
            mock_redis_service.return_value = mock_redis_instance
            
            consumer = RawLogToPubSubConsumer()
            log_data = {"source_id": 123, "message": "test"}
            result = consumer._publish_to_channel("123", log_data)
            
            assert result is False

    def test_consumer_start_stop(self):
        consumer = RawLogToPubSubConsumer()
        
        assert consumer._running is False
        assert consumer._thread is None
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            consumer.start()
            
            assert consumer._running is True
            mock_thread.assert_called_once()
            mock_thread_instance.start.assert_called_once()
            
            consumer.stop()
            
            assert consumer._running is False
            mock_thread_instance.join.assert_called_once()

    def test_consumer_start_when_already_running(self):
        consumer = RawLogToPubSubConsumer()
        consumer._running = True
        
        with patch('threading.Thread') as mock_thread:
            consumer.start()
            
            mock_thread.assert_not_called() 