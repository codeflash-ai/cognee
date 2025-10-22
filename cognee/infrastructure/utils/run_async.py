import asyncio
from functools import partial
import inspect

# Cache signatures to avoid repeated expensive inspect.signature calls
_signature_cache: dict[int, inspect.Signature] = {}


async def run_async(func, *args, loop=None, executor=None, **kwargs):
    if loop is None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()

    # Use fast signature-parameter check
    if _has_loop_param(func):
        pfunc = partial(func, *args, loop=loop, **kwargs)
    else:
        pfunc = partial(func, *args, **kwargs)

    return await loop.run_in_executor(executor, pfunc)


def _has_loop_param(func) -> bool:
    func_id = id(func)
    sig = _signature_cache.get(func_id)
    if sig is None:
        sig = inspect.signature(func)
        _signature_cache[func_id] = sig
    return "loop" in sig.parameters
