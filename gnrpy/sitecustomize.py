# We force the default encoding to UTF-8.
# This is required to make tons of stuff (WSGI,
# interactive console) work with non-ascii chars.

import sys

sys.setdefaultencoding('utf-8')