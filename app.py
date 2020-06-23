import uvloop
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pivotbot import tick

uvloop.install()

scheduler = AsyncIOScheduler(timezone='Asia/Jakarta')
scheduler.add_job(tick, 'cron',
                  hour='7',
                  minute='0',
                  second='30')
scheduler.start()
print(f'PivotBot is running, press Ctrl+C to exit')

try:
    asyncio.get_event_loop().run_forever()
except (KeyboardInterrupt, SystemExit):
    pass
