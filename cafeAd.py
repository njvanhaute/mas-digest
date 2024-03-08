from dataclasses import dataclass
from datetime import datetime

@dataclass
class CafeAd:
    name: str
    date_posted: datetime
    link: str