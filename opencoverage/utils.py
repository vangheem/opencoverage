import asyncio
import contextvars
from functools import partial


async def run_async(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    child = partial(func, *args, **kwargs)
    context = contextvars.copy_context()
    func = context.run
    args = (child,)
    return await loop.run_in_executor(None, func, *args)
