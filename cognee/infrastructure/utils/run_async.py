import asyncio
from functools import partial
import inspect


async def run_async(func, *args, loop=None, executor=None, **kwargs):
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()

    func_code = getattr(func, "__code__", None)
    if func_code is not None and func_code.co_varnames:
        if "loop" in func_code.co_varnames[: func_code.co_argcount]:
            pfunc = partial(func, *args, loop=loop, **kwargs)
        else:
            pfunc = partial(func, *args, **kwargs)
    else:
        if "loop" in inspect.signature(func).parameters:
            pfunc = partial(func, *args, loop=loop, **kwargs)
        else:
            pfunc = partial(func, *args, **kwargs)

    return await loop.run_in_executor(executor, pfunc)
