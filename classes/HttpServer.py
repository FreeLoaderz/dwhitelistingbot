#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Tornado HTTP Handler Class
    Version : 1.0
    Date: 20.11.21

    Discord Extension
"""

import logging
import json
import config
from diskord import Webhook
import aiohttp
import socket


from tornado.web import RequestHandler


def sendToSocket(user,message):
    host='127.0.0.1' #client ip
    port = 4005
    server = ('127.0.0.1', 4000)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host,port))
    message = "{}::{}".format(user,message)
    s.sendto(message.encode('utf-8'), server)
    s.close()


class ProfileHandler(RequestHandler):
    def initialize(self, logger):
        self.logger = logger

    def _set_response_success(self):
        self.set_status(200)
        self.add_header('Access-Control-Allow-Origin', '*')
        self.add_header('Content-type', 'application/json')
        self.flush()
        self.finish()


    def _set_response_fail(self):
        self.set_status(500, "Internal Server Error")
        self.add_header('Content-type', 'text/html')
        self.flush()
        self.finish()

    def options(self):
        try:
            self.set_status(204, "ok")
            self.set_header('Access-Control-Allow-Origin', '*')
            self.add_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.add_header('Access-Control-Allow-Headers', '*')
            self.add_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            #self.flush()
            self.finish()
        except:
            self.logger.error("Error in OPTIONS request")
            self._set_response_fail()


    async def post(self):
       
        try:
	    api_key = self.request.headers['x-api-key']
	    self.logger.info(api_key)
	    if (self.request.headers['Content-Type'] == 'application/json'):
		data = json.loads(self.request.body)
		self.logger.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
			str(self.path_args), str(self.request.headers), data)

	    if (api_key == str(config.my_api_key)):
		self.logger.debug("Valid api_key")
		user = data['userid']
		message = data['message']

		sendToSocket(user,message)

		self.set_status(200,'Ok')
		self.set_header('Access-Control-Allow-Origin', '*')
		self.add_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
		self.add_header('Access-Control-Allow-Headers', '*')
		self.add_header('Cache-Control', 'no-store, no-cache, must-revalidate')
		self.add_header('Content-type', 'application/json')
		#self.write(result)
		#self.flush()
		self.finish()
	    else:
	    	self._set_response_fail()
        except:
            self.logger.error("Error in POST request")
            self._set_response_fail()

    def get(self):
         self.set_status(403, "Forbidden")
         self.flush()
         self.finish()
