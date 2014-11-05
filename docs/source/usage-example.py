#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
usage-example.py
"""

# quickstart
# ==========

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


# more, misc
# ==========

# get manual saves inside a specific timewindow
# ---------------------------------------------

import datetime as dt
import time

t_fmt="%m/%d/%Y %H:%M:%S"
t_stop = dt.datetime.now()
t_start = t_stop + dt.timedelta(days=-1)
ts_stop = t_stop.strftime(t_fmt)
ts_start = t_start.strftime(t_fmt)

epoch_time = time.time()
epoch_time_as_dt = dt.datetime.fromtimestamp(epoch_time)
print epoch_time, "==", epoch_time_as_dt

res = nsrs.core.get_manualsaves_json(ts_start=ts_start,ts_stop=ts_stop)

import json
res = json.loads(res)

for rec in res:
    print "record keys:", rec.keys()
    print "---", dt.datetime.fromtimestamp(float(rec['savetime'])) #unix-epoch-time to human-readable
    print rec


# "raw"-hacking / development 
# ===========================
#
# - nsrs.core.do_nsradmin
# - nsrs.core.do_mminfo
# ...

queryspec='level=manual,savetime>11/03/2014 00:00:00,savetime<11/04/2014 23:59:59'
reportspec='savetime,nsavetime,client,name,level,volume,ssbrowse,ssretent,sumsize,ssid(53)'
csv_header, csv_data = nsrs.core.do_mminfo_csv(queryspec=queryspec, reportspec=reportspec, nsr_server="nsr.example.com")
print "CSV_HEADER: ", csv_header


