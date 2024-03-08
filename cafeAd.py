from dataclasses import dataclass
from datetime import datetime

@dataclass
class CafeAd:
    id: int
    name: str
    date_posted: datetime