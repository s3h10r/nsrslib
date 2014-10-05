#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""

import nsrslib as nsrs
import nsrslib.settings as settings

print settings.NSR_SERVER

print nsrs.get_version()

# query for nsr-server defined in settings.NSR_SERVER

print nsrs.get_clients() 

# query for any other nsr-server

print nsrs.get_clients(nsr_server="other-nsr-server.example.com")

