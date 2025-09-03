import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from services.websocket.manager import WebSocketManager


@pytest.fixture
def ws_manager():
    return WebSocketManager()


@pytest.fixture
def mock_redis_client():
    mock_client = AsyncMock()
    mock_client.ping = AsyncMock(return_value=True)
    return mock_client


def create_mock_pubsub():
    mock_pubsub = AsyncMock()
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.listen = AsyncMock()
    return mock_pubsub


class TestManager:
    
    @pytest.mark.asyncio
    async def test_subscribe_to_logs_creates_separate_pubsub_instances(self, ws_manager, mock_redis_client):
        ws_manager.redis_client = mock_redis_client
        
        mock_pubsub1 = create_mock_pubsub()
        mock_pubsub2 = create_mock_pubsub()
        
        mock_redis_client.pubsub = MagicMock(side_effect=[mock_pubsub1, mock_pubsub2])
        
        await ws_manager.subscribe_to_logs(1, "conn1")
        await ws_manager.subscribe_to_logs(2, "conn2")
        
        assert "conn1" in ws_manager.connection_pubsubs
        assert "conn2" in ws_manager.connection_pubsubs
        assert ws_manager.connection_pubsubs["conn1"] != ws_manager.connection_pubsubs["conn2"]
        
        mock_pubsub1.subscribe.assert_called_once_with("logs:source:1")
        mock_pubsub2.subscribe.assert_called_once_with("logs:source:2")
    
    @pytest.mark.asyncio
    async def test_listen_to_logs_uses_correct_pubsub_instance(self, ws_manager):
        mock_pubsub1 = create_mock_pubsub()
        mock_pubsub2 = create_mock_pubsub()
        
        ws_manager.connection_pubsubs = {
            "conn1": mock_pubsub1,
            "conn2": mock_pubsub2
        }
        
        mock_message = {
            "type": "message",
            "data": json.dumps({"source_id": 1, "message": "test log"})
        }
        mock_pubsub1.listen.return_value = [mock_message]
        
        ws_manager.broadcast_to_connection = AsyncMock()
        
        await ws_manager.listen_to_logs(1, "conn1")
        
        mock_pubsub1.listen.assert_called()
        mock_pubsub2.listen.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_remove_connection_cleans_up_pubsub_instance(self, ws_manager):
        mock_pubsub = create_mock_pubsub()
        
        ws_manager.connection_pubsubs = {
            "conn1": mock_pubsub
        }
        
        ws_manager.active_connections = {"conn1": MagicMock()}
        ws_manager.connection_metadata = {"conn1": {"source_id": 1}}
        ws_manager.connection_timeouts = {"conn1": MagicMock()}
        
        ws_manager.redis_client = AsyncMock()
        
        await ws_manager.remove_connection("conn1")
        
        mock_pubsub.close.assert_called_once()
        assert "conn1" not in ws_manager.connection_pubsubs
    
    @pytest.mark.asyncio
    async def test_disconnect_redis_cleans_up_all_pubsub_instances(self, ws_manager):
        mock_pubsub1 = create_mock_pubsub()
        mock_pubsub2 = create_mock_pubsub()
        
        ws_manager.connection_pubsubs = {
            "conn1": mock_pubsub1,
            "conn2": mock_pubsub2
        }
        
        ws_manager.redis_client = AsyncMock()
        
        await ws_manager.disconnect_redis()
        
        mock_pubsub1.close.assert_called_once()
        mock_pubsub2.close.assert_called_once()
        assert len(ws_manager.connection_pubsubs) == 0 