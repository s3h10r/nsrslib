# we're using the __init__ module to put back some APIs at top level
# so instead:
#
#   from nsrslib.core import get_clients
#
# we can do:
#
#   from nsrslib import get_clients

__version__="0.0.94"

from core import get_clients
from core import get_manualsaves

from core import get_clients_json
from core import get_manualsaves_json


def get_version():
    return __version__
