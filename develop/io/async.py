
import asyncio
import time
 
from threading import Thread
 
 
def start_loop(loop):
    asyncio.set_event_loop(loop)
    print("start loop", time.time())
    loop.run_forever()
 
 
async def do_some_work(x):
    print('start {}'.format(x))
    await asyncio.sleep(x)
    print('Done after {}s'.format(x))
 
 
new_loop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(new_loop,))
t.start()
 
asyncio.run_coroutine_threadsafe(do_some_work(6), new_loop)
asyncio.run_coroutine_threadsafe(do_some_work(4), new_loop)