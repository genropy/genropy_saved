from gnr.core.gnrbag import Bag
from gnr.web.gnrwsgisite import GnrWsgiSite
from paste import httpserver
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
import optparse
import threading
import atexit
import logging
from gnr.core.gnrsys import expandpath
MAXFD = 1024

wsgi_options=dict(
    port=8080,
    host='0.0.0.0',
    reload=False,
    set_user=None,
    set_group=None,
    session_key='session',
    server_name='Genropy',
    debug=True
    )

DNS_SD_PID = None

def start_bonjour(host=None, port=None, server_name=None,
    server_description=None,home_uri=None):
    global DNS_SD_PID
    if DNS_SD_PID:
        return
    if host=='0.0.0.0': host=''
    if host=='127.0.0.1': 
        return
    if not server_name: server_name='Genro'
    if not server_description: server_description='port '+str(port)
    name = server_name + ": " + server_description
    type = "_http._tcp"
    port = str(port)
    cmds = [['/usr/bin/avahi-publish-service', ["-H", host, name,type, port]],['/usr/bin/dns-sd', ['-R', name, type, "."+host, port, "path=/"]]]

    for cmd, args in cmds:
        # TODO:. This check is flawed.  If one has both services installed and
        # avahi isn't the one running, then this won't work.  We should either
        # try registering with both or checking what service is running and use
        # that.  Program availability on the filesystem was never enough...
        if os.path.exists(cmd):
            DNS_SD_PID = os.spawnv(os.P_NOWAIT, cmd, [cmd]+args)
            atexit.register(stop_bonjour)
            break

def stop_bonjour():
    import signal
    if not DNS_SD_PID:
        return
    try:
        os.kill(DNS_SD_PID, signal.SIGTERM)
    except OSError:
        pass


class ServerException(Exception):
    pass
    
class DaemonizeException(Exception):
    pass

class NewServer(object):
    min_args = 0
    usage = '[start|stop|restart|status] [var=value]'
    summary = "Start this genropy application"
    description = """\
    This command serves a genropy web application.  

    If start/stop/restart is given, then --daemon is implied, and it will
    start (normal operation), stop (--stop-daemon), or do both.

    """
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
    parser.add_option('--log-file',
                      dest='log_file',
                      metavar='LOG_FILE',
                      help="Save output to the given log file (redirects stdout)")
    parser.add_option('--reload',
                      dest='reload',
                      action='store_true',
                      help="Use auto-restart file monitor")
    parser.add_option('--debug',
                      dest='debug',
                      action='store_true',
                      help="Use weberror debugger")
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
                      
    parser.add_option('-c','--config',
                      dest='config_path',
                      default="~/.gnr",
                      help="gnrserve directory path")
    
    parser.add_option('-p','--port',
                      dest='port',
                      help="Sets server listening port (Default: 8080)")

    parser.add_option('-H','--host',
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

    parser.add_option('-s','--site',
                dest='site_name',
                help="Use command on site identified by supplied name")

    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)

    default_verbosity = 1

    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'
    _monitor_environ_key = 'PASTE_MONITOR_SHOULD_RUN'

    possible_subcommands = ('start', 'stop', 'restart', 'status')
    
    def __init__(self,site_script=None, server_name='Genro Server',server_description='Development'):
        self.site_script = site_script
        self.server_description=server_description
        self.server_name=server_name
        (self.options,self.args)=self.parser.parse_args()
        self.load_gnr_config()
        self.set_enviroment()
        if hasattr(self.options, 'site_name') and self.options.site_name:
            if not self.gnr_config:
                raise ServerException(
                    'Error: no ~/.gnr/ or /etc/gnr/ found')
            self.site_path = self.site_name_to_path(self.options.site_name)
            self.site_script=os.path.join(self.site_path,'root.py')
            if not os.path.isfile(self.site_script):
                raise ServerException(
                    'Error: no root.py in the site provided (%s)' % self.options.site_name)
        else:
            self.site_path = os.path.dirname(os.path.realpath(site_script))
        self.init_options()
        

    def site_name_to_path(self,site_name):
        path_list=[]
        if 'sites' in self.gnr_config['gnr.defaults_xml']:
            path_list.extend([expandpath(path) for path in self.gnr_config['gnr.defaults_xml'].digest('sites:#a.path') if os.path.isdir(expandpath(path))])
        if 'projects' in self.gnr_config['gnr.defaults_xml']:
            projects = [expandpath(path) for path in self.gnr_config['gnr.defaults_xml'].digest('projects:#a.path') if os.path.isdir(expandpath(path))]
            for project_path in projects:
                path_list.extend(glob.glob(os.path.join(project_path,'*/sites')))
        for path in path_list:
            site_path = os.path.join(path,site_name)
            if os.path.isdir(site_path):
                return site_path
        raise ServerException(
            'Error: no site named %s found' % site_name) 
    
    def load_gnr_config(self):
        config_path = expandpath(self.options.config_path)
        if os.path.isdir(config_path):
            self.gnr_config=Bag(config_path)
        else:
            self.gnr_config=Bag()
    
    def set_enviroment(self):
        for var,value in self.gnr_config['gnr.defaults_xml'].digest('enviroment:#k,#a.value'):
            var=var.upper()
            if not os.getenv(var):
                os.environ[var]=str(value)
    
    def init_options(self): 
        self.siteconfig=self.get_config()
        options = self.options.__dict__
        for option in options.keys():
            if not options.get(option):
                site_option = self.siteconfig['wsgi?%s'%option]
                self.options.__dict__[option] = site_option or wsgi_options.get(option)

    def get_config(self):
        site_config_path = os.path.join(self.site_path,'siteconfig.xml')
        site_config = self.gnr_config['gnr.siteconfig.default_xml']
        for path, site_template in self.gnr_config['gnr.defaults_xml'].digest('sites:#a.path,#a.site_template'):
            if path == os.path.dirname(self.site_path):
                if site_config:
                    site_config.update(self.gnr_config['gnr.siteconfig.%s_xml'%site_template] or Bag())
                else:
                    site_config = self.gnr_config['gnr.siteconfig.%s_xml'%site_template]
        if site_config:
            site_config.update(Bag(site_config_path))
        else:
            site_config = Bag(site_config_path)
        return site_config

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
        start_bonjour(host=self.options.host, port=self.options.port, server_name=self.options.server_name, server_description=self.server_description,home_uri=self.home_uri)

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

        if self.options.reload:
            if os.environ.get(self._reloader_environ_key):
                from paste import reloader
                if self.options.verbose > 1:
                    print 'Running reloading file monitor'
                reloader.install(int(self.options.reload_interval))
                if False: #self.requires_config_file:  #VERIFICARE
                    reloader.watch_file(self.args[0])
            else:
                return self.restart_with_reloader()

        if self.options.bonjour:
            self.set_bonjour()
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

    def serve(self):
        try:
            gnrServer=GnrWsgiSite(self.site_script, site_name = self.options.site_name, _config = self.siteconfig, _gnrconfig = self.gnr_config)
            httpserver.serve(gnrServer, host=self.options.host, port=self.options.port)
        except (SystemExit, KeyboardInterrupt), e:
            if self.options.verbose > 1:
                raise
            if str(e):
                msg = ' '+str(e)
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
            import signal
            os.kill(pid, signal.SIGTERM)
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
        while 1:
            args = [sys.executable] + sys.argv
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
                        os.kill(proc.pid, signal.SIGTERM)
                    except (OSError, IOError):
                        pass

            if reloader:
                # Reloader always exits with code 3; but if we are
                # a monitor, any exit code will restart
                if exit_code != 3:
                    return exit_code
            if self.options.verbose > 0:
                print '-'*20, 'Restarting', '-'*20

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
                    raise ServerException(
                        "Bad group: %r; no such group exists" % group)
                gid = entry.gr_gid
        try:
            uid = int(user)
            user = pwd.getpwuid(uid).pw_name
        except ValueError:
            try:
                entry = pwd.getpwnam(user)
            except KeyError:
                raise ServerException(
                    "Bad username: %r; no such user exists" % user)
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

