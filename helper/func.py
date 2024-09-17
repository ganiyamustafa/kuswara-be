from typing import Union, Callable, Any
from datetime import datetime

async def time_check(f: Callable[..., Any], *args: Any, **kwargs: Any):
  # initialize starting second time
  start = datetime.now()

  # exec function
  result = await f(*args, **kwargs)

  # initialize end second time
  end = datetime.now()

  # log time in second
  print((end - start).total_seconds())

  return result