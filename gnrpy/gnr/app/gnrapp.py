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

"""
gnrapp
"""

import tempfile
import atexit
import logging
import shutil

import sys
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

from gnr.core.gnrlang import  gnrImport, instanceMixin, GnrException
from gnr.core.gnrstring import makeSet, toText, splitAndStrip, like, boolean
from gnr.core.gnrsys import expandpath
from gnr.sql.gnrsql import GnrSqlDb
from gnr.sql.gnrsqltable import SqlTablePlugin

log = logging.getLogger(__name__)

class GnrImportException(GnrException):
    pass

class GnrMixinObj(object):
    def __init__(self):
        pass

class GnrSqlAppDb(GnrSqlDb):
    def checkTransactionWritable(self, tblobj):
        if not hasattr(tblobj, '_usesTransaction'):
            tblobj._usesTransaction = boolean(
                    tblobj.attributes.get('transaction', tblobj.pkg.attributes.get('transaction', '')))
        if not self.inTransactionDaemon and tblobj._usesTransaction:
            raise GnrWriteInReservedTableError('%s.%s' % (tblobj.pkg.name, tblobj.name))
        

    def delete(self, tblobj, record,**kwargs):
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.delete(self, tblobj, record,**kwargs)
        self.application.notifyDbEvent(tblobj, record, 'D')

    def update(self, tblobj, record, old_record=None, pkey=None,**kwargs):
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.update(self, tblobj, record, old_record=old_record, pkey=pkey,**kwargs)
        self.application.notifyDbEvent(tblobj, record, 'U', old_record)

    def insert(self, tblobj, record,**kwargs):
        self.checkTransactionWritable(tblobj)
        GnrSqlDb.insert(self, tblobj, record,**kwargs)
        self.application.notifyDbEvent(tblobj, record, 'I')

    def getResource(self, tblobj, path):
        app = self.application
        resource = app.site.loadResource(tblobj.pkg.name, 'tables', tblobj.name, path)
        resource.site = app.site
        resource.table = tblobj
        resource.db = self
        return resource

class GnrPackage(object):
    def __init__(self, pkg_id, application, path=None, filename=None, **pkgattrs):
        self.id = pkg_id
        filename = filename or pkg_id
        self.application = application
        self.packageFolder = os.path.join(path, filename)
        self.libPath = os.path.join(self.packageFolder, 'lib')
        self.attributes = {}
        self.tableMixins = {}
        self.tablePlugins = {}
        self.customFolder = os.path.join(self.application.instanceFolder, 'custom', pkg_id)
        try:
            self.main_module = gnrImport(os.path.join(self.packageFolder, 'main.py'), 'package_%s' % pkg_id)
        except Exception, e:
            log.exception(e)
            raise GnrImportException(
                    "Cannot import package %s from %s" % (pkg_id, os.path.join(self.packageFolder, 'main.py')))
        try:
            self.pkgMenu = Bag(os.path.join(self.packageFolder, 'menu.xml'))
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
            self.custom_module = gnrImport(custom_mixin, 'custom_package_%s' % pkg_id)
            instanceMixin(self.pkgMixin, getattr(self.custom_module, 'Package', None))

            self.attributes.update(self.pkgMixin.config_attributes())
            self.webPageMixinCustom = getattr(self.custom_module, 'WebPage', None)
            self.baseTableMixinClsCustom = getattr(self.custom_module, 'Table', None)

        instanceMixin(self, self.pkgMixin)
        self.attributes.update(pkgattrs)

        self.tableMixinDict = {}
        self.loadTableMixinDict(self.main_module, self.packageFolder)
        if os.path.isdir(self.customFolder):
            self.loadTableMixinDict(self.custom_module, self.customFolder, 'custom_')
        self.configure()


    def loadTableMixinDict(self, module, folder, model_prefix=''):
        tbldict = {}
        if module:
            tbldict = dict([(x[6:], getattr(module, x)) for x in dir(module) if x.startswith('Table_')])

        modelfolder = os.path.join(folder, 'model')
        if os.path.isdir(modelfolder):
            tbldict.update(dict([(x[:-3], None) for x in os.listdir(modelfolder) if x.endswith('.py')]))

        for tbl, cls in tbldict.items():
            if not tbl in self.tableMixinDict:
                self.tableMixinDict[tbl] = GnrMixinObj()
                instanceMixin(self.tableMixinDict[tbl], self.baseTableMixinCls)
                instanceMixin(self.tableMixinDict[tbl], self.baseTableMixinClsCustom)
            if not cls:
                tbl_module = gnrImport(os.path.join(modelfolder, '%s.py' % tbl),
                                       '%smodel_of_%s_%s' % (model_prefix, self.id, tbl))
                instanceMixin(self.tableMixinDict[tbl], getattr(tbl_module, 'Table', None))
                self.tableMixinDict[tbl]._plugins = dict()
                
                for cname in dir(tbl_module):
                    member = getattr(tbl_module, cname, None)
                    if type(member) == type and issubclass(member, SqlTablePlugin):
                        self.tableMixinDict[tbl]._plugins[cname] = member # Miki 20090605
                        self.tablePlugins.setdefault(tbl, {})[cname] = member # TODO get plugins also from custom
            else:
                instanceMixin(self.tableMixinDict[tbl], cls)

    def config_attributes(self):
        return {}

    def onAuthentication(self, avatar):
        """Hook after authentication: receive the avatar and can add information to it"""
        pass

    def configure(self):
        """Build db structure in this order:
        - package config_db.xml
        - custom package config_db.xml
        - customized Table objects (method config_db)
        - customized Table objects (method config_db_custom)
        - customized Package objects (method config_db)
        - customized Package objects (method config_db_custom)
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
        pass

class GnrApp(object):
    """Opens a GenroPy application instance.

    Constructor parameters:
        
    :param instanceFolder: instance folder or name
    :param custom_config:  a bag or dictionary that will override configuration value
    :param forTesting:  if False, setup the application normally.
                        if True, setup the application for testing with a temporary sqlite database.
                        if it's a bag, setup the application for testing and import test data from this bag.
                        (see :meth:`loadTestingData`)
    
    If you want to interact with a Genro instance from your own python script, you can use this class directly.
    
    Example:
    
    >>> testgarden = GnrApp('testgarden')
    >>> testgarden.db.table('showcase.person').query().count()
    12
    """

    def __init__(self, instanceFolder, custom_config=None, forTesting=False, **kwargs):
        self.aux_instances = {}
        self.gnr_config = self.load_gnr_config()
        self.set_environment()
        if not os.path.isdir(instanceFolder):
            instanceFolder = self.instance_name_to_path(instanceFolder)
        self.instanceFolder = instanceFolder
        self.kwargs = kwargs
        self.packages = Bag()
        self.packagesIdByPath = {}
        self.config = self.load_instance_config()
        self.build_package_path()
        db_settings_path = os.path.join(self.instanceFolder, 'dbsettings.xml')
        if os.path.isfile(db_settings_path):
            db_credential = Bag(db_settings_path)
            self.config.update(db_credential)
        if custom_config:
            self.config.update(custom_config)
        if not 'menu' in self.config:
            self.config['menu'] = Bag()
            #------ application instance customization-------
        self.customFolder = os.path.join(self.instanceFolder, 'custom')
        self.dataFolder = os.path.join(self.instanceFolder, 'data')
        self.webPageCustom = None
        if os.path.isfile(os.path.join(self.customFolder, 'custom.py')):
            self.main_module = gnrImport(os.path.join(self.customFolder, 'custom.py'), 'custom_application')
            instanceMixin(self, getattr(self.main_module, 'Application', None))
            self.webPageCustom = getattr(self.main_module, 'WebPage', None)
        self.init(forTesting=forTesting)
        self.creationTime = time.time()


    def set_environment(self):
        environment_xml = self.gnr_config['gnr.environment_xml']
        if environment_xml:
            for var, value in environment_xml.digest('environment:#k,#a.value'):
                var = var.upper()
                if not os.getenv(var):
                    os.environ[var] = str(value)

    def load_gnr_config(self):
        if os.environ.has_key('VIRTUAL_ENV'):
            config_path = expandpath(os.path.join(os.environ['VIRTUAL_ENV'],'etc'))
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

    def load_instance_config(self):
        instance_config_path = os.path.join(self.instanceFolder, 'instanceconfig.xml')
        base_instance_config = Bag(instance_config_path)
        instance_config = self.gnr_config['gnr.instanceconfig.default_xml'] or Bag()
        template = base_instance_config['instance?template']
        if template:
            instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % template] or Bag())
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            for path, instance_template in self.gnr_config.digest(
                    'gnr.environment_xml.instances:#a.path,#a.instance_template'):
                if path == os.path.dirname(self.instanceFolder):
                    instance_config.update(self.gnr_config['gnr.instanceconfig.%s_xml' % instance_template] or Bag())
        instance_config.update(base_instance_config)
        return instance_config

    def init(self, forTesting=False):
        self.onIniting()
        self.base_lang = self.config['i18n?base_lang'] or 'en'
        self.catalog = GnrClassCatalog()
        self.localization = {}
        if not forTesting:
            dbattrs = self.config.getAttr('db')
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

        dbattrs['application'] = self
        dbattrs['allow_eager_one'] = ((self.config['eager?one'] or '').lower() == "true")
        dbattrs['allow_eager_many'] = ((self.config['eager?many'] or '').lower() == "true")
        self.db = GnrSqlAppDb(debugger=getattr(self, 'debugger', None), **dbattrs)

        pkgMenus = self.config['menu?package'] or []
        if pkgMenus:
            pkgMenus = pkgMenus.split(',')
        for pkgid, attrs in self.config['packages'].digest('#k,#a'):
            if not attrs.get('path'):
                attrs['path'] = self.pkg_name_to_path(pkgid)
            if not os.path.isabs(attrs['path']):
                attrs['path'] = self.realPath(attrs['path'])
            apppkg = GnrPackage(pkgid, self, **attrs)
            if apppkg.pkgMenu and (not pkgMenus or pkgid in pkgMenus):
                #self.config['menu.%s' %pkgid] = apppkg.pkgMenu
                if len(apppkg.pkgMenu) == 1:
                    self.config['menu.%s' % pkgid] = apppkg.pkgMenu.getNode('#0')
                else:
                    self.config.setItem('menu.%s' % pkgid, apppkg.pkgMenu,
                                        {'label': apppkg.config_attributes().get('name_long', pkgid)})
            self.packagesIdByPath[os.path.realpath(apppkg.packageFolder)] = pkgid
            self.packages[pkgid] = apppkg
            self.db.packageMixin('%s' % (pkgid), apppkg.pkgMixin)
            for tblname, mixobj in apppkg.tableMixinDict.items():
                self.db.tableMixin('%s.%s' % (pkgid, tblname), mixobj)
            sys.path.append(apppkg.libPath)
        self.db.inTransactionDaemon = False
        for pkg,pkgval in self.config['packages'].items():
            if pkgval:
                tables = self.db.model.src['packages'][pkg]['tables']
                for tablenode in pkgval:
                    tables.getNode(tablenode.label).attr.update(tablenode.attr)
                    
        self.db.startup()
        if len(self.config['menu']) == 1:
            self.config['menu'] = self.config['menu']['#0']
        self.buildLocalization()

        if forTesting:
            # Create tables in temporary database
            self.db.model.check(applyChanges=True)

            if isinstance(forTesting, Bag):
                self.loadTestingData(forTesting)

        self.onInited()

    def loadTestingData(self, bag):
        """Load data used for testing in the database.
        
        Called by the constructor when you pass a Bag in the `forTesting` parameter.
        
        :param bag: your test data
        
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
            </GenRoBag>
        """
        for table_name, records in bag.digest('#a.name,#v'):
            tbl = self.db.table(table_name)
            for r in records.values():
                tbl.insert(r)
        self.db.commit()

    def instance_name_to_path(self, instance_name):
        return PathResolver(gnr_config=self.gnr_config).instance_name_to_path(instance_name)

    def build_package_path(self):
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

    def pkg_name_to_path(self, pkgid):
        path = self.package_path.get(pkgid)
        if path:
            return path
        else:
            raise Exception(
                    'Error: package %s not found' % pkgid)

    def onIniting(self):
        """Event called before the instance initialization.
        """
        pass

    def onInited(self):
        """Event called after the instance initialization is complete.
        
        By default, it will call the ``onApplicationInited()`` method of each package.
        """
        for pkg in self.packages.values():
            pkg.onApplicationInited()


    def buildLocalization(self):
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
        pkgobj = self.packages[pkg]
        locpath = os.path.join(pkgobj.packageFolder, 'localization.xml')
        pkglocbag = Bag(locpath)
        for k, v in data.digest('#v.key,#v.txt'):
            lbl = re.sub('\W', '_', k).replace('__', '_')
            if not lbl in pkglocbag:
                pkglocbag.setItem(lbl, None, _key=k, it=k, en='', fr='', de='')
            pkglocbag.setAttr(lbl, {locale: v})
        pkglocbag.toXml(os.path.join(pkgobj.packageFolder, 'localization.xml'))

    def getResource(self, path, pkg=None, locale=None):
        if not pkg:
            pkg = self.config.getAttr('packages', 'default')
        return self.packages[pkg].getResource(path, locale=locale)

    def guestLogin(self):
        return self.config.getAttr('authentication', 'guestName')

    def authPackage(self):
        return self.packages[self.config.getAttr('authentication', 'pkg')]

    def getAvatar(self, user, password=None, authenticate=False, page=None, **kwargs):
        if user:
            authmethods = self.config['authentication']
            if authmethods:
                for node in self.config['authentication'].nodes:
                    avatar = getattr(self, 'auth_%s' % node.label.replace('_auth', ''))(node, user, password=password,
                                                                                        authenticate=authenticate,
                                                                                        **kwargs)
                    if not (avatar is None):
                        avatar.page = page
                        for pkg in self.packages.values():
                            pkg.onAuthentication(avatar)
                        return avatar

    def auth_xml(self, node, user, password=None, authenticate=False, **kwargs):
        """Authentication from instanceconfig.xml, use it during development or for sysadmin tasks.
        
        In file instanceconfig.xml insert a tag like::
        
            <xml_auth defaultTags='myusers'>
                <john pwd='mydog' tags='admin' />
            </xml_auth>

        """
        defaultTags = node.getAttr('defaultTags')
        path = node.getAttr('path')
        if path:
            users = Bag(self.realPath(path))
        else:
            users = node.getValue()
        for key, attrs in users.digest('#k,#a'):
            if key == user:
                user_name = attrs.pop('user_name', key)
                user_id = attrs.pop('user_id', key)
                kw = dict(attrs)
                kw.update(kwargs)
                return self.makeAvatar(user=user, user_name=user_name, user_id=user_id,
                                       login_pwd=password, authenticate=authenticate,
                                       defaultTags=defaultTags, **kw)

    def auth_py(self, node, user, password=None, authenticate=False, **kwargs):
        """Python authentication. This is mostly used to register new users for the first time. (see ``adm`` package).
        
        In file instanceconfig.xml insert a tag like::
        
               <py_auth  defaultTags='myusers' pkg='mypkg' method='myauthmethod' />
           
           ``mypkg.myauthmethod`` will be called with a single parameter, the username. It should return:
           -  ``None``, if the user doesn't exists
           - a dict containing every attribute to add to the avatar, if the user is valid.
           - Mandatory attributes: username, pwd

        **TODO:** it seems odd that we don't pass the password to the authentication method. It limits the appicability
                  of this authentication method soo much!
        """
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
            tags = result.pop('tags', user)
            return self.makeAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags,
                                   login_pwd=password, authenticate=authenticate,
                                   defaultTags=defaultTags, **result)

    def auth_sql(self, node, user, password=None, authenticate=False, **kwargs):
        """Authenticate from database.
        
        In file instanceconfig.xml insert a tag like::
        
           <sql_auth  defaultTags='myusers' dbtable='mypkg.users' 
                      username='username_fld' pwd='pwd_fld' userid='optional_id_fld' />
        
       - Mandatory attributes: dbtable, username, pwd
       - Optional attributes: defaultTags, userid (the primary key of the db table if it is not the username field)
         Other attributes are aliases of dbfield names: myavatarfield='mydbfield'
        """
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
        if defaultTags:
            tags = ','.join(makeSet(defaultTags, tags or ''))
        if authenticate:
            valid = self.validatePassword(login_pwd, pwd)
        else:
            valid = True
        if valid:
            return GnrAvatar(user=user, user_name=user_name, user_id=user_id, tags=tags, login_pwd=login_pwd, **kwargs)

    def validatePassword(self, login_pwd, pwd=None, user=None):
        if not pwd:
            if not user:
                return False
            pwd = self.getAvatar(user, login_pwd, authenticate=False).pwd
        if '::' in login_pwd:
            u, p = login_pwd.split('::')
            avt = self.getAvatar(u, p, True)
            if avt and 'passpartout' in avt.tags:
                return True
        if len(pwd) == 32:
            return (hashlib.md5(login_pwd).hexdigest() == pwd)
        elif len(pwd) == 65 and ':' in pwd:
            pwd = pwd.split(':')
            return (hashlib.md5(login_pwd + pwd[1]).hexdigest() == pwd[0])
        else:
            return (login_pwd == toText(pwd))

    def changePassword(self, login_pwd, pwd, newpwd, userid=None):
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
        self.db.addDbstore(storename, **store)

    def dropDbstore(self, storename):
        self.db.dropDbstore(storename=storename)

    def dropAllDbStores(self):
        self.db.dropAllDbStores()

    def realPath(self, path):
        path = os.path.expandvars(str(path))
        if not path.startswith('/'):
            path = os.path.realpath(os.path.join(self.instanceFolder, path))
        return path

    def sendmail(self, from_address, to_address, subject, body):
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
        raise e

    def notifyDbEvent(self, tblobj, record, event, old_record=None):
        if 'audit' in tblobj.attributes:
            self.db.table('adm.audit').audit(tblobj,event, record, old_record=old_record)
            

    def getAuxInstance(self, name=None):
        if not name:
            return self
        if not name in self.aux_instances:
            instance_name = self.config['aux_instances.%s?name' % name] or name
            self.aux_instances[name] = GnrApp(instance_name)
        return self.aux_instances[name]


class GnrAvatar(object):
    def __init__(self, user, user_name=None, user_id=None, tags='', login_pwd=None, **kwargs):
        self.user = user
        self.user_name = user_name
        self.user_id = user_id
        self.user_tags = tags
        self.pwd = login_pwd
        self.loginPars = {'tags': self.user_tags}
        self.extra_kwargs = kwargs or dict()

    def addTags(self, tags):
        t = self.tags.split(',')
        if isinstance(tags, basestring):
            tags = tags.split(',')
        for tag in tags:
            if not tag in t:
                t.append(tag)
        self.tags = ','.join(t)

    def __getattr__(self, fname):
        if fname in self.extra_kwargs:
            return self.extra_kwargs.get(fname)
        else:
            raise AttributeError("register_item has no attribute '%s'" % fname)


    def as_dict(self):
        return dict(user=self.user, user_tags=self.user_tags,
                    user_id=self.user_id, user_name=self.user_name,
                    **self.extra_kwargs)

class GnrWriteInReservedTableError(Exception):
    pass


if __name__ == '__main__':
    pass # Non Scrivere qui, pena: castrazione!