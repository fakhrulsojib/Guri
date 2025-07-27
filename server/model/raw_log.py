from pydantic import BaseModel
from datetime import datetime

class RawLog(BaseModel):
    provider: str
    data: str
    timestamp: datetime