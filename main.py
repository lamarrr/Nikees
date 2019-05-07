import asyncio
from apis import config
# assert conditions in config file
import concurrent.futures as fut
from util import kolor as kr
import queue
import tasker
import requests
import selenium
import discord


note = kr.StyleRule(foreground="blue", bold=True)
err = kr.StyleRule(foreground="red", bold=True)



# notification_queue
NOTIFS = queue.Queue()
BOT: discord.Client = None


async def start_bot():
    global BOT
    import bot
    note.print("[Discord Bot] Starting...")
    coru, BOT = bot.main(NOTIFS)
    print(BOT)
    return await coru

"""
async def start_mail_bot():
        global PROC_NOTIFS
        while True:
                payload, iid, display_name, uid = PROC_NOTIFS.get()
                print("Sending")
                user=discord.User(id=iid, discriminator=uid, username=display_name)
                await  BOT.send_message(user, payload)


def start_mail_bot_thr():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_mail_bot())
        loop.close()

"""
"""

async def start_mail_bot():
    global PROC_NOTIFS
    print("Mail bot started")
    while True:
        payload, iid, display_name, uid = PROC_NOTIFS.get()
        print("Sending")
        user = discord.User(id=iid, discriminator=uid, username=display_name)
        for u in BOT.get_all_members():
            if str(u) == uid:
                await BOT.send_message(user, payload)
"""

def start_task_executor():
    note.print("[Task Executor] Starting...")
    note.print("[Task Executor] Waiting for task...")

    itask = tasker.pop_any_task()
    if itask:
        tasker.execute_task(itask[0], itask[1])
    print("executed task", itask)
    while itask != None:
        print("executed task", itask)
        itask = tasker.pop_any_task()
        tasker.execute_task(itask[0], itask[1])

    while True:
        NOTIFS.get()
        note.print("[Task Executor] Gotten Registration task")
        task = tasker.pop_any_task()
        try:
            tasker.execute_task(task[0], task[1])
        except requests.ConnectionError as p:
            raise p
        except Exception as e:
            raise e


"""async def start_bot():
        await _start_bot()

async def start_task_executor():
        print("Start task executor")

"""

thread_pool = fut.ThreadPoolExecutor()
tasker_fut = thread_pool.submit(start_task_executor)
#thread_pool2 = fut.ProcessPoolExecutor()
#mail_bot_fut = thread_pool2.submit(start_mail_bot)

loop = asyncio.get_event_loop()
#loop2 = asyncio.get_event_loop()
loop.run_until_complete(start_bot())
#loop2.run_until_complete(start_mail_bot())
#mail_bot_fut.result()
tasker_fut.result()
loop.close()


"""
# initiate multithreaded processes
# A. listen on discord for requests

# B. check continuously for registration tasks
# > thread first executes all registered but unfinished tasks in logs/tasks.json > log the tasks (probably due to unexpected abortion)
# > then executes tasks if any in global queue > log the tasks
# > 

# C. send finished tasks to users pm
# > by predicating "delivered" field


# D. 
"""
