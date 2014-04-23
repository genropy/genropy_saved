# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package       : GenroPy app - see LICENSE for details
# module gnrapp : Genro application architecture.
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import tempfile
import atexit
import logging
import shutil

import sys
import imp
import os
import hashlib
import re
import smtplib
import time
import glob
from email.MIMEText import MIMEText
from gnr.utils import ssmtplib
from gnr.app.gnrdeploy import PathResolver
from gnr.core.gnrclasses import GnrClassCatalog
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import getUuid


from gnr.core.gnrlang import  gnrImport, instanceMixin, GnrException
from gnr.core.gnrstring import makeSet, toText, splitAndStrip, like, boolean
from gnr.core.gnrsys import expandpath
from gnr.sql.gnrsql import GnrSqlDb

log = logging.getLogger(__name__)

class NullLoader(object):
    """TODO"""
    def load_module(self,fullname):
        """TODO
        
        :param fullname: TODO"""
        if fullname in sys.modules:
            return sys.modules[fullname]

class GnrModuleFinder(object):
    """TODO"""
    
    path_list=[]

    def __init__(self, path_entry, app):
        self.path_entry = path_entry
        self.app = app
        self.instance_lib = os.path.join(app.instanceFolder, 'lib')
        if not path_entry==self.instance_lib and not path_entry in self.path_list:
            raise ImportError
        return

    def __str__(self):
        return '<%s for "%s">' % (self.__class__.__name__, self.path_entry)

    def find_module(self, fullname, path=None):
        """TODO
        
        :param fullname: TODO
        :param path: TODO"""
        path = path or self.path_entry
        splitted=fullname.split('.')
        if splitted[0] == 'gnrpkg' and len(splitted)==1:
            if 'gnrpkg' in sys.modules:
                pkg_module=sys.modules['gnrpkg']
            else:
                pkg_module=imp.new_module('gnrpkg')
                sys.modules['gnrpkg']=pkg_module
                pkg_module.__file__ = None
                pkg_module.__name__ = 'gnrpkg'
                pkg_module.__path__ = [self.instance_lib]
                pkg_module.__loader__ = self
                pkg_module.__package__ = 'gnrpkg'
            return NullLoader()
        elif splitted[0] == 'gnrpkg' and len(splitted)==2:
            pkg = splitted[1]
            pkg_module = self._get_gnrpkg_module(pkg)
            if pkg_module:
                return NullLoader()
        elif splitted[0] == 'gnrpkg' and len(splitted)>2:
            pkg = splitted[1]
            mod_fullname='.'.join(splitted[2:])
            if pkg in self.app.packages:
                pkg_module = self._get_gnrpkg_module(pkg)
                mod_file,mod_pathname,mod_description=imp.find_module(mod_fullname, pkg_module.__path__)
                return GnrModuleLoader(mod_file,mod_pathname,mod_description)
        return None
        
    def _get_gnrpkg_module(self, pkg):
        gnrpkg = self.app.packages[pkg]
        gnrpkg_module_name= 'gnrpkg.%s'%pkg 
        if gnrpkg_module_name in sys.modules:
            pkg_module=sys.modules[gnrpkg_module_name]
        else:
            pkg_module=imp.new_module(gnrpkg_module_name)
            sys.modules[gnrpkg_module_name]=pkg_module
            if os.path.isdir(os.path.join(gnrpkg.customFolder,'lib')):
                module_path=[os.path.join(gnrpkg.customFolder,'lib')]
            else:
                module_path=[]
            module_path.append(os.path.join(gnrpkg.packageFolder,'lib'))
            pkg_module.__file__ = None
            pkg_module.__name__ = gnrpkg_module_name
            pkg_module.__path__ = module_path
            self.path_list.extend(module_path)
            pkg_module.__loader__ = self
            pkg_module.__package__ = 'gnrpkg'
        return pkg_module
            
class GnrModuleLoader(object):
    """TODO"""
    def __init__(self, file, pathname, description):
        self.file=file
        self.pathname=pathname
        self.description=description

    def load_module(self, fullname):
        """TODO"""
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            try:
                mod = imp.load_module(fullname,self.file, self.pathname, self.description)
                sys.modules[fullname]=mod
            finally:
                if self.file:
                    self.file.close()
        return mod

class GnrImportException(GnrException):
    """TODO"""
    pass

class GnrMixinObj(object):
    """TODO"""
    def __init__(self):
        pass

class GnrSqlAppDb(GnrSqlDb):
    """TODO"""
    def checkTransactionWritable(self, tblobj):
        """TODO
        
        :param tblobj: the :ref:`database table <table>` object"""
        if self.currentEnv.get('forced_transaction'):
            return
        if not hasattr(tblobj, '_usesTransaction'):
            tblobj._usesTransaction = boolean(
                    tblobj.attributes.get('transaction', tblobj.pkg.attributes.get('transaction', '')))
        if not self.inTransactionDaemon and tblobj._usesTransaction:
            raise GnrWriteInReservedTableError('%s.%s' % (tblobj.pkg.name, tblobj.name))

    def notifyDbUpdate(self,tblobj,recordOrPkey=None,**kwargs):
        if isinstance(recordOrPkey,list):
            records = recordOrPkey
        elif not recordOrPkey and kwargs:
            records = tblobj.query(**kwargs).fetch()
        else:
            broadcast = tblobj.attributes.get('broadcast')
            if broadcast is False:
                return
            if isinstance(recordOrPkey,basestring):
                if isinstance(broadcast,basestring):
                    records = [tblobj.record(pkey=recordOrPkey).output('dict')]
                else:
                    records = [{tblobj.pkey:recordOrPkey}]
            else:
                records = [recordOrPkey]
        for record in records:
            self.application.notifyDbEvent(tblobj, record, 'U')
        
    def delete(self, tblobj, record, **kwargs):
        """Delete a record in the database
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: the record to be deleted"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.delete(self, tblobj, record,**kwargs)
        if self.systemDbEvent():
            return
        self.application.notifyDbEvent(tblobj, record, 'D')
        
    def update(self, tblobj, record, old_record=None, pkey=None,**kwargs):
        """Update a record in the database
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: the new record
        :param old_record: the old record to be updated
        :param pkey: the record :ref:`primary key <pkey>`"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.update(self, tblobj, record, old_record=old_record, pkey=pkey,**kwargs)
        if self.systemDbEvent():
            return
        self.application.notifyDbEvent(tblobj, record, 'U', old_record)
        
    def insert(self, tblobj, record, **kwargs):
        """Insert a record in the database

        :param tblobj: the :ref:`database table <table>` object
        :param record: the record to be inserted"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.insert(self, tblobj, record,**kwargs)
        if self.systemDbEvent():
            return
        self.application.notifyDbEvent(tblobj, record, 'I')
       

    def raw_delete(self, tblobj, record, **kwargs):

        """Delete a record in the database
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: the record to be deleted"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.raw_delete(self, tblobj, record,**kwargs)
        if self.systemDbEvent():
            return
        self.application.notifyDbEvent(tblobj, record, 'D')
        
    def raw_update(self, tblobj, record, old_record=None,pkey=None,**kwargs):
        """Update a record in the database
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: the new record
        :param old_record: the old record to be updated
        :param pkey: the record :ref:`primary key <pkey>`"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.raw_update(self, tblobj, record, pkey=pkey,**kwargs)
        if self.systemDbEvent():
            return
        old_record = record or dict(record)
        self.application.notifyDbEvent(tblobj, record, 'U', old_record)
        
    def raw_insert(self, tblobj, record, **kwargs):
        """Insert a record in the database

        :param tblobj: the :ref:`database table <table>` object
        :param record: the record to be inserted"""
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.raw_insert(self, tblobj, record,**kwargs)
        if self.systemDbEvent():
            return
        self.application.notifyDbEvent(tblobj, record, 'I')

    def getResource(self, tblobj, path):
        """TODO

        :param tblobj: the :ref:`database table <table>` object
        :param path: TODO"""
        app = self.application
        resource = app.site.loadResource(tblobj.pkg.name, 'tables', tblobj.name, path)
        resource.site = app.site
        resource.table = tblobj
        resource.db = self
        return resource
    
    def onDbCommitted(self):
        """TODO"""
        self.application.onDbCommitted()
        
    def getFromStore(self, path, dflt):
        """TODO
        
        :param path: TODO
        :param dflt: TODO"""
        return self.currentPage.pageStore().getItem(path,dflt)
        
    @property
    def currentPage(self):
        return self.application.site.currentPage if hasattr(self.application,'site') else None

    @property
    def currentUser(self):
        return self.currentEnv.get('user') or (self.currentPage and self.currentPage.user)

    def localVirtualColumns(self,table):
        page = self.currentPage
        if not page:
            return
        maintable = getattr(page,'maintable',None)
        result = Bag()
        fmethods = [v for v in [getattr(page,k) for k in dir(page) if k.startswith('formulacolumn_')]]
        for f in fmethods:
            fckw = dict(f.formulaColumn_kw)
            ftable = fckw.get('table',maintable)
            if ftable == table:
                r = f()
                if isinstance(r,list):
                    for c in r:
                        kw = dict(fckw)
                        kw.update(c)
                        result.setItem(kw.pop('name'),None,**kw)
                else:
                    fckw['sql_formula'] = r
                    result.setItem(fckw.pop('name'),None,**fckw)
        return result

    def customVirtualColumns(self,table):
        if self.package('adm') and table!='adm.userobject':
            userobject = self.table('adm.userobject')
            pkg,tbl = table.split('.')
            f = userobject.query(where='$tbl=:t AND objtype=:fc',t=table,fc='formulacolumn',bagFields=True).fetch()
            result = Bag()

            for r in f:
                b = Bag(r['data'])
                kw = b.asDict(ascii=True)
                kw['name_long'] = r['description']
                result.setItem(b.pop('fieldname'),None,**kw)
            return result



class GnrPackagePlugin(object):
    """TODO"""
    def __init__(self, pkg, path):
        self.pkg = pkg
        self.application = self.pkg.application
        plugin_id = os.path.basename(path)
        self.id = plugin_id
        self.path = path
        self.pluginFolder=path
        model_path = os.path.join(self.pluginFolder,'model')
        self.model_path = model_path if os.path.isdir(model_path) else ''
        resources_path = os.path.join(self.pluginFolder,'resources')
        self.resources_path = resources_path if os.path.isdir(resources_path) else ''
        webpages_path = os.path.join(self.pluginFolder,'webpages')
        self.webpages_path = webpages_path if os.path.isdir(webpages_path) else ''
        config_path = os.path.join(self.pluginFolder,'config.xml')
        menu_path = os.path.join(self.pluginFolder,'menu.xml')
        self.menuBag = Bag(menu_path) if os.path.isfile(menu_path) else Bag()
        self.config = Bag(config_path) if os.path.isfile(config_path) else Bag()
        self.application.config['package_plugins.%s.%s'%(pkg.id,self.id)]=self.config
        
class GnrPackage(object):
    """TODO"""
    def __init__(self, pkg_id, application, path=None, filename=None, **pkgattrs):
        self.id = pkg_id
        filename = filename or pkg_id
        self.application = application
        self.packageFolder = os.path.join(path, filename)
        self.libPath = os.path.join(self.packageFolder, 'lib')
        sys.path.append(self.libPath)
        self.attributes = {}
        self.tableMixins = {}
        self.plugins = {}
        self.loadPlugins()
        self.customFolder = os.path.join(self.application.instanceFolder, 'custom', pkg_id)
        try:
            self.main_module = gnrImport(os.path.join(self.packageFolder, 'main.py'),avoidDup=True)
        except Exception, e:
            log.exception(e)
            raise GnrImportException(
                    "Cannot import package %s from %s" % (pkg_id, os.path.join(self.packageFolder, 'main.py')))
        try:
            menupath = os.path.join(self.packageFolder, 'menu.xml')
            self.pkgMenu = Bag(menupath) if os.path.isfile(menupath) else Bag()
            for pluginname,plugin in self.plugins.items():
                self.pkgMenu.update(plugin.menuBag)
        except:
            self.pkgMenu = Bag()
        
        self.pkgMixin = GnrMixinObj()
        instanceMixin(self.pkgMixin, getattr(self.main_module, 'Package', None))
        
        self.baseTableMixinCls = getattr(self.main_module, 'Table', None)
        self.baseTableMixinClsCustom = None
        
        self.webPageMixin = getattr(self.main_module, 'WebPage', None)
        self.webPageMixinCustom = None
        
        self.attributes.update(self.pkgMixin.config_attributes())
        custom_mixin = os.path.join(self.customFolder, 'custom.py')
        self.custom_module = None
        if os.path.isfile(custom_mixin):
            self.custom_module = gnrImport(custom_mixin,avoidDup=True, silent=False)
            instanceMixin(self.pkgMixin, getattr(self.custom_module, 'Package', None))
        
            self.attributes.update(self.pkgMixin.config_attributes())
            self.webPageMixinCustom = getattr(self.custom_module, 'WebPage', None)
            self.baseTableMixinClsCustom = getattr(self.custom_module, 'Table', None)
        
        instanceMixin(self, self.pkgMixin)
        self.attributes.update(pkgattrs)
        
    def initTableMixinDict(self):
        self.tableMixinDict = {}
        modelFolder = os.path.join(self.packageFolder, 'model')
        self.loadTableMixinDict(self.main_module, modelFolder)
        for pkgid, apppkg in self.application.packages.items():
            externalPkgModelFolder = os.path.join(apppkg.packageFolder,'model','_packages',self.id)
            self.loadTableMixinDict(self.main_module, externalPkgModelFolder, fromPkg=pkgid)
        for plugin in self.getPlugins():
            pluginModelFolder = os.path.join(plugin.path, 'model')
            self.loadTableMixinDict(self.main_module, pluginModelFolder, pluginId=plugin.id)
        if os.path.isdir(self.customFolder):
            customModelFolder = os.path.join(self.customFolder, 'model')
            self.loadTableMixinDict(self.custom_module, customModelFolder, model_prefix='custom_')
        self.configure()
        
    @property
    def db(self):
        return self.application.db
    
    def loadPlugins(self):
        """TODO"""
        plugin_folders=glob.glob(os.path.join(self.application.pluginFolder,self.id,'*'))
        for plugin_folder in plugin_folders:
            plugin = GnrPackagePlugin(self, plugin_folder)
            self.plugins[plugin.id] = plugin
        
    def getPlugins(self):
        """TODO"""
        return self.plugins.values()
    
    def loadTableMixinDict(self, module, modelfolder, model_prefix='', pluginId=None, fromPkg=None):
        """TODO
        
        :param module: TODO
        :param modelfolder: TODO
        :param model_prefix: TODO"""
        tbldict = {}
        if module:
            tbldict = dict([(x[6:], getattr(module, x)) for x in dir(module) if x.startswith('Table_')])
        #modelfolder=os.path.join(folder,'model')
        
        if os.path.isdir(modelfolder):
            tbldict.update(dict([(x[:-3], None) for x in os.listdir(modelfolder) if x.endswith('.py')]))
        tblkeys = tbldict.keys()
        tblkeys.sort()
        for tbl in tblkeys:
            cls = tbldict[tbl]
            if not tbl in self.tableMixinDict:
                self.tableMixinDict[tbl] = GnrMixinObj()
                instanceMixin(self.tableMixinDict[tbl], self.baseTableMixinCls)
                instanceMixin(self.tableMixinDict[tbl], self.baseTableMixinClsCustom)
            if not cls:
                tbl_module = gnrImport(os.path.join(modelfolder, '%s.py' % tbl),
                                       avoidDup=True, silent=False)
                tbl_cls = getattr(tbl_module, 'Table', None)
                if not fromPkg:
                    instanceMixin(self.tableMixinDict[tbl], tbl_cls)
                else:
                    instanceMixin(self.tableMixinDict[tbl], tbl_cls, methods='config_db,trigger_*', suffix='%s'%fromPkg)
                    instanceMixin(self.tableMixinDict[tbl], tbl_cls, exclude='config_db,trigger_*')
                
                self.tableMixinDict[tbl]._plugins = dict()
                #self.tableMixinDict[tbl]._filename = tbl
                # mbertoldi commented out the following two lines as they are useless
                #for cname in dir(tbl_module):
                #    member = getattr(tbl_module, cname, None)
            else:
                if not fromPkg:
                    instanceMixin(self.tableMixinDict[tbl], cls)
            if pluginId:
                setattr(self.tableMixinDict[tbl],'_pluginId',pluginId)
                
    def config_attributes(self):
        """Return an empty dict. You can fill it with the following keys:
        
        * ``sqlschema`` includes a string with the name of the database schema.
        
          .. note:: we suggest you to call with the same name both the schema and the
                    package. For more information, check the
                    :ref:`introduction to a package <packages_introduction>`.
                    
        * ``comment`` includes a comment string.
        * ``name_short`` includes a string of the :ref:`name_short` of the schema.
        * ``name_long`` includes a string of the :ref:`name_long` of the schema.
        * ``name_plural`` includes a string of the :ref:`name_plural` of the schema.
        
        If you follow the instructions of the :ref:`project_autocreation` documentation section,
        you will find your :ref:`packages_main` file with the ``config_attributes`` method filled
        as the following one::
        
            def config_attributes(self):
                return dict(comment='packageName',sqlschema='packageName',
                            name_short='packageName', name_long='packageName', name_full='packageName')
                            
        where ``packageName`` is the name of your package (as you can see, by default your schema will
        be called with the same name of your package)"""
        return {}
        
    def onAuthentication(self, avatar):
        """Hook after authentication: receive the avatar and can add information to it
        
        :param avatar: the avatar (user that logs in)"""
        pass
        
    def configure(self):
        """Build db structure in this order:
        
        * package config_db.xml
        * custom package config_db.xml
        * customized Table objects (method config_db)
        * customized Table objects (method config_db_custom)
        * customized Package objects (method config_db)
        * customized Package objects (method config_db_custom)
        """
        struct = self.application.db.model.src
        struct.package(self.id, **self.attributes)
        
        config_db_xml = os.path.join(self.packageFolder, 'model', 'config_db.xml')
        if os.path.isfile(config_db_xml):
            if hasattr(self, '_structFix4D'):
                config_db_xml = self._structFix4D(struct, config_db_xml)
            struct.update(config_db_xml)
        
        config_db_xml = os.path.join(self.customFolder, 'model', 'config_db.xml')
        if os.path.isfile(config_db_xml):
            if hasattr(self, '_structFix4D'):
                config_db_xml = self._structFix4D(struct, config_db_xml)
            struct.update(config_db_xml)
        
    def onApplicationInited(self):
        """TODO"""
        pass  

    def envPreferences(self):
        "key:preference path, value:path inside dbenv"
        return {}        


class GnrApp(object):
    """Opens a GenroPy application :ref:`instance <instances>`
    
    :param instanceFolder: instance folder or name
    :param custom_config:  a :ref:`bag` or dictionary that will override configuration value
    :param forTesting:  if ``False``, setup the application normally.
                        if ``True``, setup the application for testing with a temporary sqlite database.
                        If it's a bag, setup the application for testing and import test data from this bag.
                        (see :meth:`loadTestingData()`)
    
    If you want to interact with a Genro instance from your own python script, you can use this class directly.
    
    Example:
    
    >>> testgarden = GnrApp('testgarden')
    >>> testgarden.db.table('showcase.person').query().count()
    12"""
    def __init__(self, instanceFolder=None, custom_config=None, forTesting=False, 
                debug=False, restorepath=None,**kwargs):
        self.aux_instances = {}
        self.gnr_config = self.load_gnr_config()
        self.debug=debug
        self.set_environment()
        self.remote_db = None
        if instanceFolder:
            if ':' in instanceFolder:
                instanceFolder,self.remote_db  = instanceFolder.split(':',1)

            if not os.path.isdir(instanceFolder):
                instanceFolder = self.instance_name_to_path(instanceFolder)
        self.instanceFolder = instanceFolder or ''
        sys.path.append(os.path.join(self.instanceFolder, 'lib'))
        sys.path_hooks.append(self.get_modulefinder)
        self.pluginFolder = os.path.normpath(os.path.join(self.instanceFolder, 'plugin'))
        self.kwargs = kwargs
        self.packages = Bag()
        self.packagesIdByPath = {}
        self.config = self.load_instance_config()
        self.instanceMenu = self.load_instance_menu()

        self.build_package_path()
        db_settings_path = os.path.join(self.instanceFolder, 'dbsettings.xml')

        if os.path.isfile(db_settings_path):
            db_credential = Bag(db_settings_path)
            self.config.update(db_credential)
        if custom_config:
            self.config.update(custom_config)
        if self.remote_db:
            remote_db_node = self.config.getNode('remote_db.%s' %self.remote_db)
            remotedbattr = remote_db_node.attr
            if remotedbattr and 'ssh_host' in remotedbattr:
                db_node = self.config.getNode('db')
                sshattr = dict(db_node.attr)
                sshattr.update(remotedbattr)
                sshattr['forwarded_port'] = sshattr.pop('port',None)
                db_node.attr['port'] = self.gnrdaemon.sshtunnel_port(**sshattr)
        if not 'menu' in self.config:
            self.config['menu'] = Bag()
            #------ application instance customization-------
        self.customFolder = os.path.join(self.instanceFolder, 'custom')
        self.dataFolder = os.path.join(self.instanceFolder, 'data')
        self.webPageCustom = None
        if os.path.isfile(os.path.join(self.customFolder, 'custom.py')):
            self.main_module = gnrImport(os.path.join(self.customFolder, 'custom.py'),avoidDup=True, silent=False)
            instanceMixin(self, getattr(self.main_module, 'Application', None))
            self.webPageCustom = getattr(self.main_module, 'WebPage', None)
        self.init(forTesting=forTesting,restorepath=restorepath)
        self.creationTime = time.time()
        
    def get_modulefinder(self, path_entry):
        """TODO"""
        return GnrModuleFinder(path_entry,self)
        
    def set_environment(self):
        """TODO"""
        environment_xml = self.gnr_config['gnr.environment_xml']
        if environment_xml:
            for var, value in environment_xml.digest('environment:#k,#a.value'):
                var = var.upper()
                if not os.getenv(var):
                    os.environ[var] = str(value)
                    
    def load_gnr_config(self):
        """TODO"""
        if os.environ.has_key('VIRTUAL_ENV'):
            config_path = expandpath(os.path.join(os.environ['VIRTUAL_ENV'],'etc','gnr'))
            if os.path.isdir(config_path):
                return Bag(config_path)
            else:
                log.warn('Missing genro configuration in %s', config_path)
                return Bag()
        if sys.platform == 'win32':
            config_path = '~\gnr'
        else:
            config_path = '~/.gnr'
        config_path = expandpath(config_path)
        if os.path.isdir(config_path):
            return Bag(config_path)
        config_path = expandpath('/etc/gnr')
        if os.path.isdir(config_path):
            return Bag(config_path)
        log.warn('Missing genro configuration')
        return Bag()
        
    def load_instance_menu(self):
        """TODO"""
        instance_menu_path = os.path.join(self.instanceFolder, 'menu.xml')
        if os.path.exists(instance_menu_path):
            return Bag(instance_menu_path)

    def load_instance_config(self):
        """TODO"""
        if not self.instanceFolder:
            return Bag()
        instance_config_path = os.path.join(self.instanceFolder, 'instanceconfig.xml')
        base_instance_config = Bag(instance_config_path)
        instance_config = self.gnr_config['gnr.instanceconfig.default_xml'] or Bag()
        template = base_instance_config['instance?template']
        if template:
            instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % template] or Bag())
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            for path, instance_template in self.gnr_config.digest(
                    'gnr.environment_xml.instances:#a.path,#a.instance_template') or []:
                if path == os.path.dirname(self.instanceFolder):
                    instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % instance_template] or Bag())
        instance_config.update(base_instance_config)
        return instance_config
        
    def init(self, forTesting=False,restorepath=None):
        """Initiate a :class:`GnrApp`
        
        :param forTesting:  if ``False``, setup the application normally.
                            if ``True``, setup the application for testing with a temporary sqlite database.
                            If it's a :ref:`bag`, setup the application for testing and import test data from this bag.
                            (see :meth:`loadTestingData()`)"""
        self.onIniting()
        self.base_lang = self.config['i18n?base_lang'] or 'en'
        self.catalog = GnrClassCatalog()
        self.localization = {}
        if not forTesting:
            dbattrs = self.config.getAttr('db') or {}
            
            if self.remote_db:
                dbattrs.update(self.config.getAttr('remote_db.%s' %self.remote_db))
            if dbattrs and dbattrs.get('implementation') == 'sqlite':
                dbattrs['dbname'] = self.realPath(dbattrs.pop('filename'))
        else:
            # Setup for testing with a temporary sqlite database
            tempdir = tempfile.mkdtemp()
            dbattrs = {}
            dbattrs['implementation'] = 'sqlite'
            dbattrs['dbname'] = os.path.join(tempdir, 'testing')
            # We have to use a directory, because genro sqlite adapter will creare a sqlite file for each package
                
            logging.info('Testing database dir: %s', tempdir)
            
            @atexit.register
            def removeTemporaryDirectory():
                shutil.rmtree(tempdir)
                
        dbattrs['in_to_any'] = boolean(dbattrs.get('in_to_any',False))
        dbattrs['application'] = self
        self.db = GnrSqlAppDb(debugger=getattr(self, 'debugger', None), **dbattrs)
        
        pkgMenus = self.config['menu?package'] or []
        if pkgMenus:
            pkgMenus = pkgMenus.split(',')
        for pkgid, attrs in self.config['packages'].digest('#k,#a'):
            pkgid = attrs.get('pkgcode',None) or pkgid
            if ':' in pkgid:
                project,pkgid=pkgid.split(':')
            else:
                project=None
            if not attrs.get('path'):
                attrs['path'] = self.pkg_name_to_path(pkgid,project)
            if not os.path.isabs(attrs['path']):
                attrs['path'] = self.realPath(attrs['path'])
            apppkg = GnrPackage(pkgid, self, **attrs)
            self.packagesIdByPath[os.path.realpath(apppkg.packageFolder)] = pkgid
            self.packages[pkgid] = apppkg

        for pkgid, apppkg in self.packages.items():
            apppkg.initTableMixinDict()
            if apppkg.pkgMenu and (not pkgMenus or pkgid in pkgMenus):
                #self.config['menu.%s' %pkgid] = apppkg.pkgMenu
                if len(apppkg.pkgMenu) == 1:
                    self.config['menu.%s' % pkgid] = apppkg.pkgMenu.getNode('#0')
                else:
                    self.config.setItem('menu.%s' % pkgid, apppkg.pkgMenu,
                                        {'label': apppkg.config_attributes().get('name_long', pkgid),'pkg_menu':pkgid})


            self.db.packageMixin('%s' % (pkgid), apppkg.pkgMixin)
            for tblname, mixobj in apppkg.tableMixinDict.items():
                self.db.tableMixin('%s.%s' % (pkgid, tblname), mixobj)

        self.db.inTransactionDaemon = False
        self.pkgBroadcast('onDbStarting')
        self.db.startup(restorepath=restorepath)
        if len(self.config['menu']) == 1:
            self.config['menu'] = self.config['menu']['#0']
        if self.instanceMenu:
            self.config['menu']=self.instanceMenu

        self.buildLocalization()
        if forTesting:
            # Create tables in temporary database
            self.db.model.check(applyChanges=True)
                
            if isinstance(forTesting, Bag):
                self.loadTestingData(forTesting)
        self.onInited()
            

    def importFromSourceInstance(self,source_instance=None):
        to_import = ''
        if ':' in source_instance:
            source_instance,to_import = source_instance.split(':')
        source_instance = GnrApp(source_instance)
        to_import = source_instance.db.packages.keys() if not to_import else to_import.split(',')
        set_to_import = set()
        while to_import:
            k = to_import.pop(0)
            if k == '*':
                to_import[:] = source_instance.db.packages.keys()+to_import
            elif  '.' in k:
                if not k.startswith('!'):
                    set_to_import.add(k)
                else:
                    set_to_import.remove(k[1:])
            else:
                if not k.startswith('!'):
                    set_to_import = set_to_import.union(set([t.fullname for t in source_instance.db.packages[k].tables.values()]))
                else:
                    set_to_import = set_to_import.difference(set([t.fullname for t in source_instance.db.packages[k[1:]].tables.values()]))
        
        imported_tables = set([t for t in set_to_import if self.db.table(t).countRecords()>0])
        set_to_import = set_to_import.difference(imported_tables)
        tables_to_import = list(set_to_import)
        while tables_to_import:
            tbl = tables_to_import.pop(0)
            dest_tbl = self.db.table(tbl).model
            src_tbl = source_instance.db.table(tbl).model
            dependencies=[('.'.join(n.value.split('.')[:-1]) , n.attr.get('deferred'))  for n in dest_tbl.relations_one if n.label in src_tbl.relations_one] 
            dependencies= set([t for t,d in dependencies if t!=dest_tbl.fullname and not( d and t in tables_to_import )])
            if dependencies.issubset(imported_tables):
                print '\nIMPORTING',tbl
                dest_tbl.dbtable.importFromAuxInstance(source_instance, empty_before=False,raw_insert=True)
                print '\nSTILL TO IMPORT',tables_to_import
                imported_tables.add(tbl)
            else:
                print '\nCANT IMPORT',tbl,dependencies.difference(imported_tables)
                tables_to_import.append(tbl)
        

    def loadTestingData(self, bag):
        """Load data used for testing in the database.
        
        Called by the constructor when you pass a :ref:`bag` into the *forTesting* parameter
        
        :param bag: a :ref:`bag` your test data
        
        Use this format in your test data::
        
            <?xml version="1.0" encoding="UTF-8"?>
            <GenRoBag>
                <table name="package.table">
                    <some_name>
                        <field1>ABCDEFG</field2>
                        <field2>1235</field2>
                        <!-- ... more fields ... -->
                    </some_name>
                    <!-- ... more records ... -->
                </table>
                <!-- ... more tables ... -->
            </GenRoBag>"""
        for table_name, records in bag.digest('#a.name,#v'):
            tbl = self.db.table(table_name)
            for r in records.values():
                tbl.insert(r)
        self.db.commit()

    def instance_name_to_path(self, instance_name):
        """TODO

        :param instance_name: the name of the :ref:`instance <instances>`"""
        return PathResolver(gnr_config=self.gnr_config).instance_name_to_path(instance_name)

    def build_package_path(self):
        """Build the path of the :ref:`package <packages>`"""
        self.package_path = {}
        path_list = []
        project_packages_path = os.path.normpath(os.path.join(self.instanceFolder, '..', '..', 'packages'))
        if os.path.isdir(project_packages_path):
            path_list.append(project_packages_path)
        if 'packages' in self.gnr_config['gnr.environment_xml']:
            path_list.extend(
                    [expandpath(path) for path in self.gnr_config['gnr.environment_xml'].digest('packages:#a.path') if
                     os.path.isdir(expandpath(path))])
        for path in path_list:
            for package in os.listdir(path):
                if package not in self.package_path and os.path.isdir(os.path.join(path, package)):
                    self.package_path[package] = path

    def pkg_name_to_path(self, pkgid, project=None):
        """TODO
        
        :param pkgid: the id of the :ref:`package <packages>`
        :param project: TODO"""
        path = None
        if project:
            project_path = self.project_path(project)
            if project_path:
                path = os.path.join(project_path,'packages')
                if not os.path.isdir(os.path.join(path, pkgid)):
                    path=None
        else:
            path = self.package_path.get(pkgid)
            
        if path:
            return path
        else:
            raise Exception(
                    'Error: package %s not found' % pkgid)
        
    def project_path(self, project):
        """TODO
        
        :param project: TODO"""
        for project_path in self.gnr_config['gnr.environment_xml.projects'].digest('#a.path'):
            path = expandpath(project_path) 
            if os.path.isdir(path) and project in os.listdir(path):
                return os.path.join(path,project)

    def onIniting(self):
        """Hook method called before the :ref:`instance <instances>` initialization"""
        pass

    def onInited(self):
        """Hook method called after the instance initialization is complete.
        
        By default, it will call the :meth:`onApplicationInited()
        <gnr.app.gnrapp.GnrPackage.onApplicationInited>` method of each package"""
        self.pkgBroadcast('onApplicationInited')
    
    def pkgBroadcast(self,method,*args,**kwargs):
        for pkg in self.packages.values():
            handler = getattr(pkg,method,None)
            if handler:
                handler(*args,**kwargs)
        

    def buildLocalization(self):
        """TODO"""
        self.localization = {}
        for pkg in self.packages.values():
            try:
                pkgloc = Bag(os.path.join(pkg.packageFolder, 'localization.xml'))
            except:
                pkgloc = Bag()
            try:
                customLoc = Bag(os.path.join(pkg.customFolder, 'localization.xml'))
            except:
                customLoc = Bag()
            pkgloc.update(customLoc)

            self.localization.update(self._compileLocalization(pkgloc, pkgname=pkg.id))
        self.localizationTime = time.time()
        
    def _compileLocalization(self, locbag, pkgname=None):
        loc = {}
        for attrs in locbag.digest('#a'):
            _key = attrs.get('_key')
            if _key:
                if pkgname: _key = '%s|%s' % (pkgname, _key.lower())
                loc[_key] = dict([(k, v) for k, v in attrs.items() if not k.startswith('_')])
        return loc
        
    def updateLocalization(self, pkg, data, locale):
        """TODO

        :param pkg: the :ref:`package <packages>` object
        :param data: TODO
        :param locale: the current locale (e.g: en, en_us, it)"""
        pkgobj = self.packages[pkg]
        locpath = os.path.join(pkgobj.packageFolder, 'localization.xml')
        pkglocbag = Bag(locpath)
        for k, v in data.digest('#v.key,#v.txt'):
            lbl = re.sub('\W', '_', k).replace('__', '_')
            if not lbl in pkglocbag:
                pkglocbag.setItem(lbl, None, _key=k, it=k, en='', fr='', de='')
            pkglocbag.setAttr(lbl, {locale: v})
        pkglocbag.toXml(os.path.join(pkgobj.packageFolder, 'localization.xml'))
    
    def localizeText(self, txt,pkg=None,localelang=None):
        """Translate the *txt* string following the browser's locale
        
        :param txt: the text to be translated"""
        loc = None
        txtlower = txt.lower()
        if pkg:
            key = '%s|%s' % (pkg, txtlower)
            loc = self.localization.get(key)
        if not loc:
            loc = self.localization.get(txtlower)
        if loc:
            loctxt = loc.get(localelang)
            if loctxt:
                txt = loctxt
        return txt
    

    def getResource(self, path, pkg=None, locale=None):
        """TODO

        :param path: TODO
        :param pkg: the :ref:`package <packages>` object
        :param locale: the current locale (e.g: en, en_us, it)"""
        if not pkg:
            pkg = self.config.getAttr('packages', 'default')
        return self.packages[pkg].getResource(path, locale=locale)
        
    def guestLogin(self):
        """TODO"""
        return self.config.getAttr('authentication', 'guestName')
        
    def authPackage(self):
        """TODO"""
        return self.packages[self.config.getAttr('authentication', 'pkg')]
        
    def getAvatar(self, user, password=None, authenticate=False, page=None, **kwargs):
        """TODO

        :param user: MANDATORY. The guest username
        :param password: the username's password
        :param authenticate: boolean. If ``True``, to enter in the application a password is required
        :param page: TODO"""
        if user:
            authmethods = self.config['authentication']
            if authmethods:
                for node in self.config['authentication'].nodes:
                    authmode = node.label.replace('_auth', '')
                    avatar = getattr(self, 'auth_%s' % authmode)(node, user, password=password,
                                                                 authenticate=authenticate,
                                                                 **kwargs)
                                                                             
                    if not (avatar is None):
                        avatar.page = page
                        avatar.authmode = authmode
                        self.pkgBroadcast('onAuthentication',avatar)
                        return avatar
                        
    def auth_xml(self, node, user, password=None, authenticate=False, **kwargs):
        """Authentication from :ref:`instances_instanceconfig` - use it during development
        or for sysadmin tasks.
        
        For more information, check the :ref:`instanceconfig_xml_auth` section
        
        :param node: MANDATORY. The :ref:`bagnode`
        :param user: the username
        :param password: the password
        :param authenticate: boolean. If ``True``, to enter in the application a password is required"""
        defaultTags = node.getAttr('defaultTags')
        path = node.getAttr('path')
        if path:
            users = Bag(self.realPath(path))
        else:
            users = node.getValue()
        if not users:
            return
        for key, attrs in users.digest('#k,#a'):
            if key == user:
                user_name = attrs.pop('user_name', key)
                user_id = attrs.pop('user_id', key)
                kw = dict(attrs)
                kw.update(kwargs)
                return self.makeAvatar(user=user, user_name=user_name, user_id=user_id,
                                       login_pwd=password, authenticate=authenticate,
                                       defaultTags=defaultTags, **kw)
                                       
    def auth_py(self, node, user, password=None, authenticate=False,tags=None, **kwargs):
        """Python authentication. This is mostly used to register new users for the first time. (see ``adm`` package).
        
        In file instanceconfig.xml insert a tag like::
        
            <py_auth  defaultTags='myusers' pkg='mypkg' method='myauthmethod' />
        
        ``mypkg.myauthmethod`` will be called with a single parameter, the username. It should return:
        
        * ``None``, if the user doesn't exists
        * a dict containing every attribute to add to the avatar, if the user is valid
        
        More information in the :ref:`instanceconfig_py_auth` section
        
        :param node: the :ref:`bagnode`
        :param user: the username
        :param password: the password
        :param authenticate: boolean. If ``True``, to enter in the application a password is required
        
        **TODO:** it seems odd that we don't pass the password to the authentication method. It limits the appicability
                  of this authentication method soo much!"""
        defaultTags = node.getAttr('defaultTags')
        attrs = dict(node.getAttr())
        pkg = attrs.get('pkg')
        if pkg:
            handler = getattr(self.packages[pkg], attrs['method'])
        else:
            handler = getattr(self, attrs['method'])
        if handler:
            result = handler(user, **kwargs)
        if result:
            user_name = result.pop('user_name', user)
            user_id = result.pop('user_id', user)
            user_record_tags = result.pop('tags', user)
            if not tags:
                tags = user_record_tags
            elif user_record_tags:
                tags = tags.split(',')
                tags.extend(user_record_tags.split(','))
                tags = ','.join(list(set(tags)))
            return self.makeAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags,
                                   login_pwd=password, authenticate=authenticate,
                                   defaultTags=defaultTags, **result)
                                   
    def auth_sql(self, node, user, password=None, authenticate=False, **kwargs):
        """Authentication from database.
        
        In the :ref:`instances_instanceconfig` file insert a tag like::
        
           <sql_auth defaultTags='myusers' dbtable='mypkg.users' 
                     username='username_fld' pwd='pwd_fld' userid='optional_id_fld' />
        
        where:
        
        * dbtable, username and pwd are mandatory attributes
        * Optional attributes: defaultTags, userid (the primary key of the db table if it is not the username field)
        
        Other attributes are aliases of dbfield names: myavatarfield='mydbfield'
        
        :param node: the :ref:`bagnode`
        :param user: the username
        :param password: the password
        :param authenticate: boolean. If ``True``, to enter in the application a password is required"""
        attrs = dict(node.getAttr())
        defaultTags = attrs.pop('defaultTags', None)
        kwargs = {}
        kwargs[str(attrs['username'])] = user
        dbtable = attrs.pop('dbtable')
        try:
            tblobj = self.db.table(dbtable)
            rec = tblobj.record(**kwargs).output('bag')
            result = dict([(str(k), rec[v]) for k, v in attrs.items()])
            user_name = result.pop('user_name', user)
            user_id = result[tblobj.pkey]
            return self.makeAvatar(user=user, user_name=user_name, user_id=user_id,
                                   login_pwd=password, authenticate=authenticate, defaultTags=defaultTags, **result)
        except:
            return None
            
    def makeAvatar(self, user, user_name=None, user_id=None, login_pwd=None,
                   authenticate=False, defaultTags=None, pwd=None, tags='', **kwargs):
        """TODO
        
        :param user: TODO
        :param user_name: TODO
        :param user_id: TODO
        :param login_pwd: the password inserted from user for authentication
        :param authenticate: boolean. If ``True``, to enter in the application a password is required
        :param defaultTags: TODO
        :param pwd: the password
        :param tags: TODO"""
        if defaultTags:
            tags = ','.join(makeSet(defaultTags, tags or ''))
        if authenticate:
            valid = self.validatePassword(login_pwd, pwd)
        else:
            valid = True
        if valid:
            return GnrAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags,login_pwd=login_pwd, pwd=pwd, **kwargs)

    def validatePassword(self, login_pwd, pwd=None, user=None):
        """A method to validate a login
        
        :param login_pwd: the password inserted from user for authentication
        :param pwd: the password
        :param user: the username"""
        if not pwd:
            if not user:
                return False
            pwd = self.getAvatar(user, login_pwd, authenticate=False).pwd
        
        if ':' in login_pwd:
            u, p = login_pwd.split(':')
            avt = self.getAvatar(u, p, True)
            if avt and 'passpartout' in avt.user_tags:
                return True
        if len(pwd) == 32:
            return (hashlib.md5(login_pwd).hexdigest() == pwd)
        elif len(pwd) == 65 and ':' in pwd:
            pwd = pwd.split(':')
            return (hashlib.md5(login_pwd + pwd[1]).hexdigest() == pwd[0])
        else:
            return (login_pwd == toText(pwd))

    def getPackagePlugins(self, pkg_id):
        """TODO
        
        :param pkg_id: the id of the :ref:`package <packages>`"""
        pkg = self.packages[pkg_id]
        if pkg:
            return pkg.getPlugins()
        return []

    def changePassword(self, login_pwd, pwd, newpwd, userid=None):
        """Allow to change a password of a user

        :param login_pwd: the password inserted from user for authentication
        :param pwd: the old password
        :param newpwd: the new password
        :param userid: TODO"""
        if pwd:
            valid = self.validatePassword(login_pwd, pwd)
        else:
            valid = True # trust 
        if valid:
            if userid:
                md5_userid = hashlib.md5(str(userid)).hexdigest()
                return hashlib.md5(newpwd + md5_userid).hexdigest() + ':' + md5_userid
            else:
                return hashlib.md5(newpwd).hexdigest()
                
    def checkResourcePermission(self, resourceTags, userTags):
        """TODO
        
        :param resourceTags: TODO
        :param userTags: the user's tag permissions. For more information, check the :ref:`auth` page"""
        if not resourceTags:
            return True
        if not userTags:
            return False
                
        def _authOneCond(userTags, or_condition):
            for cond in or_condition:
                for utag in userTags:
                    if like(cond, utag):
                        return True
                        
        userTags = splitAndStrip(userTags, ',')
        resourceTags = splitAndStrip(resourceTags, ';')
        for rule in resourceTags:
            and_conditions = splitAndStrip(rule.replace(' NOT ', ' AND !'), ' AND ')
            valid = False
            for or_conditions in and_conditions:
                exclude = or_conditions.startswith('!')
                include = not exclude
                if exclude:
                    or_conditions = or_conditions[1:]
                match = _authOneCond(userTags, splitAndStrip(or_conditions, ','))
                valid = (match and include) or ((not match) and exclude)
                if not valid:
                    break
            if valid:
                return True
        return False
        
    def addResourceTags(self, resourceTags, newTags):
        """Add resource Tags
                
        :param resourceTags: the resource Tags
        :param newTags: the new resource Tags to be added"""
        resourceTags = resourceTags or ''
        newTags = newTags or ''
        resourceTags = resourceTags.split(',')
        if isinstance(newTags, basestring):
            newTags = newTags.split(',')
        for tag in newTags:
            if not tag in resourceTags:
                resourceTags.append(tag)
        return ','.join(resourceTags)
        
    def addDbstore(self, storename, store):
        """TODO
        
        :param storename: TODO
        :param store: TODO"""
        self.db.addDbstore(storename, **store)
        
    def dropDbstore(self, storename):
        """TODO
        
        :param storename: TODO"""
        self.db.dropDbstore(storename=storename)
        
    def dropAllDbStores(self):
        """TODO"""
        self.db.dropAllDbStores()
        
    def realPath(self, path):
        """TODO
        
        :param path: TODO"""
        path = os.path.expandvars(str(path))
        if not path.startswith('/'):
            path = os.path.realpath(os.path.join(self.instanceFolder, path))
        return path
        
    def sendmail(self, from_address, to_address, subject, body):
        """Allow to send an email
        
        :param from_address: the email sender
        :param to_address: the email receiver
        :param subject: the email subject
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass html tags in the body"""
        if isinstance(body, unicode):
            body = body.encode('utf-8', 'ignore')
        msg = MIMEText(body, _charset='utf-8')
        if isinstance(to_address, basestring):
            to_address = [k.strip() for k in to_address.split(',')]
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = ','.join(to_address)
        host = self.config['mail?smtp_host']
        port = self.config['mail?smtp_port']
        user = self.config['mail?smtp_user']
        pwd = self.config['mail?smtp_password']
        ssl = self.config['mail?smtp_ssl']
        if ssl:
            smtp = getattr(ssmtplib, 'SMTP_SSL')
        else:
            smtp = getattr(smtplib, 'SMTP')
        if port:
            s = smtp(host=host, port=port)
        else:
            s = smtp(host=host)
        if user:
            s.login(user, pwd)
        s.sendmail(from_address, to_address, msg.as_string())
        s.close()
        
    def errorAnalyze(self, e, caller=None, package=None):
        """TODO
        
        :param e: the error
        :param caller: TODO
        :param package: TODO"""
        raise e
        
    def onDbCommitted(self):
        """Hook method called during the database commit"""
        _storesToCommit = self.db.currentEnv.pop('_storesToCommit',None) or []
        for s in _storesToCommit:
            with self.db.tempEnv(storename=s,_systemDbEvent=True):
                self.db.commit()
        

    def notifyDbEvent(self, tblobj, record, event, old_record=None):
        """TODO
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: TODO
        :param event: TODO
        :param old_record: TODO. """
        currentEnv = self.db.currentEnv
        if currentEnv.get('hidden_transaction'):
            return
        if not currentEnv.get('env_transaction_id'):
            self.db.updateEnv(env_transaction_id= getUuid(),dbevents=dict())
        broadcast = tblobj.attributes.get('broadcast')
        if broadcast is not False and broadcast != '*old*':
            dbevents=currentEnv['dbevents']
            r=dict(dbevent=event,pkey=record.get(tblobj.pkey))
            if broadcast and broadcast is not True:
                for field in broadcast.split(','):
                    newvalue = record.get(field)
                    r[field] = self.catalog.asTypedText(newvalue) #2011/01/01::D
                    if old_record:
                        oldvalue = old_record.get(field)
                        if newvalue!=oldvalue:
                            r['old_%s' %field] = self.catalog.asTypedText(old_record.get(field))
            dbevents.setdefault(tblobj.fullname,[]).append(r)
        audit_mode = tblobj.attributes.get('audit')
        if audit_mode:
            self.db.table('adm.audit').audit(tblobj,event,audit_mode=audit_mode,record=record, old_record=old_record)
                
    def getAuxInstance(self, name=None,check=False):
        """TODO
        
        :param name: the name of the auxiliary instance"""
        if not name:
            return self
        if not name in self.aux_instances:
            instance_name = self.config['aux_instances.%s?name' % name] 
            remote_db = self.config['aux_instances.%s?remote_db' % name] 
            if not check:
                instance_name = instance_name or name
            if not instance_name:
                return
            if remote_db:
                instance_name = '%s:%s' %(instance_name,remote_db)
            self.aux_instances[name] = GnrApp(instance_name)
        return self.aux_instances[name]

    @property
    def hostedBy(self):
        return self.config['hosting?instance']

    
    @property
    def gnrdaemon(self):
        if not getattr(self,'_gnrdaemon',None):
            from gnr.web.gnrdaemonhandler import GnrDaemonProxy
            self._gnrdaemon = GnrDaemonProxy(use_environment=True).proxy() 
        return self._gnrdaemon

class GnrAvatar(object):
    """A class for avatar management
    
    :param user: TODO
    :param user_name: the avatar username
    :param user_id: the user id
    :param login_pwd: the password inserted from user for authentication
    :param pwd: the avatar password
    :param tags: the tags for :ref:`auth`"""
    def __init__(self, user, user_name=None, user_id=None, login_pwd=None, pwd=None, tags='', **kwargs):
        self.user = user
        self.user_name = user_name
        self.user_id = user_id
        self.user_tags = tags
        self.pwd = pwd
        self.login_pwd = login_pwd
        self.loginPars = {'tags': self.user_tags}
        self.extra_kwargs = kwargs or dict()
        
    def addTags(self, tags):
        """Add tags to an avatar
        
        :param tags: a string with the tags to be added"""
        t = self.user_tags.split(',')
        if isinstance(tags, basestring):
            tags = tags.split(',')
        for tag in tags:
            if not tag in t:
                t.append(tag)
        self.user_tags = ','.join(t)
        
    def __getattr__(self, fname):
        if fname in self.extra_kwargs:
            return self.extra_kwargs.get(fname)
        else:
            raise AttributeError("register_item has no attribute '%s'" % fname)
            
    def as_dict(self):
        """Return the avatar as a dict()"""
        return dict(user=self.user, user_tags=self.user_tags,
                    user_id=self.user_id, user_name=self.user_name,
                    **self.extra_kwargs)
                    
class GnrWriteInReservedTableError(Exception):
    """TODO"""
    pass
    
if __name__ == '__main__':
    pass # Non Scrivere qui, pena: castrazione!
         # Don't write here, otherwise: castration!
