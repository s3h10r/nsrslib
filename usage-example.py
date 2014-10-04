#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
TODO
"""

import nsrslib as nsrs
import nsrslib.settings as settings

print settings.NSR_SERVER

nsrs.bla()

# dyn.  overwrite NSR_SERVER setting?
# without changing func-signature (no param)?
# kwargs?

nsrs.init_settings(NEW_NSR_SERVER="zaphod")
nsrs.bla()

nsrs.get_clients()
