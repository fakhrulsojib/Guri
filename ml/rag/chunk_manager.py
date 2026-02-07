import re
from dataclasses import dataclass, field
from typing import List, Dict
import hashlib
from datetime import datetime

@dataclass
class LogChunk:
    source_id: str
    template: str
    log_level: str
    start_time: float
    end_time: float
    count: int = 1
    sample_vars: List[str] = field(default_factory=list)
    raw_ids: List[int] = field(default_factory=list)

    @property
    def id(self) -> str:
        # Deterministic ID based on source, template, and hour window
        hour = datetime.fromtimestamp(self.start_time).strftime('%Y%m%d%H')
        content_hash = hashlib.md5(f"{self.source_id}:{self.template}:{self.log_level}".encode()).hexdigest()
        return f"source_{self.source_id}_{hour}_{content_hash}"

    @property
    def check_content(self) -> str:
        """Text representation for embedding"""
        duration_mins = (self.end_time - self.start_time) / 60
        return (
            f"Source: {self.source_id}\n"
            f"Level: {self.log_level}\n"
            f"Event Pattern: {self.template}\n"
            f"Occurrence Count: {self.count}\n"
            f"Time Window: {datetime.fromtimestamp(self.start_time).isoformat()} to {datetime.fromtimestamp(self.end_time).isoformat()}\n"
            f"Duration: {duration_mins:.1f} mins\n"
            f"Example Variables: {', '.join(self.sample_vars[:5])}"
        )

class ChunkManager:
    def __init__(self):
        # Regex to match common variable parts (IPs, UUIDs, Dates, Numbers)
        self.var_patterns = [
            (r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?', '<TIMESTAMP>'),
            (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '<IP>'),
            (r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b', '<UUID>'),
            (r'\b\d+\b', '<NUM>'),
            (r'0x[0-9a-fA-F]+', '<HEX>')
        ]

    def _get_template(self, message: str) -> str:
        template = message
        for pattern, replacement in self.var_patterns:
            template = re.sub(pattern, replacement, template)
        return template

    def cluster_logs(self, logs: List[Dict]) -> List[LogChunk]:
        """
        Group logs by (source_id, log_level, template)
        Assumes logs are within the same hour/batch window for simplicity,
        or caller handles windowing.
        """
        clusters: Dict[str, LogChunk] = {}

        for log in logs:
            source_id = str(log.get('source_id', 'unknown'))
            raw_msg = log.get('body', '') or log.get('message', '')
            level = log.get('severity', 'INFO')
            timestamp = 0.0
            
            # Handle various timestamp formats from DB/Kafka
            ts_val = log.get('timestamp')
            if isinstance(ts_val, datetime):
                timestamp = ts_val.timestamp()
            elif isinstance(ts_val, (int, float)):
                timestamp = float(ts_val)
            # else: parse string if needed, skipping for now
            
            template = self._get_template(raw_msg)
            key = f"{source_id}:{level}:{template}"

            if key not in clusters:
                clusters[key] = LogChunk(
                    source_id=source_id,
                    template=template,
                    log_level=level,
                    start_time=timestamp,
                    end_time=timestamp,
                    count=0,
                    sample_vars=[],
                    raw_ids=[]
                )
            
            chunk = clusters[key]
            chunk.count += 1
            chunk.end_time = max(chunk.end_time, timestamp)
            chunk.start_time = min(chunk.start_time, timestamp) if chunk.start_time > 0 else timestamp
            if log.get('id'):
                chunk.raw_ids.append(log['id'])
            
            # Extract variables (naive diff)
            # In a real system, we'd extract specific matched groups.
            # Here we just keep a few raw examples if they are short enough
            if len(chunk.sample_vars) < 5 and len(raw_msg) < 200:
                if raw_msg not in chunk.sample_vars:
                    chunk.sample_vars.append(raw_msg)

        return list(clusters.values())
