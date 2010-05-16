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


"""
core.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import os
import sys
import time
import traceback
import urllib


#from decimal import Decimal

from gnr.core.gnrlog import gnrlogging

gnrlogger = gnrlogging.getLogger('gnr.web.gnrwebcore')


#from mako.template import Template
try:
    import json
except:
    import simplejson as json

from gnr.core.gnrbag import Bag, TraceBackResolver

from gnr.core.gnrlang import GnrObject
from gnr.core.gnrstring import  toText, toJson
from gnr.core import gnrdate

from gnr.sql.gnrsql_exceptions import GnrSqlSaveException,GnrSqlDeleteException

AUTH_OK=0
AUTH_NOT_LOGGED=1
AUTH_FORBIDDEN=-1


class GnrWebClientError(Exception):
    pass

class GnrWebServerError(Exception):
    pass


class GnrBaseWebPage(GnrObject):
    
    
    def newCookie(self, name, value, **kw):
        return self.request.newCookie(name, value, **kw)
        
    def newMarshalCookie(self, name, value, secret=None, **kw):
        return self.request.newMarshalCookie(name,value,secret=secret,**kw)

        
    def get_cookie(self, cookieName, cookieType, secret = None,  path=None):
        return self.request.get_cookie(cookieName, cookieType,
                                    secret = secret,  path =path)

    def add_cookie(self,cookie):
        self.response.add_cookie(cookie)

    def get_session(self, **kwargs):
        session = self.request._request.environ['beaker.session']
        return session
        
    def _get_clientContext(self):
        cookie=self.get_cookie('genroContext','simple')
        if cookie:
            return Bag(urllib.unquote(cookie.value))
        else:
            return Bag()
    
    def _set_clientContext(self,bag):
        value=urllib.quote(bag.toXml())
        cookie=self.get_cookie('genroContext','simple', path=self.site.default_uri)
        cookie.value = value
        self.add_cookie(cookie)
        
    clientContext = property(_get_clientContext,_set_clientContext)
        
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
    

    
    def rpc_decodeDatePeriod(self, datestr, workdate=None, locale=None):
        workdate = workdate or self.workdate
        locale = locale or self.locale
        period=datestr
        valid=False
        try:
            returnDate = gnrdate.decodeDatePeriod(datestr, workdate=workdate, locale=locale, returnDate=True)
            valid=True
        except:
            returnDate = (None, None)
            period=None
        result = Bag()
        result['from'] = returnDate[0]
        result['to'] = returnDate[1]
        result['prev_from'] = gnrdate.dateLastYear(returnDate[0])
        result['prev_to'] = gnrdate.dateLastYear(returnDate[1])
        result['period'] = period
        result['valid']=valid
        result['period_string'] = gnrdate.periodCaption(locale=locale,*returnDate)
        return result
    
    def rpc_ping(self, **kwargs):
        pass
    
    def rpc_setInServer(self, path, value=None, **kwargs):
        self.session.modifyPageData(path, value)
    
    def rpc_setViewColumns(self, contextTable=None, gridId=None, relation_path=None, contextName=None, query_columns=None, **kwargs):
        self.app.setContextJoinColumns(table=contextTable, contextName=contextName, reason=gridId,
                                       path=relation_path, columns=query_columns)
    
    
    def mixins(self):
        """Implement this method in your page for mixin the page with methods from the local _resources folder
        @return: list of mixin names, moduleName:className"""
        return []
        
    def requestWrite(self, txt, encoding='utf-8'):
        self.responseWrite(txt,encoding=encoding)

    def responseWrite(self, txt, encoding='utf-8'):
        self.response.write(txt.encode(encoding))



    def _get_siteStatus(self):
        if not hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            
            if os.path.isfile(path):
                self._siteStatus=Bag(path)
            else:
                self._siteStatus=Bag()
        return self._siteStatus
    siteStatus = property(_get_siteStatus)
    
    def siteStatusSave(self):
        if hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            self._siteStatus.toXml(path)
        
    def pageAuthTags(self, method=None, **kwargs):
        return ""
    
    def rpc_doLogin(self, login=None, guestName=None, **kwargs):
        """Service method that set user's avatar into its connection if
        - The user exists and his password is correct.
        - The user is guest
        """
        loginPars={}
        if guestName:
            avatar = self.application.getAvatar(guestName)
        else:
            avatar = self.application.getAvatar(login['user'], password=login['password'], authenticate=True,page=self)
        if avatar:
            if not self.connection.cookie:
                self.connection.initConnection()
            #if not self.user:
            #    connection=self.connection
            #    self._user = self.connection.cookie_data.get('user')
            self.avatar = avatar
            self._user = avatar.id
            self.connection.updateAvatar(avatar)
            self.site.onAuthenticated(avatar)
            login['message'] = ''
            loginPars=avatar.loginPars
        else:
            login['message'] = 'invalid login'
        return (login,loginPars)


        
    def _checkAuth(self, method=None, **parameters):
        auth = AUTH_OK
        pageTags = self.pageAuthTags(method=method, **parameters)
        if pageTags:
            if not self.user:
                if not self.connection.cookie:
                    self.connection.initConnection()
                self._user = self.connection.cookie_data.get('user')
            if not self.user:
                auth = AUTH_NOT_LOGGED
            elif not self.application.checkResourcePermission(pageTags, self.userTags):
                auth = AUTH_FORBIDDEN
                
            if auth == AUTH_NOT_LOGGED and method != 'main':# and method!='onClosePage':
                if not self.connection.oldcookie:
                    pass
                    #self.raiseUnauthorized()
                auth = 'EXPIRED'
                
        elif parameters.get('_loginRequired') == 'y':
            auth = AUTH_NOT_LOGGED
        return auth
        
    def pageLocalDocument(self, docname):
        folder = os.path.join(self.connectionFolder, self.page_id)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return os.path.join(folder, docname)
    
    def freezeSelection(self, selection, name):
        selection.freeze(self.pageLocalDocument(name), autocreate=True)
        
    def unfreezeSelection(self, dbtable=None, name=None):
        assert name,'name is mandatory'
        if isinstance(dbtable, basestring):
            dbtable = self.db.table(dbtable)
        selection = self.db.unfreezeSelection(self.pageLocalDocument(name))
        if dbtable:
            assert dbtable == selection.dbtable, 'unfrozen selection does not belong to the given table'
        return selection
    
    def getUserSelection(self, selectionName=None, selectedRowidx=None,filterCb=None,columns=None,
                          condition=None, table=None,condition_args=None):
        # table is for checking if the selection belong to the table
        assert selectionName,'selectionName is mandatory'
        if isinstance(table, basestring):
            table = self.db.table(table)
        selection = self.unfreezeSelection(dbtable=table, name=selectionName)
        table = table or selection.dbtable 
        if filterCb:
            filterCb=getattr(self, 'rpc_%s' %filterCb)
            selection.filter(filterCb)
        elif selectedRowidx:
            if isinstance(selectedRowidx, basestring):
                selectedRowidx = [int(x) for x  in selectedRowidx.split(',')]
                selectedRowidx = set(selectedRowidx) #use uniquify (gnrlang) instead
            selection.filter(lambda r: r['rowidx'] in selectedRowidx)
        if columns:
            condition_args=condition_args or {}
            pkeys = selection.output('pkeylist')
            where = 't0.%s in :pkeys' %table.pkey
            if condition:
                where = '%s AND %s' % (where,condition)
            selection = table.query(columns=columns,where=where,
                                    pkeys=pkeys,addPkeyColumn=False,
                                    **condition_args).selection()
        return selection
        
    def _get_pageArgs(self):
        return self.session.pagedata['pageArgs'] or {}
    pageArgs = property(_get_pageArgs)
    
    def rpc_updateSessionContext(self, context, path, evt, value=None, attr=None):
        self.session.loadSessionData()
        self.session.setInPageData('context.%s.%s' % (context, path), value, attr)
        self.session.saveSessionData()
        
    def setInClientData(self, _client_path, value, _attributes=None, page_id=None, connection_id=None, fired=False, save=False, **kwargs):
        """@param save: remember to save on the last setInClientData. The first call to setInClientData implicitly lock the session util 
                        setInClientData is called with save=True
        """
        _attributes = dict(_attributes or {})
        _attributes.update(kwargs)
        _attributes['_client_path'] = _client_path
        if connection_id == None or connection_id==self.connection.connection_id:
            self.session.setInPageData('_clientDataChanges.%s' % _client_path.replace('.','_'), 
                                        value, _attributes=_attributes, page_id=page_id)
            if save: self.session.saveSessionData()
        else:
            pass
    
    def sendMessage(self,message):
        self.setInClientData('gnr.servermsg', message, fired=True, save=True,
                            src_page_id=self.page_id,src_user=self.user,src_connection_id=self.connection.connection_id)
   
    def _get_catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = self.application.catalog
        return self._catalog
    catalog = property(_get_catalog)
    
    def _set_locale(self, val):
        self._locale = val
    def _get_locale(self): # TODO IMPLEMENT DEFAULT FROM APP OR AVATAR 
        if not hasattr(self, '_locale'):
            self._locale = self.connection.locale or self.request.headers.get('Accept-Language', 'en').split(',')[0] or 'en'
        return self._locale
    locale = property(_get_locale, _set_locale)
    
    def rpc_changeLocale(self, locale):
        self.connection.locale = locale.lower()
        

    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, dtype=None):
        locale = locale or self.locale
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
    

        
    def getAbsoluteUrl(self, path, **kwargs):
        """return an external link to the page
        @param path: the path to the page from 'pages' folder
        """
        return self.request.construct_url(self.getDomainUrl(path, **kwargs))

    def resolvePathAsUrl(self, *args,  **kwargs):
        return self.diskPathToUri(self.resolvePath(*args, **kwargs))
        
    def resolvePath(self, *args, **kwargs):
        folder = kwargs.pop('folder', None)
        sitefolder = self.siteFolder
        if folder == '*data':
            diskpath = os.path.join(sitefolder, 'pages','..', 'data',  *args)
            return diskpath
        elif folder == '*users':
            diskpath = os.path.join(sitefolder,'pages','..', 'data', '_users', *args)
            return diskpath
        elif folder == '*home':
            diskpath = os.path.join(sitefolder,'pages','..', 'data', '_users', self.user, *args)
            return diskpath
        elif folder == '*pages':
            diskpath = os.path.join(sitefolder, 'pages',  *args)
        elif folder == '*lib':
            diskpath = os.path.join(sitefolder, 'pages', '_lib', *args)
        elif folder == '*static':
            diskpath = os.path.join(sitefolder, 'pages', 'static', *args)
        else:
            diskpath = os.path.join(os.path.dirname(self.filename), *args)
        diskpath = os.path.normpath(diskpath)
        return diskpath
        
    def diskPathToUri(self, tofile, fromfile=None):
        fromfile = fromfile or self.filename
        pagesfolder = self.folders['pages']
        relUrl = tofile.replace(pagesfolder, '').lstrip('/')
        path = fromfile.replace(pagesfolder, '')
        rp = '../'*(len(path.split('/'))-1)
        
        path_info = self.request.path_info
        if path_info: # != '/index'
            rp = rp + '../'*(len(path_info.split('/'))-1)
        return '%s%s' % (rp, relUrl)
    
    def _get_siteName(self):
        return os.path.basename(self.siteFolder.rstrip('/'))
    siteName = property(_get_siteName)
    
    
    def _get_dbconnection(self):
        if not self._dbconnection: 
            self._dbconnection=self.db.adapter.connect()
        return 
    dbconnection = property(_get_dbconnection)
    
    
    def _get_application(self):
        if not hasattr(self,'_application'):
            self._application= self.app.gnrapp
        return self._application
    application = property(_get_application)
    
    def _get_packages(self):
        return self.db.packages
    packages = property(_get_packages)
    
    def _get_package(self):
        pkgId = self.packageId
        if pkgId:
            return self.db.package(pkgId)
    package = property(_get_package)

    def _get_tblobj(self):
        if self.maintable:
            return self.db.table(self.maintable)
    tblobj = property(_get_tblobj)
         
    def formSaver(self,formId,table=None,method=None,_fired='',datapath=None,
                    resultPath='dummy',changesOnly=True,onSaving=None,onSaved=None,saveAlways=False,**kwargs):
        method = method or 'saveRecordCluster'
        controller = self.pageController()
        data = '==genro.getFormCluster("%s");' 
        onSaved = onSaved or ''
        _onCalling = kwargs.pop('_onCalling',None)
        if onSaving:
            _onCalling = """var currform = genro.formById("%s");
                            var onSavingCb = function(record,form){%s};
                             %s
                            var result = onSavingCb(data.getItem('record'),currform);
                            if(result===false){
                                currform.status = null;
                                return false;
                            }else if(result instanceof gnr.GnrBag){
                                $1.data.setItem('record',result);
                            }""" %(formId,onSaving,_onCalling or '')
        
        _onError="""var cb = function(){genro.formById("%s").status=null;};
                    genro.dlg.ask(kwargs._errorTitle,error,{"confirm":"Confirm"},
                                  {"confirm":cb});""" %formId
        if changesOnly:
            data = '==genro.getFormChanges("%s");'
        controller.dataController('genro.formById("%s").save(always)' %formId,_fired=_fired,
                                 datapath=datapath,always=saveAlways)
        kwargs['fireModifiers'] = _fired.replace('^','=')
        controller.dataRpc(resultPath, method=method ,nodeId='%s_saver' %formId ,_POST=True,
                           datapath=datapath,data=data %formId, _onCalling=_onCalling,
                           _onResult='genro.formById("%s").saved();%s;' %(formId,onSaved), 
                           _onError=_onError,_errorTitle='!!Saving error',
                           table=table,**kwargs)
                       
    def formLoader(self,formId,resultPath,table=None,pkey=None,  datapath=None,
                    _fired=None,loadOnStart = False,lock=False,
                    method=None,onLoading=None,onLoaded=None,loadingParameters=None,
                    **kwargs):
        pkey = pkey or '*newrecord*'
        method = method or 'loadRecordCluster'
        onResultScripts=[]
        onResultScripts.append('genro.formById("%s").loaded()' % formId)
        if onLoaded:
            onResultScripts.append(onLoaded)
        loadingParameters = loadingParameters or '=gnr.tables.maintable.loadingParameters'
        controller = self.pageController()
        controller.dataController('genro.formById(frmId).load();',
                                _fired=_fired, _onStart=loadOnStart,_delay=1,frmId=formId,
                                datapath=datapath)
                    
        controller.dataRpc(resultPath, method=method, pkey=pkey, table=table,
                           nodeId='%s_loader' %formId,datapath=datapath,_onCalling=onLoading,
                           _onResult=';'.join(onResultScripts),lock=lock,
                           loadingParameters=loadingParameters,
                           **kwargs)
                    
    def rpc_loadRecordCluster(self, table=None, pkey=None, recordGetter='app.getRecord', **kwargs):
        table = table or self.maintable
        getterHandler = self.getPublicMethod('rpc', recordGetter)
        record, recinfo = getterHandler(table=table, pkey=pkey, **kwargs)
        return record, recinfo
        

    def rpc_saveRecordCluster(self, data,table=None,_nocommit=False,rowcaption=None, **kwargs):
        #resultAttr = None #todo define what we put into resultAttr
        resultAttr = {}
        onSavingMethod='onSaving'
        onSavedMethod='onSaved'
        maintable=getattr(self,'maintable') 
        table=table or maintable
        tblobj = self.db.table(table)
        if table!=maintable:
            onSavingMethod='onSaving_%s'% table.replace('.','_')
            onSavedMethod='onSaved_%s' % table.replace('.','_')
        onSavingHandler=getattr(self,onSavingMethod,None)
        onSavedHandler=getattr(self,onSavedMethod,None)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        onSavedKwargs = dict()
        if onSavingHandler:
            onSavedKwargs = onSavingHandler(recordCluster, recordClusterAttr, resultAttr=resultAttr) or {}
        record = tblobj.writeRecordCluster(recordCluster,recordClusterAttr)
        if onSavedHandler:
            onSavedHandler(record, resultAttr=resultAttr,  **onSavedKwargs)
        if not _nocommit:
            self.db.commit()
        if not 'caption' in resultAttr:
            resultAttr['caption'] = tblobj.recordCaption(record,rowcaption=rowcaption)
        return (record[tblobj.pkey],resultAttr)

        
    def rpc_deleteRecordCluster(self, data, table=None, **kwargs):
        maintable=getattr(self,'maintable') 
        table=table or maintable
        tblobj = self.db.table(table)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        try: #try:
            self.onDeleting(recordCluster,recordClusterAttr)
            recordClusterAttr['_deleterecord'] = True
            record = tblobj.writeRecordCluster(recordCluster,recordClusterAttr)
            self.onDeleted(record)
            self.db.commit()
            return 'ok'
        except GnrSqlDeleteException, e:
            return ('delete_error',{ 'msg':e.message})    
            
    def rpc_deleteDbRow(self,table,pkey=None,**kwargs):
        """
            Method for deleting a single record from a given tablename 
            and from a record or its pkey.
        """
        try:
            tblobj = self.db.table(table)
            record = tblobj.record(pkey,for_update=True, mode='bag')
            deleteAttr = dict()
            self.onDeleting(record,deleteAttr)
            tblobj.delete(record)
            self.onDeleted(record)
            self.db.commit()
            return pkey,deleteAttr
        except GnrSqlDeleteException, e:
            return ('delete_error',{ 'msg':e.message})
                
    def setLoadingParameters(self, table,**kwargs):
        self.pageSource().dataFormula('gnr.tables.%s.loadingParameters' %table.replace('.','_'), 
                                       '',_onStart=True, **kwargs)
        
    def toJson(self,obj):
        return toJson(obj)
    
    def setOnBeforeUnload(self, root, cb, msg):
        root.script("""genro.checkBeforeUnload = function(e){
                       if (%s){
                           return "%s";
                       }
                }""" % (cb, self._(msg)))
        
        
    def rpc_onClosePage(self, **kwargs):
        self.site.onClosePage(self)
        self.session.removePageData()
        self.connection.pageFolderRemove()
        self.connection.cookieToRefresh()
        
    def mainLeftContent(self,parentBC,**kwargs):
        pass
        
    def pageController(self,**kwargs):
        return self.pageSource().dataController(**kwargs)

    def pageSource(self, nodeid=None):
        if nodeid:
            return self._root.nodeById(nodeid)
        else:
            return self._root
            
    def rootWidget(self, root, **kwargs):
        return root.contentPane(**kwargs)
        
    def main(self, root,**kwargs): #You MUST override this !
        root.h1('You MUST override this main method !!!')
    
    def _createContext(self, root):
        if self._cliCtxData:
            self.session.loadSessionData()
            for ctxName, ctxValue in self._cliCtxData.items():
                root.defineContext(ctxName, '_serverCtx.%s' % ctxName, ctxValue, savesession=False)
            self.session.saveSessionData()
                
    def setJoinCondition(self, ctxname, target_fld='*', from_fld='*', condition=None, one_one=None, applymethod=None, **kwargs):
        """define join condition in a given context (ctxname)
           the condition is used to limit the automatic selection of related records
           If target_fld AND from_fld equals to '*' the condition is an additional where clause added to any selection
           
           self.setJoinCondition('mycontext',
                              target_fld = 'mypkg.rows.document_id',
                              from_fld = 'mypkg.document.id',
                              condition = "mypkg.rows.date <= :join_wkd",
                              join_wkd = "^mydatacontext.foo.bar.mydate", one_one=False)
                              
            @param ctxname: name of the context of the main record 
            @param target_fld: the many table column of the relation, '*' means the main table of the selection
            @param from_fld: the one table column of the relation, '*' means the main table of the selection
            @param condition: the sql condition
            @param one_one: the result is returned as a record instead of as a selection. 
                            If one_one is True the given condition MUST return always a single record
            @param applymethod: a page method to be called after selecting the related records
            @param kwargs: named parameters to use in condition. Can be static values or can be readed 
                           from the context at query time. If a parameter starts with '^' it is a path in 
                           the context where the value is stored. 
                           If a parameter is the name of a defined method the method is called and the result 
                           is used as the parameter value. The method has to be defined as 'ctxname_methodname'.
        """
        self._cliCtxData['%s.%s_%s' % (ctxname, target_fld.replace('.','_'), from_fld.replace('.','_'))] = Bag(dict(target_fld=target_fld, from_fld=from_fld, condition=condition, one_one=one_one, applymethod=applymethod, params=Bag(kwargs)))
        
    def setJoinColumns(self, ctxname, target_fld, from_fld, joincolumns):
        self._cliCtxData['%s.%s_%s.joincolumns' % (ctxname,
                                                target_fld.replace('.','_'),
                                                from_fld.replace('.','_'))] = joincolumns
    
    
    def forbiddenPage(self, root, **kwargs):
        dlg = root.dialog(toggle="fade", toggleDuration=250, onCreated='widget.show();')
        f = dlg.form()
        f.div(content = 'Forbidden Page',text_align="center",font_size='24pt')
        tbl = f.contentPane(_class='dojoDialogInner').table()
        row = tbl.tr()
        row.td(content='Sorry. You are not allowed to use this page.', align="center",font_size='16pt', color='#c90031')
        cell = tbl.tr().td()
        cell.div(float='right',padding='2px').button('Back', action='genro.pageBack()')
        

    def windowTitle(self):
        return os.path.splitext(os.path.basename(self.filename))[0].replace('_',' ').capitalize()

    def _errorPage(self,err,method=None,kwargs=None):
        page = self.domSrcFactory.makeRoot(self)
        sc=page.stackContainer(height='80ex',width='50em',selected='^_dev.traceback.page')
        p1=sc.contentPane(background_color='silver')
        #msc=sc.menu()
        #msc.menuline('Close traceback',action='genro.wdgById("traceback_main").hide()')
        p1.div('Sorry: an error occurred on server while executing the method:<br> %s <br><br>Check parameters before executing again last command.' % method,
                    text_align='center',padding='1em',font_size='2em',color='gray',margin='auto')
        p1.button(label='See errors',action='FIRE _dev.traceback.page=1',position='absolute',bottom='1em',right='1em')
        accordion = sc.accordionContainer()
        accordion.accordionPane(title='traceback').div(border='1px solid gray',background_color='silver',padding='5px',margin_top='3em').pre(traceback.format_exc())
        errBag = TraceBackResolver()()
        for k, tb in errBag.items():
            currpane = accordion.accordionPane(title=k)
            currpane.div(tb['line'],font_size='1.2em',margin='4px')
            tbl = currpane.table(_class='bagAttributesTable').tbody()
            for node in tb['locals'].nodes:
                v = node.getStaticValue()
                tr = tbl.tr()
                tr.td(node.label, align='right')
                try:
                    if not isinstance(v, basestring):
                        v = str(v)
                    if not isinstance(v, unicode):
                        v = v.decode('ascii','ignore')
                except:
                    v = 'unicode error'
                tr.td(v.encode('ascii','ignore'))
        return page
        
        
    def handleMessages(self):
        t1=time.time()
        messages = self.site.getMessages(user=self.user, page_id=self.page_id, connection_id=self.connection.connection_id) or []
        t2=time.time()-t1
        if t2>1000:
            print t2
        for message in messages:
            message_body = Bag(message['body'])
            message_type = message['message_type']
            #message_id = message['id']
            handler = getattr(self,'msg_%s'%message_type,self.msg_undefined)
            if message['dst_page_id']:
                mode = 'page'
            elif message['dst_connection_id']:
                mode = 'connection'
            elif message['dst_user']:
                mode = 'user'
            getattr(self, 'handleMessages_%s'%mode,lambda *a,**kw: None)(handler=handler, message_body=message_body,src_page_id=message['src_page_id'],
                                                                        src_connection_id=message['src_connection_id'],src_user=message['src_user'])
    
    def handleMessages_user(self,handler,**kwargs):
        handler(**kwargs)
        
    def handleMessages_connection(self,handler,**kwargs):
        handler(**kwargs)
            
    def handleMessages_page(self,handler,message_id=None, **kwargs):
        handler(message_id=message_id,**kwargs)
        
        
    def msg_servermsg(self,message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        self.setInClientData('gnr.servermsg', message_body['servermsg'], fired=True, save=True,
                            src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                            message_id=message_id)
    
    def msg_servercode(self, message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        self.setInClientData('gnr.servercode', message_body['servercode'], fired=True, save=True,
                            src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                            message_id=message_id)
    
    def msg_datachange(self, message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        for change in message_body:
            self.setInClientData(change.attr.pop('_client_data_path'), change.value , _attributes=change.attr, save=True,
                                src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                                message_id=message_id)
    
    
    def msg_undefined(self, message):
        pass
        

    def rpc_resolverRecall(self, resolverPars=None, **auxkwargs):
        if isinstance(resolverPars,basestring):
            resolverPars = json.loads(resolverPars) #should never happen
        resolverclass = resolverPars['resolverclass']
        resolvermodule = resolverPars['resolvermodule']

        args = resolverPars['args'] or []
        kwargs = {}
        for k,v in (resolverPars['kwargs'] or {}).items():
            k = str(k)
            if k.startswith('_serialized_'):
                pool, k = k.replace('_serialized_','').split('_')
                v = getattr(self, pool)[v]
            kwargs[k] = v
        kwargs.update(auxkwargs)
        self.response.content_type = "text/xml"
        resolverclass=str(resolverclass)
        resolver=None
        if resolverclass in globals():
            resolver= globals()[resolverclass](*args,**kwargs)
        else:
            resolver = getattr(sys.modules[resolvermodule],resolverclass)(*args,**kwargs)
        #elif hasattr(self, 'class_%s' % resolverclass):
        #    h=getattr(self, 'class_%s' % resolverclass)
        #    c=h()
        #    resolver=c(*args,**kwargs)
        #elif hasattr(self, 'globals') and resolverclass in self.globals:
        #    resolver = self.globals[resolverclass](*args,**kwargs)
        #else:
        #    #raise str(resolverclass)
        #    #handle this case!
        #    pass
        if resolver is not None:
            resolver._page=self
            return resolver()
    
    # ----See gnrwebpage.py
    #def debugger(self,debugtype='py',**kwargs):
    #    self.site.debugger(debugtype,_frame=sys._getframe(1),**kwargs)
        
    def remote_bottomHelperContent(self,parent,**kwargs):
        #src = self.domSrcFactory.makeRoot(self)
        #src.data('debugger.main',Bang)
        sc=parent.stackContainer()
        bc=sc.borderContainer()
        left=bc.contentPane(region='left',width='160px',background_color='silver',overflow='hidden').formbuilder(cols=1)
        left.checkBox(value='^debugger.sqldebug',label='Debug SQL')
        left.checkBox(value='^debugger.pydebug',label='Debug Python')
        left.button('Clear Debugger',action='genro.setData("debugger.main",null)')
        bc.contentPane(region='center').tree(storepath='debugger.main',isTree=False,fired='^debugger.tree_redraw',
                                             getIconClass="""return 'treeNoIcon';""",persist=False,inspect='shift')
        parent.dataController("genro.debugopt=sqldebug?(pydebug? 'sql,py' :'sql' ):(pydebug? 'py' :null )",
                            sqldebug='^debugger.sqldebug',pydebug='^debugger.pydebug')
        parent.dataController("FIRE debugger.tree_redraw;",sqldebug='^debugger.main',_delay=1)
        
    def rpc_resetApp(self, **kwargs):
        self.siteStatus['resetTime'] = time.time()
        self.siteStatusSave()
        
    def rpc_applyChangesToDb(self, **kwargs):
        return self._checkDb(applychanges=True)
        
    def rpc_checkDb(self):
        return self._checkDb(applychanges=False)
        
    def _checkDb(self, applychanges=False, changePath=None, **kwargs):
        changes = self.application.checkDb()
        if applychanges:
            if changePath:
                changes = self.db.model.modelBagChanges.getAttr(changePath, 'changes')
                self.db.execute(changes)
            else:
                for x in self.db.model.modelChanges:
                    self.db.execute(x)
            self.db.commit()
            self.application.checkDb()
        return self.db.model.modelBagChanges
        
    def rpc_tableStatus(self,**kwargs):
        strbag = self._checkDb(applychanges=False)
        for pkgname, pkg in self.db.packages.items():
            for tablename in pkg.tables.keys():
                records=self.db.query('%s.%s' % (pkgname, tablename)).count()
                strbag.setAttr('%s.%s' %(pkgname,tablename), recordsnum=records)
        return strbag
        
    def createFileInData(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'data', *args)
            dirname=os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile=file(path, 'w')
            return outfile
           
    def createFileInStatic(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'pages','static', *args)
            dirname=os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile=file(path, 'w')
            return outfile
            
    def createFolderInData(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'data', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path
    
    def createFolderInStatic(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'pages','static', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path

    

