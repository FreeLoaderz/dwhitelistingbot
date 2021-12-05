#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Created on Wed Oct 13 11:31:08 2021

    @author: Torben Poguntke
    @e-mail: torben.poguntke@iu-study.org
    @topic: NFT whitelisting and registration tool on Cardano implementing Blockfrost
    This setup is made for Cryptroll and maintained by the author, copy or reuse of the tool or source code
    is forbidden.

    Configuration file for Whitelisting discord extension

    File-Version: v1.0
    Date: 22.11.21

"""

import logging

# Whitelisting Tool
registration_server_url="http://192.168.178.91:8799/register"
api_key = ""
my_api_key = ""
cardano_address = 'addr_test1vpk9r05lp6v7k8aq5phg0phnsdj52s7yqgn2y24js3kemvcqmfrkp'
channel_id=906925940238594099 
legit_role = 'TestWhitelist'
role_id=916737388670230538
timedelta=15 # minutes
logfile="discord_bot.log"
loglevel=logging.INFO
httpPath="notify"
discord_server_name='Erus Automation'
