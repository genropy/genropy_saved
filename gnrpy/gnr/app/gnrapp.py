# -*- coding: utf-8 -*-
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

from __future__ import print_function
from builtins import str
from past.builtins import basestring
#from builtins import object
import tempfile
import atexit
import logging
import shutil
import locale
import sys
import imp
import os
import hashlib
import re
import smtplib
import time
import glob
from email.mime.text import MIMEText
from gnr.utils import ssmtplib
from gnr.app.gnrdeploy import PathResolver
from gnr.app.gnrconfig import MenuStruct
from gnr.core.gnrclasses import GnrClassCatalog
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import extract_kwargs

from gnr.core.gnrlang import  objectExtract,gnrImport, instanceMixin, GnrException
from gnr.core.gnrstring import makeSet, toText, splitAndStrip, like, boolean
from gnr.core.gnrsys import expandpath
from gnr.sql.gnrsql import GnrSqlDb
from gnr.app.gnrlocalization import AppLocalizer
from gnr.app.gnrconfig import getGnrConfig
log = logging.getLogger(__name__)

class GnrRestrictedAccessException(GnrException):
    """GnrRestrictedAccessException"""
    code = 'GNRAPP-001'
    description = '!!User not allowed'


class NullLoader(object):
    """TODO"""
    def load_module(self,fullname):
        """TODO
        
        :param fullname: TODO"""
        if fullname in sys.modules:
            return sys.modules[fullname]

class ApplicationCache(object):
    def __init__(self,application=None):
        self.application = application
        self.cache = {}
    
    def getItem(self,key):
        return self.cache.get(key,None)
    
    def setItem(self,key,value):
        self.cache[key] = value

    def updatedItem(self,key):
        self.cache.pop(key,None)

    def expiredItem(self,key):
        return key not in self.cache


class GnrModuleFinder(object):
    """TODO"""
    
    path_list=[]
    app_list=set()
    instance_lib = None
    def __init__(self, path_entry, app):
        self.path_entry = path_entry
        self.app = app
        if app not in self.app_list:
            self.app_list.add(app)
        if self.instance_lib is None:
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
        splitted=fullname.split('.')
        if splitted[0] != 'gnrpkg':
            return
        n_segments = len(splitted)
        if n_segments==1:
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
        elif n_segments==2:
            pkg = splitted[1]
            pkg_module = self._get_gnrpkg_module(pkg)
            if pkg_module:
                return NullLoader()
        elif n_segments>2:
            pkg = splitted[1]
            mod_fullname='.'.join(splitted[2:])
            if self.pkg_in_app_list(pkg):
                pkg_module = self._get_gnrpkg_module(pkg)
                mod_file,mod_pathname,mod_description=imp.find_module(mod_fullname, pkg_module.__path__)
                return GnrModuleLoader(mod_file,mod_pathname,mod_description)
        return None
    
    def pkg_in_app_list(self, pkg):
        for a in self.app_list:
            if pkg in a.packages:
                return a.packages[pkg]

    def _get_gnrpkg_module(self, pkg):
        gnrpkg = self.pkg_in_app_list(pkg)
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
        print(self.pathname)
        print(fullname)
        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            try:
                imp.acquire_lock()
                mod = imp.load_module(fullname,self.file, self.pathname, self.description)
                sys.modules[fullname]=mod
            finally:
                if imp.lock_held():
                    imp.release_lock()
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

    @property
    def localizer(self):
        return self.application.localizer


    def notifyDbUpdate(self,tblobj,recordOrPkey=None,**kwargs):
        self.application.notifyDbUpdate(tblobj,recordOrPkey=recordOrPkey,**kwargs)
    
        
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
        GnrSqlDb.raw_update(self, tblobj, record,old_record=old_record, pkey=pkey,**kwargs)
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
                if isinstance(r,dict):
                    r = [r]
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

    def _getUserConfiguration(self,table=None,user=None,user_group=None):
        if self.package('adm'):
            return self.table('adm.user_config').getInfoBag(tbl=table,user=user,
                                                        user_group=user_group)



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
        self.menuBag = MenuStruct(os.path.join(self.pluginFolder,'menu'),application=self.application,autoconvert=True)
        self.config = Bag(config_path) if os.path.isfile(config_path) else Bag()
        self.application.config['package_plugins.%s.%s'%(pkg.id,self.id)]=self.config
        
class GnrPackage(object):
    """TODO"""
    def __init__(self, pkg_id, application, path=None, filename=None, project=None,**pkgattrs):
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
        self._pkgMenu = None
        self.projectInfo = None
        if not project:
            projectPath = os.path.normpath(os.path.join(self.packageFolder,'..','..'))
            projectInfoPath = os.path.join(projectPath,'info.xml')
            project = os.path.split(projectPath)[1]
            if os.path.exists(projectInfoPath):
                self.projectInfo = Bag(projectInfoPath)
        if not self.projectInfo:
            self.projectInfo = Bag(('project',None,dict(name=project,code=project,language='en'))) 
        self.project = project 
        self.customFolder = os.path.join(self.application.instanceFolder, 'custom', pkg_id)
        try:
            self.main_module = gnrImport(os.path.join(self.packageFolder, 'main.py'),avoidDup=True)
        except Exception as e:
            log.exception(e)
            raise GnrImportException(
                    "Cannot import package %s from %s" % (pkg_id, os.path.join(self.packageFolder, 'main.py')))    
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
        self.disabled = boolean(self.attributes.get('disabled'))

    def initTableMixinDict(self):
        self.tableMixinDict = {}
        modelFolder = os.path.join(self.packageFolder, 'model')
        self.loadTableMixinDict(self.main_module, modelFolder)
        for pkgid, apppkg in list(self.application.packages.items()):
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
    def language(self):
        return self.attributes.get('language') or self.projectInfo['project?language']

    @property
    def pkgMenu(self):
        if self._pkgMenu is None:
            pkgMenu = MenuStruct(os.path.join(self.packageFolder, 'menu'),application=self.application,autoconvert=True)
            for pluginname,plugin in list(self.plugins.items()):
                pkgMenu.update(plugin.menuBag)
            self._pkgMenu = pkgMenu
        return self._pkgMenu

    @property
    def db(self):
        return self.application.db
    
    def required_packages(self):
        return []
    
    def loadPlugins(self):
        """TODO"""
        plugin_folders=glob.glob(os.path.join(self.application.pluginFolder,self.id,'*'))
        for plugin_folder in plugin_folders:
            plugin = GnrPackagePlugin(self, plugin_folder)
            self.plugins[plugin.id] = plugin
        
    def getPlugins(self):
        """TODO"""
        return list(self.plugins.values())
    
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
        tblkeys = list(tbldict.keys())
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
                    special_methods = ['config_db','trigger_onInserting','trigger_onInserted','trigger_onUpdating',
                                        'trigger_onUpdated','trigger_onDeleting','trigger_onDeleted']
                    special_methods = ','.join(special_methods)
                    instanceMixin(self.tableMixinDict[tbl], tbl_cls, methods=special_methods, suffix='%s'%fromPkg)
                    instanceMixin(self.tableMixinDict[tbl], tbl_cls, exclude=special_methods)
                
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
    
    def onDbSetup(self):
        self.tableBroadcast('onDbSetup,onDbSetup_*')

    def onDbUpgrade(self):
        self.tableBroadcast('onDbUpgrade,onDbUpgrade_*')

    def tableBroadcast(self,evt,autocommit=False,**kwargs):
        changed = False
        for evt in evt.split(','):
            changed = changed or self._tableBroadcast(evt,**kwargs)
        return changed
    
    def _tableBroadcast(self,evt,autocommit=False,**kwargs):
        changed = False
        db = self.application.db
        for tname,tblobj in list(db.packages[self.id].tables.items()):
            if evt.endswith('*'):
                handlers = list(objectExtract(tblobj.dbtable,evt[:-1]).values())
            else:
                handlers = [getattr(tblobj.dbtable,evt,None)]

            handler = getattr(tblobj.dbtable,evt,None)
            for handler in [_f for _f in handlers if _f]:
                result = handler(**kwargs)
                changed = changed or result
        if changed and autocommit:
            db.commit()
        return changed


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
        self.gnr_config = getGnrConfig(set_environment=True)
        self.debug=debug
        self.remote_db = None
        self.instanceFolder = ''
        self.instanceName = ''
        self.project_packages_path = None
        if instanceFolder:
            if '@' in instanceFolder:
                instanceFolder,self.remote_db  = instanceFolder.split('@',1)
            self.instanceFolder = self.instance_name_to_path(instanceFolder)
            self.instanceName = os.path.basename(self.instanceFolder)
            project_packages_path = os.path.normpath(os.path.join(self.instanceFolder, '..', '..', 'packages'))
            if os.path.isdir(project_packages_path):
                self.project_packages_path = project_packages_path
            if os.path.exists(os.path.join(self.instanceFolder,'config','instanceconfig.xml')):
                self.instanceFolder = os.path.join(self.instanceFolder,'config')

        sys.path.append(os.path.join(self.instanceFolder, 'lib'))
        sys.path_hooks.append(self.get_modulefinder)
        self.pluginFolder = os.path.normpath(os.path.join(self.instanceFolder, 'plugin'))
        self.kwargs = kwargs
        self.packages = Bag()
        self.packagesIdByPath = {}
        self.config = self.load_instance_config()
        self.config_locale = self.config('default?server_locale')
        if self.config_locale :
            os.environ['GNR_LOCALE'] = self.config_locale
        self.instanceMenu = self.load_instance_menu()
        self.cache = ApplicationCache(self)
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
        if 'menu' not in self.config:
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
        
    def load_instance_menu(self):
        """TODO"""
        return MenuStruct(os.path.join(self.instanceFolder, 'menu'),application=self,autoconvert=True)

    def load_instance_config(self):
        """TODO"""
        if not self.instanceFolder:
            return Bag()

        def normalizePackages(config):
            if config['packages']:
                packages = Bag()
                for n in config['packages']:
                    packages.setItem(n.attr.get('pkgcode') or n.label, n.value, n.attr)
                config['packages']  = packages
            return config
        instance_config_path = os.path.join(self.instanceFolder, 'instanceconfig.xml')
        base_instance_config = normalizePackages(Bag(instance_config_path))
        instance_config = normalizePackages(self.gnr_config['gnr.instanceconfig.default_xml']) or Bag()
        template = base_instance_config['instance?template']
        if template:
            instance_config.update(normalizePackages(self.gnr_config['gnr.instanceconfig.%s_xml' % template]) or Bag())
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            for path, instance_template in self.gnr_config.digest(
                    'gnr.environment_xml.instances:#a.path,#a.instance_template') or []:
                if path == os.path.dirname(self.instanceFolder):
                    instance_config.update(normalizePackages(self.gnr_config['gnr.instanceconfig.%s_xml' % instance_template]) or Bag())
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
            dbattrs['implementation'] = dbattrs.get('implementation') or 'sqlite'
            if dbattrs.get('dbname') == '_dummydb':
                pass
            elif self.remote_db:
                dbattrs.update(self.config.getAttr('remote_db.%s' %self.remote_db))
            elif dbattrs and dbattrs.get('implementation') == 'sqlite':
                dbname = dbattrs.pop('filename',None) or dbattrs['dbname']
                if not os.path.isabs(dbname):
                    dbname = self.realPath(os.path.join('..','data',dbname))
                dbattrs['dbname'] = dbname
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
        dbattrs['application'] = self
        self.db = GnrSqlAppDb(debugger=getattr(self, 'sqlDebugger', None), **dbattrs)
        
        

        for pkgid,pkgattrs,pkgcontent in self.config['packages'].digest('#k,#a,#v'):
            self.addPackage(pkgid,pkgattrs=pkgattrs,pkgcontent=pkgcontent)


        for pkgid, apppkg in list(self.packages.items()):
            apppkg.initTableMixinDict()
            self.db.packageMixin('%s' % (pkgid), apppkg.pkgMixin)
            for tblname, mixobj in list(apppkg.tableMixinDict.items()):
                self.db.tableMixin('%s.%s' % (pkgid, tblname), mixobj)
        self.db.inTransactionDaemon = False
        self.pkgBroadcast('onDbStarting')
        self.db.startup(restorepath=restorepath)
        if len(self.config['menu']) == 1:
            self.config['menu'] = self.config['menu']['#0']
        if self.instanceMenu:
            self.config['menu']=self.instanceMenu
            
        self.localizer = AppLocalizer(self)
        if forTesting:
            # Create tables in temporary database
            self.db.model.check(applyChanges=True)
                
            if isinstance(forTesting, Bag):
                self.loadTestingData(forTesting)
        self.onInited()

    def addPackage(self,pkgid,pkgattrs=None,pkgcontent=None):
        if ':' in pkgid:
            project,pkgid=pkgid.split(':')
        else:
            project=None
        if pkgid in self.packages:
            return 
        attrs = pkgattrs or {}
        if not attrs.get('path'):
            attrs['path'] = self.pkg_name_to_path(pkgid,project)
        if not os.path.isabs(attrs['path']):
            attrs['path'] = self.realPath(attrs['path'])
        apppkg = GnrPackage(pkgid, self, **attrs)
        apppkg.content = pkgcontent or Bag()
        for reqpkgid in apppkg.required_packages():
            self.addPackage(reqpkgid)
        self.packagesIdByPath[os.path.realpath(apppkg.packageFolder)] = pkgid
        self.packages[pkgid] = apppkg
    
        
    def applicationMenuBag(self):
        pkgMenus = self.config['menu?package']
        if pkgMenus:
            pkgMenus = pkgMenus.split(',')
        menuBag = Bag()
        for pkgid, apppkg in list(self.packages.items()):
            pkgMenuBag = apppkg.pkgMenu
            if pkgMenuBag and (not pkgMenus or pkgid in pkgMenus):
                #self.config['menu.%s' %pkgid] = apppkg.pkgMenu
                if len(pkgMenuBag) == 1:
                    menuBag[pkgid] = pkgMenuBag.getNode('#0')
                else:
                    menuBag.setItem(pkgid, pkgMenuBag,{'label': apppkg.config_attributes().get('name_long', pkgid),'pkg_menu':pkgid})
        return menuBag

    def importFromSourceInstance(self,source_instance=None):
        to_import = ''
        if ':' in source_instance:
            source_instance,to_import = source_instance.split(':')
        source_instance = GnrApp(source_instance)
        to_import = list(source_instance.db.packages.keys()) if not to_import else to_import.split(',')
        set_to_import = set()
        while to_import:
            k = to_import.pop(0)
            if k == '*':
                to_import[:] = list(source_instance.db.packages.keys())+to_import
            elif  '.' in k:
                if not k.startswith('!'):
                    set_to_import.add(k)
                else:
                    set_to_import.remove(k[1:])
            else:
                if not k.startswith('!'):
                    set_to_import = set_to_import.union(set([t.fullname for t in list(source_instance.db.packages[k].tables.values())]))
                else:
                    set_to_import = set_to_import.difference(set([t.fullname for t in list(source_instance.db.packages[k[1:]].tables.values())]))
        
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
                print('\nIMPORTING',tbl)
                dest_tbl.dbtable.importFromAuxInstance(source_instance, empty_before=False,raw_insert=True)
                print('\nSTILL TO IMPORT',tables_to_import)
                imported_tables.add(tbl)
            else:
                print('\nCANT IMPORT',tbl,dependencies.difference(imported_tables))
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
            for r in list(records.values()):
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
        if self.project_packages_path:
            path_list.append(self.project_packages_path)
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
        result = []
        for method in method.split(','):
            result+=self._pkgBroadcast(method,*args,**kwargs)
        return result
    
    def _pkgBroadcast(self,method,*args,**kwargs):
        result = []
        for pkgId,pkg in self.packages.items():
            if pkg.attributes.get('readOnly'):
                continue
            if method.endswith('*'):
                handlers = list(objectExtract(self,method[:-1]).values())
            else:
                handlers = [getattr(pkg,method,None)]
            for handler in [_f for _f in handlers if _f]:
                r = handler(*args,**kwargs)
                if r is not None:
                    result.append((pkgId,r))
        return result

    @property
    def locale(self):
        return (self.config_locale or os.environ.get('GNR_LOCALE') or locale.getdefaultlocale()[0]).replace('_','-')

    def setPreference(self, path, data, pkg):
        if self.db.package('adm'):
            self.db.table('adm.preference').setPreference(path, data, pkg=pkg)

    def getPreference(self, path, pkg=None, dflt=None, mandatoryMsg=None):
        if self.db.package('adm'):
            return self.db.table('adm.preference').getPreference(path, pkg=pkg, dflt=dflt, mandatoryMsg=mandatoryMsg)
    
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
            if user=='gnrtoken':
                user = self.db.table('sys.external_token').authenticatedUser(password)
                if not user:
                    return
                authenticate = False
            if authmethods:
                for node in self.config['authentication'].nodes:
                    nodeattr = node.attr
                    authmode = nodeattr.get('mode') or node.label.replace('_auth', '')
                    avatar = getattr(self, 'auth_%s' % authmode)(node, user, password=password,
                                                                 authenticate=authenticate,
                                                                 **kwargs)
                    if not (avatar is None):
                        avatar.page = page
                        avatar.authmode = authmode
                        errors = self.pkgBroadcast('onAuthentication',avatar)
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
                                       group_code=kw.pop('group_code','xml_group'),
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
        external_user = False
        if pkg:
            pkg = self.packages[pkg]
        if authenticate and attrs.get('service_type'):
            authService = self.site.getService(service_type=node.attr.get('service_type') or node.label,service_name=node.attr.get('service_name'))
            external_user = authService(user=user,password=password)
            if external_user:
                if authService.case == 'u':
                    user = user.upper()
                elif authService.case == 'l':
                    user = user.lower()
                authenticate = False #it has been authenticated by the service
                if external_user is not True and hasattr(pkg,'onExternalUser'):
                    pkg.onExternalUser(external_user)
        if pkg:
            handler = getattr(pkg, attrs['method'])
        else:
            handler = getattr(self, attrs['method'])
        if handler:
            result = handler(user,service=attrs.get('service'), **kwargs)
        if result:
            user_name = result.pop('user_name', user)
            user_id = result.pop('user_id', user)
            user_record_tags = result.pop('tags', user)
            menubag = result.pop('menubag',None)
            if not tags:
                tags = user_record_tags
            elif user_record_tags:
                tags = tags.split(',')
                tags.extend(user_record_tags.split(','))
                tags = ','.join(list(set(tags)))
            return self.makeAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags,
                                   login_pwd=password, authenticate=authenticate,
                                   external_user=external_user,
                                   defaultTags=defaultTags,menubag=menubag, **result)
                                   
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
            result = dict([(str(k), rec[v]) for k, v in list(attrs.items())])
            user_name = result.pop('user_name', user)
            user_id = result[tblobj.pkey]
            return self.makeAvatar(user=user, user_name=user_name, user_id=user_id,
                                   login_pwd=password, authenticate=authenticate, defaultTags=defaultTags, **result)
        except:
            return None

    def checkAllowedIp(self,allowed_ip):
        "override"
        return False
            
    def makeAvatar(self, user, user_name=None, user_id=None, login_pwd=None,
                   authenticate=False, defaultTags=None, pwd=None, tags='',allowed_ip=None, **kwargs):
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
            if valid and not self.checkAllowedIp(allowed_ip):
                raise GnrRestrictedAccessException('Not allowed access')
        else:
            valid = True
        if valid:
            return GnrAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags,login_pwd=login_pwd, pwd=pwd, **kwargs)

    def validatePassword(self, login_pwd, pwd=None, user=None):
        """A method to validate a login
        
        :param login_pwd: the password inserted from user for authentication
        :param pwd: the password
        :param user: the username"""
        if not login_pwd:
            return False
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
            return (hashlib.md5(login_pwd.encode()).hexdigest() == pwd)
        elif len(pwd) == 65 and ':' in pwd:
            pwd = pwd.split(':')
            return (hashlib.md5(login_pwd.encode() + pwd[1].encode()).hexdigest() == pwd[0])
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
                md5_userid = hashlib.md5(str(userid).encode()).hexdigest()
                return hashlib.md5(newpwd.encode() + md5_userid.encode()).hexdigest() + ':' + md5_userid
            else:
                return hashlib.md5(newpwd.encode()).hexdigest()
                
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

    @extract_kwargs(checkpref=True)
    def allowedByPreference(self,checkpref=None,checkpref_kwargs=None,**kwargs):
        if not checkpref:
            return True
        if isinstance(checkpref,dict):
            checkpref = checkpref.get('')
        preflist = splitAndStrip(checkpref, ' OR ')
        allowed = []
        prefdata = self.getPreference(checkpref_kwargs.get('path')) or Bag()
        for pref in preflist:
            allowed.append([n for n in [prefdata[pr] for pr in splitAndStrip(pref, ' AND ')] if not n])
        return len([n for n in allowed if not n])>0

        
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
            if tag not in resourceTags:
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
        if not os.path.isabs(path):
            path = os.path.realpath(os.path.join(self.instanceFolder, path))
        return path
        
    def sendmail(self, from_address, to_address, subject, body):
        """Allow to send an email
        
        :param from_address: the email sender
        :param to_address: the email receiver
        :param subject: the email subject
        :param body: the email body. If you pass ``html=True`` attribute,
                     then you can pass html tags in the body"""
        if isinstance(body, str):
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
        pass

    def notifyDbEvent(self, tblobj, record, event, old_record=None):
        pass

    def getLegacyDb(self,name=None):
        externaldb = getattr(self,'legacy_db_%s' %name,None)
        if not externaldb:
            config = self.config
            connection_params = config.getAttr('legacy_db.%s' %name)
            externaldb = GnrSqlDb(implementation=connection_params.get('implementation'),
                                dbname=connection_params.get('dbname') or connection_params.get('filename') or name,
                                host=connection_params.get('host'),user=connection_params.get('user'),
                                password = connection_params.get('password'))
            externaldb.importModelFromDb()
            externaldb.model.build()
            setattr(self,'legacy_db_%s' %name,externaldb)
            print('got externaldb',name)
        return externaldb

    def importFromLegacyDb(self,packages=None,legacy_db=None,thermo_wrapper=None,thermo_wrapper_kwargs=None):
        if not packages:
            packages = list(self.packages.keys())
        else:
            packages = packages.split(',')
        tables = self.db.tablesMasterIndex()['_index_'].digest('#a.tbl')
        if thermo_wrapper:
            thermo_wrapper_kwargs = thermo_wrapper_kwargs or dict()
            thermo_wrapper_kwargs['maxidx'] = len(tables)
            tables = thermo_wrapper(tables,**thermo_wrapper_kwargs)
        for table in tables:
            pkg,tablename = table.split('.')
            if pkg in packages:
                self.importTableFromLegacyDb(table,legacy_db=legacy_db)
        self.db.commit()
        self.db.closeConnection()

    def importTableFromLegacyDb(self,tbl,legacy_db=None):
        destbl = self.db.table(tbl)
        legacy_db = legacy_db or destbl.attributes.get('legacy_db')
        if not legacy_db:
            return
        if destbl.query().count():
            print('do not import again',tbl)
            return
        
   
        sourcedb = self.getLegacyDb(legacy_db)
        table_legacy_name =  destbl.attributes.get('legacy_name')
        columns = None
        if not table_legacy_name:
            table_legacy_name = '%s.%s' %(tbl.split('.')[0],tbl.replace('.','_'))
        else:
            columns = []
            for k,c in list(destbl.columns.items()):
                colummn_legacy_name = c.attributes.get('legacy_name')
                if colummn_legacy_name:
                    columns.append(" $%s AS %s " %(colummn_legacy_name,k))
            columns = ', '.join(columns)
        columns = columns or '*'
        oldtbl = None
        try:
            oldtbl = sourcedb.table(table_legacy_name)
        except Exception:
            print('missing table in legacy',table_legacy_name)
        if not oldtbl:
            return
        q = oldtbl.query(columns=columns,addPkeyColumn=False,bagFields=True)
        f = q.fetch()
        sourcedb.closeConnection()
        rows = []
        adaptLegacyRow =  getattr(destbl,'adaptLegacyRow',None)
        for r in f:
            r = dict(r)
            destbl.recordCoerceTypes(r)
            if adaptLegacyRow:
                adaptLegacyRow(r)
            rows.append(r)
        if rows:
            destbl.insertMany(rows)
        print('imported',tbl)

    def getAuxInstance(self, name=None,check=False):
        """TODO
        
        :param name: the name of the auxiliary instance"""
        if not name:
            return self
        if name in self.aux_instances:
            return self.aux_instances[name]
        instance_node = self.config.getNode('aux_instances.%s' % name)
        if not instance_node:
            if check:
                return
            raise Exception('aux_instance %s is not declared' %name)
        instance_name = instance_node.getAttr('name') or name
        remote_db = instance_node.getAttr('remote_db')
        if remote_db:
            instance_name = '%s@%s' %(instance_name,remote_db)
        self.aux_instances[name] = self.createAuxInstance(instance_name)
        return self.aux_instances[name]
    
    def createAuxInstance(self,instance_name):
        return GnrApp(instance_name)

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
    def __init__(self, user, user_name=None, user_id=None, login_pwd=None, pwd=None, tags='', menubag=None,**kwargs):
        self.user = user
        self.user_name = user_name
        self.user_id = user_id
        self.user_tags = tags
        self.pwd = pwd
        self.login_pwd = login_pwd
        self.loginPars = {'tags': self.user_tags}
        self.extra_kwargs = kwargs or dict()
        self.menubag = Bag(menubag) if menubag else None
        
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
