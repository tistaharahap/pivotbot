from pivotbot import tick
import asyncio

asyncio.get_event_loop().run_until_complete(tick())
