#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
nsr script library core functions

some simple funcs for doing nsradmin stuff via python
by wrapping calls to the nsradmin / mminfo command. 

could be used on a networker server or on any host where the
networker client-software is installed.

to check if basic commands are working on your machine try:

    ./core.py selfcheck

USE AT YOUR OWN RISK! NO WARRENTY! FOR NOTHING!

Copyright (C) 2009-11 Sven Hessenmüller <sven.hessenmueller@gmail.com>
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
__version__="0.0.84-refactoring"
__date__= "20110204"
__copyright__ = "Copyright (c) 2009-11 %s" % __author__
__license__ = "GPL"


### --- some nsr-independent helpers
# using _-prefix for not showing in pydoc

def _execCmd(sCmd,env={}): 
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


# === TODOs, marked as private so the dunnot appear in pydoc 

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

# === END TODOs


# --- other output formats etc.

def get_clients_json(nsr_server=settings.NSR_SERVER):
    """
    """
    import json

    res = get_clients(nsr_server=nsr_server)
    return json.dumps(res,indent=4)


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print __doc__
        sys.exit(1)

    if sys.argv[1] == "selfcheck":
        logger.critical("TODO...")

