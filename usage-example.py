#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""

import nsrslib as nsrs
import nsrslib.settings as settings

print "nsrslib version: ", nsrs.get_version()

print settings.NSR_SERVER

# query for nsr-server defined in settings.NSR_SERVER

print nsrs.get_clients() 

# query for any other nsr-server

print nsrs.get_clients(nsr_server="other-nsr-server.example.com")

# same data as json... 

clientconf = nsrs.get_clients_json(nsr_server=srv)
print clientconf

# ... and transformed back into a python-datastructure

import json
datastruct = json.loads(clientconf)
for client in datastruct:
    print client

