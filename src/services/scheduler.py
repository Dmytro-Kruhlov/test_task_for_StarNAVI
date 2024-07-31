# import schedule
#
# import asyncio
#
#
# def run_continuously(interval=1):
#
#     cease_continuous_run = asyncio.Event()
#
#     async def continuous_run():
#         while not cease_continuous_run.is_set():
#             schedule.run_pending()
#             await asyncio.sleep(interval)
#
#     loop = asyncio.get_event_loop()
#     loop.create_task(continuous_run())
#     return cease_continuous_run
#
#
# def schedule_task(delay: int, task, *args):
#     print(f"Scheduling task to run after {delay} seconds")
#     schedule.every(delay).seconds.do(task, *args)
#     print(f"Task scheduled: {task.__name__} with args: {args}")
#
#
# run_continuously()