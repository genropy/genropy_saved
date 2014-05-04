import os
import sys
from gnr.core.gnrbag import Bag
from gnr.core.gnrsys import expandpath
import random
import string

class GnrConfigException(Exception):
    pass

def get_config_path():
    if sys.platform == 'win32':
        config_path = '~\gnr'
    else:
        config_path = '~/.gnr'
    config_path  = expandpath(config_path)
    return config_path

def get_random_password(size = 12):
    return ''.join( random.Random().sample(string.letters+string.digits, size)).lower()


def build_environment_xml(path=None, gnrpy_path=None, gnrdaemon_password=None):
    genropy_home = os.path.dirname(gnrpy_path)
    genropy_projects = os.path.join(genropy_home,'projects')
    genropy_tutorial_projects = os.path.join(genropy_home,'tutorial','projects')
    genropy_packages = os.path.join(genropy_home,'packages')
    genropy_resources = os.path.join(genropy_home,'resources')
    genropy_webtools = os.path.join(genropy_home,'webtools')
    dojo_11_path = os.path.join(genropy_home, 'dojo_libs', 'dojo_11')
    gnr_d11_path = os.path.join(genropy_home,'gnrjs', 'gnr_d11')
    environment_bag = Bag()
    environment_bag.setItem('environment.gnrhome', None, dict(value=genropy_home))
    environment_bag.setItem('projects.genropy', None, dict(path=genropy_projects))
    environment_bag.setItem('projects.genropy_tutorial', None, dict(path=genropy_tutorial_projects))
    environment_bag.setItem('packages.genropy', None, dict(path=genropy_packages))
    environment_bag.setItem('static.js.dojo_11',None, dict(path=dojo_11_path, cdn=""))
    environment_bag.setItem('static.js.gnr_11', None, dict(path=gnr_d11_path))
    environment_bag.setItem('resources.genropy', None, dict(path=genropy_resources))
    environment_bag.setItem('webtools.genropy', None, dict(path=genropy_webtools))
    environment_bag.setItem('gnrdaemon', None, dict(host='localhost', port='40404', hmac_key=gnrdaemon_password))
    environment_bag.toXml(path,typevalue=False,pretty=True)

def build_instanceconfig_xml(path=None):
    instanceconfig_bag = Bag()
    instanceconfig_bag.setItem('packages',None)
    instanceconfig_bag.setItem('authentication.xml_auth',None, dict(defaultTags='user,xml'))
    password = get_random_password(size=6)
    instanceconfig_bag.setItem('authentication.xml_auth.admin',None, dict(pwd=password, tags='_DEV_,admin,user'))
    print "Default password for user admin is %s, you can change it by editing %s" %(password, path)
    instanceconfig_bag.toXml(path,typevalue=False,pretty=True)
    
def build_siteconfig_xml(path=None, gnrdaemon_password=None):
    siteconfig_bag = Bag()
    siteconfig_bag.setItem('wsgi', None, dict(debug=True, reload=True, port='8080'))
    siteconfig_bag.setItem('gui', None, dict(css_theme='ludo'))
    siteconfig_bag.setItem('jslib', None, dict(dojo_version='11', gnr_version='11'))
    siteconfig_bag.setItem('resources.common', None)
    siteconfig_bag.setItem('resources.js_libs', None)
    siteconfig_bag.setItem('gnrdaemon', None, dict(host='localhost', port='40404', hmac_key=gnrdaemon_password))
    siteconfig_bag.toXml(path,typevalue=False,pretty=True)

def create_folder(folder_path=None):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    elif not os.path.isdir(folder_path):
        raise GnrConfigException("A file named %s already exists so i couldn't create a folder at same path" % folder_path)

def check_file(xml_path=None):
    if os.path.exists(xml_path):
        raise GnrConfigException("A file named %s already exists so i couldn't create a config file at same path" % xml_path)

def initgenropy(gnrpy_path=None):
    if not gnrpy_path or not os.path.basename(gnrpy_path)=='gnrpy':
        raise GnrConfigException("You are not running this script inside a valid gnrpy folder")
    config_path  = get_config_path()
    instanceconfig_path = os.path.join(config_path,'instanceconfig')
    siteconfig_path = os.path.join(config_path,'siteconfig')
    for folder_path in (config_path, instanceconfig_path, siteconfig_path):
        create_folder(folder_path=folder_path)

    enviroment_xml_path = os.path.join(config_path,'environment.xml')
    default_instanceconfig_xml_path = os.path.join(instanceconfig_path,'default.xml')
    default_siteconfig_xml_path = os.path.join(siteconfig_path,'default.xml')

    for xml_path in (enviroment_xml_path, default_instanceconfig_xml_path, default_siteconfig_xml_path):
        check_file(xml_path=xml_path)

    gnrdaemon_password = get_random_password()

    build_environment_xml(path=enviroment_xml_path, gnrpy_path=gnrpy_path, gnrdaemon_password=gnrdaemon_password)
    build_instanceconfig_xml(path=default_instanceconfig_xml_path)
    build_siteconfig_xml(path=default_siteconfig_xml_path, gnrdaemon_password=gnrdaemon_password)



if __name__ == '__main__':
    initgenropy(gnrpy_path=os.getcwd())