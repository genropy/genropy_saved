try:
  import wsgi
  from gnr.web.serveruwsgi import Server
except ImportError:
  from gnr.web.serverwsgi import Server
# preserve the following line for backward compatibility
NewServer = Server