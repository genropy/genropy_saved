from gnr.core.gnrbag import Bag
from gnr.web.gnrwsgisite import GnrWsgiSite
from paste import httpserver
import sys
import os
import re
import errno
import time
import glob
import subprocess

    

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

wsgi_options = dict(
        port=8080,
        host='0.0.0.0',
        reload=False,
        set_user=None,
        set_group=None,
        server_name='Genropy',
        debug=True,
        profile=False,
        noclean=False
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
        (self.options, self.args) = self.parser.parse_args()
        enable_colored_logging(level=self.LOGGING_LEVELS[self.options.log_level])
        self.load_gnr_config()
        self.set_environment()
        self.site_name = self.options.site_name or (self.args and self.args[0])
        if self.site_name:
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

    def set_bonjour(self):
        start_bonjour(host=self.options.host, port=self.options.port, server_name=self.site_name,
                      server_description=self.server_description, home_uri=self.siteconfig['wsgi?home_uri'] or '/')


    def run(self):
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
        
        if (self.options.monitor_restart
            and not os.environ.get(self._monitor_environ_key)):
            return self.restart_with_monitor()


        if self.options.verbose > 0:
            if hasattr(os, 'getpid'):
                msg = 'Starting server in PID %i.' % os.getpid()
            else:
                msg = 'Starting server.'
            print msg

        self.serve()


    def serve(self):
        try:
            gnrServer = GnrWsgiSite(self.site_script, site_name=self.site_name, _config=self.siteconfig,
                                    _gnrconfig=self.gnr_config,
                                    counter=getattr(self.options, 'counter', None), noclean=self.options.noclean,
                                    options=self.options)
            GnrReloaderMonitor.add_reloader_callback(gnrServer.on_reloader_restart)
            httpserver.serve(gnrServer, host=self.options.host, port=self.options.port)
        except (SystemExit, KeyboardInterrupt), e:
            if self.options.verbose > 1:
                raise
            if str(e):
                msg = ' ' + str(e)
            else:
                msg = ''
            print 'Exiting%s (-v to see traceback)' % msg


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

