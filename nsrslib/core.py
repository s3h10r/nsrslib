#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
nsr scripting library core functions

some simple funcs for doing nsradmin stuff via python
by wrapping calls to the `nsradmin` / `mminfo` command. 

could be used on a networker server or on any host where the
networker client-software is installed.

USE AT YOUR OWN RISK! NO WARRENTY! FOR NOTHING!

Copyright (C) 2009-2014 Sven Hessenmüller <sven.hessenmueller@gmail.com>
"""

import datetime
import json
import logging
import string # template...
import subprocess
import sys

import settings # nsrslib user-parameters

LOGFILE = "/tmp/bla"
logging.basicConfig(
#    filename=LOGFILE",
#    level = logging.DEBUG,
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(pathname)s %(message)s' )


logger = logging.getLogger(__name__)

__author__="sven.hessenmueller@gmail.com"
__version__="0.0.94-refactoring"
__copyright__ = "Copyright (c) 2009-2014 %s" % __author__
__license__ = "GPLv3+"


### --- some nsr-independent helpers
# using _-prefix for not showing in pydoc

def _exec_cmd(sCmd,env={}): 
    """
    executes a given Command

    returns
        rc, output
    """
    import subprocess as sub

    p = sub.Popen([sCmd], shell=True, stdout=sub.PIPE, stderr=sub.STDOUT, env=env)

    output = p.stdout.readlines()
    p.wait()
    rc = p.returncode

    if rc != 0:
        logger.critical("command failed with rc %i: %s" % (rc,sCmd))
        logger.critical("got %s" % (output))

    return rc, output

### --- END helpers


# === nsradmin based funcs

def do_nsradmin(cmd=None, nsr_server=settings.NSR_SERVER):
    """
    sends raw command-string to nsradmin

    returns
        stdoutput of nsradmin as list
    """

    templ_cmd = string.Template('echo -e \'$cmd\' | $NSRADMIN -s $SERVER -i -')
    ncmd = templ_cmd.substitute({'cmd':cmd, 'NSRADMIN': settings.BIN_NSRADMIN, 'SERVER' : nsr_server}) 

    logger.debug(ncmd)

    # using executable=/bin/bash 'cauz `echo -e` doesn't work on /bin/sh under solaris10
    p = subprocess.Popen(ncmd, shell=True, executable="/bin/bash", stdout =subprocess.PIPE)

    res = p.stdout.readlines()
    rc = p.wait()
    if rc != 0:
        logger.critical("exec of cmd for nasradmin failed! rc %d" % rc)
        raise Exception, "exec of cmd for nsradmin failed! rc %d" % rc
    return res


def get_clients(nsr_server=settings.NSR_SERVER):
    """
    returns

        list of nsr-clients as dict

        [
 
            { 'name'  : <clientname>, 
              'group' : <nsr-group>,
              'ssets' : [<saveset1>, <saveset2>, ... ],
              'retention_policy' : <retention policy>,
              ...
            },

            ...
        ]
    """

    res = do_nsradmin('. type: NSR client\nshow name\nshow group\nshow save set\n \
        show retention policy\nprint\n', nsr_server=nsr_server)

    for l in res:
        logger.debug(l.strip())


    clients = []

    client = None
    hook = None
    parser_warnings = None

    for line in res:
        logger.debug("--- line: %s" % line)
        if line.find('name:') >= 0: # new client record
            hook = 'name:'
            if client: # store previous client
                client['group'] = group
                client['ssets'] = ssets
                client['retention_policy'] = retention_policy
                clients.append(client)
                logger.debug("fetched client: %s" % client['name'])
                if parser_warnings:
                    logger.warning("%s : %s" % (client['name'], parser_warnings))

            client = {} 
            client_name = None
            group = None
            ssets = []
            retention_policy = None
            parser_warnings = None

            client_name = line.split(":")[1].strip().rstrip(';')
            client = {'name' : client_name} # init

        elif line.find('group:') >= 0:
            hook = 'group:'
            group = line.split(":")[1].strip().rstrip(';')
            client['group'] = group

        if ( line.find('save set:') >= 0 ) or hook=='save set:':
            hook = 'save set:'
            if len(line.strip()) > 0:
                ssets.append(line.strip())

        if ( line.find('retention policy:') >= 0 ):
            hook = 'retention policy:'
            retention_policy = line.split(":")[1].strip().rstrip(';')

    # store last client too :)

    client['group'] = group
    client['ssets'] = ssets
    client['retention_policy'] = retention_policy
    clients.append(client)
    logger.debug("fetched client: %s" % client['name'])
    if parser_warnings:
        logger.warning("%s : %s" % (client['name'], parser_warnings))

    # --- END storing clients


    # cleanup_dirty saveset fields etc. 
    clients_clean = []
    for c in clients:
        client_clean = {}
        ssets_old = c['ssets']
        ssets_new = []
        for sset in ssets_old:
            if sset.find('save set:') >= 0:
                sset = sset.replace("save set:","")
            sset_clean = sset.replace('\\\\','\\') # damned windows stuff...
            sset_clean = sset_clean.replace('"','').strip().rstrip(";").split(",")
            sset_clean = [s.strip() for s in sset_clean if s not in '']
            for sset in sset_clean:
                ssets_new.append(sset)

        client_clean['name'] = c['name']
        client_clean['ssets'] = ssets_new
        client_clean['group'] = c['group']
        client_clean['retention_policy'] = c['retention_policy']

        clients_clean.append(client_clean)

    logger.info("total 'client+group'-definitions fetched for nsr-server '%s': %i" % (nsr_server, len(clients_clean))) 
    return clients_clean


# --- TODOs, marked as private so the dunnot appear in pydoc 

def _get_pools(ignore_empty_pools = True, nsr_server=settings.NSR_SERVER):
    """
    **TODO** refactored version
    """
    raise Exception, "TODO..."

def _get_pool_datavol_in_timeslot(pool="POOL1",ts_begin = None, ts_end = None, nsr_server=settings.NSR_SERVER):
    """
    **TODO** refactored version
    """
    raise Exception, "TODO..."

def _get_nsr_config(nsr_server=settings.NSR_SERVER):
    """
    **TODO** get "complete" nsr-config as plaintext
    """
    raise Exception, "TODO..."

# --- END TODOs


# === mminfo based funcs

def do_mminfo_csv(queryspec=None, reportspec=None, nsr_server=settings.NSR_SERVER):
    """
    sends query to mminfo

    returns

        header_csv (list), data_csv (list)
    """

    exportspec="c';'" # use csv-delimiter ';'

    if reportspec:
        templ_cmd = string.Template("$MMINFO -s $SERVER -q '$QUERYSPEC' -r '$REPORTSPEC' -x $EXPORTSPEC")
        ncmd = templ_cmd.substitute({'MMINFO': settings.BIN_MMINFO, 'SERVER' : nsr_server, 'QUERYSPEC' : queryspec, 'REPORTSPEC' : reportspec, 'EXPORTSPEC' : exportspec}) 
    else:
        templ_cmd = string.Template("$MMINFO -s $SERVER -q '$QUERYSPEC' -x $EXPORTSPEC")
        ncmd = templ_cmd.substitute({'MMINFO': settings.BIN_MMINFO, 'SERVER' : nsr_server, 'QUERYSPEC' : queryspec, 'EXPORTSPEC' : exportspec})

    logger.debug(ncmd)
    if not queryspec:
        raise Exception, "no queryspec defined" # TODOP3: maybe an usefull default query makes sense?

    rc, res = _exec_cmd(ncmd)

    csv_header_mminfo = []
    csv_data = []
    for i,l in enumerate(res):
        if i == 0:
            csv_header_mminfo = l.strip().split(';')
            continue
        csv_data.append(l.strip().split(';'))

    #funfact
    # sometimes reportspec-keys differs from the csv_header mminfo returns :-(
    # example:
    #    reportspec='savetime,nsavetime,client,name,level,volume,ssbrowse,ssretent,sumsize,ssid(53)'
    #    csv_head=['date-time', 'savetime', ...]
    # therefore we use the reportspec-keys to build our own csv_header
    # to present a "consistent naming" 
    csv_header = [ el.split('(')[0] for el in reportspec.split(',') ] # 'ssid(53)' => 'ssid', ...
    logger.info("csv_header (mminfo): %s " % csv_header_mminfo)
    logger.info("csv_header: %s " % csv_header)
    if cmp(csv_header_mminfo,csv_header) != 0:
        logger.info("csv_header != csv_header_mminfo. this should be ok...")
    
    return csv_header, csv_data

    
def get_manualsaves(ts_start=None, ts_stop=None,nsr_server=settings.NSR_SERVER):
    """
    returns

        list of manual saves matching the given timewindow as dict

        [
 
            { 'client'    : <client-name>,
              'savetime' :  <nsavetime>, # unix_epoch_time, see `man mminfo`
              'level'     : 'manual',
              'name'      : <saveset>,
              ...
            },

            ...
        ]
    """

    REPORTSPEC='savetime,nsavetime,client,name,level,volume,ssbrowse,ssretent,sumsize,ssid(53),group'

    queryspec='level=manual' 
    if ts_start and ts_stop: # specific timewindow (strongly recommended!) # eg "11/03/2014 00:00:00", "11/04/2014 23:59:59"
        queryspec='level=manual,savetime>=%s,savetime<=%s' % (ts_start,ts_stop) 
    logger.info("get_manualsaves uses queryspec: '%s'" % queryspec)
    
    csv_h, csv_data = do_mminfo_csv(queryspec=queryspec, reportspec=REPORTSPEC, nsr_server=nsr_server)

    res = []

    def new_record():
        record = {}
        for h in csv_h:
            record[h] = None
        return record

    for i,l in enumerate(csv_data):
        record = new_record()
        for pos,h in enumerate(csv_h):
            record[h] = l[pos]
        res.append(record)

    return res

# ===

# --- other output formats etc.

def get_clients_json(nsr_server=settings.NSR_SERVER):
    """
    """
    import json

    res = get_clients(nsr_server=nsr_server)
    return json.dumps(res,indent=4)

def get_manualsaves_json(ts_start=None, ts_stop=None,nsr_server=settings.NSR_SERVER):
    """
    """
    import json
    res = get_manualsaves(ts_start=ts_start, ts_stop=ts_stop, nsr_server=nsr_server)
    return json.dumps(res,indent=4)


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print __doc__
        sys.exit(1)

