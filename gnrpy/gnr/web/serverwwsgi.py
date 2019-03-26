from gnr.core.gnrbag import Bag
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwsgisite import GnrWsgiSite
from werkzeug.serving import run_simple
from werkzeug.debug.tbtools import get_current_traceback, render_console_html
from werkzeug.debug import DebuggedApplication,_ConsoleFrame
from werkzeug.wrappers import Response, Request
import glob
from datetime import datetime
import os
import optparse
import atexit
import logging
from gnr.core.gnrsys import expandpath
from gnr.core.gnrlog import enable_colored_logging
from gnr.app.gnrconfig import getGnrConfig, gnrConfigPath
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.DEBUG)
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
        remote_edit=None,
        remotesshdb=None,
        gzip=None,
        websocket=True
        )

DNS_SD_PID = None

class GnrDebuggedApplication(DebuggedApplication):
    
    def debug_application(self, environ, start_response):
        """Run the application and conserve the traceback frames."""
        app_iter = None
        try:
            app_iter = self.app(environ, start_response)
            for item in app_iter:
                yield item
            if hasattr(app_iter, 'close'):
                app_iter.close()
        except Exception:
            if hasattr(app_iter, 'close'):
                app_iter.close()
            traceback = get_current_traceback(
                skip=1, show_hidden_frames=self.show_hidden_frames,
                ignore_system_exceptions=True)
            for frame in traceback.frames:
                self.frames[frame.id] = frame
            self.tracebacks[traceback.id] = traceback
            request = Request(environ)
            debug_url = '%sconsole?error=%i'%(request.host_url, traceback.id)

            print('Error occurred, debug on: %s', debug_url)

            try:
                start_response('500 INTERNAL SERVER ERROR', [
                    ('Content-Type', 'text/html; charset=utf-8'),
                    # Disable Chrome's XSS protection, the debug
                    # output can cause false-positives.
                    ('X-XSS-Protection', '0'),
                    ('X-Debug-Url', debug_url)
                ])
            except Exception:
                # if we end up here there has been output but an error
                # occurred.  in that situation we can do nothing fancy any
                # more, better log something into the error log and fall
                # back gracefully.
                environ['wsgi.errors'].write(
                    'Debugging middleware caught exception in streamed '
                    'response at a point where response headers were already '
                    'sent.\n')
            else:
                is_trusted = bool(self.check_pin_trust(environ))
                yield traceback.render_full(evalex=self.evalex,
                                            evalex_trusted=is_trusted,
                                            secret=self.secret) \
                    .encode('utf-8', 'replace')
            traceback.log(environ['wsgi.errors'])


    def display_console(self, request):
        """Display a standalone shell."""
        error = request.args.get('error', type=int)
        traceback = self.tracebacks.get(error)
        is_trusted = bool(self.check_pin_trust(request.environ))
        if traceback:
            return Response(traceback.render_full(evalex=self.evalex,
                                            evalex_trusted=is_trusted,
                                            secret=self.secret) \
                    .encode('utf-8', 'replace'),
                        mimetype='text/html')
        if 0 not in self.frames:
            if self.console_init_func is None:
                ns = {}
            else:
                ns = dict(self.console_init_func())
            ns.setdefault('app', self.app)
            self.frames[0] = _ConsoleFrame(ns)
        return Response(render_console_html(secret=self.secret,
                                            evalex_trusted=is_trusted),
                        mimetype='text/html')


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
    parser.add_option('--websocket',
                      dest='websocket',
                      action='store_true',
                      help="Use websocket")
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

    parser.add_option('--remote_edit',
                      dest='remote_edit',
                      action='store_true',
                      help="Enable remote edit")
    parser.add_option('-g','--gzip',
                      dest='gzip',
                      action='store_true',
                      help="Enable gzip compressions")


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
        if hasattr(self.options, 'config_path') and self.options.config_path:
            self.config_path = self.options.config_path
        else:
            self.config_path = gnrConfigPath()
        self.gnr_config = getGnrConfig(config_path=self.config_path, set_environment=True)
        
        self.site_name = self.options.site_name or (self.args and self.args[0]) or os.getenv('GNR_CURRENT_SITE')
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

    def isVerbose(self, level=0):
        return self.options.verbose and self.options.verbose>level

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


    def init_options(self):
        self.siteconfig = self.get_config()
        options = self.options.__dict__
        envopt = dictExtract(os.environ,'GNR_WSGI_OPT_')
        for option in options.keys():
            if options.get(option, None) is None: # not specified on the command-line
                site_option = self.siteconfig['wsgi?%s' % option]
                self.options.__dict__[option] = site_option or wsgi_options.get(option) or envopt.get(option)

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

    def run(self):
        self.reloader = not (self.options.reload == 'false' or self.options.reload == 'False' or self.options.reload == False or self.options.reload == None)
        self.debug = not (self.options.debug == 'false' or self.options.debug == 'False' or self.options.debug == False or self.options.debug == None)
        self.serve()

    def serve(self):
        site_name='%s:%s' %(self.site_name,self.remote_db) if self.remote_db else self.site_name
        gnrServer = GnrWsgiSite(self.site_script, site_name=site_name, _config=self.siteconfig,
                                    _gnrconfig=self.gnr_config,
                                    counter=getattr(self.options, 'counter', None), noclean=self.options.noclean,
                                    options=self.options)
        with gnrServer.register.globalStore() as gs:
            gs.setItem('RESTART_TS',datetime.now())
            #GnrReloaderMonitor.add_reloader_callback(gnrServer.on_reloader_restart)
        atexit.register(gnrServer.on_site_stop)
        if self.debug:
            gnrServer = GnrDebuggedApplication(gnrServer, evalex=True, pin_security=False)
        run_simple(self.options.host, int(self.options.port), gnrServer, use_reloader=self.reloader)
        #run_simple(self.options.host, int(self.options.port), gnrServer, use_debugger=self.debug, use_evalex=self.debug, use_reloader=self.reloader)
        