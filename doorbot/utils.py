import asyncio

async def safe_loop(logger, coro_fn):
    while True:
        try:
            await coro_fn()
        except Exception as e:
            logger.error(f"{coro_fn.__name__} - Exception: {e}")
            await asyncio.sleep(5)
