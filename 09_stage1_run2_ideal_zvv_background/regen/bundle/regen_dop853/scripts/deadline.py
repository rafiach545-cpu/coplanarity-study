#!/usr/bin/env python3
"""Epoch seconds of the next 14:00 China time (Asia/Shanghai) after now: no new job is launched after it."""
import datetime as dt
from zoneinfo import ZoneInfo
z = ZoneInfo("Asia/Shanghai"); now = dt.datetime.now(z); d = now.replace(hour=14, minute=0, second=0, microsecond=0)
if d <= now: d += dt.timedelta(days=1)
print(int(d.timestamp()), d.isoformat())
