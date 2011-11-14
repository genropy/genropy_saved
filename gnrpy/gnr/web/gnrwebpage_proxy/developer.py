#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  developer.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import os
import datetime
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrdecorator import public_method

class GnrWebDeveloper(GnrBaseProxy):
    def init(self, **kwargs):
        self.db = self.page.db
        self.debug = getattr(self.page, 'debug', False)
        self._debug_calls = Bag()

    def output(self, debugtype, **kwargs):
        page = self.page
        debugopt = getattr(page, 'debugopt', '') or ''
        if debugopt and debugtype in debugopt:
            getattr(self, 'output_%s' % debugtype)(page, **kwargs)

    def output_sql(self, page, sql=None, sqlargs=None, dbtable=None, error=None):
        dbtable = dbtable or '-no table-'
        kwargs=dict(sqlargs)
        kwargs.update(sqlargs)
        value = sql
        if error:
            kwargs['sqlerror'] = str(error)
        self._debug_calls.addItem('%03i Table %s' % (len(self._debug_calls), dbtable.replace('.', '_')), value,
                                  **kwargs)

    def event_onCollectDatachanges(self):
        page = self.page
        if page.debugopt and self._debug_calls:
            path = 'gnr.debugger.main.c_%s' % self.page.callcounter
            page.setInClientData(path, self._debug_calls)

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
                tablesbag.getNode(n.label).attr.update(pkeys=dict([(pkey,True) for pkey in n.value.keys()],_customClasses=_class))
            return tablesbag
                
    @public_method
    def importMoverLines(self,table=None,objtype=None,pkeys=None):
        databag = Bag(self.page.site.getStaticPath('user:temp','mover','data','%s_%s.xml' %(table.replace('.','_'),objtype)))
        tblobj = self.db.table(table) if objtype=='record' else self.db.table('adm.userobject')
        for pkey in pkeys.keys():
            tblobj.insertOrUpdate(databag.getItem(pkey))
        self.db.commit()
        
    @public_method
    def getMoverTableRows(self,tablerow=None,movercode=None,**kwargs):
        pkeys = tablerow['pkeys'].keys()
        table = tablerow['table']
        objtype = tablerow['objtype']
        tblobj = self.db.table(table)
        columns,mask = tblobj.rowcaptionDecode(tblobj.rowcaption)
        if columns:
            columns = ','.join(columns)
        f = tblobj.query(where='$pkey IN :pkeys',pkeys=tablerow['pkeys'].keys(),columns=columns).fetch()
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
                        result.setItem(pkey,None,_pkey=pkey,xml_caption=xml_caption,_customClasses='mover_xml',objtype=objtype,table=table)
                    else:
                        result.getNode(pkey).attr.update(xml_caption=xml_caption,_customClasses='mover_both',objtype=objtype,table=table)
        return result

    def tarMover(self,movername='mover'):
        import tarfile
        import StringIO
        tf = StringIO.StringIO() 
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
            pkeys = pkeys.keys()
            databag = self.db.table(table).toXml(pkeys=pkeys,rowcaption=True,
                                                    path=os.path.join(moverpath,'data','%s.xml' %movercode))
            indexbag.setItem('movers.%s' %movercode,None,table=table,count=len(pkeys),reftable=reftable,objtype=objtype)
            indexbag.setItem('records.%s' %movercode,None,table=table)
            for n in databag:
                indexbag.setItem('records.%s.%s' %(movercode,n.label),None,pkey=n.attr['pkey'],caption=n.attr.get('caption')) 
        indexbag.toXml(indexpath,autocreate=True)
        
    def log(self, msg):
        if self.debug:
            f = file(self.logfile, 'a')
            f.write('%s -- %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))
            f.close()

    def _get_logfile(self):
        if not hasattr(self, '_logfile'):
            logdir = os.path.normpath(os.path.join(self.page.site.site_path, 'data', 'logs'))
            if not os.path.isdir(logdir):
                os.makedirs(logdir)
            self._logfile = os.path.join(logdir, 'error_%s.log' % datetime.date.today().strftime('%Y%m%d'))
        return self._logfile

    logfile = property(_get_logfile)