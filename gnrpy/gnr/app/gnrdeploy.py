from __future__ import print_function
from past.builtins import execfile
from builtins import str
from past.builtins import basestring
from builtins import object
import os
import sys
import glob

import shutil
import random
import string
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrsys import expandpath
from gnr.core.gnrlang import uniquify, GnrException
from collections import defaultdict
from gnr.app.gnrconfig import MenuStruct,IniConfStruct
from gnr.app.gnrconfig import getGnrConfig,gnrConfigPath, setEnvironment

class GnrConfigException(Exception):
    pass


def which(cmd, mode=os.F_OK | os.X_OK, path=None):
    """Given a command, mode, and a PATH string, return the path which
    conforms to the given mode on the PATH, or None if there is no such
    file.
    `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
    of os.environ.get("PATH"), or can be overridden with a custom search
    path.
    """
    # Check that a given file can be accessed with the correct mode.
    # Additionally check that `file` is not a directory, as on Windows
    # directories pass the os.access check.
    def _access_check(fn, mode):
        return (os.path.exists(fn) and os.access(fn, mode)
            and not os.path.isdir(fn))
    # If we're given a path with a directory part, look it up directly rather
    # than referring to PATH directories. This includes checking relative to the
    # current directory, e.g. ./script
    if os.path.dirname(cmd):
        if _access_check(cmd, mode):
            return cmd
        return None
    if path is None:
        path = os.environ.get("PATH", os.defpath)
    if not path:
        return None
    path = path.split(os.pathsep)
    if sys.platform == "win32":
        # The current directory takes precedence on Windows.
        if not os.curdir in path:
            path.insert(0, os.curdir)
        # PATHEXT is necessary to check on Windows.
        pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
        # See if the given file matches any of the expected path extensions.
        # This will allow us to short circuit when given "python.exe".
        # If it does match, only test that one, otherwise we have to try
        # others.
        if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
            files = [cmd]
        else:
            files = [cmd + ext for ext in pathext]
    else:
        # On other platforms you don't have things like PATHEXT to tell you
        # what file suffixes are executable, so just pass on cmd as-is.
        files = [cmd]
    seen = set()
    for dir in path:
        normdir = os.path.normcase(dir)
        if not normdir in seen:
            seen.add(normdir)
            for thefile in files:
                name = os.path.join(dir, thefile)
                if _access_check(name, mode):
                    return name
    return None



def get_random_password(size = 12):
    return ''.join( random.Random().sample(string.ascii_letters+string.digits, size)).lower()

def get_gnrdaemon_port(set_last=False):
    base_config_path  = gnrConfigPath(no_virtualenv=True)
    if not base_config_path or not os.path.exists(base_config_path):
        return '40404'
    environment_xml_path = os.path.join(base_config_path,'environment.xml')
    if not os.path.exists(environment_xml_path):
        return '40404'
    environment_bag = Bag(environment_xml_path)
    gnrdaemon_port = int(environment_bag['gnrdaemon?last_port'] or environment_bag['gnrdaemon?port'] or '40404') + 1
    if set_last:
        environment_bag.getNode('gnrdaemon').attr.update(last_port = gnrdaemon_port)
        environment_bag.toXml(environment_xml_path, typevalue=False,pretty=True)
    return str(gnrdaemon_port)

def build_environment_xml(path=None, gnrpy_path=None, gnrdaemon_password=None, gnrdaemon_port=None):
    genropy_home = os.path.dirname(gnrpy_path)
    genropy_projects = os.path.join(genropy_home,'projects')
    custom_projects = os.path.normpath(os.path.join(genropy_home,'..','genropy_projects'))
    create_folder(custom_projects)
    genropy_packages = os.path.join(genropy_home,'packages')
    genropy_resources = os.path.join(genropy_home,'resources')
    genropy_webtools = os.path.join(genropy_home,'webtools')
    dojo_11_path = os.path.join(genropy_home, 'dojo_libs', 'dojo_11')
    gnr_d11_path = os.path.join(genropy_home,'gnrjs', 'gnr_d11')
    environment_bag = Bag()
    environment_bag.setItem('environment.gnrhome', None, dict(value=genropy_home))
    environment_bag.setItem('projects.genropy', None, dict(path=genropy_projects))
    environment_bag.setItem('projects.custom', None, dict(path=custom_projects))
    environment_bag.setItem('packages.genropy', None, dict(path=genropy_packages))
    environment_bag.setItem('static.js.dojo_11',None, dict(path=dojo_11_path, cdn=""))
    environment_bag.setItem('static.js.gnr_11', None, dict(path=gnr_d11_path))
    environment_bag.setItem('resources.genropy', None, dict(path=genropy_resources))
    environment_bag.setItem('webtools.genropy', None, dict(path=genropy_webtools))
    gnrdaemon_port = gnrdaemon_port or get_gnrdaemon_port(set_last=True)
    environment_bag.setItem('gnrdaemon', None, dict(host='localhost', port=gnrdaemon_port, hmac_key=gnrdaemon_password))
    environment_bag.toXml(path,typevalue=False,pretty=True)

def build_instanceconfig_xml(path=None):
    instanceconfig_bag = Bag()
    instanceconfig_bag.setItem('packages',None)
    instanceconfig_bag.setItem('authentication.xml_auth',None, dict(defaultTags='user,xml'))
    password = get_random_password(size=6)
    instanceconfig_bag.setItem('authentication.xml_auth.admin',None, dict(
        pwd=password, tags='superadmin,_DEV_,admin,user'))
    print("Default password for user admin is %s, you can change it by editing %s" %(password, path))
    instanceconfig_bag.toXml(path,typevalue=False,pretty=True)
    
def build_siteconfig_xml(path=None, gnrdaemon_password=None, gnrdaemon_port=None):
    siteconfig_bag = Bag()
    siteconfig_bag.setItem('wsgi', None, dict(debug=True, reload=True, port='8080'))
    siteconfig_bag.setItem('gui', None, dict(css_theme='ludo'))
    siteconfig_bag.setItem('jslib', None, dict(dojo_version='11', gnr_version='11'))
    siteconfig_bag.setItem('resources.common', None)
    siteconfig_bag.setItem('resources.js_libs', None)
    siteconfig_bag.setItem('gnrdaemon', None, dict(host='localhost', port=gnrdaemon_port or '40404', hmac_key=gnrdaemon_password))
    siteconfig_bag.toXml(path,typevalue=False,pretty=True)

def create_folder(folder_path=None):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    elif not os.path.isdir(folder_path):
        raise GnrConfigException("A file named %s already exists so i couldn't create a folder at same path" % folder_path)

def check_file(xml_path=None):
    if os.path.exists(xml_path):
        raise GnrConfigException("A file named %s already exists so i couldn't create a config file at same path" % xml_path)

def initgenropy(gnrpy_path=None,gnrdaemon_password=None):
    if not gnrpy_path or not os.path.basename(gnrpy_path)=='gnrpy':
        raise GnrConfigException("You are not running this script inside a valid gnrpy folder")
    config_path  = gnrConfigPath(force_return=True)
    instanceconfig_path = os.path.join(config_path,'instanceconfig')
    siteconfig_path = os.path.join(config_path,'siteconfig')
    for folder_path in (config_path, instanceconfig_path, siteconfig_path):
        create_folder(folder_path=folder_path)

    environment_xml_path = os.path.join(config_path,'environment.xml')
    default_instanceconfig_xml_path = os.path.join(instanceconfig_path,'default.xml')
    default_siteconfig_xml_path = os.path.join(siteconfig_path,'default.xml')

    for xml_path in (environment_xml_path, default_instanceconfig_xml_path, default_siteconfig_xml_path):
        check_file(xml_path=xml_path)
    gnrdaemon_password = gnrdaemon_password or get_random_password()
    gnrdaemon_port = get_gnrdaemon_port(set_last=True)
    build_environment_xml(path=environment_xml_path, gnrpy_path=gnrpy_path, gnrdaemon_password=gnrdaemon_password,
        gnrdaemon_port=gnrdaemon_port)
    build_instanceconfig_xml(path=default_instanceconfig_xml_path)
    build_siteconfig_xml(path=default_siteconfig_xml_path, gnrdaemon_password=gnrdaemon_password, gnrdaemon_port=gnrdaemon_port)



GNRDAEMON_SERVICE_TPL = """
[Unit]
Description=GnrDaemon Service
After=multi-user.target

[Service]
Type=idle
User=%(user)s
%(environments)s
ExecStart=%(binpath)s

[Install]
WantedBy=multi-user.target
"""

def gnrdaemonServiceBuilder():
    import pwd
    service_name = 'gnrdaemon'
    if 'VIRTUAL_ENV' in os.environ or hasattr(sys,'real_prefix'):
        pyprefix = os.environ.get('VIRTUAL_ENV', sys.prefix)
        environments = "Environment=VIRTUAL_ENV=%s" %pyprefix
        service_name = '%s_%s'%(service_name, os.path.basename(pyprefix))
    else:
        environments = ''
    current_username = pwd.getpwuid(os.getuid())[0]
    binpath = which('gnrdaemon')
    content = GNRDAEMON_SERVICE_TPL %dict(environments=environments,binpath=binpath, user= current_username)
    service_name = '%s.service'%service_name
    with open(service_name,'w') as service_file:
        service_file.write(content)
    print("""
Gnrdaemon service created Now run these commands:

$ sudo cp %(service_name)s /lib/systemd/system/%(service_name)s
$ sudo chmod 644 /lib/systemd/system/%(service_name)s
$ sudo systemctl daemon-reload  # Refresh the available service list
$ sudo systemctl enable %(service_name)s
$ sudo systemctl start %(service_name)s
...
$ sudo systemctl status %(service_name)s
$ sudo journalctl -e -u %(service_name)s
        """ % dict(service_name=service_name))


GNRSITERUNNERSERVICE_TPL = """
[Unit]
Description=GnrSupervisorSiteRunner Service
After=multi-user.target

[Service]
Type=forking
%(environments)s
User=%(user)s
ExecStart=%(binpath)s
ExecReload=%(ctl_binpath)s reload
ExecStop=%(ctl_binpath)s shutdown

[Install]
WantedBy=multi-user.target
"""

def gnrsiterunnerServiceBuilder():
    import pwd
    current_username = pwd.getpwuid(os.getuid())[0]
    daemon_path = which('supervisord')
    ctl_binpath = which('supervisorctl')
    binroot = ''
    service_name = 'gnrsiterunner'
    if 'VIRTUAL_ENV' in os.environ or hasattr(sys, 'real_prefix'):
        pyprefix = os.environ.get('VIRTUAL_ENV', sys.prefix)
        environments = "Environment=VIRTUAL_ENV=%s" %pyprefix
        binroot = os.path.join(pyprefix,'bin')
        service_name = '%s_%s'%(service_name, os.path.basename(pyprefix))
    else:
        environments = ''
    gnr_path = gnrConfigPath()
    supervisor_conf_path_ini = os.path.join(gnr_path,'supervisord.conf')
    supervisor_log_path = os.path.join(gnr_path,'supervisord.log')
    binpath = '%s -c %s -l %s' % (daemon_path,supervisor_conf_path_ini,
        supervisor_log_path)
    content = GNRSITERUNNERSERVICE_TPL %dict(environments=environments,binpath=binpath,
            user=current_username, ctl_binpath=ctl_binpath)
    service_name = '%s.service'%service_name
    with open(service_name,'w') as service_file:
        service_file.write(content)
    print("""
Gnrsiterunner service created, now run these commands:

$ sudo cp %(service_name)s /lib/systemd/system/%(service_name)s
$ sudo chmod 644 /lib/systemd/system/%(service_name)s
$ sudo systemctl daemon-reload  # Refresh the available service list
$ sudo systemctl enable %(service_name)s

$ sudo systemctl start %(service_name)s
...
$ sudo systemctl status %(service_name)s
# Blah blah blah you should see something happy and green
# Want to check your logs?
$ sudo journalctl -e -u %(service_name)s
        """ % dict(service_name=service_name))

def activateVirtualEnv(name=None):
    activate_file=os.path.join(name, "bin", "activate_this.py")
    execfile(activate_file, dict(__file__=activate_file))

def createVirtualEnv(name=None, copy_genropy=False, copy_projects=None, 
    branch=None):
    import virtualenv
    venv_path = os.path.join(os.getcwd(), name)
    print('Creating virtual environment %s in %s'%(name, venv_path))
    virtualenv.create_environment(name)
    gitrepos_path = os.path.join(venv_path, 'gitrepos')
    if not os.path.exists(gitrepos_path):
        os.makedirs(gitrepos_path)
    activateVirtualEnv(name)
    if copy_projects:
        projects_path = os.path.join(gitrepos_path, 'genropy_projects')
        if not os.path.exists(projects_path):
            os.makedirs(projects_path)
        projects = copy_projects.split(',')
        path_resolver = PathResolver()
        for project in projects:
            prj_path = path_resolver.project_name_to_path(project)
            if prj_path:
                destpath = os.path.join(projects_path, project)
                print('Copying project %s from %s to %s'%(project, prj_path, destpath))
                try:
                    shutil.copytree(prj_path, destpath)
                except shutil.Error as e:
                    print(e)
    if copy_genropy:
        newgenropy_path = os.path.join(gitrepos_path, 'genropy')
        gnr_config = getGnrConfig()
        genropy_path = gnr_config['gnr.environment_xml.environment.gnrhome?value']
        if genropy_path:
            print('Copying genropy from %s to %s'%(genropy_path,newgenropy_path))
            shutil.copytree(genropy_path,newgenropy_path)
            if branch:
                curr_cwd = os.getcwd()
                os.chdir(newgenropy_path)
                import subprocess
                print('Switching to branch %s'%branch)
                subprocess.check_call(['git', 'stash'])
                subprocess.check_call(['git', 'fetch'])
                subprocess.check_call(['git', 'checkout', branch])
                subprocess.check_call(['git', 'pull'])
                os.chdir(curr_cwd)
            gnrpy_path = os.path.join(newgenropy_path,'gnrpy')
            pip_path = os.path.join(venv_path,'bin', 'pip')
            subprocess.check_call([pip_path, 'install', 'paver'])
            paver_path = os.path.join(venv_path,'bin', 'paver')
            os.chdir(gnrpy_path)
            subprocess.check_call([paver_path, 'develop'])
            venv_exec_path = os.path.join(venv_path,'bin', 'python')
            initgenropy(gnrpy_path=gnrpy_path)
            os.chdir(curr_cwd)
    

def projectBag(project_name,packages=None,branches=None,exclude_branches=None):
    p=PathResolver()
    result = Bag()
    branches = branches.split(',') if isinstance(branches,basestring) else (branches or [])
    packages = packages.split(',') if isinstance(packages,basestring) else (packages or [])

    dr = DirectoryResolver(p.project_name_to_path(project_name),include='*.py',dropext=True)
    for pkg,pkgval in list(dr['packages'].items()):
        if packages and pkg not in packages:
            continue
        packagecontent = Bag()
        result[pkg] = packagecontent
        for tbl in list(pkgval['model'].keys()):
            if tbl=='_packages':
                continue
            packagecontent['tables.%s' %tbl] = '%s.%s' %(pkg,tbl)
        for branch in branches:
            branchbag = Bag()
            packagecontent[branch.replace('.','_')] = branchbag
            branchval  = pkgval.pop(branch)
            if branchval:
                for path in branchval.getIndexList():
                    branchbag[path] = path.split('.')[-1]
    return result

    
class EntityNotFoundException(GnrException):
    pass
    

    
class UnknownEntityTypeException(GnrException):
    pass
    

class PathResolver(object):
    """TODO"""
    entities = dict(
            instance='instances',
            site='sites',
            resource='resources',
            package='packages',
            project='projects')
            
    def __init__(self, gnr_config=None):
        self.gnr_config = gnr_config or getGnrConfig()
        setEnvironment(self.gnr_config)
        
        
                
    def js_path(self, lib_type='gnr', version='11'):
        """TODO Return the configuration static js path, with *lib_type* and *version* specified
        
        :param lib_type: Genro Javascript library == gnr
        :param version: the Genro Javascript library version related to the Dojo one. The number of Dojo
                        version is written without any dot. E.g: '11' is in place of '1.1'"""
        path = self.gnr_config['gnr.environment_xml.static.js.%s_%s?path' % (lib_type, version)]
        if path:
            path = os.path.join(expandpath(path), 'js')
        return path
        
    def entity_name_to_path(self, entity_name, entity_type, look_in_projects=True):
        """TODO
        
        :param entity_name: TODO
        :param entity_type: TODO
        :param look_in_projects: TODO"""
        entity = self.entities.get(entity_type)
        if not entity:
            raise UnknownEntityTypeException('Error: entity type %s not known' % entity_type)
        if entity in self.gnr_config['gnr.environment_xml']:
            for path in [expandpath(path) for path in
                         self.gnr_config['gnr.environment_xml'].digest('%s:#a.path' % entity) if
                         os.path.isdir(expandpath(path))]:
                entity_path = os.path.join(path, entity_name)
                if os.path.isdir(entity_path):
                    return expandpath(entity_path)
        if look_in_projects and 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [expandpath(path) for path in self.gnr_config['gnr.environment_xml'].digest('projects:#a.path')
                        if os.path.isdir(expandpath(path))]
            for project_path in projects:
                folders = glob.glob(os.path.join(project_path, '*',entity,entity_name))
                if folders:
                    return expandpath(folders[0])
                elif entity_type=='site':
                    folders = glob.glob(os.path.join(project_path, '*','instances',entity_name))
                    if folders:
                        sitepath = expandpath(os.path.join(folders[0],'site'))
                        root_py_path = expandpath(os.path.join(folders[0],'root.py'))
                        if os.path.exists(root_py_path):
                            if not os.path.exists(sitepath):
                                os.makedirs(sitepath)
                            return sitepath

                        
        raise EntityNotFoundException('Error: %s %s not found' % (entity_type, entity_name))
        
    def site_name_to_path(self, site_name):
        """TODO
        
        :param site_name: TODO"""
        return self.entity_name_to_path(site_name, 'site')
    
    def get_instanceconfig(self,instance_name):
        instanceFolder = self.instance_name_to_path(instance_name)
        instanceName = os.path.basename(instanceFolder)

        project_packages_path = os.path.normpath(os.path.join(instanceFolder, '..', '..', 'packages'))
        if os.path.isdir(project_packages_path):
            project_packages_path = project_packages_path
        if os.path.exists(os.path.join(instanceFolder,'config','instanceconfig.xml')):
            instanceFolder = os.path.join(instanceFolder,'config')
        
        if not instanceFolder:
            return Bag()

        def normalizePackages(config):
            if config['packages']:
                packages = Bag()
                for n in config['packages']:
                    packages.setItem(n.attr.get('pkgcode') or n.label, n.value, n.attr)
                config['packages']  = packages
            return config
        instance_config_path = os.path.join(instanceFolder, 'instanceconfig.xml')
        base_instance_config = normalizePackages(Bag(instance_config_path))
        instance_config = normalizePackages(self.gnr_config['gnr.instanceconfig.default_xml']) or Bag()
        template = base_instance_config['instance?template']
        if template:
            instance_config.update(normalizePackages(self.gnr_config['gnr.instanceconfig.%s_xml' % template]) or Bag())
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            for path, instance_template in self.gnr_config.digest(
                    'gnr.environment_xml.instances:#a.path,#a.instance_template') or []:
                if path == os.path.dirname(instanceFolder):
                    instance_config.update(normalizePackages(self.gnr_config['gnr.instanceconfig.%s_xml' % instance_template]) or Bag())
        instance_config.update(base_instance_config)
        return instance_config


    def get_siteconfig(self,site_name):
        site_config = self.gnr_config['gnr.siteconfig.default_xml']
        site_config_path = self.site_name_to_config_path(site_name)
        path_list = []
        if 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [(expandpath(path), site_template) for path, site_template in
                        self.gnr_config['gnr.environment_xml.projects'].digest('#a.path,#a.site_template') if
                        os.path.isdir(expandpath(path))]
            for project_path, site_template in projects:
                sites = glob.glob(os.path.join(project_path, '*/sites'))
                path_list.extend([(site_path, site_template) for site_path in sites])
            for path, site_template in path_list:
                if path == site_name:
                    if site_config:
                        site_config.update(self.gnr_config['gnr.siteconfig.%s_xml' % site_template] or Bag())
                    else:
                        site_config = self.gnr_config['gnr.siteconfig.%s_xml' % site_template]
        if site_config:
            site_config.update(Bag(site_config_path))
        else:
            site_config = Bag(site_config_path)
        return site_config


    def site_name_to_config_path(self,site_name):
        site_path = self.site_name_to_path(site_name)
        site_config_path = os.path.join(site_path,'siteconfig.xml')
        if os.path.exists(site_config_path):
            return site_config_path
        site_config_path = os.path.join(self.instance_name_to_path(site_name),'config','siteconfig.xml')
        if os.path.exists(site_config_path):
            return site_config_path

    def instance_name_to_path(self, instance_name):
        """TODO
        
        :param instance_name: TODO"""
        return self.entity_name_to_path(instance_name, 'instance')
        
    def package_name_to_path(self, package_name):
        """TODO
        
        :param package_name: TODO"""
        return self.entity_name_to_path(package_name, 'package')
        
    def resource_name_to_path(self, resource_name):
        """TODO
        
        :param resource_name: TODO"""
        return self.entity_name_to_path(resource_name, 'resource')
        
    def project_name_to_path(self, project_name):
        """TODO
        
        :param project_name: TODO"""
        return self.entity_name_to_path(project_name, 'project', look_in_projects=False)
        
    def project_repository_name_to_path(self, project_repository_name, strict=True):
        """TODO
        
        :param project_repository_name: TODO
        :param strict: TODO"""
        if not strict or 'gnr.environment_xml.projects.%s' % project_repository_name in self.gnr_config:
            path = self.gnr_config['gnr.environment_xml.projects.%s?path' % project_repository_name]
            if path:
                return expandpath(path)
        else:
            raise EntityNotFoundException('Error: Project Repository %s not found' % project_repository_name)
            
class ProjectMaker(object):
    """Handle the autocreation of a package.
    
    To autocreate a package, please type in your console::
        
        gnrmkpackage packagename
        
    where ``packagename`` is the name of your ``package`` folder."""
    def __init__(self, project_name, base_path=None):
        self.project_name = project_name
        self.base_path = base_path or '.'
        
    def do(self):
        """Create the project path with its subfolders paths: the path of the ``packages`` folder,
        the path of the ``sites`` folder, the path of the ``instances`` folder and the path of the
        ``resources`` folder."""
        self.project_path = os.path.join(self.base_path, self.project_name)
        self.packages_path = os.path.join(self.project_path, 'packages')
        self.instances_path = os.path.join(self.project_path, 'instances')
        for path in (self.project_path, self.packages_path, self.instances_path):
            if not os.path.isdir(path):
                os.mkdir(path)
                


class SiteMaker(object):
    #deprecated 
    """Handle the autocreation of the ``sites`` folder.
    
    To autocreate the ``sites`` folder, please type in your console::
        
        gnrmksite sitesname
        
    where 'sitesname' is the name of your ``sites`` folder.
    """
    def __init__(self, site_name, base_path=None, resources=None, instance=None, dojo_version='11',
                 wsgi_port=None, wsgi_reload=None, wsgi_mainpackage=None, wsgi_debug=None, config=None):
        self.site_name = site_name
        self.base_path = base_path or '.'
        self.resources = resources or []
        self.instance = instance
        self.wsgi_port = wsgi_port
        self.wsgi_reload = wsgi_reload
        self.wsgi_mainpackage = wsgi_mainpackage
        self.wsgi_debug = wsgi_debug
        self.dojo_version = dojo_version
        self.config = config
        
    def do(self):
        """TODO"""
        self.site_path = os.path.join(self.base_path, self.site_name)
        pages_path = os.path.join(self.site_path, 'pages')
        root_py_path = os.path.join(self.site_path, 'root.py')
        siteconfig_xml_path = os.path.join(self.site_path, 'siteconfig.xml')
        if not os.path.isdir(self.site_path):
            os.mkdir(self.site_path)
        if not os.path.isdir(pages_path):
            os.mkdir(pages_path)
        if not os.path.isfile(root_py_path):
            root_py = open(root_py_path, 'w')
            root_py.write("""#!/usr/bin/env python2.6
import sys
sys.stdout = sys.stderr
from gnr.web.gnrwsgisite import GnrWsgiSite
site = GnrWsgiSite(__file__)

def application(environ,start_response):
    return site(environ,start_response)

if __name__ == '__main__':
    from gnr.web.server import NewServer
    server=NewServer(__file__)
    server.run()""")
            root_py.close()
        if not os.path.isfile(siteconfig_xml_path):
            if not self.config:
                siteconfig = Bag()
                if self.instance:
                    siteconfig.setItem('instances.%s' % self.instance, None)
                for resource in self.resources:
                    if isinstance(resource, tuple) or isinstance(resource, list):
                        resource, resource_path = resource
                        siteconfig.setItem('resources.%s' % resource, None, path=resource_path)
                    else:
                        siteconfig.setItem('resources.%s' % resource, None)
                wsgi_options = dict()
                for option in ('reload', 'debug', 'port', 'mainpackage'):
                    value = getattr(self, 'wsgi_%s' % option, None)
                    if value:
                        wsgi_options[option] = value
                siteconfig.setItem('wsgi', None, **wsgi_options)
                siteconfig['connection_timeout'] = None
                siteconfig['connection_refresh'] = None
                siteconfig.setItem('dojo', None, version=self.dojo_version)
            else:
                siteconfig = self.config
            siteconfig.toXml(siteconfig_xml_path,typevalue=False,pretty=True)
            
class InstanceMaker(object):
    """Handle the autocreation of the ``instances`` folder.
    
    To autocreate the ``instances`` folder, please type in your console::
        
        gnrmkinstance instancesname
        
    where ``instancesname`` is the name of your ``instances`` folder.
    """
    def __init__(self, instance_name, base_path=None, packages=None, authentication=True, authentication_pkg=None,
                 db_dbname=None, db_implementation=None, db_host=None, db_port=None,
                 db_user=None, db_password=None, use_dbstores=False, config=None,main_package=None):
        self.instance_name = instance_name
        self.base_path = base_path or '.'
        self.packages = packages or []
        self.db_dbname = db_dbname or instance_name
        self.authentication = authentication
        self.main_package = main_package
        if self.authentication:
            self.authentication_pkg = authentication_pkg
            if not self.authentication_pkg and self.packages:
                package = self.packages[0]
                if isinstance(package, tuple) or isinstance(package, list):
                    package = package[0]
                self.authentication_pkg = package
            if not self.authentication_pkg:
                self.authentication_pkg = 'adm'
        self.db_implementation = db_implementation
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.use_dbstores = use_dbstores
        self.config = config
        self.instance_path = os.path.join(self.base_path, self.instance_name)
        self.config_path = os.path.join(self.instance_path,'config')
    
    def do(self):
        self.do_instance()
        self.do_site()

    def do_instance(self):
        custom_path = os.path.join(self.instance_path, 'custom')
        data_path = os.path.join(self.instance_path, 'data')
        instanceconfig_xml_path = os.path.join(self.config_path, 'instanceconfig.xml')
        folders_to_make = [self.instance_path,self.config_path, custom_path, data_path]
        if self.use_dbstores:
            dbstores_path = os.path.join(self.instance_path, 'dbstores')
            folders_to_make.append(dbstores_path)
        for path in folders_to_make:
            if not os.path.isdir(path):
                os.mkdir(path)
        if not os.path.isfile(instanceconfig_xml_path):
            if not self.config:
                instanceconfig = Bag()
                db_options = dict()
                for option in ('dbname', 'implementation', 'host', 'port', 'username', 'password'):
                    value = getattr(self, 'db_%s' % option, None)
                    if value:
                        db_options[option] = value
                instanceconfig.setItem('db', None, **db_options)
                instanceconfig.setItem('packages', None)
                for package in self.packages:
                    if isinstance(package, tuple) or isinstance(package, list):
                        package, package_path = package
                        instanceconfig.setItem('packages.%s' % package.replace(':','_'), None, path=package_path,pkgcode=package)
                    else:
                        instanceconfig.setItem('packages.%s' % package.replace(':','_'), None,pkgcode=package)
                if self.authentication:
                    instanceconfig.setItem('authentication', None, pkg=self.authentication_pkg)
                    instanceconfig.setItem('authentication.py_auth', None, defaultTags="user", pkg="adm",
                                           method="authenticate")
            else:
                instanceconfig = self.config
            instanceconfig.toXml(instanceconfig_xml_path,typevalue=False,pretty=True)
            
    def do_site(self):
        """TODO"""
        self.site_path = os.path.join(self.instance_path, 'site')
        root_py_path = os.path.join(self.instance_path, 'root.py')
        siteconfig_xml_path = os.path.join(self.config_path, 'siteconfig.xml')
        if not os.path.isdir(self.site_path):
            os.mkdir(self.site_path)
        if not os.path.isfile(root_py_path):
            root_py = open(root_py_path, 'w')
            root_py.write("""#!/usr/bin/env python2.6
import sys
sys.stdout = sys.stderr
from gnr.web.gnrwsgisite import GnrWsgiSite
site = GnrWsgiSite(__file__)

def application(environ,start_response):
    return site(environ,start_response)

if __name__ == '__main__':
    from gnr.web.server import NewServer
    server=NewServer(__file__)
    server.run()""")
            root_py.close()
        if not os.path.isfile(siteconfig_xml_path):
            if not self.config:
                siteconfig = Bag()
                wsgi_options = dict()
                wsgi_options.setdefault('mainpackage',self.main_package)
                for option in ('reload', 'debug', 'port', 'mainpackage'):
                    value = getattr(self, 'wsgi_%s' % option, None)
                    if value:
                        wsgi_options[option] = value
                siteconfig.setItem('wsgi', None, **wsgi_options)
            else:
                siteconfig = self.config
            siteconfig.toXml(siteconfig_xml_path,typevalue=False,pretty=True)
            
class PackageMaker(object):
    """Handle the autocreation of the ``packages`` folder.
    
    To autocreate the ``packages`` folder, please type in your console::
        
        gnrmkpackage packagesname
        
    where ``packagesname`` is the name of your ``packages`` folder.
    """
    def __init__(self, package_name, base_path=None, sqlschema=None, sqlprefix=True,
                 name_short=None, name_long=None, name_full=None,
                 login_url=None, comment=None,helloworld=False):
        self.package_name = package_name
        self.base_path = base_path or '.'
        self.name_short = name_short or self.package_name.capitalize()
        self.name_full = name_full or self.package_name.capitalize()
        self.name_long = name_long or self.package_name.capitalize()
        self.sqlschema = sqlschema or self.package_name.lower()
        self.sqlprefix = sqlprefix
        self.comment = comment or '%s package' % self.package_name
        self.login_url = login_url or '%s/login' % self.package_name
        self.helloworld = helloworld
        self.package_path = os.path.join(self.base_path, self.package_name)
        self.model_path = os.path.join(self.package_path, 'model')
        self.lib_path = os.path.join(self.package_path, 'lib')
        self.webpages_path = os.path.join(self.package_path, 'webpages')
        self.resources_path = os.path.join(self.package_path, 'resources')
        self.framedindex_path = os.path.join(self.webpages_path,'index.py')
        self.main_py_path = os.path.join(self.package_path, 'main.py')
        
    def do(self):
        """Creates the files of the ``packages`` folder"""
        for path in (self.package_path, self.model_path, self.lib_path, self.webpages_path, self.resources_path):
            if not os.path.isdir(path):
                os.mkdir(path)
        sqlprefixstring = ''
        if not os.path.exists(self.main_py_path):
            if self.sqlprefix is not None:
                if self.sqlprefix not in (True, False):
                    self.sqlprefix = "'%s'" % self.sqlprefix
                sqlprefixstring = "sqlprefix=%s,"%(self.sqlprefix)
            main_py_options = dict(comment=self.comment, sqlschema=self.sqlschema, sqlprefixstring=sqlprefixstring, name_short=self.name_short,
                                   name_long=self.name_long, name_full=self.name_full, login_url=self.login_url)
            main_py = open(self.main_py_path, 'w')
            main_py.write("""#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='%(comment)s',sqlschema='%(sqlschema)s',%(sqlprefixstring)s
                    name_short='%(name_short)s', name_long='%(name_long)s', name_full='%(name_full)s')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass
""" % main_py_options)
            main_py.close()

        if not os.path.exists(self.framedindex_path):
            with open(self.framedindex_path, 'w') as indexpage:
                indexpage.write("""# -*- coding: utf-8 -*-
            
class GnrCustomWebPage(object):
    py_requires = 'plainindex'
    """)
        if self.helloworld:
            with open(os.path.join(self.webpages_path,'hello_world.py'), 'w') as helloworld:
                helloworld.write("""# -*- coding: utf-8 -*-
            
class GnrCustomWebPage(object):
    def main_root(self,root,**kwargs):
        root.h1('Hello world',text_align='center')
    """)
            
class ResourceMaker(object):
    """Handle the creation of the ``resources`` folder"""
    def __init__(self, resource_name, base_path=None):
        self.resource_name = resource_name
        self.base_path = base_path or '.'
        
    def do(self):
        """TODO"""
        self.resource_path = os.path.join(self.base_path, self.resource_name)
        for path in (self.resource_path, ):
            if not os.path.isdir(path):
                os.mkdir(path)
        
class ThPackageResourceMaker(object):
    def __init__(self,application,package=None,tables=None,force=False,menu=False,columns=2,guess_size=False,indent=4, bag_columns=None):
        self.option_force = force
        self.option_menu = menu
        self.option_columns = columns
        self.option_guess_size = guess_size
        self.option_indent = indent
        self.pkg_tables = defaultdict(list)
        self.app = application 
        self.package = package
        self.bag_columns=bag_columns or dict(view=False, form=False)
        self.tables = tables if tables else list(self.app.db.packages[self.package].tables.keys()) 
        self.packageFolder = self.app.packages(package).packageFolder

    
    def makeResources(self):
        for table in self.tables:
            self.createResourceFile(table)
        if self.option_menu:
            self.makeMenu()

    def makeMenu(self):
        with open(os.path.join(self.packageFolder,'menu.py'),'w') as out_file:
            self.out_file = out_file
            self.writeHeaders()
            self.write('def config(root,application=None):')
            pkgobj =  self.app.db.package(self.package)
            self.write("%s = root.branch('%s')"%(self.package,(pkgobj.name_long or self.package.capitalize())),indent=1) 
            hasLookups = False
            for t in self.tables:
                tblobj = self.app.db.table('%s.%s' %(self.package,t))
                if tblobj.attributes.get('lookup'):
                    hasLookups = True
                else:
                    self.write("%s.thpage('%s',table='%s')" %(self.package,(tblobj.name_plural or tblobj.name_long or tblobj.name.capitalize()),
                            tblobj.fullname),indent=1)
            if hasLookups:
                self.write("%s.lookups('Lookup tables',lookup_manager='%s')" %(self.package,self.package),indent=1)


    def write(self,line=None, indent=0):
        line = line or ''
        self.out_file.write('%s%s\n'%(self.option_indent*indent*' ',line))

    def writeHeaders(self):
        self.write('#!/usr/bin/python3')
        self.write('# -*- coding: utf-8 -*-')
        self.write()
    
    def writeImports(self):
        self.write("from gnr.web.gnrbaseclasses import BaseComponent")
        self.write("from gnr.core.gnrdecorator import public_method")
        self.write()
    
    def writeViewClass(self, tblobj, columns):
        self.write("class View(BaseComponent):")
        self.write()
        self.write("def th_struct(self,struct):", indent=1)
        self.write('r = struct.view().rows()', indent=2)
        for column, size, dtype in columns:
            if self.option_guess_size:
                self.write("r.fieldcell('%s', width='%iem')"%(column,size), indent=2)
            else:
                self.write("r.fieldcell('%s')"%column, indent=2)
        self.write()
        self.write("def th_order(self):", indent=1)
        self.write("return '%s'"%columns[0][0], indent=2)
        self.write()
        self.write("def th_query(self):", indent=1)
        searchcol = tblobj.attributes.get('caption_field') 
        
        if not searchcol:
            l = [c for c in list(tblobj.columns.values()) if c.attributes.get('dtype') in ('A','T','C') and not c.attributes.get('_sysfield')]
            if l:
                searchcol = l[0].name
        self.write("return dict(column='%s', op='contains', val='')"%searchcol, indent=2)
        self.write()
        self.write()
        self.write()

    def writeFormClass(self, tblobj, columns):
        children = self.getChildrenRelations(tblobj)
        self.write("class Form(BaseComponent):")
        self.write()
        self.write("def th_form(self, form):", indent=1)
        if children:
            self.write("bc = form.center.borderContainer()", indent=2)
            self.write("top = bc.contentPane(region='top',datapath='.record')", indent=2)
            self.write("fb = top.formbuilder(cols=%i, border_spacing='4px')"%self.option_columns, indent=2)
            for column, size, dtype in columns:
                self.write("fb.field('%s')"%column, indent=2)
            if len(children)>1:
                self.write("tc = bc.tabContainer(region='center',margin='2px')", indent=2)
                for c in children:
                    self.write("tab_%s = tc.contentPane(title='%s')" %(c.replace('@',''),(tblobj.name_plural or tblobj.name_long)), indent=2)
                    self.write("tab_%s.dialogTableHandler(relation='%s')" %(c.replace('@',''),c), indent=2)
            else:
                self.write("center = bc.contentPane(region='center')", indent=2)
                self.write("center.plainTableHandler(relation='%s')" %children[0], indent=2)
        else:
            self.write("pane = form.record", indent=2)
            self.write("fb = pane.formbuilder(cols=%i, border_spacing='4px')"%self.option_columns, indent=2)
            for column, size, dtype in columns:
                tag=''
                if dtype=='X':
                    if isinstance( self.bag_columns['form'], basestring):
                        tag = ", tag='%s'" %  self.bag_columns['form'] 
                self.write("fb.field('%s' %s)"% (column, tag), indent=2)
                
        self.write()
        self.write()
        self.write("def th_options(self):", indent=1)
        self.write("return dict(dialog_height='400px', dialog_width='600px')", indent=2)


    def getChildrenRelations(self,tblobj):
        result = []
        for relation,j in tblobj.relations.digest('#k,#a.joiner'):
            if j and j['mode'] == 'M' and j.get('onDelete') == 'cascade':
                result.append(relation)
        return result

    def createResourceFile(self, table):
        resourceFolder = os.path.join(self.packageFolder,'resources', 'tables', table)
        if not os.path.exists(resourceFolder):
            os.makedirs(resourceFolder)
        name = 'th_%s.py'%table
        path = os.path.join(resourceFolder, name)
        if os.path.exists(path) and not self.option_force:
            print('%s exist: will be skipped, use -f/--force to force replace' % name)
            return
        view_columns=[]
        form_columns=[]
        max_size = 35
        tbl_obj =  self.app.db.table('%s.%s'%(self.package,table))
        for col_name,column in list(tbl_obj.columns.items()):
            dtype = column.dtype
            if column.attributes.get('_sysfield') or dtype =='O': 
                continue
            if column.dtype=='A':
                size = column.attributes.get('size','')
                if size:
                    if ':' in size:
                        size =size.split(':')[1]
                else:
                    size=max_size
                size = max(int(size),max_size)
            else:
                size = 7
            if dtype!='X' or self.bag_columns['view']:
                view_columns.append((column.name,size,dtype))
            if dtype!='X' or self.bag_columns['form']:
                form_columns.append((column.name,size,dtype))
            

        with open(path,'w') as out_file:
            self.out_file = out_file
            self.writeHeaders()
            self.writeImports()
            self.writeViewClass(tbl_obj, view_columns)
            self.writeFormClass(tbl_obj, form_columns)
            print('%s created' % name)

################################# DEPLOY CONF BUILDERS ################################

GUNICORN_DEFAULT_CONF_TEMPLATE ="""

bind = 'unix:%(gunicorn_socket_path)s'
pidfile = '%(pidfile_path)s'
daemon = False
accesslog = '%(logs_path)s/access.log'
errorlog = '%(logs_path)s/error.log'
logfile = '%(logs_path)s/main.log'
workers = %(workers)i
loglevel = 'error'
chdir = '%(chdir)s'
reload = False
capture_output = True
worker_class = 'gevent'
max_requests = %(max_requests)i
max_requests_jitter = %(max_requests_jitter)i
timeout = 1800
graceful_timeout = 600
"""


NGINX_TEMPLATE = """
map $http_x_forwarded_proto $real_scheme {
            default $http_x_forwarded_proto;
            ''      $scheme;
}
server {
        listen 80;

        server_name %(domain)s;

        root %(site_path)s;

        access_log %(logs_path)s/nginx_access.log;
        error_log %(logs_path)s/nginx_error.log;
        proxy_connect_timeout       1800;
	    proxy_send_timeout          1800;
	    proxy_read_timeout          1800;
	    send_timeout                1800;
        location /websocket {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-Proto $real_scheme;
            proxy_pass http://unix:%(gnrasync_socket_path)s;
        }
        %(supervisord_location)s
        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $real_scheme;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_pass http://unix:%(gunicorn_socket_path)s;
        }
}

"""


class GunicornDeployBuilder(object):
    default_port = 8080
    default_processes = 1
    default_threads = 8
    conf_template = GUNICORN_DEFAULT_CONF_TEMPLATE
    
    

    def __init__(self, site_name, **kwargs):
        self.site_name = site_name
        self.path_resolver = PathResolver()
        self.site_path = self.path_resolver.site_name_to_path(site_name)
        self.instance_path = self.path_resolver.instance_name_to_path(site_name)
        self.site_config = self.path_resolver.get_siteconfig(site_name)
        if os.path.exists(os.path.join(self.site_path,'siteconfig.xml')):
            self.config_folder = self.site_path #oldconfig
        else:
            self.config_folder = os.path.join(self.instance_path,'config')
        self.gnr_path = gnrConfigPath()
        self.supervisor_conf_path_py = os.path.join(self.gnr_path,'supervisord.py') 
        self.supervisor_conf_path_ini = os.path.join(self.gnr_path,'supervisord.conf')
        self.supervisor_log_path = os.path.join(self.gnr_path,'supervisord.log')
        self.supervisord_socket_path = os.path.join(self.gnr_path,'supervisord.sock')
        self.supervisord_monitor_parameters = self.path_resolver.gnr_config.getAttr('gnr.environment_xml.supervisord')
        self.bin_folder = os.path.join(os.environ.get('VIRTUAL_ENV'),'bin') if 'VIRTUAL_ENV' in  os.environ else ''
        self.socket_path = os.path.join(self.site_path, 'sockets')
        self.logs_path = os.path.join(self.site_path, 'logs')
        self.pidfile_path = os.path.join(self.site_path, '%s_pid' % site_name)
        self.gunicorn_conf_path = os.path.join(self.config_folder,'gunicorn.py')
        self.gnrasync_socket_path = os.path.join(self.socket_path, "async.tornado" )
        self.gunicorn_socket_path = os.path.join(self.socket_path,'gunicorn.sock')
        

        self.create_dirs()
        import multiprocessing
        self.default_workers = multiprocessing.cpu_count()* 2 + 1
        self.default_max_requests = 300
        self.default_max_requests_jitter = 50
        self.options = kwargs

    def create_dirs(self):
        for dir_path in (self.socket_path,self.logs_path):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def write_gunicorn_conf(self):
        pars = dict()
        opt = self.options
        pars['gunicorn_socket_path'] = self.gunicorn_socket_path
        pars['pidfile_path'] = self.site_name
        pars['workers'] = int(opt.get('workers') or self.default_workers)
        pars['pidfile_path'] = self.pidfile_path
        pars['site_path'] = self.site_path
        pars['logs_path'] = self.logs_path
        pars['max_requests'] = self.default_max_requests
        pars['max_requests_jitter'] = self.default_max_requests_jitter
        pars['chdir'] = self.site_path if os.path.exists(os.path.join(self.site_path,'root.py')) else self.instance_path
        conf_content = GUNICORN_DEFAULT_CONF_TEMPLATE %pars
        print('write gunicorn file',self.gunicorn_conf_path)
        with open(self.gunicorn_conf_path,'w') as conf_file:
            conf_file.write(conf_content)

    def local_supervisor_conf(self):
        root = IniConfStruct()
        supervisord = root.section(u"supervisord")
        supervisord.parameter("nodaemon",value="true")
        group = root.section('group',self.site_name)
        gunicorn = group.section('program','%s_gunicorn' %self.site_name)
        gunicorn.parameter('command','%s -c %s root' %(os.path.join(self.bin_folder,'gunicorn'),self.gunicorn_conf_path))
        gunicorn.parameter('stdout_logfile','/dev/stdout')
        gunicorn.parameter('stdout_logfile_maxbytes','0')
        gunicorn.parameter('stderr_logfile','/dev/stderr')
        gunicorn.parameter('stderr_logfile_maxbytes','0')

        gnrasync = group.section('program','%s_gnrasync' %self.site_name)
        gnrasync.parameter('command','%s %s' %(os.path.join(self.bin_folder,'gnrasync'),self.site_name))
        self.taskWorkersConf(group)
        root.toIniConf(os.path.join(self.config_folder,'supervisord.conf'))
    
    def taskWorkersConf(self,group):
        taskworkers = self.site_config.getAttr('taskworkers') or {'count':'1'}
        if taskworkers:
            tw_base = group.section('program','%s_taskworkers' %self.site_name)
            nice = taskworkers.pop('nice',None)
            nicecommand = 'nice' if nice is None else 'nice -%s' %nice
            tw_base.parameter('process_name',"%s_gnrtaskworker%%(process_num)s" %self.site_name)
            tw_base.parameter('command','%s %s %s' %(nicecommand,os.path.join(self.bin_folder,'gnrtaskworker'),self.site_name))
            reserved_workers = self.site_config['taskworkers']
            tw_base.parameter('numprocs',taskworkers.pop('count','1'))
            for key,val in taskworkers.items():
                key = key.split('_')[1]
                subnice = taskworkers.pop('nice_%s' %key,nice)
                subnicecommand = 'nice' if subnice is None else nicecommand
                tw =  group.section('program','%s_taskworkers_%s' %(self.site_name,key))
                tw.parameter('process_name',"%s_gnrtaskworker_%s_%%(process_num)s" %(self.site_name,key))
                tw.parameter('command','%s %s %s --code %s' %(subnicecommand,os.path.join(self.bin_folder,'gnrtaskworker'),self.site_name,key))
                tw.parameter('numprocs',val)


    def main_supervisor_conf(self):
        if os.path.isfile(self.supervisor_conf_path_py):
            root = IniConfStruct(self.supervisor_conf_path_py)
        else:
            root = IniConfStruct()
            supervisord = root.section(u"supervisord")
            supervisord.parameter("loglevel",value="error")
        root.pop(self.site_name)    
        root.pop('xmlrpcmonitor')
        root.pop('rpcinterface_supervisor')       
        group = root.section('group',self.site_name)
        gunicorn = group.section('program','%s_gunicorn' %self.site_name)
        gunicorn.parameter('command','%s -c %s root' %(os.path.join(self.bin_folder,'gunicorn'),self.gunicorn_conf_path))
        gnrasync = group.section('program','%s_gnrasync' %self.site_name)
        gnrasync.parameter('command','%s %s' %(os.path.join(self.bin_folder,'gnrasync'),self.site_name))
        self.taskWorkersConf(group)

        if self.supervisord_monitor_parameters:
            self.xmlRpcServerConf(root)
        root.toPython(self.supervisor_conf_path_py)
        root.toIniConf(self.supervisor_conf_path_ini)

    def xmlRpcServerConf(self,root):
        mp = self.supervisord_monitor_parameters
        if mp.get('port'):
            sec = root.section(u"inet_http_server",label='xmlrpcmonitor')
            sec.parameter("port",value='*:%(port)s' %mp)
            sec.parameter('username',value=mp['username'])
            sec.parameter('password',value=mp['password'])
        else:
            sec = root.section(u"unix_http_server",label='xmlrpcmonitor')
            sec.parameter("file",value=self.supervisord_socket_path)
            sec.parameter('chmod',value=mp.get('chmod','0777'))
            sec.parameter('chown',value=mp.get('chown','nobody:nogroup'))
            sec.parameter('username',value=mp['username'])
            sec.parameter('password',value=mp['password'])
        sec = root.section("rpcinterface",name='supervisor',label='rpcinterface_supervisor')
        sec.parameter('supervisor.rpcinterface_factory',value='supervisor.rpcinterface:make_main_rpcinterface')

    def supervisord_monitor_location(self):
        mp = self.supervisord_monitor_parameters
        if not mp or mp.get('port'):
            return ''
        
        return """
        location /supervisord {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-Proto $real_scheme;
            proxy_pass http://unix:%(supervisord_socket_path)s;
        }""" %{'supervisord_socket_path':self.supervisord_socket_path }


    def write_nginx_conf(self,domain=None):
        pars = {}
        pars['domain'] = domain
        pars['site_path'] = self.site_path
        pars['logs_path'] = self.logs_path
        pars['gnrasync_socket_path'] = self.gnrasync_socket_path
        pars['gunicorn_socket_path'] = self.gunicorn_socket_path
        pars['supervisord_location'] = self.supervisord_monitor_location()
        conf_content = NGINX_TEMPLATE %pars
        with open('%s.conf' %self.site_name,'w') as conf_file:
            conf_file.write(conf_content)
