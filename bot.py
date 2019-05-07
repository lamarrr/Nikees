import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands
import platform
import re
from typing import Tuple
import enum
import queue
import os.path
import concurrent.futures


import tasker
from apis import config
import auth
from util import kolor as kr


# %
ERR3 = "%s you are not yet authorized to generate accounts\nRequest details:\n\n\tquantity:  %s\n\tcountry:  %s\n\ttype:  %s\n\nplease ensure you typed in the correct quantity and type and do ensure you've requested for authorization (by using ! auth <Your_Order_Number>  i.e. ! auth 1234567) or contact %s to place your order."


imp = kr.StyleRule(bold=True)
note = kr.StyleRule(foreground="blue", bold=True)
err = kr.StyleRule(foreground="red", bold=True)
succ = kr.StyleRule(foreground="green", bold=True)


def main(notification: queue.Queue):

    PATH = __file__.split(os.path.sep)
    # Si#4440

    DOC = open(os.path.sep.join(
        (os.path.sep.join(PATH[:-1]), "docs", "help.txt"))).read()
    ERR_DOC = open(os.path.sep.join(
        (os.path.sep.join(PATH[:-1]), "docs", "error.txt"))).read()

    # Here you can modify the bot's prefix and description and wether it sends help in direct messages or not.
    client = Bot(description="Nike Bot", command_prefix="ACE", pm_help=False)

    MESSAGES = []

    # countries: implementation state
    SUPPORTED_COUNTRIES = {	"GB": {"implemented":	True,	"full":	"United Kingdom"},
                            "US": {"implemented":	True,	"full":	"United States"},
                            "CN": {"implemented":	False,	"full": "China"}
                            }
    IMPLEMENTED_COUNTRIES_STR = ""
    # pepare str
    for _ in range(1):
        m = []
        for _, v in SUPPORTED_COUNTRIES.items():
            if v["implemented"]:
                m.append(v["full"].upper())
        IMPLEMENTED_COUNTRIES_STR += ("\n\t\t".join(m))

    # ! gen cn catchall polkgj.com 5
    cmd_help = re.compile(r"%s\s*help" % config.discord_command_prefix)
    cmd_gen_catchall = re.compile(
        r"%s\s*gen\s+(cn|gb|us|CN|GB|US|[A-Za-z]{2})\s+catchall\s+(\w+\.\w+)\s+([0-9]+)" % config.discord_command_prefix)
    cmd_auth = re.compile(r"%s\s*auth\s+(\w+)" % config.discord_command_prefix)
    cmd_gen_rand = re.compile(
        r"%s\s*gen\s+(cn|gb|us|CN|GB|US|[A-Za-z]{2})\s+random\s+([0-9]+)" % config.discord_command_prefix)
    cmd_err = re.compile(r"%s\s*(auth|gen)" % config.discord_command_prefix)
    cmd_gen_gmail = re.compile(
        r"%s\s*gen\s+(cn|gb|us|CN|GB|US|[A-Za-z]{2})\s+gmail\s+(\w+@gmail.com)\s+([0-9]+)" % config.discord_command_prefix)

    class CMD(enum.Enum):
        info = 0
        auth = 1
        gen_gmail = 2
        gen_catchall = 3
        gen_rand = 4
        err = 5

    cprompts = (cmd_help, cmd_auth, cmd_gen_gmail,
                cmd_gen_catchall, cmd_gen_rand, cmd_err)

    def parse_message(message) -> Tuple[CMD, tuple]:
        index = 0
        # if all doesnt resolve then its an error
        for parser in cprompts:
            match = parser.search(message)
            if match:
                return CMD(index), match.groups()
            index += 1
        return None, None

    @client.event
    async def on_message(message):
        if (not message.id in MESSAGES):
            cmd_type, values = parse_message(message.content)
            if cmd_type:
                # TODO: check user authorization before exec'ing commands

                # await process(message.author.name)
                # spider#9521

                # catchall
                # country,domain,qty

                # random
                # country,qty

                # gmail
                # country,mail,qty

                if (client.user.name+"#"+config.discord_bot_id) != str(message.author):
                    # print(message.author.mention)
                    # print(cmd_type,values)
                    # print(message.author,client.user.id,client.user.name,config.discord_bot_id)
                    # print(message.author.id)
                    # print(message.author.name)

                    if cmd_type == CMD.gen_rand:
                        country, qty = values
                        country = country.upper()
                        #qty = int(qty)
                        if auth.is_auth(str(message.author), country, qty, "random"):

                            if country in SUPPORTED_COUNTRIES:
                                if SUPPORTED_COUNTRIES[country]["implemented"]:
                                    note.print("[Discord Bot] user: %s requested for Nike (randomly generated) accounts, quantity: %s, country: %s" % (
                                        message.author, qty, country))
                                    resp = ":white_check_mark: %s  your request for; type: random, quantity: %s, country: %s, has been recieved and will be delivered to you shortly" % (
                                        message.author.mention, qty, country)
                                    # pop auth
                                    # init and add task
                                    authd_order = auth.pop_auth(
                                        str(message.author), qty, country, "random")
                                    task = tasker.init_task(
                                        message.author.id, message.author.name, authd_order)
                                    tasker.log_task(task)
                                    notification.put(1)
                                    await client.send_message(message.channel, resp)
                                else:
                                    resp = ":warning: %s sorry, country: %s not implemented yet \n implemented countries are: %s" % (
                                        message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                    await client.send_message(message.channel, resp)
                            else:
                                resp = ":warning: %s sorry, country: %s not supported yet \n implemented and supported countries are: %s" % (
                                    message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                await client.send_message(message.channel, resp)
                        else:
                            err.print("[Discord Bot] Failed random account generation attempt by user: %s " % str(
                                message.author))
                            await client.send_message(message.channel, ERR3 % (message.author.mention, qty, country, "random", config.discord_admin))

                    elif cmd_type == CMD.gen_gmail:
                        country, mail, qty = values
                        country = country.upper()
                        #qty = int(qty)
                        if auth.is_auth(str(message.author), country, qty, "gmail"):

                            if country in SUPPORTED_COUNTRIES:
                                if SUPPORTED_COUNTRIES[country]["implemented"]:
                                    note.print("[Discord Bot] user: %s requested for Nike (gmail generated) accounts, quantity: %s, country: %s" % (
                                        message.author, qty, country))
                                    resp = ":white_check_mark: %s  your request for; type: gmail, quantity: %s, country: %s, has been recieved and will be delivered to you shortly" % (
                                        message.author.mention, qty, country)
                                    authd_order = auth.pop_auth(
                                        str(message.author), qty, country, "gmail")
                                    task = tasker.init_task(
                                        message.author.id, message.author.name, authd_order, mail)
                                    tasker.log_task(task)
                                    notification.put(1)

                                    await client.send_message(message.channel, resp)
                                else:
                                    resp = ":warning: %s sorry, country: %s not implemented yet \n implemented countries are: %s" % (
                                        message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                    await client.send_message(message.channel, resp)
                            else:
                                resp = ":warning: %s sorry, country: %s not supported yet \n implemented and supported countries are: %s" % (
                                    message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                await client.send_message(message.channel, resp)
                        else:
                            err.print("[Discord Bot] Failed gmail account generation attempt by user: %s " % str(
                                message.author))
                            await client.send_message(message.channel, ERR3 % (message.author.mention, qty, country, "random", config.discord_admin))

                    elif cmd_type == CMD.gen_catchall:
                        country, domain, qty = values
                        country = country.upper()
                        #qty = int(qty)
                        if auth.is_auth(str(message.author), country, qty, "catchall"):

                            if country in SUPPORTED_COUNTRIES:
                                if SUPPORTED_COUNTRIES[country]["implemented"]:
                                    note.print("[Discord Bot] user: %s requested for Nike (catchall generated) accounts, quantity: %s, country: %s" % (
                                        message.author, qty, country))
                                    resp = ":white_check_mark: %s  your request for; type: catchall, quantity: %s, country: %s, has been recieved and will be delivered to you shortly" % (
                                        message.author.mention, qty, country)
                                    authd_order = auth.pop_auth(
                                        str(message.author), qty, country, "catchall")
                                    task = tasker.init_task(
                                        message.author.id, message.author.name, authd_order, domain)
                                    tasker.log_task(task)
                                    notification.put(1)
                                    await client.send_message(message.channel, resp)
                                else:
                                    resp = ":warning: %s sorry, country: %s not implemented yet \n implemented countries are: %s" % (
                                        message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                    await client.send_message(message.channel, resp)
                            else:
                                resp = ":warning: %s sorry, country: %s not supported yet \n implemented and supported countries are: %s" % (
                                    message.author.mention, country, IMPLEMENTED_COUNTRIES_STR)
                                await client.send_message(message.channel, resp)
                        else:
                            err.print("[Discord Bot] Failed catchall account generation attempt by user: %s " % str(
                                message.author))
                            await client.send_message(message.channel, ERR3 % (message.author.mention, qty, country, "random", config.discord_admin))

                    elif cmd_type == CMD.auth:
                        order_number = values[0]
                        # check db > orders.txt
                        usr = str(message.author)
                        # print(usr)
                        # check if in tasks.json or processing.json
                        u_order = auth.get_order(usr, order_number)
                        # print(u_order)
                        if u_order:
                            uid, order_number_f, country, qty, account_type = u_order
                            auth.pop_order(order_number)
                            auth.log_auth(uid, order_number_f,
                                          country, qty, account_type)
                            succ.print("[Discord Bot] Successfully authorized user: %s, to generate %s %s %s Nike+ accounts" % (
                                uid, qty, country, account_type))
                            await client.send_message(message.channel, ":white_check_mark: Hello {user_mention}, you've been approved to generate {qty} {country} Nike+ accounts\n Feel free to generate your accounts any time or type \"!help\" for more options and commands".format(user_mention=message.author.mention,
                                                                                                                                                                                                                                                                                        qty=qty,
                                                                                                                                                                                                                                                                                        country=country))
                        else:
                            err.print("[Discord Bot] Failed authorization attempt by user: %s " % str(
                                message.author))
                            await client.send_message(message.channel, ":question: Hello {user_mention}, you don't seem to have placed an order for Nike accounts, Please contact {admin} to place your order or ensure you typed the right order number and your order was placed with this account\
																		".format(user_mention=message.author.mention, admin=config.discord_admin))

                    elif cmd_type == CMD.info:
                        await client.send_message(message.channel, DOC.format(sym=config.discord_command_prefix, SI=config.discord_admin, user=message.author.mention))

                    elif cmd_type == CMD.err:
                        await client.send_message(message.channel, ERR_DOC.format(sym=config.discord_command_prefix, user=message.author.mention))
        MESSAGES.append(message.id)

        """
    	def mail_bot():
        print("Mail bot started")
        while True:
            payload, iid, display_name, uid = PROC_NOTIFS.get()
            print("Sending")
            user = discord.User(id=iid, discriminator=uid,
                                username=display_name)
            for u in BOT.get_all_members():
            	if str(u) == uid:
                	await BOT.send_message(user, payload)
                	continue
	"""
    @client.event
    async def on_ready():
        succ.print('[Discord Bot] Logged in as ' +
                   client.user.name+" (ID:"+client.user.id+")")
        print("[Discord Bot] Connected to "+str(len(client.servers)) +
              " server(s), Visible to "+str(len(set(client.get_all_members())))+" user(s)")
        print('[Discord Bot] Invite {} via:'.format(client.user.name)+imp.style(
            '  https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n\n').format(client.user.id))
        await client.change_presence(game=discord.Game(name='Nike Bot'))
        return None

    """
	@client.command()
	async def ping(*args):
		await client.say(":ping_pong: Pong!")
		await asyncio.sleep(3)
		await client.say("say something")
	"""
    return client.start(config.discord_bot_token), client

    # async def process_order(usr):
    # check tasks.json file
    # await client.send_message(discord.User(id="415497055818088448",name="lamarrr"),content="Hello lamarrr, Your request with order number: XXXXXXX is being processed and will be delivered shortly")

    # 1-5 esc4


if __name__ == "__main__":
    pass
    # main(queue.Queue(),queue.Queue())
