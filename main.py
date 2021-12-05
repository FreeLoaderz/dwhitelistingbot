#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 18:50:12 2021

@author: Torben Poguntke
@e-mail: torben.poguntke@iu-study.org
@topic: NFT discrod whitelisting discord extension

This is the main file for executing the program
"""


import threading
import config
import logging
from logging.handlers import RotatingFileHandler
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer
from classes.HttpServer import ProfileHandler
import os
import socket
import asyncio

from diskord.ext import tasks

import diskord
import requests
import json
import queue

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(config.logfile, mode='a', maxBytes=5*1024*1024, backupCount=2,delay=0,encoding=None)
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logging.basicConfig(filename=config.logfile,
                    format='%(asctime)s %(message)s',
                    datefmt="%y-%m-%d %H:%M:%S",
                    level=config.loglevel)
logger = logging.getLogger(__name__)
logger.setLevel(config.loglevel) # The logger still needs its verbose level
logger.addHandler(handler)

queue = queue.Queue()

class DiscordClient(diskord.Client):

    def __init__(self, *args, **kwargs):
        super(DiscordClient, self).__init__(*args, **kwargs)
        self.guild = diskord.utils.get(self.guilds, name='Erus Automation')

    @tasks.loop(seconds=5)
    async def send_dm_message(self):
        if not queue.empty():
            current_input = queue.get()
            print('Input: {}'.format(current_input))
            #print('User: {}'.format(u))
            user = self.guild.get_member_named(str(current_input['user']))
            #print('DUser: {}'.format(user))
            if user != None:
                dm = await user.create_dm()
                await dm.send(content=current_input['data'])

    async def on_ready(self):
        #print(f'Logged on as {self.user}!')
        self.guild = diskord.utils.get(self.guilds, name=config.discord_server_name)
        print("Server: {}".format(self.guild))
        self.send_dm_message.start()

    async def on_message(self, message):


        if message.author == client.user:
            return

        if (message.content.startswith('!!whitelist-me') and not(message.author.bot) and
            (message.channel.id == config.channel_id or type(message.channel) == diskord.DMChannel)) :

            user = message.author
            user = await self.guild.query_members(user_ids=[user.id]) # list of members with userid
            user = user[0]
            role = user.get_role(config.role_id)
            #print("{}".format(role))
            #print("{}".format(role))
            #member = message.guild.get_member(user.id)
            #print(member)
            dm = await user.create_dm()

            if (role.name == config.legit_role):
                await dm.send('Hello {}!\n I see you want to register. Your role is {}, so you are allowed to whitelist; congratulations!'.format(user.name,role))
                await dm.send('We go on directly. It works like this:\n1. Prepare yourself to send a small amount of Ada to register your wallet.')
                await dm.send('2. When you feel ready, I will inform you about the amount of ADA you have to send to the corresponding Cardano address.')
                await dm.send('3.You have 15 Minutes time until that amount has to reach my wallet. Otherwise, you have to start again and your registration fails after that 15 minutes.')
                await dm.send('IMPORTANT INFO:')
                await dm.send('Only send **THE EXACT** amount of Ada, otherwise you will not be registered, and your Ada will be lost!')
                await dm.send('DO NOT send any Ada when the 15 minutes have expired. Your Ada will get lost in this case.')
                await dm.send('I will inform you when your transaction reached me and your registration was successful or when the registration time expired.')
                await dm.send('You get most of your Ada sent back directly. You only pay some transaction fees. It is cheap! (~0.4 Ada)')
                await dm.send('You can register one wallet only. If you register again, you overwrite the previously registered wallet.')
                await dm.send('If the registration time expires, no worries just start again using `!!whitelist-me`.')
                await dm.send('--------------------------------------------------------')
                await dm.send('If you are ready send `!&!register_now` in this channel.')
            else:
                await message.channel.send('Hello {}!\nI see you want to register. I am very sorry but you are not allowed to get whitelisted :disappointed_relieved: '.format(user.name))

        if (message.content.startswith('!&!register_now')
                and not(message.author.bot)
                and type(message.channel) == diskord.channel.DMChannel
                and message.author != client.user):
            user = message.author
            user = await self.guild.query_members(user_ids=[user.id]) # list of members with userid
            user = user[0]
            role = user.get_role(config.role_id)
            history = []

            async for m in message.channel.history(limit = 12):
                logger.debug("{}".format(m.content))
                history.append(m.content)


            userdata = json.dumps({"username":str(message.author)})
            logger.debug("{}".format(history))
            if(role.name == config.legit_role
               #and not ('**You have 15 minutes from now!**' in history)
               and message.author != client.user
               ):
                logger.debug("--------------------------------------------------------------------")
                logger.debug('')
                logger.debug('Postdata: {}'.format(userdata))

                headers = {
                  'Content-Type': 'application/json',
                  'x-api-key': config.api_key
                }

                respond = requests.post(config.registration_server_url
                                , data = userdata
                                , headers=headers)
                logger.debug("\nRespond: {}\n".format(respond))
                logger.debug('')
                logger.debug("--------------------------------------------------------------------")
                logger.info("Status Code: {}".format(respond.status_code))
                if (respond.status_code == 200):
                    body = respond.json()
                    dust = body['dust']
                    cardano_address=config.cardano_address
                    #print ("{},{}".format(message.created_at, type(message.created_at)))

                    await message.channel.send('Please send **exactly** `{:,}` Ada to `{}` '.format(float(dust/1000000),cardano_address))
                    await message.channel.send('**You have 15 minutes from now!**')
                elif(respond.status_code == 292):
                    await message.channel.send('You have a running registration process, wait until it expires before you start a new one!')
                else:
                    await message.channel.send('Ups!! something went wrong, Sorry! Try again later and please inform the admins. Thank you!')

            else:
                await message.channel.send('Please send a `!!whitelist-me` first and assure to not send me other messages as what I ask you for during registration.')

intents = diskord.Intents.default()
intents.members = True
client = DiscordClient(intents=intents)

token = os.environ['DISCORD_TOKEN']

def runTornado (loop):
    asyncio.set_event_loop(loop)
    io_loop = tornado.ioloop.IOLoop.instance()
    application = tornado.web.Application([
            (r"/{}".format(config.httpPath), ProfileHandler, dict(logger=logger))
        ])

    server = HTTPServer(application)
    server.listen(8787)
    io_loop.start()


def runDiscord(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.run(token))


def localSocket():
        host = '127.0.0.1' #Server ip
        port = 4000
        asyncio.set_event_loop(loop)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host, port))

        print("Server Started")
        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            if (str(addr) == "('127.0.0.1', 4005)"):
                d = data.split('::')
                payload = {'user': d[0],'data':d[1]}
                queue.put(payload)
        s.close()



#Token to environment varialbes not to script.
if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    loop2 = asyncio.new_event_loop()

    threading.Thread(target=localSocket,daemon=True).start()
    threading.Thread(target=runTornado, args=(loop2,), daemon=True).start()
    runDiscord(loop)


