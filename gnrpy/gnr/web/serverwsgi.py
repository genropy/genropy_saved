from gnr.core.gnrbag import Bag
from gnr.web.gnrwsgisite import GnrWsgiSite
from paste import httpserver
try:
  from waitress.server import create_server
  HAS_WAITRESS = True
except ImportError:
  from paste import httpserver
  HAS_WAITRESS = False
import sys
import os
import re
import errno
import time
import glob

try:
    import subprocess
except ImportError:
    from paste.util import subprocess24 as subprocess

from paste.reloader import Monitor
from paste.util.classinstance import classinstancemethod
import optparse
import threading
import atexit
import logging
from gnr.core.gnrsys import expandpath, listdirs
from gnr.core.gnrlog import enable_colored_logging
fnull = open(os.devnull, 'w')
MAXFD = 1024
import re
CONN_STRING_RE=r"(?P<ssh_user>\w*)\:?(?P<ssh_password>\w*)\@(?P<ssh_host>(\w|\.)*)\:?(?P<ssh_port>\w*)(\/?(?P<db_user>\w*)\:?(?P<db_password>\w*)\@(?P<db_host>(\w|\.)*)\:?(?P<db_port>\w*))?"
CONN_STRING = re.compile(CONN_STRING_RE)

wsgi_options = dict(
        port=8080,
        host='0.0.0.0',
        reload=False,
        set_user=None,
        set_group=None,
        server_name='Genropy',
        debug=True,
        profile=False,
        noclean=False,
        restore=False,
        source_instance=None,
        remotesshdb=None
        )

DNS_SD_PID = None

def gnr_reloader_install(poll_interval=1):
    """
    Install the reloading monitor.

    On some platforms server threads may not terminate when the main
    thread does, causing ports to remain open/locked.  The
    ``raise_keyboard_interrupt`` option creates a unignorable signal
    which causes the whole application to shut-down (rudely).
    """
    mon = GnrReloaderMonitor(poll_interval=poll_interval)
    t = threading.Thread(target=mon.periodic_reload)
    t.setDaemon(True)
    t.start()


class GnrReloaderMonitor(Monitor):
    global_reloader_callbacks = []

    def __init__(self, poll_interval):
        self.reloader_callbacks = []
        super(GnrReloaderMonitor, self).__init__(poll_interval)

    def check_reload(self):
        filenames = list(self.extra_files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                print >> sys.stderr, "Error calling paste.reloader callback %r:" % file_callback
                import traceback
                traceback.print_exc()
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError), exc:
                continue
            if filename is not None:
                filenames.append(filename)
        for filename in filenames:
            try:
                stat = os.stat(filename)
                if stat:
                    mtime = stat.st_mtime
                else:
                    mtime = 0
            except (OSError, IOError):
                continue
            if filename.endswith('.pyc') and os.path.exists(filename[:-1]):
                mtime = max(os.stat(filename[:-1]).st_mtime, mtime)
            elif filename.endswith('$py.class') and \
                    os.path.exists(filename[:-9] + '.py'):
                mtime = max(os.stat(filename[:-9] + '.py').st_mtime, mtime)
            if not self.module_mtimes.has_key(filename):
                self.module_mtimes[filename] = mtime
            elif self.module_mtimes[filename] < mtime:
                print >> sys.stderr, (
                    "-- [%i-%i-%i %i:%i:%i] -- %s changed; reloading..." % (time.localtime()[:6]+(filename,)))
                return False
        return True

    def add_reloader_callback(self, cls, callback):
        """Add a callback -- a function that takes no parameters -- that will
        return a list of filenames to watch for changes."""
        if self is None:
            for instance in cls.instances:
                instance.add_reloader_callback(callback)
            cls.global_reloader_callbacks.append(callback)
        else:
            self.reloader_callbacks.append(callback)

    add_reloader_callback = classinstancemethod(add_reloader_callback)

    def periodic_reload(self):
        while True:
            if not self.check_reload():
            # use os._exit() here and not sys.exit() since within a
            # thread sys.exit() just closes the given thread and
            # won't kill the process; note os._exit does not call
            # any atexit callbacks, nor does it do finally blocks,
            # flush open files, etc.  In otherwords, it is rude.
                for cb in self.reloader_callbacks:
                    cb()
                os._exit(3)
                break
            time.sleep(self.poll_interval)
#def stop_tunnel(tunnel):
#    tunnel.stop()

#def start_tunnel(ssh_user=None, ssh_password=None, ssh_host=None, ssh_port=None,
#            db_user=None, db_password=None, db_host=None, db_port=None,first_run=None,**kwargs):
#    from gnr.core.gnrssh import SshTunnel
#    import getpass
#    ssh_host = ssh_host
#    ssh_port = ssh_port
#    username = ssh_user
#    forwarded_port = db_port
#    forwarded_host = db_host
#    if not ssh_password:
#        password = getpass.getpass('Enter SSH password:')
#    else:
#        password = ssh_password
#        if first_run:
#            cont = ''
#            while not (cont and cont[0] in ('Y','y','S','s')):
#                cont = raw_input('Press Y to continue with SSH remote connection ')
#
#
#    tunnel = SshTunnel(forwarded_port=forwarded_port, forwarded_host=forwarded_host,
#            ssh_host=ssh_host, ssh_port=ssh_port, 
#            username=username, password=password)
#    tunnel.prepare_tunnel()
#    local_port = tunnel.local_port
#    tunnel.serve_tunnel()
#    atexit.register(stop_tunnel, tunnel)
#    return local_port

    
def start_bonjour(host=None, port=None, server_name=None, server_description=None, home_uri=None):
    global DNS_SD_PID
    if DNS_SD_PID:
        return
    if host == '0.0.0.0': host = ''
    if host == '127.0.0.1':
        return
    if not server_name: server_name = 'Genro'
    if not server_description: server_description = 'port ' + str(port)
    name = server_name + ": " + server_description
    type = "_http._tcp"
    port = str(port)
    cmds = [['/usr/bin/avahi-publish-service', ["-H", host, name, type, port]],
            ['/usr/bin/dns-sd', ['-R', name, type, "." + host, port, "path=/"]]]

    for cmd, args in cmds:
    # TODO:. This check is flawed.  If one has both services installed and
    # avahi isn't the one running, then this won't work.  We should either
    # try registering with both or checking what service is running and use
    # that.  Program availability on the filesystem was never enough...
        if os.path.exists(cmd):
            DNS_SD_PID = subprocess.Popen([cmd] + args,stdout=fnull)
            #DNS_SD_PID = os.spawnv(os.P_NOWAIT, cmd, [cmd] + args)
            atexit.register(stop_bonjour)
            break


def stop_bonjour():
    global DNS_SD_PID
    #import signal

    if not DNS_SD_PID:
        return
    try:
        DNS_SD_PID.terminate()
        #os.kill(DNS_SD_PID, signal.SIGTERM)
    except OSError:
        DNS_SD_PID.kill()
        pass
    fnull.close()

class ServerException(Exception):
    pass

class DaemonizeException(Exception):
    pass

class Server(object):
    min_args = 0
    usage = '[start|stop|restart|status] [var=value]'
    summary = "Start this genropy application"
    description = """\
    This command serves a genropy web application.  

    If start/stop/restart is given, then --daemon is implied, and it will
    start (normal operation), stop (--stop-daemon), or do both.

    """

    LOGGING_LEVELS = {'notset': logging.NOTSET,
                      'debug': logging.DEBUG,
                      'info': logging.INFO,
                      'warning': logging.WARNING,
                      'error': logging.ERROR,
                      'critical': logging.CRITICAL}

    parser = optparse.OptionParser(usage)
    if hasattr(os, 'fork'):
        parser.add_option('--daemon',
                          dest="daemon",
                          action="store_true",
                          help="Run in daemon (background) mode")
    parser.add_option('--pid-file',
                      dest='pid_file',
                      metavar='FILENAME',
                      help="Save PID to file (default to paster.pid if running in daemon mode)")
    parser.add_option('-L', '--log-level', dest="log_level", metavar="LOG_LEVEL",
                      help="Logging level",
                      choices=LOGGING_LEVELS.keys(),
                      default="warning")
    parser.add_option('--log-file',
                      dest='log_file',
                      metavar='LOG_FILE',
                      help="Save output to the given log file (redirects stdout)")
    parser.add_option('--reload',
                      dest='reload',
                      action='store_true',
                      help="Use auto-restart file monitor")
    parser.add_option('--noreload',
                      dest='reload',
                      action='store_false',
                      help="Do not use auto-restart file monitor")
    parser.add_option('--debug',
                      dest='debug',
                      action='store_true',
                      help="Use weberror debugger")
    parser.add_option('--nodebug',
                      dest='debug',
                      action='store_false',
                      help="Don't use weberror debugger")
    parser.add_option('--profile',
                      dest='profile',
                      action='store_true',
                      help="Use profiler at /__profile__ url")
    parser.add_option('--bonjour',
                      dest='bonjour',
                      action='store_true',
                      help="Use bonjour server announcing")
    parser.add_option('--reload-interval',
                      dest='reload_interval',
                      default=1,
                      help="Seconds between checking files (low number can cause significant CPU usage)")

    parser.add_option('-c', '--config',
                      dest='config_path',
                      help="gnrserve directory path")

    parser.add_option('-p', '--port',
                      dest='port',
                      help="Sets server listening port (Default: 8080)")

    parser.add_option('-H', '--host',
                      dest='host',
                      help="Sets server listening address (Default: 0.0.0.0)")
    parser.add_option('--monitor-restart',
                      dest='monitor_restart',
                      action='store_true',
                      help="Auto-restart server if it dies")
    parser.add_option('--status',
                      action='store_true',
                      dest='show_status',
                      help="Show the status of the (presumably daemonized) server")
    parser.add_option('--restore',
                      dest='restore',
                      help="Restore from path")
    parser.add_option('--source_instance',
                      dest='source_instance',
                      help="Import from instance")
   #parser.add_option('--remotesshdb',
   #                  dest='remotesshdb',
   #                  help="""Allow remote db connections over ssh tunnels.
   #                  use connection string in the form: ssh_user@ssh_host:ssh_port/db_user:db_password@db_host:db_port
   #                  if db part in the connection string is omitted the defaults from instanceconfig are used.
   #                  ssh_port is defaulted to 22 if omitted""")

    if hasattr(os, 'setuid'):
    # I don't think these are available on Windows
        parser.add_option('--user',
                          dest='set_user',
                          metavar="USERNAME",
                          help="Set the user (usually only possible when run as root)")
        parser.add_option('--group',
                          dest='set_group',
                          metavar="GROUP",
                          help="Set the group (usually only possible when run as root)")

    parser.add_option('--stop-daemon',
                      dest='stop_daemon',
                      action='store_true',
                      help='Stop a daemonized server (given a PID file, or default paster.pid file)')

    parser.add_option('--verbose',
                      dest='verbose',
                      action='store_true',
                      help='Verbose')

    parser.add_option('-s', '--site',
                      dest='site_name',
                      help="Use command on site identified by supplied name")

    parser.add_option('-n', '--noclean',
                      dest='noclean',
                      help="Don't perform a clean (full reset) restart",
                      action='store_true')

    parser.add_option('--counter',
                      dest='counter',
                      help="Startup counter")

    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)

    default_verbosity = 1

    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'
    _monitor_environ_key = 'PASTE_MONITOR_SHOULD_RUN'

    possible_subcommands = ('start', 'stop', 'restart', 'status')

    def __init__(self, site_script=None, server_name='Genro Server', server_description='Development'):
        self.site_script = site_script
        self.server_description = server_description
        self.server_name = server_name
        #self.remotesshdb = None
        (self.options, self.args) = self.parser.parse_args()
        enable_colored_logging(level=self.LOGGING_LEVELS[self.options.log_level])
        self.load_gnr_config()
        self.set_environment()
        self.site_name = self.options.site_name or (self.args and self.args[0])
        self.remote_db = ''
        if self.site_name:
            if ':' in self.site_name:
                self.site_name,self.remote_db  = self.site_name.split(':',1)
            if not self.gnr_config:
                raise ServerException(
                        'Error: no ~/.gnr/ or /etc/gnr/ found')
            self.site_path, self.site_template = self.site_name_to_path(self.site_name)
            self.site_script = os.path.join(self.site_path, 'root.py')
            if not os.path.isfile(self.site_script):
                raise ServerException(
                        'Error: no root.py in the site provided (%s)' % self.site_name)
        else:
            self.site_path = os.path.dirname(os.path.realpath(site_script))
        self.init_options()


    def site_name_to_path(self, site_name):
        path_list = []
        if 'sites' in self.gnr_config['gnr.environment_xml']:
            path_list.extend([(expandpath(path), site_template) for path, site_template in
                              self.gnr_config['gnr.environment_xml.sites'].digest('#a.path,#a.site_template') if
                              os.path.isdir(expandpath(path))])
        if 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [(expandpath(path), site_template) for path, site_template in
                        self.gnr_config['gnr.environment_xml.projects'].digest('#a.path,#a.site_template') if
                        os.path.isdir(expandpath(path))]
            for project_path, site_template in projects:
                sites = glob.glob(os.path.join(project_path, '*/sites'))
                path_list.extend([(site_path, site_template) for site_path in sites])
        for path, site_template in path_list:
            site_path = os.path.join(path, site_name)
            if os.path.isdir(site_path):
                return site_path, site_template
        raise ServerException(
                'Error: no site named %s found' % site_name)

    def load_gnr_config(self):
        if hasattr(self.options, 'config_path') and self.options.config_path:
            config_path = self.options.config_path
        else:
            if sys.platform == 'win32':
                config_path = '~\gnr'
            else:
                config_path = '~/.gnr'
        config_path = self.config_path = expandpath(config_path)
        if os.path.isdir(config_path):
            self.gnr_config = Bag(config_path)
        else:
            self.gnr_config = Bag()

    def set_environment(self):
        for var, value in self.gnr_config['gnr.environment_xml'].digest('environment:#k,#a.value'):
            var = var.upper()
            if not os.getenv(var):
                os.environ[str(var)] = str(value)

    def init_options(self):
        self.siteconfig = self.get_config()
        options = self.options.__dict__
        for option in options.keys():
            if options.get(option, None) is None: # not specified on the command-line
                site_option = self.siteconfig['wsgi?%s' % option]
                self.options.__dict__[option] = site_option or wsgi_options.get(option)

    def get_tunnel_db_params(self,ssh_connection,dbattrs=None):
        conn_dict = self.parse_connection_string(ssh_connection)
        if not dbattrs:
            dbattrs = self.instance_config.getAttr('db')
        conn_dict['ssh_port'] = int(conn_dict['ssh_port'] or 22)
        conn_dict['db_user'] = conn_dict['db_user'] or dbattrs.get('user')
        conn_dict['db_password'] = conn_dict['db_password'] or dbattrs.get('password')
        conn_dict['db_host'] = conn_dict['db_host'] or dbattrs.get('host')
        conn_dict['db_port'] = conn_dict['db_port'] or dbattrs.get('port')
        if conn_dict['db_port']:
            conn_dict['db_port'] = int(conn_dict['db_port'])
        return conn_dict

    def parse_connection_string(self, connection_string):
        match = re.search(CONN_STRING, connection_string)
        return dict(
        ssh_user = match.group('ssh_user') or None,
        ssh_password = match.group('ssh_password') or None,
        ssh_host = match.group('ssh_host') or None,
        ssh_port = match.group('ssh_port') or None,
        db_user = match.group('db_user') or None,
        db_password = match.group('db_password') or None,
        db_host = match.group('db_host') or None,
        db_port = match.group('db_port') or None)
    

    def get_config(self):
        site_config_path = os.path.join(self.site_path, 'siteconfig.xml')
        base_site_config = Bag(site_config_path)
        site_config = self.gnr_config['gnr.siteconfig.default_xml'] or Bag()
        template = site_config['site?template'] or getattr(self, 'site_template', None)
        if template:
            site_config.update(self.gnr_config['gnr.siteconfig.%s_xml' % template] or Bag())
        if 'sites' in self.gnr_config['gnr.environment_xml']:
            for path, site_template in self.gnr_config.digest('gnr.environment_xml.sites:#a.path,#a.site_template'):
                if path == os.path.dirname(self.site_path):
                    site_config.update(self.gnr_config['gnr.siteconfig.%s_xml' % site_template] or Bag())
        site_config.update(base_site_config)
        return site_config

    @property 
    def site_config(self):
        if not hasattr(self, '_site_config'):
            self._site_config = self.get_config()
        return self._site_config

    @property 
    def instance_config(self):
        if not hasattr(self, '_instance_config'):
            self._instance_config = self.get_instance_config()
        return self._instance_config

    def get_instance_config(self):
        instance_path = os.path.join(self.site_path, 'instance')
        if not os.path.isdir(instance_path):
            instance_path = os.path.join(self.site_path, '..', '..', 'instances', self.site_name)
        if not os.path.isdir(instance_path):
            instance_path = self.site_config['instance?path'] or self.site_config['instances.#0?path']
        instance_config_path = os.path.join(instance_path, 'instanceconfig.xml')
        base_instance_config = Bag(instance_config_path)
        instance_config = self.gnr_config['gnr.instanceconfig.default_xml'] or Bag()
        template = instance_config['instance?template'] or getattr(self, 'instance_template', None)
        if template:
            instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % template] or Bag())
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            for path, instance_template in self.gnr_config.digest('gnr.environment_xml.instances:#a.path,#a.instance_template'):
                if path == os.path.dirname(instance_path):
                    instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % instance_template] or Bag())
        instance_config.update(base_instance_config)
        return instance_config


    def set_user(self):
        if not hasattr(self.options, 'set_user'):
        # Windows case:
            self.options.set_user = self.options.set_group = None
            # @@: Is this the right stage to set the user at?
            self.change_user_group(
                    self.options.set_user, self.options.set_group)
            if (len(self.args) > 1
                and self.args[1] in self.possible_subcommands):
                self.cmd = self.args[1]
                self.restvars = self.args[2:]
            else:
                self.cmd = None
                self.restvars = self.args[1:]
        else:
            if (self.args
                and self.args[0] in self.possible_subcommands):
                self.cmd = self.args[0]
                self.restvars = self.args[1:]
            else:
                self.cmd = None
                self.restvars = self.args[:]

    def set_bonjour(self):
        start_bonjour(host=self.options.host, port=self.options.port, server_name=self.site_name,
                      server_description=self.server_description, home_uri=self.siteconfig['wsgi?home_uri'] or '/')

    def setup_tunnel(self,conn_dict=None,first_run=None):
        db_port = start_tunnel(first_run=first_run,**conn_dict)
        return dict(port=db_port, host='localhost', user=conn_dict['db_user'], password=conn_dict['db_password'])


    def check_cmd(self):
        if self.cmd not in (None, 'start', 'stop', 'restart', 'status'):
            raise ServerException(
                    'Error: must give start|stop|restart (not %s)' % self.cmd)

        if self.cmd == 'status' or self.options.show_status:
            return self.show_status()

        if self.cmd == 'restart' or self.cmd == 'stop':
            result = self.stop_daemon()
            if result:
                if self.cmd == 'restart':
                    print "Could not stop daemon; aborting"
                else:
                    print "Could not stop daemon"
                return result
            if self.cmd == 'stop':
                return result

    def check_logfile(self):
        if getattr(self.options, 'daemon', False):
            if not self.options.log_file:
                self.options.log_file = 'genro.log'
        if self.options.log_file:
            try:
                writeable_log_file = open(self.options.log_file, 'a')
            except IOError, ioe:
                msg = 'Error: Unable to write to log file: %s' % ioe
                raise ServerException(msg)
            writeable_log_file.close()

    def check_pidfile(self):
        if getattr(self.options, 'daemon', False):
            if not self.options.pid_file:
                self.options.pid_file = 'genro.pid'
        if self.options.pid_file:
            try:
                writeable_pid_file = open(self.options.pid_file, 'a')
            except IOError, ioe:
                msg = 'Error: Unable to write to pid file: %s' % ioe
                raise ServerException(msg)
            writeable_pid_file.close()

    def set_pid_and_log(self):
        if self.options.pid_file:
            self.record_pid(self.options.pid_file)

        if self.options.log_file:
            stdout_log = LazyWriter(self.options.log_file, 'a')
            sys.stdout = stdout_log
            sys.stderr = stdout_log
            logging.basicConfig(stream=stdout_log)

    def run(self):
        if self.options.stop_daemon:
            return self.stop_daemon()
        self.set_user()
        if not (
        self.options.reload == 'false' or self.options.reload == 'False' or self.options.reload == False or self.options.reload == None):
            if os.environ.get(self._reloader_environ_key):
                if self.options.verbose > 1:
                    print 'Running reloading file monitor'
                gnr_reloader_install(int(self.options.reload_interval))
                menu_path = os.path.join(self.site_path, 'menu.xml')
                site_config_path = os.path.join(self.site_path, 'siteconfig.xml')
                for file_path in (menu_path, site_config_path):
                    if os.path.isfile(file_path):
                        GnrReloaderMonitor.watch_file(file_path)
                config_path = expandpath(self.config_path)
                if os.path.isdir(config_path):
                    for file_path in listdirs(config_path):
                        GnrReloaderMonitor.watch_file(file_path)
            else:
                return self.restart_with_reloader()
        first_run = int(getattr(self.options, 'counter', 0) or 0) == 0
        if self.options.bonjour and first_run:
            self.set_bonjour()
       #if True or first_run:
       #    self.handle_tunnel(first_run=first_run)
        if self.cmd:
            return self.check_cmd()
        self.check_logfile()
        self.check_pidfile()
        if getattr(self.options, 'daemon', False):
            try:
                self.daemonize()
            except DaemonizeException, ex:
                if self.options.verbose > 0:
                    print str(ex)
                return

        if (self.options.monitor_restart
            and not os.environ.get(self._monitor_environ_key)):
            return self.restart_with_monitor()

        self.set_pid_and_log()

        if self.options.verbose > 0:
            if hasattr(os, 'getpid'):
                msg = 'Starting server in PID %i.' % os.getpid()
            else:
                msg = 'Starting server.'
            print msg

        self.serve()
#
    #def handle_tunnel(self,first_run=None):
    #    if self.remote_db :
    #        dbattrs = self.instance_config.getAttr('db' )
    #        remote_db = self.instance_config.getAttr('remote_db.%s' %self.remote_db)
    #        dbattrs.update(remote_db)
    #        if dbattrs.get('ssh_host'):
    #            conn_dict = self.get_tunnel_db_params(dbattrs['ssh_host'],dbattrs=dbattrs)
    #            self.remotesshdb = self.setup_tunnel(conn_dict,first_run=first_run)
    #    elif hasattr(self.options,'remotesshdb') and self.options.remotesshdb:
    #        conn_dict = self.get_tunnel_db_params(self.options.remotesshdb)
    #        self.remotesshdb = self.setup_tunnel(conn_dict=conn_dict,first_run=first_run)
#

    def serve(self):
        try:
            site_name='%s:%s' %(self.site_name,self.remote_db) if self.remote_db else self.site_name
            gnrServer = GnrWsgiSite(self.site_script, site_name=site_name, _config=self.siteconfig,
                                    _gnrconfig=self.gnr_config,
                                    counter=getattr(self.options, 'counter', None), noclean=self.options.noclean,
                                    options=self.options)
            GnrReloaderMonitor.add_reloader_callback(gnrServer.on_reloader_restart)
            if HAS_WAITRESS:
                server = create_server(gnrServer, host=self.options.host, port=self.options.port)
                print '[Waitress] serving on %s:%s'%(self.options.host,str(self.options.port))
                server.run()
            else:
                httpserver.serve(gnrServer, host=self.options.host, port=self.options.port)
        except (SystemExit, KeyboardInterrupt), e:
            if self.options.verbose > 1:
                raise
            if str(e):
                msg = ' ' + str(e)
            else:
                msg = ''
            print 'Exiting%s (-v to see traceback)' % msg


    def daemonize(self):
        pid = live_pidfile(self.options.pid_file)
        if pid:
            raise DaemonizeException(
                    "Daemon is already running (PID: %s from PID file %s)"
                    % (pid, self.options.pid_file))
        if self.options.verbose > 0:
            print 'Entering daemon mode'
        pid = os.fork()
        if pid:
        # The forked process also has a handle on resources, so we
        # *don't* want proper termination of the process, we just
        # want to exit quick (which os._exit() does)
            os._exit(0)
        os.setsid()
        pid = os.fork()
        if pid:
            os._exit(0)

        # @@: Should we set the umask and cwd now?

        import resource  # Resource usage information.

        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if (maxfd == resource.RLIM_INFINITY):
            maxfd = MAXFD
            # Iterate through and close all file descriptors.
        for fd in range(0, maxfd):
            try:
                os.close(fd)
            except OSError:  # ERROR, fd wasn't open to begin with (ignored)
                pass

        if (hasattr(os, "devnull")):
            REDIRECT_TO = os.devnull
        else:
            REDIRECT_TO = "/dev/null"
        os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)
        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)  # standard output (1)
        os.dup2(0, 2)  # standard error (2)

    def record_pid(self, pid_file):
        pid = os.getpid()
        if self.options.verbose > 1:
            print 'Writing PID %s to %s' % (pid, pid_file)
        f = open(pid_file, 'w')
        f.write(str(pid))
        f.close()
        atexit.register(_remove_pid_file, pid, pid_file, self.options.verbose)

    def stop_daemon(self):
        pid_file = self.options.pid_file or 'paster.pid'
        if not os.path.exists(pid_file):
            print 'No PID file exists in %s' % pid_file
            return 1
        pid = read_pidfile(pid_file)
        if not pid:
            print "Not a valid PID file in %s" % pid_file
            return 1
        pid = live_pidfile(pid_file)
        if not pid:
            print "PID in %s is not valid (deleting)" % pid_file
            try:
                os.unlink(pid_file)
            except (OSError, IOError), e:
                print "Could not delete: %s" % e
                return 2
            return 1
        for j in range(10):
            if not live_pidfile(pid_file):
                break
                #import signal
            #global DNS_SD_PID
            #if DNS_SD_PID:
            #os.kill(DNS_SD_PID, signal.SIGTERM)
            #DNS_SD_PID = None
            time.sleep(1)
        else:
            print "failed to kill web process %s" % pid
            return 3
        if os.path.exists(pid_file):
            os.unlink(pid_file)
        return 0

    def show_status(self):
        pid_file = self.options.pid_file or 'paster.pid'
        if not os.path.exists(pid_file):
            print 'No PID file %s' % pid_file
            return 1
        pid = read_pidfile(pid_file)
        if not pid:
            print 'No PID in file %s' % pid_file
            return 1
        pid = live_pidfile(pid_file)
        if not pid:
            print 'PID %s in %s is not running' % (pid, pid_file)
            return 1
        print 'Server running in PID %s' % pid
        return 0

    def restart_with_reloader(self):
        self.restart_with_monitor(reloader=True)

    def restart_with_monitor(self, reloader=False):
        if self.options.verbose > 0:
            if reloader:
                print 'Starting subprocess with file monitor'
            else:
                print 'Starting subprocess with monitor parent'
        run_counter = 0
        while 1:
            args = [sys.executable] + sys.argv + ['--counter', str(run_counter)]
            run_counter += 1
            new_environ = os.environ.copy()
            if reloader:
                new_environ[self._reloader_environ_key] = 'true'
            else:
                new_environ[self._monitor_environ_key] = 'true'
            proc = None
            try:
                try:
                    _turn_sigterm_into_systemexit()
                    proc = subprocess.Popen(args, env=new_environ)
                    exit_code = proc.wait()
                    proc = None
                except KeyboardInterrupt:
                    print '^C caught in monitor process'
                    if self.options.verbose > 1:
                        raise
                    return 1
            finally:
                if (proc is not None
                    and hasattr(os, 'kill')):
                    import signal

                    try:
                    #global DNS_SD_PID
                    #if DNS_SD_PID:
                    #os.kill(DNS_SD_PID, signal.SIGTERM)
                    #DNS_SD_PID = None
                        os.kill(proc.pid, signal.SIGTERM)
                    except (OSError, IOError):
                        pass
            stop_bonjour()
            if reloader:
            # Reloader always exits with code 3; but if we are
            # a monitor, any exit code will restart
                if exit_code != 3:
                    return exit_code
            if self.options.verbose > 0:
                print '-' * 20, 'Restarting', '-' * 20


    def change_user_group(self, user, group):
        if not user and not group:
            return
        import pwd, grp

        uid = gid = None
        if group:
            try:
                gid = int(group)
                group = grp.getgrgid(gid).gr_name
            except ValueError:
                import grp

                try:
                    entry = grp.getgrnam(group)
                except KeyError:
                    raise ServerException("Bad group: %r; no such group exists" % group)
                gid = entry.gr_gid
        try:
            uid = int(user)
            user = pwd.getpwuid(uid).pw_name
        except ValueError:
            try:
                entry = pwd.getpwnam(user)
            except KeyError:
                raise ServerException("Bad username: %r; no such user exists" % user)
            if not gid:
                gid = entry.pw_gid
            uid = entry.pw_uid
        if self.options.verbose > 0:
            print 'Changing user to %s:%s (%s:%s)' % (
            user, group or '(unknown)', uid, gid)
        if gid:
            os.setgid(gid)
        if uid:
            os.setuid(uid)

class LazyWriter(object):
    """
    File-like object that opens a file lazily when it is first written
    to.
    """

    def __init__(self, filename, mode='w'):
        self.filename = filename
        self.fileobj = None
        self.lock = threading.Lock()
        self.mode = mode

    def open(self):
        if self.fileobj is None:
            self.lock.acquire()
            try:
                if self.fileobj is None:
                    self.fileobj = open(self.filename, self.mode)
            finally:
                self.lock.release()
        return self.fileobj

    def write(self, text):
        fileobj = self.open()
        fileobj.write(text)
        fileobj.flush()

    def writelines(self, text):
        fileobj = self.open()
        fileobj.writelines(text)
        fileobj.flush()

    def flush(self):
        self.open().flush()

def live_pidfile(pidfile):
    """(pidfile:str) -> int | None
    Returns an int found in the named file, if there is one,
    and if there is a running process with that process id.
    Return None if no such process exists.
    """
    pid = read_pidfile(pidfile)
    if pid:
        try:
            os.kill(int(pid), 0)
            return pid
        except OSError, e:
            if e.errno == errno.EPERM:
                return pid
    return None

def read_pidfile(filename):
    if os.path.exists(filename):
        try:
            f = open(filename)
            content = f.read()
            f.close()
            return int(content.strip())
        except (ValueError, IOError):
            return None
    else:
        return None

def _remove_pid_file(written_pid, filename, verbosity):
    current_pid = os.getpid()
    if written_pid != current_pid:
    # A forked process must be exiting, not the process that
    # wrote the PID file
        return
    if not os.path.exists(filename):
        return
    f = open(filename)
    content = f.read().strip()
    f.close()
    try:
        pid_in_file = int(content)
    except ValueError:
        pass
    else:
        if pid_in_file != current_pid:
            print "PID file %s contains %s, not expected PID %s" % (
            filename, pid_in_file, current_pid)
            return
    if verbosity > 0:
        print "Removing PID file %s" % filename
    try:
        os.unlink(filename)
        return
    except OSError, e:
    # Record, but don't give traceback
        print "Cannot remove PID file: %s" % e
        # well, at least lets not leave the invalid PID around...
    try:
        f = open(filename, 'w')
        f.write('')
        f.close()
    except OSError, e:
        print 'Stale PID left in file: %s (%e)' % (filename, e)
    else:
        print 'Stale PID removed'


def ensure_port_cleanup(bound_addresses, maxtries=30, sleeptime=2):
    """
    This makes sure any open ports are closed.

    Does this by connecting to them until they give connection
    refused.  Servers should call like::

        import paste.script
        ensure_port_cleanup([80, 443])
    """
    atexit.register(_cleanup_ports, bound_addresses, maxtries=maxtries,
                    sleeptime=sleeptime)

def _cleanup_ports(bound_addresses, maxtries=30, sleeptime=2):
# Wait for the server to bind to the port.
    import socket
    import errno

    for bound_address in bound_addresses:
        for attempt in range(maxtries):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(bound_address)
            except socket.error, e:
                if e.args[0] != errno.ECONNREFUSED:
                    raise
                break
            else:
                time.sleep(sleeptime)
        else:
            raise SystemExit('Timeout waiting for port.')
        sock.close()

def _turn_sigterm_into_systemexit():
    """
    Attempts to turn a SIGTERM exception into a SystemExit exception.
    """
    try:
        import signal
    except ImportError:
        return

    def handle_term(signo, frame):
        raise SystemExit

    signal.signal(signal.SIGTERM, handle_term)

