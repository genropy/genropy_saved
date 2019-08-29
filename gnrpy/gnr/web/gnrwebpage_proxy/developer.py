 #!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  developer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from future import standard_library
standard_library.install_aliases()
from builtins import str
#from builtins import object
import os
import datetime
import urllib.parse

from time import time
from gnr.core.gnrbag import Bag,NetBag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method

class GnrWebDeveloper(GnrBaseProxy):
    def init(self, **kwargs):
        #self.db = self.page.db
        self.debug = getattr(self.page, 'debug', False)
        self._sqlDebugger = None


    @property
    def sqlDebugger(self):
        if not self._sqlDebugger:
            self._sqlDebugger = GnrSqlDebugger(self)
        return self._sqlDebugger

    @property
    def db(self):
        return self.page.db


    def maintenanceServerUrl(self):
        helpdesk = self.page.getPreference('helpdesk',pkg='adm')
        url = helpdesk['url']
        user = helpdesk['user']
        password = helpdesk['password']
        return self.authenticatedUrl(url=url,user=user,password=password)
        
    def authenticatedUrl(self,url=None,user=None,password=None):
        sp = urllib.parse.urlsplit(url)
        return '%s://%s:%s@%s%s' %(sp.scheme,user,password,sp.netloc,sp.path)
    

    def getTaskReference(self):
        task_reference = getattr(self.page,'task_reference',None) 
        if task_reference:
            return task_reference
        maintable = getattr(self.page,'maintable',None)
        pkg = maintable.split('.')[0] or self.page.package.name
        project_code = self.db.application.packages[pkg].project
        siteName = self.page.siteName
        pagename = 'webpage.%s' %self.page.pagename
        return '%s/%s/%s' %(project_code,pkg,maintable or pagename)


    @public_method
    def getCurrentTickets(self,**kwargs):
        helpdesk = self.page.getPreference('helpdesk',pkg='adm')
        result = NetBag(self.maintenanceServerUrl(),'get_tickets',
                            client_reference=helpdesk['client_reference'],
                            task_reference=self.getTaskReference())()
        
        return result


    @public_method
    def getNewTicketInfo(self,**kwargs):
        helpdesk = self.page.getPreference('helpdesk',pkg='adm')
        result = NetBag(self.maintenanceServerUrl(),'get_newticket_info',
                    task_reference=self.getTaskReference())()
        return result

    @public_method
    def saveNewTicket(self,record=None,**kwargs):
        helpdesk = self.page.getPreference('helpdesk',pkg='adm')
        result = NetBag(self.maintenanceServerUrl(),'save_ticket',record=record,
                            client_reference=helpdesk['client_reference'],
                            task_reference=self.getTaskReference(),
                            report_avatar=Bag(self.page.avatar.as_dict()))()
        return result
        #return dict(path=filepath)

    @public_method
    def loadTicket(self,pkey=None,**kwargs):
        return NetBag(self.maintenanceServerUrl(),'load_ticket',pkey=pkey)()


    def event_onCollectDatachanges(self):
        if self._sqlDebugger:
            self.sqlDebugger.onCollectDatachanges()


    def onDroppedMover(self,file_path=None):
        import tarfile
        f = tarfile.open(file_path)
        f.extractall(self.page.site.getStaticPath('user:temp'))        
        os.remove(file_path)
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        indexbag = Bag(indexpath)
        indexbag.getNode('movers').attr.update(imported=True)
        indexbag.toXml(indexpath)
        
    @public_method
    def loadCurrentMover(self):
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        if os.path.isfile(indexpath):
            indexbag = Bag(indexpath)
            imported = indexbag['movers?imported']
            tablesbag = indexbag['movers']
            _class = 'mover_imported' if imported else None
            for n in indexbag['records']:
                tablesbag.getNode(n.label).attr.update(pkeys=dict([(pkey,True) for pkey in list(n.value.keys())],_customClasses=_class))
            return tablesbag
                
    @public_method
    def importMoverLines(self,table=None,objtype=None,pkeys=None):
        databag = Bag(self.page.site.getStaticPath('user:temp','mover','data','%s_%s.xml' %(table.replace('.','_'),objtype)))
        tblobj = self.db.table(table) if objtype=='record' else self.db.table('adm.userobject')
        for pkey in list(pkeys.keys()):
            tblobj.insertOrUpdate(databag.getItem(pkey))
        self.db.commit()
        
    @public_method
    def getMoverTableRows(self,tablerow=None,movercode=None,**kwargs):
        pkeys = list(tablerow['pkeys'].keys())
        table = tablerow['table']
        objtype = tablerow['objtype']
        tblobj = self.db.table(table)
        columns,mask = tblobj.rowcaptionDecode(tblobj.rowcaption)
        if columns:
            columns = ','.join(columns)
        f = tblobj.query(where='$pkey IN :pkeys',pkeys=list(tablerow['pkeys'].keys()),columns=columns).fetch()
        result = Bag()
        for r in f:
            result.setItem(r['pkey'],None,_pkey=r['pkey'],db_caption=tblobj.recordCaption(record=r),_customClasses='mover_db')
        indexpath = self.page.site.getStaticPath('user:temp','mover','index.xml')
        if os.path.isfile(indexpath):
            indexbag = Bag(indexpath)
            moverrows = indexbag.getItem('records.%s' %movercode)
            if not moverrows:
                return result
            for pkey in pkeys:
                rownode = moverrows.getNode(pkey)
                if rownode:
                    xml_caption=rownode.attr['caption']
                    if not pkey in result:
                        result.setItem(pkey,None,_pkey=pkey,xml_caption=xml_caption,_customClasses='mover_xml',objtype=objtype,table=tablerow['reftable'])
                    else:
                        result.getNode(pkey).attr.update(xml_caption=xml_caption,_customClasses='mover_both',objtype=objtype,table=tablerow['reftable'])
        return result

    def tarMover(self,movername='mover'):
        import tarfile
        import io
        tf = io.StringIO() 
        f = tarfile.open(mode = 'w:gz',fileobj=tf)
        moverpath = self.page.site.getStaticPath('user:temp','mover')
        f.add(moverpath,arcname='mover')
        f.close()     
        result = tf.getvalue()
        tf.close()
        return result
    
    @public_method
    def downloadMover(self,data=None,movername=None,**kwargs):
        self.saveCurrentMover(data=data)
        return self.tarMover(movername=movername)
    
    @public_method
    def saveCurrentMover(self,data):
        moverpath = self.page.site.getStaticPath('user:temp','mover')
        indexpath = os.path.join(moverpath,'index.xml')
        indexbag = Bag()
        if not os.path.isdir(moverpath):
            os.makedirs(moverpath)
        for movercode,table,pkeys,reftable,objtype in data.digest('#k,#a.table,#a.pkeys,#a.reftable,#a.objtype'):
            pkeys = list(pkeys.keys())
            databag = self.db.table(table).toXml(pkeys=pkeys,rowcaption=True,
                                                    path=os.path.join(moverpath,'data','%s.xml' %movercode))
            indexbag.setItem('movers.%s' %movercode,None,table=table,count=len(pkeys),reftable=reftable,objtype=objtype)
            indexbag.setItem('records.%s' %movercode,None,table=table)
            for n in databag:
                indexbag.setItem('records.%s.%s' %(movercode,n.label),None,pkey=n.attr['pkey'],caption=n.attr.get('caption')) 
        indexbag.toXml(indexpath,autocreate=True)

    @public_method
    def loadModuleSource(self,module=None):
        if os.path.exists(module):
            with open(module,'r') as f:
                return f.read()

   # @public_method
   # def loadModuleElement(self,module=None,element=None):
   #     return GnrRedBaron(module,element=element)
#
   # @public_method
   # def saveModuleElement(self,module=None,element=None):
   #     return GnrRedBaron(module,element=element)
#
class GnrSqlDebugger(object):
    def __init__(self,parent):
        self.parent = parent
        self._debug_calls = Bag()

    def output(self, page, sql=None, sqlargs=None, dbtable=None, error=None,delta_time=None):
        dbtable = dbtable or '-no table-'
        kwargs=dict(sqlargs)
        kwargs.update(sqlargs)
        delta_time = int((delta_time or 0)*1000)
        if sqlargs and sql:
            formatted_sqlargs = dict([(k,'<span style="background-color:yellow;cursor:pointer;" title="%s" >%%(%s)s</span>' %(v,k)) for k,v in list(sqlargs.items())])
            value = sql %(formatted_sqlargs)
        if error:
            kwargs['sqlerror'] = str(error)
        self._debug_calls.addItem('%03i Table %s' % (len(self._debug_calls), dbtable.replace('.', '_')), value,_execution_time=delta_time,_time_sql=delta_time,_description=dbtable,_type='sql',
                                  **kwargs)

    def onCollectDatachanges(self):
        page = self.parent.page
        if page.debug_sql and self._debug_calls:
            path = 'gnr.debugger.main.c_%s' % page.callcounter
            attributes=dict(server_time=int((time()-page._start_time)*1000))
            call_kwargs = dict(page._call_kwargs)
            attributes['methodname'] = call_kwargs.pop('method')
            call_kwargs.pop('_lastUserEventTs',None)
            if not call_kwargs.get('_debug_info') and ('table' in call_kwargs or 'dbtable' in call_kwargs):
                call_kwargs['_debug_info'] = 'table: %s' %(call_kwargs.get('table') or call_kwargs.get('dbtable'))
            attributes['debug_info'] = call_kwargs.pop('_debug_info',None)
            #attributes['_method_parameters'] = call_kwargs
            attributes['sql_count'] = len(self._debug_calls)
            attributes['sql_total_time'] = self._debug_calls.sum('#a._time_sql')
            attributes['not_sql_time'] = attributes['server_time'] - attributes['sql_total_time']
            attributes['r_count'] = page.callcounter
            page.setInClientData(path, self._debug_calls,attributes=attributes)
