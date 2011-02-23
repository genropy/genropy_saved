# -*- coding: UTF-8 -*-
# Genro  
# Copyright (c) 2004 Softwell sas - Milano see LICENSE for details
# Author Giovanni Porcari, Francesco Cavazzana, Saverio Porcari, Francesco Porcari
import os
import time, datetime
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import logging

gnrlogger = logging.getLogger(__name__)

from gnr.core.gnrlang import errorLog
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.app.gnrapp import GnrApp

from gnr.sql.gnrsql_exceptions import NotMatchingModelError
from gnr.sql.gnrsqlmodel import DbModelSrc

from gnr.xtnd.sync4Dtransaction import TransactionManager4D

class GnrSync4DException(Exception):
    pass

class Struct4D(object):
    def __init__(self, app, packages_folder=None):
        self.app = app
        self.instance_folder = app.instanceFolder
        self.folder4dstructBag = Bag(self.folder4dstruct + '/')['structure']
        self.names4d = self.buildNames4d()
        self.packages_folder = packages_folder
        
    @property
    def folder4d(self):
        return self.app.folder4d


    @property
    def folder4dstruct(self):
        path = os.path.join(self.folder4d, 'structure')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    def areaFolder(self, area):
        path = os.path.join(self.packages_folder, area)
        print 'areaFolder:', path
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    def modelFolder(self, area):
        path = os.path.join(self.areaFolder(area), 'model')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    def fromNameAs(self, name):
        if ' AS ' in name:
            name4d, nameSql = name.split(' AS ', 1)
        else:
            name4d, nameSql = name, name
        return name4d.strip(), nameSql.strip().lstrip('_').lower()

    def nameConverter(self, table='', field='', fullname=None, mode='4D'):
        if not fullname:
            fullname = '%s_[%s]%s' % (mode, table, field)
        else:
            fullname = '%s_%s' % (mode, fullname)
        return self.names4d.get(fullname.lower())

    def get4dTables(self):
        return [k[4:-1] for k, v in self.names4d.items() if k.startswith('4d') and not v[2]]

    def buildNames4d(self):
        result = {}
        namesdict = {}
        for sname, sbag in self.folder4dstructBag.items():
            sname = sname.lower()
            tablesbag = sbag['tables4d']
            if tablesbag:
                for tbag in tablesbag.values():
                    table4D, tableSql = self.fromNameAs(tbag['name'])
                    path4d = '4D_[%s]' % table4D
                    namesdict[
                    tableSql] = None # in namesdict put the table with area name avoiding multi area duplicates
                    if tableSql.startswith('%s_' % sname): #strip the area code from table name
                        tableSql = tableSql.lower().split('_', 1)[1]
                    result[path4d.lower()] = (sname, tableSql, None)
                    for fldbag in tbag['fields'].values():
                        name4D, nameSql = self.fromNameAs(fldbag['name'])
                        path4d = '4D_[%s]%s' % (table4D, name4D)
                        result[path4d.lower()] = (sname, tableSql, nameSql)
            tablesbag = sbag['tablesGnr']
            if tablesbag:
                for tbag in tablesbag.values():
                    table4D, tableSql = self.fromNameAs(tbag['name'])
                    path4d = 'GNR_[%s]' % table4D
                    if tableSql in namesdict:
                        tableSql = tableSql + '_tbl'
                    if tableSql.startswith('%s_' % sname): #strip the area code from table name
                        tableSql = tableSql.lower().lstrip('_').split('_', 1)[1]
                    result[path4d.lower()] = (sname, tableSql, None)
                    for fldbag in tbag['fields'].values():
                        name4D, nameSql = self.fromNameAs(fldbag['name'])
                        path4d = 'GNR_[%s]%s' % (table4D, name4D)
                        result[path4d.lower()] = (sname, tableSql, nameSql)
        return result

    def build(self, configBag):
        for sname, sbag in self.folder4dstructBag.items():
            sname = sname.lower()
            area = self.buildArea(sname, sbag)
            if area: #if an area has no tables don't build the folder at all
                sqlstructfile = os.path.join(self.modelFolder(sname), 'config_db.xml')
                area.toXml(sqlstructfile)
                configBag.setItem('packages.%s' % sname, None, alias=sname)

    def buildArea(self, sname, sbag):
        result = DbModelSrc.makeRoot()
        pkg = result.package(name=sname)
        tablesbag = sbag['tables4d']
        exportArea = False
        if tablesbag:
            exportArea = True
            for tbag in tablesbag.values():
                self.buildTable(pkg, tbag)
        tablesbag = sbag['tablesGnr']
        if tablesbag:
            exportArea = True
            for tbag in tablesbag.values():
                self.buildTable(pkg, tbag, mode='GNR')
        if exportArea:
            return result

    def buildTable(self, pkg, tbag, mode='4D'):
        name4D, name = self.fromNameAs(tbag['name'])
        name = self.nameConverter(table=name4D, mode=mode)[1]
        name_short = name
        comment = 'imported from 4d %s' % name4D
        pkey4d = tbag['pkey.name4d']
        pkey = None
        if pkey4d:
            pkey = self.nameConverter(table=name4D, field=tbag['pkey.name4d'], mode=mode)[2]
        table = pkg.table(name=name, comment=comment,
                          name_short=name_short,
                          pkey=pkey)
        for fldbag in tbag['fields'].values():
            self.buildField(table, fldbag)
        if 'extrafields' in tbag:
            for fldbag in tbag['extrafields'].values():
                self.buildField(table, fldbag)

    def buildField(self, table, fldbag):
        name4D, name = self.fromNameAs(fldbag['name'])
        comment = 'imported from 4d %s' % name4D
        dtype = fldbag['type']
        len_max = None
        size = None
        if dtype.startswith('A'):
            len_max = dtype[1:].strip().strip('_')
            len_max = str(int(len_max) + 2)
            dtype = 'A'
            if len_max:
                size = '0:%s' % len_max
        fld = table.column(name, dtype=dtype, name_long=name4D, comment=comment,
                           unique=fldbag['unique'], indexed=fldbag['indexed'],
                           size=size)
        if fldbag['relate']:
            case_insensitive = False
            sqltarget = self.nameConverter(table=fldbag['relate.table4d'], field=fldbag['relate.field4d'])
            if sqltarget:
                if (dtype == 'A' and int(len_max) > 10 and sqltarget[2].lower() != 'sy_id'):
                    case_insensitive = True
            else: # no link to 4d table, try genro table
                sqltarget = self.nameConverter(table=fldbag['relate.tablegnr'], field=fldbag['relate.fieldgnr'],
                                               mode='GNR')
                case_insensitive = True
            if sqltarget:
                target = '%s.%s.%s' % (sqltarget[0], sqltarget[1], sqltarget[2])
                fld.relation(target)
            else:
                print "Error: missing field \n%s" % str(fldbag['relate'])


class GnrAppSync4D(GnrApp):
    
    def __init__(self, *args, **kwargs):
        self.sync4d_name = kwargs.pop('sync4d_name','sync4d')
        super(GnrAppSync4D,self).__init__(*args,**kwargs)
    
    def onIniting(self):
        basepath = self.config.getAttr('packages', 'path')
        if not basepath:
            basepath = os.path.normpath(os.path.join(self.instanceFolder, '..', '..', 'packages'))
        if not os.path.isdir(basepath):
            raise GnrSync4DException('missing package path')
        self.s4d = Struct4D(self, basepath)
        self.checkChanges = False
        if not self.config['packages']:
            self.rebuildRecipe()

    def onInited(self):
        self._startLog()
        gnrpkg = self.db.package('gnr')
        self.sync4d_timing = int(gnrpkg.getAttr('sync4d_timing', 0)) or 4
        self.area_zz = self.config.getAttr('packages', 'area_zz')
        self.transaction4d = TransactionManager4D(self, 'gnr')

    def _startLog(self):
        logdir = os.path.join(self.instanceFolder, 'logs')
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logfile = os.path.join(logdir, 'gnrsync4d.log')
        loghandler = TimedRotatingFileHandler(logfile, 'MIDNIGHT', 1, 28)
        loghandler.setLevel(logging.DEBUG)
        formatter = Formatter('%(asctime)s - %(name)-12s: %(levelname)-8s %(message)s')
        loghandler.setFormatter(formatter)

        rootlogger = logging.getLogger('')
        rootlogger.setLevel(logging.DEBUG)
        rootlogger.addHandler(loghandler)
        if 'admin' in self.db.packages:
            self.db.package('admin').mailLog(self.processName)

    def _get_processName(self):
        return 'sync4d daemon: %s' % self.instanceFolder
    processName = property(_get_processName)

    @property
    def folder4d(self):
        path = os.path.join(self.instanceFolder, self.sync4d_name)
        if not os.path.isdir(path):
            os.mkdir(path)
        return path
        


    def _get_folderdialog4d(self):
        path = os.path.join(self.folder4d, 'dialog4d')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    folderdialog4d = property(_get_folderdialog4d)

    def _get_folder4dDataIn(self):
        path = os.path.join(self.folder4d, 'data')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    folder4dDataIn = property(_get_folder4dDataIn)

    def _get_folder4dDataOut(self):
        path = os.path.join(self.folder4d, 'imported')
        if not os.path.isdir(path):
            os.mkdir(path)
        return path

    folder4dDataOut = property(_get_folder4dDataOut)

    def beforeLoop(self):
        if self.checkChanges:
            changes = self.db.checkDb()
            if changes:
                raise NotMatchingModelError('\n'.join(self.db.model.modelChanges))
        self.running = True

    def loop(self):
        self.beforeLoop()
        while self.running:
            self.do()
            time.sleep(self.sync4d_timing)

    def do(self):
        try:
            self.lookFor4dFiles()
            self.lookForBackSync()
            return True
        except:
            tb_text = errorLog(self.processName)
            gnrlogger.error(tb_text)
            raise

    def lookForBackSync(self):
        l = self.db.table('gnr.sync_out').query(columns='*',
                                                where="$client = :client",
                                                client='sync4d',
                                                order_by="$request", limit=10).fetch()
        while l:
            for t in l:
                self.syncOutTransaction(t)
            l = self.db.table('gnr.sync_out').query(columns='*',
                                                    where="$client = :client",
                                                    client='sync4d',
                                                    order_by="$request", limit=10).fetch()

    def syncOutTransaction(self, transaction):
        fname = '%s_%s_%s_%s.xml' % (transaction['request'].strftime('%Y-%m-%d_%H%M%S'),
                                     transaction['request'].microsecond,
                                     transaction['maintable'],
                                     transaction['action'])
        fname = os.path.join(self.folderdialog4d, 'test', fname)
        trbag = Bag()
        trbag['command'] = 'sync_in'
        trbag['maintable'] = transaction['maintable']
        trbag['action'] = transaction['action']
        trbag['data'] = Bag(transaction['data'])
        trbag.toXml(fname)
        self.db.table('gnr.sync_out').delete(transaction)
        self.db.commit()

    def lookFor4dFiles(self):
        dataInPath = self.folder4dDataIn
        folders = [f for f in os.listdir(dataInPath) if not f.startswith('.')]
        if folders:
            folders.sort()
            for folder in folders:
                self.importFolder(dataInPath, folder)
                if folder != datetime.date.today().strftime("%Y-%m-%d"):
                    path = os.path.join(dataInPath, folder)
                    l = os.listdir(path)
                    for f in l:
                        if f.startswith('.'): os.remove(os.path.join(path, f))
                    if not os.listdir(path):
                        os.rmdir(path)

    def importFolder(self, dataInPath, folder):
        folderpath = os.path.join(dataInPath, folder)
        names = [f for f in os.listdir(folderpath) if not f.startswith('.')]
        names.sort()
        for fname in names:
            fullname = os.path.join(folderpath, fname)
            self.importFile(fullname)
            dataOutPath = os.path.join(self.folder4dDataOut, folder)
            if not os.path.exists(dataOutPath):
                os.mkdir(dataOutPath)
            os.rename(fullname, os.path.join(dataOutPath, fname))


    def importFile(self, fullname):
        try:
            b = Bag(fullname)
        except:
            time.sleep(10) # 4D may be still writing the file, wait some seconds and try again
            b = Bag(fullname)
        if 'transaction' in b:
            for tr, attr in b.digest('#v,#a'):
                n = tr.getNode('trigger')
                attr.update(n.getAttr())
                self.writeTransaction(n.value, attr, file_name=fullname)
        else:
            self.writeImport(b, file_name=fullname)

    def writeTransaction(self, data, attr, file_name=None):
        if not data:
            return
        request_ts = None
        if attr.get('sy_date') and attr.get('sy_time'):
            request_ts = datetime.datetime.combine(attr.get('sy_date'), attr.get('sy_time'))

        if self.area_zz:
            pkg = self.area_zz
            tbl = attr['from'].lower()
        else:
            pkg, tbl = attr['from'].lower().lstrip('_').split('_', 1)
        self.setSubTriggerSchemata(data)

        self.transaction4d.writeTransaction(mode='sync', action=attr['mode'],
                                            maintable='%s.%s' % (pkg, tbl),
                                            data=data.toXml(),
                                            request_id=attr.get('sy_id'),
                                            file_name=file_name,
                                            queue_id='sync4d',
                                            request_ts=request_ts
                                            )
        gnrlogger.info("%s --> %s - %s" % (file_name, attr['mode'], '%s.%s' % (pkg, tbl)))

    def writeImport(self, b, file_name=None):
        if self.area_zz:
            pkg = self.area_zz
            tbl = b['FROM'].lower()
        else:
            pkg, tbl = b['FROM'].lower().lstrip('_').split('_', 1)
        self.transaction4d.writeTransaction(mode='import', action=b['MODE'],
                                            maintable='%s.%s' % (pkg, tbl),
                                            data=b['DATA'].toXml(),
                                            file_name=file_name,
                                            queue_id='sync4d'
                                            )
        gnrlogger.info("%s --> %s - %s" % (file_name, 'import', '%s.%s' % (pkg, tbl)))

    def setSubTriggerSchemata(self, data):
        for k, tr, attr in data.digest('#k,#v,#a'):
            if k != 'data':
                tbl = attr['from']
                if not '.' in tbl:
                    if self.area_zz:
                        pkg = self.area_zz
                        tbl = tbl.lower()
                    else:
                        pkg, tbl = tbl.lower().lstrip('_').split('_', 1)
                    attr['from'] = '%s.%s' % (pkg, tbl)
                self.setSubTriggerSchemata(tr)

    def rebuildRecipe(self):
        self.s4d.build(self.config)
        self.config.toXml(os.path.join(self.instanceFolder, 'instanceconfig.xml'))

    def importTable(self, tbl):
        if len(tbl) > 23:
            tbl = tbl[:23]
        cmdpath = os.path.join(self.folderdialog4d, 'exp_%s.xml' % tbl)
        b = Bag()
        b['command'] = 'Export4dTables'
        b['t4d.tbl'] = tbl
        b.toXml(cmdpath)

    def firstImport(self):
        tables = self.s4d.get4dTables()
        tables.sort()
        for tbl in tables:
            self.importTable(tbl)
            
            
            