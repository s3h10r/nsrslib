# we're using the __init__ module to put back some APIs at top level
# so instead:
#
#   from nsrslib.core import get_clients
#
# we can do:
#
#   from nsrslib import get_clients

from core import get_clients, get_pools
from core import init_settings 
from core import bla
