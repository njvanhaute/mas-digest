from datetime import datetime
from cafeAd import CafeAd
from typing import List
import sqlite3

DB_FILE_PATH = 'mas_digest.sqlite3'

class Database:
    def __init__(self) -> None:
        self._con = sqlite3.connect(DB_FILE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        self._cur = self._con.cursor()
        command = """CREATE TABLE IF NOT EXISTS ads   
                         (ad_id INTEGER PRIMARY KEY,
                          name,
                          date_posted TIMESTAMP
                          )"""
        self._cur.execute(command)
        command = """CREATE TABLE IF NOT EXISTS subscribers
                        (sub_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         email_addr
                         )"""
        self._cur.execute(command)

    def is_empty(self) -> bool:
        command = "SELECT COUNT(*) FROM ads"
        self._cur.execute(command)
        count, = self._cur.fetchone()
        return count == 0
        
    def add_ad(self, ad: CafeAd) -> None:
        command = "INSERT INTO ads(ad_id, name, date_posted) VALUES(?, ?, ?)"
        args = (ad.id, ad.name, ad.date_posted)
        self._cur.execute(command, args)
        self._con.commit()

    def add_ads(self, ads: List[CafeAd]) -> None:
        for ad in ads:
            self.add_ad(ad)

    def most_recent_date_posted(self) -> datetime:
        command = "SELECT date_posted FROM ads ORDER BY ad_id DESC LIMIT 1"
        self._cur.execute(command)
        date_posted, = self._cur.fetchone()
        return date_posted
    
    def add_email(self, email: str):
        command = "INSERT INTO subscribers(email_addr) VALUES(?)"
        args = (email,)
        self._cur.execute(command, args)
        self._con.commit()
    
    def get_sub_emails(self) -> List[str]:
        command = "SELECT email_addr from subscribers"
        self._cur.execute(command)
        return list(self._cur.fetchall())

    def close(self) -> None:
        self._con.close()