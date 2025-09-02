from typing import Dict
from fastapi import WebSocket
from datetime import datetime

active_connections: Dict[str, WebSocket] = {}
connection_metadata: Dict[str, Dict] = {}
connection_timeouts: Dict[str, datetime] = {} 