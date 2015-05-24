from gnr.core.gnrbag import Bag
from gnr.web.gnrwsgisite import GnrWsgiSite
import sys
import os
import time
import glob
import uwsgi
from uwsgidecorators import timer
from gnr.core.gnrsys import expandpath, listdirs
from gnr.app.gnrconfig import gnrConfigPath, getSiteHandler, getGnrConfig
from gnr.core.gnrstring import boolean
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
        restore=False,
        profile=False,
        noclean=False,
        source_instance=None,
        remote_edit=None,
        remotesshdb=None,
        gzip=None
        )

class attrDict(dict):
    
    def __init__(self, in_dict=None):
        in_dict = in_dict or dict()
        dict.__init__(self, in_dict)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

class GnrReloaderMonitor(object):
    """Class inspired by Ian Briking's paste.Monitor"""

    global_reloader_callbacks = []


    def __init__(self):
        self.module_mtimes = {}
        self.files = []
        self.file_callbacks = []
        self.reloader_callbacks = []
        

    def watch_file(self, filename):
        filename = os.path.abspath(filename)
        self.files.append(filename)


    def add_file_callback(self, callback):
        self.file_callbacks.append(callback)

    def check_changed(self):
        filenames = list(self.files)
        for file_callback in self.file_callbacks:
            try:
                filenames.extend(file_callback())
            except:
                continue
        for module in sys.modules.values():
            try:
                filename = module.__file__
            except (AttributeError, ImportError):
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
            if not filename in self.module_mtimes:
                self.module_mtimes[filename] = mtime
            elif self.module_mtimes[filename] < mtime:
                print "-- [%i-%i-%i %i:%i:%i] -- %s changed; reloading..." % (time.localtime()[:6]+(filename,))
                return True
        return False

    def add_reloader_callback(self, callback):
        self.reloader_callbacks.append(callback)


class ServerException(Exception):
    pass

class Server(object):
    
    def __init__(self, site_name=None):
        self.options = attrDict()
        self.gnr_config = getGnrConfig()
        self.config_path = gnrConfigPath()
        self.set_environment()
        self.site_name = site_name
        if self.site_name:
            if not self.gnr_config:
                raise ServerException(
                        'Error: no ~/.gnr/ or /etc/gnr/ found')
            self.site_handler = getSiteHandler(site_name)
            self.site_path = self.site_handler['site_path']
            self.site_template = self.site_handler['site_template']
            self.site_script = self.site_handler['site_script']
            if not os.path.isfile(self.site_script):
                raise ServerException(
                        'Error: no root.py in the site provided (%s)' % self.site_name)
        else:
            self.site_script = os.path.join('.', 'root.py')
        self.init_options()
        self.gnr_site = GnrWsgiSite(self.site_script, site_name=self.site_name, _config=self.siteconfig,
                                    _gnrconfig=self.gnr_config,
                                    counter=self.options.get('counter'), noclean=self.options.get('noclean'),
                                    options=self.options)
    @property
    def code_monitor(self):
        if not hasattr(self, '_code_monitor'):
            if self.options.get('reload') in ('false', 'False', False, None):
                self._code_monitor = None
            else:
                self._code_monitor = GnrReloaderMonitor()
                menu_path = os.path.join(self.site_path, 'menu.xml')
                site_config_path = os.path.join(self.site_path, 'siteconfig.xml')
                for file_path in (menu_path, site_config_path):
                    if os.path.isfile(file_path):
                        self._code_monitor.watch_file(file_path)
                config_path = expandpath(self.config_path)
                if os.path.isdir(config_path):
                    for file_path in listdirs(config_path):
                        self._code_monitor.watch_file(file_path)
                self._code_monitor.add_reloader_callback(self.gnr_site.on_reloader_restart)
        return self._code_monitor

    def set_environment(self):
        for var, value in self.gnr_config['gnr.environment_xml'].digest('environment:#k,#a.value'):
            var = var.upper()
            if not os.getenv(var):
                os.environ[str(var)] = str(value)

    def init_options(self):
        self.siteconfig = self.get_config()
        options = self.options.__dict__
        for option in wsgi_options.keys():
            if options.get(option, None) is None: # not specified on the command-line
                site_option = self.siteconfig['wsgi?%s' % option]
                self.options[option] = site_option or wsgi_options.get(option)
        for (key, dtype) in (('debug','B'),('restore','T'),('profile','B'),('remote_edit','B'),('gzip','B')):
            env_key = 'GNR_%s_%s'%(self.site_name.upper(), key.upper())
            env_value = os.getenv(env_key)
            if env_value:
                if dtype=='B':
                    env_value = boolean(env_value)
                self.options.__dict__[key] = env_value
                


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

    def __call__(self, environ, start_response):
        return self.gnr_site(environ, start_response)

server = Server(len(sys.argv) and sys.argv[-1])

@timer(3)
def code_monitor_reload(sig):
    if server.code_monitor and server.code_monitor.check_changed():
        uwsgi.reload()

def application(environ,start_response):
    return server(dict(environ),start_response)
