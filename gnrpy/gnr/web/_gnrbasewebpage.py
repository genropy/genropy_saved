# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#_gnrbasewebpage.py

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os
import sys
import time
import traceback
import urllib

import logging

gnrlogger = logging.getLogger(__name__)

try:
    import json
except:
    import simplejson as json

from gnr.core.gnrbag import Bag, TraceBackResolver
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrlang import GnrObject
from gnr.core.gnrstring import  toJson
from gnr.core import gnrdate

from gnr.sql.gnrsql_exceptions import GnrSqlSaveException, GnrSqlDeleteException

AUTH_OK = 0
AUTH_NOT_LOGGED = 1
AUTH_FORBIDDEN = -1

class GnrWebClientError(Exception):
    pass
    
class GnrWebServerError(Exception):
    pass
    
class GnrBaseWebPage(GnrObject):
    """TODO"""
    def newCookie(self, name, value, **kw):
        """TODO
        
        :param name: TODO
        :param value: TODO"""
        return self.request.newCookie(name, value, **kw)
        
    def newMarshalCookie(self, name, value, secret=None, **kw):
        """TODO
        
        :param name: TODO
        :param value: TODO
        :param secret: TODO"""
        return self.request.newMarshalCookie(name, value, secret=secret, **kw)
        
    def get_cookie(self, cookieName, cookieType, secret=None, path=None):
        """TODO
        
        :param cookieName: TODO
        :param cookieType: TODO
        :param secret: TODO
        :param path: TODO"""
        return self.request.get_cookie(cookieName, cookieType, secret=secret, path=path)
        
    def add_cookie(self, cookie):
        """TODO
        
        :param cookie: TODO"""
        self.response.add_cookie(cookie)
        
    def _get_clientContext(self):
        cookie = self.get_cookie('genroContext', 'simple')
        if cookie:
            return Bag(urllib.unquote(cookie.value))
        else:
            return Bag()
            
    def _set_clientContext(self, bag):
        value = urllib.quote(bag.toXml())
        cookie = self.get_cookie('genroContext', 'simple', path=self.site.default_uri)
        cookie.value = value
        self.add_cookie(cookie)
        
    clientContext = property(_get_clientContext, _set_clientContext)
        
    def _get_filename(self):
        try:
            return self._filename
        except AttributeError:
            self._filename = os.path.basename(self.filepath)
            return self._filename
            
    filename = property(_get_filename)
        
    def _get_canonical_filename(self):
        return self.filename
        
    canonical_filename = property(_get_canonical_filename)
    
    @public_method
    def decodeDatePeriod(self, datestr, workdate=None, locale=None):
        """TODO
        
        :param datestr: a date string. For the string format, please check the :meth:`decodeDatePeriod()
        <gnr.core.gnrdate.decodeDatePeriod>` method docstrings
        :param workdate: the :ref:`workdate`
        :param locale: the current locale (e.g: en, en_us, it)"""
        workdate = workdate or self.workdate
        locale = locale or self.locale
        period = datestr
        valid = False
        try:
            returnDate = gnrdate.decodeDatePeriod(datestr, workdate=workdate, locale=locale, returnDate=True)
            valid = True
        except:
            returnDate = (None, None)
            period = None
        result = Bag()
        result['from'] = returnDate[0]
        result['to'] = returnDate[1]
        result['prev_from'] = gnrdate.dateLastYear(returnDate[0])
        result['prev_to'] = gnrdate.dateLastYear(returnDate[1])
        result['period'] = period
        result['valid'] = valid
        result['period_string'] = gnrdate.periodCaption(locale=locale, *returnDate)
        return result
        
    def mixins(self):
        """Implement this method in your page for mixin the page with methods from the
        public :ref:`public_resources` folder
        
        :returns: a list of mixin names with the following syntax: ``moduleName:className``"""
        return []
        
    def requestWrite(self, txt, encoding='utf-8'):
        """TODO
        
        :param txt: TODO
        :param encoding: the encoding type"""
        self.responseWrite(txt, encoding=encoding)
        
    def responseWrite(self, txt, encoding='utf-8'):
        """TODO
        
        :param txt: TODO
        :param encoding: the encoding type"""
        self.response.write(txt.encode(encoding))
        
    def _get_siteStatus(self):
        if not hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            
            if os.path.isfile(path):
                self._siteStatus = Bag(path)
            else:
                self._siteStatus = Bag()
        return self._siteStatus
        
    siteStatus = property(_get_siteStatus)
        
    def siteStatusSave(self):
        """TODO"""
        if hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            self._siteStatus.toXml(path)
            
    def pageLocalDocument(self, docname, page_id=None):
        """TODO
        
        :param docname: TODO
        :param page_id: TODO"""
        page_id = page_id or self.page_id
        folder = os.path.join(self.connectionFolder, page_id)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return os.path.join(folder, docname)
        
    def freezeSelection(self, selection, name):
        """TODO
        
        :param selection: TODO
        :param name: TODO"""
        path = self.pageLocalDocument(name)
        selection.freeze(path, autocreate=True)
        return path
        
    def unfreezeSelection(self, dbtable=None, name=None, page_id=None):
        """TODO
        
        :param dbtable: specify the :ref:`database table <table>`. More information in the
                        :ref:`dbtable` section (:ref:`dbselect_examples_simple`)
        :param name: TODO
        :param page_id: TODO"""
        assert name, 'name is mandatory'
        if isinstance(dbtable, basestring):
            dbtable = self.db.table(dbtable)
        selection = self.db.unfreezeSelection(self.pageLocalDocument(name,page_id=page_id))
        if dbtable and selection is not None:
            assert dbtable == selection.dbtable, 'unfrozen selection does not belong to the given table'
        return selection
    
    @public_method
    def getUserSelection(self, selectionName=None, selectedRowidx=None, filterCb=None, columns=None,
                         sortBy=None,condition=None, table=None, condition_args=None):
        """TODO
        
        :param selectionName: TODO
        :param selectedRowidx: TODO
        :param filterCb: TODO
        :param columns: it represents the :ref:`columns` to be returned by the "SELECT"
                        clause in the traditional sql query. For more information, check the
                        :ref:`sql_columns` section
        :param condition: set a :ref:`sql_condition` for the selection
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param condition_args: the arguments of the *condition* parameter. Their syntax
                               is ``condition_`` followed by the name of the argument"""
        # table is for checking if the selection belong to the table
        assert selectionName, 'selectionName is mandatory'
        page_id = self.sourcepage_id or self.page_id
        if isinstance(table, basestring):
            table = self.db.table(table)
        selection = self.unfreezeSelection(dbtable=table, name=selectionName,page_id=page_id)
        table = table or selection.dbtable
        if filterCb:
            filterCb = self.getPublicMethod('rpc',filterCb)
            selection.filter(filterCb)
        elif selectedRowidx:
            if isinstance(selectedRowidx, basestring):
                selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
                selectedRowidx = set(selectedRowidx) #use uniquify (gnrlang) instead
            selection.filter(lambda r: r['rowidx'] in selectedRowidx)
        if sortBy:
            selection.sort(sortBy)
        if not columns:
            return selection
        if columns=='pkey':
            return selection.output('pkeylist')
        condition_args = condition_args or {}
        pkeys = selection.output('pkeylist')
        where = 't0.%s in :pkeys' % table.pkey
        if condition:
            where = '%s AND %s' % (where, condition)
        selection = table.query(columns=columns, where=where,
                                pkeys=pkeys, addPkeyColumn=False,
                                excludeDraft=False,
                                **condition_args).selection()
        return selection
        
    def getAbsoluteUrl(self, path, **kwargs):
        """Get TODO. Return an external link to the page
        
        :param path: the path to the page from the :ref:`sites_pages` folder
                     of a :ref:`project`"""
        return self.request.construct_url(self.getDomainUrl(path, **kwargs))
        
    def resolvePathAsUrl(self, *args, **kwargs):
        """TODO"""
        return self.diskPathToUri(self.resolvePath(*args, **kwargs))
        
    def resolvePath(self, *args, **kwargs):
        """TODO"""
        folder = kwargs.pop('folder', None)
        sitefolder = self.siteFolder
        if folder == '*data':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', *args)
            return diskpath
        elif folder == '*users':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', '_users', *args)
            return diskpath
        elif folder == '*home':
            diskpath = os.path.join(sitefolder, 'pages', '..', 'data', '_users', self.user, *args)
            return diskpath
        elif folder == '*pages':
            diskpath = os.path.join(sitefolder, 'pages', *args)
        elif folder == '*lib':
            diskpath = os.path.join(sitefolder, 'pages', '_lib', *args)
        elif folder == '*static':
            diskpath = os.path.join(sitefolder, 'pages', 'static', *args)
        else:
            diskpath = os.path.join(os.path.dirname(self.filename), *args)
        diskpath = os.path.normpath(diskpath)
        return diskpath
        
    def diskPathToUri(self, tofile, fromfile=None):
        """TODO
        
        :param tofile: TODO
        :param fromfile: TODO"""
        fromfile = fromfile or self.filename
        pagesfolder = self.folders['pages']
        relUrl = tofile.replace(pagesfolder, '').lstrip('/')
        path = fromfile.replace(pagesfolder, '')
        rp = '../' * (len(path.split('/')) - 1)
        
        path_info = self.request.path_info
        if path_info: # != '/index'
            rp = rp + '../' * (len(path_info.split('/')) - 1)
        return '%s%s' % (rp, relUrl)
        
    def _get_siteName(self):
        return os.path.basename(self.siteFolder.rstrip('/'))
        
    siteName = property(_get_siteName)
        
    def _get_dbconnection(self):
        if not self._dbconnection:
            self._dbconnection = self.db.adapter.connect()
        return
        
    dbconnection = property(_get_dbconnection)
        
    def _get_packages(self):
        return self.db.packages
        
    packages = property(_get_packages)
    
    @property
    def package(self):
        """TODO"""
        pkgId = self.packageId
        if pkgId:
            return self.db.package(pkgId)
            
        
    def _get_tblobj(self):
        if self.maintable:
            return self.db.table(self.maintable)
            
    tblobj = property(_get_tblobj)
        
    def formSaver(self, formId, table=None, method=None, _fired='', datapath=None,
                  resultPath='dummy', changesOnly=True, onSaving=None, onSaved=None, saveAlways=False, **kwargs):
        """TODO
        
        :param formId: the id of the :ref:`form`
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param method: TODO
        :param _fired: TODO
        :param datapath: the :ref:`datapath` form
        :param resultPath: TODO
        :param changesOnly: boolean. TODO
        :param onSaving: TODO
        :param onSaved: TODO 
        :param saveAlways: boolean. TODO"""
        method = method or 'saveRecordCluster'
        controller = self.pageController()
        data = '==genro.getFormCluster("%s");'
        onSaved = onSaved or ''
        _onCalling = kwargs.pop('_onCalling', None)
        if onSaving:
            _onCalling = """var currform = genro.formById("%s");
                            var onSavingCb = function(record,form){%s};
                             %s
                            var result = onSavingCb.call(this, data.getItem('record'), currform);
                            if(result===false){
                                currform.status = null;
                                return false;
                            }else if(result instanceof gnr.GnrBag){
                                $1.data.setItem('record',result);
                            }""" % (formId, onSaving, _onCalling or '')
                            
        _onError = """var cb = function(){genro.formById("%s").status=null;};
                    genro.dlg.ask(kwargs._errorTitle,error,{"confirm":"Confirm"},
                                  {"confirm":cb});""" % formId
        if changesOnly:
            data = '==genro.getFormChanges("%s");'
        controller.dataController('genro.formById("%s").save(always)' % formId, _fired=_fired,
                                  datapath=datapath, always=saveAlways)
        kwargs['fireModifiers'] = _fired.replace('^', '=')
        controller.dataRpc(resultPath, method=method, nodeId='%s_saver' % formId, _POST=True,
                           datapath=datapath, data=data % formId, _onCalling=_onCalling,
                           _onResult='genro.formById("%s").saved();%s;' % (formId, onSaved),
                           _onError=_onError, _errorTitle='!!Saving error',
                           table=table, **kwargs)
                           
    def formLoader(self, formId, resultPath, table=None, pkey=None, datapath=None,
                   _fired=None, loadOnStart=False, lock=False,
                   method=None, onLoading=None, onLoaded=None, loadingParameters=None, **kwargs):
        """TODO
        
        :param formId: the id of the :ref:`form`
        :param resultPath: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`
        :param datapath: the :ref:`datapath` form
        :param _fired: TODO
        :param loadOnStart: boolean TODO
        :param lock: boolean. TODO
        :param method: TODO
        :param onLoading: TODO
        :param onLoaded: TODO
        :param loadingParameters: TODO"""
        pkey = pkey or '*newrecord*'
        method = method or 'loadRecordCluster'
        onResultScripts = []
        onResultScripts.append('genro.formById("%s").loaded()' % formId)
        if onLoaded:
            onResultScripts.append(onLoaded)
        loadingParameters = loadingParameters or '=gnr.tables.maintable.loadingParameters'
        controller = self.pageController()
        controller.dataController('genro.formById(_formId).load();',
                                  _fired=_fired, _onStart=loadOnStart, _delay=1, _formId=formId,
                                  datapath=datapath)
                                  
        controller.dataRpc(resultPath, method=method, pkey=pkey, table=table,
                           nodeId='%s_loader' % formId, datapath=datapath, _onCalling=onLoading,
                           _onResult=';'.join(onResultScripts), lock=lock,
                           loadingParameters=loadingParameters,
                           virtual_columns='==genro.formById(_formId).getVirtualColumns()',
                           _formId=formId, **kwargs)
                           
    @public_method                      
    def loadRecordCluster(self, table=None, pkey=None, recordGetter='app.getRecord', **kwargs):
        """TODO
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`
        :param recordGetter: TODO"""
        table = table or self.maintable
        getterHandler = self.getPublicMethod('rpc', recordGetter)
        record, recinfo = getterHandler(table=table, pkey=pkey, **kwargs)
        return record, recinfo
    
    @public_method
    def saveRecordCluster(self, data, table=None, _nocommit=False, rowcaption=None, _autoreload=False,
                          onSavingHandler=None, onSavedHandler=None,**kwargs):
        """TODO
        
        :param data: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param rowcaption: the textual representation of a record in a user query.
                           For more information, check the :ref:`rowcaption` section
        :param onSavingHandler: TODO
        :param onSavedHandler: TODO
        """
        #resultAttr = None #todo define what we put into resultAttr
        resultAttr = {}
        gridsChanges = data.pop('grids')
        onSavingMethod = 'onSaving'
        onSavedMethod = 'onSaved'
        maintable = getattr(self, 'maintable')
        table = table or maintable
        tblobj = self.db.table(table)
        if table != maintable:
            onSavingMethod = 'onSaving_%s' % table.replace('.', '_')
            onSavedMethod = 'onSaved_%s' % table.replace('.', '_')
        onSavingHandler =  self.getPublicMethod('rpc', onSavingHandler) if onSavingHandler else getattr(self, onSavingMethod, None)
        onSavedHandler = self.getPublicMethod('rpc', onSavedHandler) if onSavedHandler else getattr(self, onSavedMethod, None)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        promisedFields = dict()
        if recordClusterAttr.get('_newrecord'):
            for k, promised in recordCluster.digest('#k,#a.promised'):
                if promised:
                    promisedFields[k] = recordCluster.pop(k)
        onSavedKwargs = dict()
        if onSavingHandler:
            onSavedKwargs = onSavingHandler(recordCluster, recordClusterAttr, resultAttr=resultAttr) or {}
        virtual_columns = self.pageStore().getItem('tables.%s.virtual_columns' % table)
        if virtual_columns:
            for virtual_col in virtual_columns.keys():
                recordCluster.pop(virtual_col, None)
        record = tblobj.writeRecordCluster(recordCluster, recordClusterAttr)
        if gridsChanges:
            fkey = record[tblobj.pkey]
            for gridchange in gridsChanges:
                grid_changeset = gridchange.value
                if recordClusterAttr.get('_newrecord'):
                    if grid_changeset['inserted']:
                        for row in grid_changeset['inserted'].values():
                            for k,v in row.items():
                                if v == '*newrecord*':
                                    row[k] = fkey
                self.app.saveEditedRows(table=gridchange.attr['table'],changeset=grid_changeset,commit=False)
        if promisedFields:
            msg = ['Saved record']
            for f in promisedFields:
                if promisedFields[f]!=record[f]:
                    pars = getattr(tblobj,'counter_%s' %f)()
                    fieldname = tblobj.column(f).name_long or f
                    fieldname.replace('!!','')
                    msgpars = dict(sequence=record[f],promised_sequence=promisedFields[f],fieldname=fieldname)
                    msg.append(dict(message=pars.get('message_failed',"!!%(fieldname)s: %(sequence)s instead of %(promised_sequence)s") %msgpars,messageType='warning'))
            resultAttr['saved_message'] = msg
                
        if onSavedHandler:
            onSavedHandler(record, resultAttr=resultAttr, **onSavedKwargs)
        if not _nocommit:
            self.db.commit()
        if not 'caption' in resultAttr:
            resultAttr['caption'] = tblobj.recordCaption(record, rowcaption=rowcaption)
        pkey = record[tblobj.pkey]
        resultAttr['lastTS'] = str(record[tblobj.lastTS]) if tblobj.lastTS else None
        for k,v in recordClusterAttr.items():
            if k.startswith('lastTS_'):
                resultAttr[k] = v
        if _autoreload:
            result = Bag()
            result.setItem('pkey',pkey,**resultAttr)
            keyToLoad=pkey if _autoreload  is  True else _autoreload
            if keyToLoad!='*dismiss*':
                record,recInfo = self.app.getRecord(pkey=keyToLoad,table=table)
                result.setItem('loadedRecord',record,**recInfo)
            return result
        else:
            return (pkey, resultAttr)
            
    @public_method    
    def deleteRecordCluster(self, data, table=None, **kwargs):
        """TODO
        
        :param data: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)"""
        maintable = getattr(self, 'maintable')
        table = table or maintable
        tblobj = self.db.table(table)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        try: #try:
            self.onDeleting(recordCluster, recordClusterAttr)
            recordClusterAttr['_deleterecord'] = True
            record = tblobj.writeRecordCluster(recordCluster, recordClusterAttr)
            self.onDeleted(record)
            self.db.commit()
            return 'ok'
        except GnrSqlDeleteException, e:
            return ('delete_error', {'msg': e.message})
    
    @public_method
    def deleteDbRow(self, table, pkey=None, **kwargs):
        """Method for deleting a single record from a given table
        
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`
        :returns: if it works, returns the primary key and the deleted attribute.
                  Else, return an exception"""
        try:
            tblobj = self.db.table(table)
            record = tblobj.record(pkey, for_update=True).output('record')
            deleteAttr = dict()
            self.onDeleting(record, deleteAttr)
            tblobj.delete(record)
            self.onDeleted(record)
            self.db.commit()
            return pkey, deleteAttr
        except GnrSqlDeleteException, e:
            return ('delete_error', {'msg': e.message})
            
    def setLoadingParameters(self, table, **kwargs):
        """
        .. warning:: deprecated since version 0.7. It has been replaced through the :ref:`th`
                     component. For more information, check the explanation about the **handler** level in
                     the :ref:`th_map_form_data` documentation section
        
        .. note:: **old documentation:**
                  
                  Set parameters at the path ``gnr.tables.TABLE.loadingParameters.PARAMETERNAME``,
                  where:
                  
                  * ``TABLE`` is the value you define for the *table* parameter
                  * ``PARAMETERNAME`` is the name you gave to the parameter.
                  
                  :param table: MANDATORY - string. You can put the following strings:
                  
                                * *maintable*: set a parameter value of a column of the table you define in the
                                  :ref:`maintable` :ref:`webpage variable <webpages_variables>`
                                
                                      **Example:** if you have a package called ``agenda`` and a :ref:`table`
                                      called ``staff`` and write in your :ref:`webpage`::
                                      
                                          maintable='staff'
                                          self.setLoadingParameters(table='maintable',price='10000')
                                          
                                      then you will find the value ``10000`` at the path:
                                      ``gnr.tables.maintable.loadingParameters.price``
                                  
                                * *PACKAGENAME.TABLENAME*: set a parameter value of a column in the table called
                                  ``TABLENAME`` of the package ``PACKAGENAME`` at the path
                                  ``gnr.tables.PACKAGENAME_TABLENAME.loadingParameters.PARAMETERNAME``, where 
                                  ``PARAMETERNAME`` is the name you gave to the parameter.
                                  
                                      **Example:** if you have a package called ``agenda`` and a :ref:`table`
                                      called ``staff`` and write in your :ref:`webpage`::
                                      
                                          self.setLoadingParameters(table='agenda.staff',price='10000')
                                          
                                      then you will find the value ``10000`` at the path:
                                      ``gnr.tables.agenda_staff.loadingParameters.price``
        """
        self.pageSource().dataFormula('gnr.tables.%s.loadingParameters' % table.replace('.', '_'),
                                      '', _onStart=True, **kwargs)
                                      
    def toJson(self, obj):
        """Return the object into Json form
        
        :param obj: the object"""
        return toJson(obj)
        
    def setOnBeforeUnload(self, root, cb, msg):
        """TODO
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` documentation section
        :param cb: TODO
        :param msg: TODO"""
        root.script("""genro.checkBeforeUnload = function(e){
                       if (%s){
                           return "%s";
                       }
                }""" % (cb, self._(msg)))
                
    def mainLeftContent(self, parentBC, **kwargs):
        """The main left content of the page
        
        :param parentBC: the root parent :ref:`bordercontainer`"""
        pass
        
    def pageController(self, **kwargs):
        """TODO
        
        :returns: TODO"""
        return self.pageSource().dataController(**kwargs)
        
    def pageSource(self, nodeId=None):
        """TODO
        
        :param nodeId: the page nodeId. For more information, check the :ref:`nodeid`
                       documentation page."""
        if nodeId:
            return self._root.nodeById(nodeId)
        else:
            return self._root
            
    def rootWidget(self, root, **kwargs):
        """Return a :ref:`contentpane`. You can attach to it any :ref:`webpage element
        <webpage_elements_index>`. You can override this method to receive a different
        :ref:`layout widget <layout>` respect to the ``contentPane``
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` section"""
        return root.contentPane(**kwargs)
        
    def main(self, root, **kwargs):
        """The main method of a webpage. You must override this method unless you're using an
        :ref:`components_active`. For more information, check the :ref:`webpages_main`
        documentation section
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` section"""
        root.h1('You MUST override this main method!!!')
        
    def forbiddenPage(self, root, **kwargs):
        """TODO
        
        :param root: the root of the page. For more information, check the
                     :ref:`webpages_main` section"""
        dlg = root.dialog(toggle="fade", toggleDuration=250, onCreated='widget.show();')
        #f = dlg.form()
        #f.div(content='Forbidden Page', text_align="center", font_size='24pt')
        tbl = dlg.contentPane(_class='dojoDialogInner').table()
        row = tbl.tr()
        row.td(content='Sorry. You are not allowed to use this page.', align="center", font_size='16pt',
               color='#c90031')
        cell = tbl.tr().td()
        cell.div(float='right', padding='2px').button('Back', action='genro.pageBack()')
        
    def windowTitle(self):
        """Return the window title"""
        return os.path.splitext(os.path.basename(self.filename))[0].replace('_', ' ').capitalize()
        
    def _errorPage(self, err, method=None, kwargs=None):
        page = self.domSrcFactory.makeRoot(self)
        sc = page.stackContainer(height='80ex', width='50em', selected='^_dev.traceback.page')
        p1 = sc.contentPane(background_color='silver')
        #msc=sc.menu()
        #msc.menuline('Close traceback',action='genro.wdgById("traceback_main").hide()')
        p1.div(
                'Sorry: an error occurred on server while executing the method:<br> %s <br><br>Check parameters before executing again last command.' % method
                ,
                text_align='center', padding='1em', font_size='2em', color='gray', margin='auto')
        p1.button(label='See errors', action='FIRE _dev.traceback.page=1', position='absolute', bottom='1em',
                  right='1em')
        accordion = sc.accordionContainer()
        accordion.accordionPane(title='traceback').div(border='1px solid gray', background_color='silver', padding='5px'
                                                       , margin_top='3em').pre(traceback.format_exc())
        errBag = TraceBackResolver()()
        for k, tb in errBag.items():
            currpane = accordion.accordionPane(title=k)
            currpane.div(tb['line'], font_size='1.2em', margin='4px')
            tbl = currpane.table(_class='bagAttributesTable').tbody()
            for node in tb['locals'].nodes:
                v = node.getStaticValue()
                tr = tbl.tr()
                tr.td(node.label, align='right')
                try:
                    if not isinstance(v, basestring):
                        v = str(v)
                    if not isinstance(v, unicode):
                        v = v.decode('ascii', 'ignore')
                except:
                    v = 'unicode error'
                tr.td(v.encode('ascii', 'ignore'))
        return page
    
    @public_method    
    def resolverRecall(self, resolverPars=None, **auxkwargs):
        """TODO
        
        :param resolverPars: TODO"""
        if isinstance(resolverPars, basestring):
            resolverPars = json.loads(resolverPars) #should never happen
        resolverclass = resolverPars['resolverclass']
        resolvermodule = resolverPars['resolvermodule']
        
        args = resolverPars['args'] or []
        kwargs = {}
        for k, v in (resolverPars['kwargs'] or {}).items():
            k = str(k)
            if k.startswith('_serialized_'):
                pool, k = k.replace('_serialized_', '').split('_')
                v = getattr(self, pool)[v]
            kwargs[k] = v
        kwargs.update(auxkwargs)
        self.response.content_type = "text/xml"
        resolverclass = str(resolverclass)
        resolver = None
        if resolverclass in globals():
            resolver = globals()[resolverclass](*args, **kwargs)
        else:
            resolver = getattr(sys.modules[resolvermodule], resolverclass)(*args, **kwargs)
        if resolver is not None:
            resolver._page = self
            return resolver()
    
    @public_method    
    def resetApp(self, **kwargs):
        """TODO"""
        self.siteStatus['resetTime'] = time.time()
        self.siteStatusSave()
    
    @public_method
    def applyChangesToDb(self, **kwargs):
        """TODO"""
        return self._checkDb(applychanges=True)
        
    @public_method    
    def checkDb(self):
        """TODO"""
        return self._checkDb(applychanges=False)
        
    def _checkDb(self, applychanges=False, changePath=None, **kwargs):
        changes = self.db.checkDb()
        if applychanges:
            if changePath:
                changes = self.db.model.modelBagChanges.getAttr(changePath, 'changes')
                self.db.execute(changes)
            else:
                for x in self.db.model.modelChanges:
                    self.db.execute(x)
            self.db.commit()
            self.db.checkDb()
        return self.db.model.modelBagChanges
    
    @public_method
    def tableStatus(self, **kwargs):
        """TODO"""
        strbag = self._checkDb(applychanges=False)
        for pkgname, pkg in self.db.packages.items():
            for tablename in pkg.tables.keys():
                records = self.db.query('%s.%s' % (pkgname, tablename)).count()
                strbag.setAttr('%s.%s' % (pkgname, tablename), recordsnum=records)
        return strbag
        
    def createFileInData(self, *args):
        """TODO"""
        if args:
            path = os.path.join(self.siteFolder, 'data', *args)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile = file(path, 'w')
            return outfile
            
    def createFileInStatic(self, *args):
        """TODO"""
        if args:
            path = os.path.join(self.siteFolder, 'pages', 'static', *args)
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile = file(path, 'w')
            return outfile
            
    def createFolderInData(self, *args):
        """TODO"""
        if args:
            path = os.path.join(self.siteFolder, 'data', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path
            
    def createFolderInStatic(self, *args):
        """TODO"""
        if args:
            path = os.path.join(self.siteFolder, 'pages', 'static', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path