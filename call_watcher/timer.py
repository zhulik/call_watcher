import asyncio
import traceback


async def timer(func, sleep_time):
    while True:
        try:
            await func()
        except Exception as err:
            traceback.print_tb(err.__traceback__)
        finally:
            await asyncio.sleep(sleep_time)