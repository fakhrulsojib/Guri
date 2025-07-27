from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RawLog(BaseModel):
    provider: str
    data: str
    timestamp: datetime