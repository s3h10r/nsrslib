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

import sys, subprocess
import string # template...
import datetime
import logging

import settings 

LOGFILE = "/tmp/bla"
logging.basicConfig(
#    filename=LOGFILE",
#    level = logging.DEBUG,
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(pathname)s %(message)s' )


logger = logging.getLogger(__name__)

__author__="sven.hessenmueller@gmail.com"
__version__="0.0.84"
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
        dict['client'] = {'group':list_of_save_sets'}
    """

    res = do_nsradmin('. type: NSR client\nshow name\nshow group\nshow save set\nprint\n', nsr_server=nsr_server)

    for l in res:
        logger.debug(l.strip())


    dictClients = {}

    lastClnt = None; curClnt = None
    lastGrp = None; curGrp = None

    for line in res:
        if line.find('name:') >= 0:
            lstClnt = curClnt
            curClnt = line.split(":")[1].strip().rstrip(';')
            if not dictClients.has_key(curClnt): # init
                dictClients[curClnt] = {}
        elif line.find('group:') >= 0:
            curGrp = line.split(":")[1].strip().rstrip(';')
            if not dictClients[curClnt].has_key(curGrp): # init
                dictClients[curClnt][curGrp] = []
        else: # save set
            if (curClnt != None) & (curGrp != None):
                if len(line.strip()) > 0:
                    dictClients[curClnt][curGrp].append(line.strip())

    # cleanup_saveset field # FIXME
    for client in dictClients.keys():
        for group in dictClients[client].keys():
            ssets_old = dictClients[client][group]
            sset_new = []
            for el in ssets_old:
                if el.find('save set:') >= 0:
                    el = el.replace("save set:","")
                el = el.replace('\\\\','\\') # damned windows stuff... 
                tmp_bla = el.replace('"','').strip().rstrip(";").split(",")
                [sset_new.append(i.strip()) for i in tmp_bla if i not in ''] # add all not empty elements
            dictClients[client][group] = sset_new 

   
    logger.debug(dictClients)
 
    return dictClients


def get_pools(ignore_empty_pools = True, nsr_server=settings.NSR_SERVER):
    """
    infos about defined networker pools (how much tapes are inside? how much are free? etc.)

    returns dctPools[<poolname>][cntVol|firstVol|lastVol|cntVolFree|cntVolExpired] 
    """
    dctPools = {}

    res = do_nsradmin('. type:NSR pool\nshow name\nprint\n', nsr_server=nsr_server)

    for line in res:
        if line.find('name:') >= 0:
            curPool = line.split(":")[1].strip().rstrip(';')
            if not dctPools.has_key(curPool): # init
                dctPools[curPool] = {}

    dctCmds = {
        'templ_cntVol' : string.Template('$MMINFO -s $SERVER -v -q pool="$POOL" -r volume 2>/dev/null | wc -l | tr -d " "'),
        'templ_firstVol' : string.Template('$MMINFO -s $SERVER -v -q pool="$POOL" -r volume 2>/dev/null | head -1'),
        'templ_lastVol' : string.Template('$MMINFO -s $SERVER -v -q pool="$POOL" -r volume 2>/dev/null | tail -1'),
   
        'templ_cntVolFree' : string.Template('$MMINFO -s $SERVER -v -m -q pool="$POOL" 2>/dev/null | grep -i "undef" | wc -l | tr -d " "'),
        'templ_cntVolExpired' : string.Template('$MMINFO -s $SERVER -v -q pool="$POOL",volrecycle,!manual -r volume 2>/dev/null | wc -l | tr -d " "')
    }

    for pool in dctPools:
        for templ in dctCmds:
            cmd = dctCmds[templ].substitute({'MMINFO': BIN_MMINFO, 'SERVER': NSR_SERVER, 'POOL':pool})

            # using executable=/bin/bash 
            p = subprocess.Popen(cmd, shell=True, executable="/bin/bash", stdout = subprocess.PIPE)

            res = p.stdout.readlines()

            if len(res) > 0:
                res = res[0].strip()

            rc = p.wait()

            if rc != 0:
                raise Exception, "exec of cmd failed! rc %d" % rc
            dctPools[pool][templ.replace("templ_","")] = res

    if bolIgnoreEmptyPools: # wanna kick out all pools without any volume (e.g. predefined unused pools)?
        lstKickme = []
        for pool in dctPools:
            if int(dctPools[pool]['cntVol']) <= 0:
                lstKickme.append(pool)

        for pool in lstKickme:
            del dctPools[pool]

    for pool in dctPools:
        dctPools[pool]['cntVolFree'] = int(dctPools[pool]['cntVolFree'])
        dctPools[pool]['cntVolExpired'] = int(dctPools[pool]['cntVolExpired'])

    logger.debug("FIXME: dctPools = %s" % dctPools)
 
    return dctPools


def get_pool_datavol_in_timeslot(pool="POOL1",ts_begin = None, ts_end = None, nsr_server=settings.NSR_SERVER):
    """
    infos about the amount of data written to a pool in a given timeslot
    ("backup-window")
    
    returns
        list,int
 
            list of volumes written to, total amount of data written in bytes 
    """

    """
    mminfo -s localhost -q 'pool=L2WORZBZ, savetime >= 05/15/2013 16:00, savetime <= 05/16/2013 16:00' -r "volume, sumsize(20)" [-xm|-x;] # totalsize, name, bla -> man mminfo

    bytes_written

    TODO: 
    size of each volume

    CSV -> XML
    """

    now = datetime.datetime.now()

    if not ts_begin:
        ts_begin = now + datetime.timedelta(days=-7) # same day last week
        ts_begin = ts_begin.replace(hour=16,minute=0,second=0, microsecond=0) # backup-start window

    if not ts_end:
        ts_end = ts_begin + datetime.timedelta(days=1) # 24h interval

    tfmt = "%m/%d/%Y %H:%M"

    query = string.Template("$MMINFO -s $SERVER -q 'pool=$POOL,savetime >= $TS_BEGIN, savetime <= $TS_END' -r 'volume,sumsize(40)' -xc,")  
    cmd = query.substitute({'MMINFO' : settings.BIN_MMINFO, 'SERVER' : nsr_server, 'POOL':pool, 'TS_BEGIN' : ts_begin.strftime(tfmt), 'TS_END' : ts_end.strftime(tfmt)})

    logger.info("exec cmd: %s" % cmd)
    rc,output = _execCmd(cmd)
    logger.debug("rc: %s" % rc)
    logger.debug("output: %s" % output)

    if rc != 0:
        #raise Exception, 'got rc %i for cmd: %s' % (rc,cmd)
        return None, None # no matches found for the query? # TODO: hardenig
 
    vols = [] # list of volumes
    sumsizeB = 0 # Bytes

    for i,l in enumerate(output):
        if i == 0: #header
            if l.strip() != "volume,sum-size":
                raise Exception, "nargh. csv-format header seems to be wrong. TODO: using xml :)"
            continue # skip header line

        vol,l_sumsize = [ el.strip() for el in l.split(',') ]
        if not vol in vols:
            vols.append(vol)
        else:
            logger.debug("ignoring volume %s" % vol)

        sumsizeB += int(l_sumsize)


    return vols,sumsizeB

# ---

def get_clients_json(nsr_server=settings.NSR_SERVER):
    """
    """
    res = get_clients()
    # ...
    raise Exception, "TODO"


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print __doc__
        sys.exit(1)

    if sys.argv[1] == "selfcheck":
        logger.critical("TODO...")

