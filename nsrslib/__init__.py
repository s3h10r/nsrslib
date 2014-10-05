# we're using the __init__ module to put back some APIs at top level
# so instead:
#
#   from nsrslib.core import get_clients
#
# we can do:
#
#   from nsrslib import get_clients

__version__="0.0.9"

from core import get_clients, get_pools

def get_version():
    return __version__
