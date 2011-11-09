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
    
    @public_method
    def listMovers(self):
        dirs = os.listdir(self.page.site.getStaticPath('site:movers'))
        result = Bag()
        for i,d in enumerate(dirs):
            if not d.startswith('.'):
                result.setItem('r_%i' %i,None,caption=d,mover=d)
        result.setItem('__newmover__',None,caption='!!New Mover',mover='')
        return result

    @public_method
    def getMoverTableRows(self,tablerow=None,movername=None,**kwargs):
        pkeys = tablerow['pkeys'].keys()
        tblobj = self.db.table(tablerow['table'])
        columns,mask = tblobj.rowcaptionDecode(tblobj.rowcaption)
        if columns:
            columns = ','.join(columns)
        f = tblobj.query(where='$pkey IN :pkeys',pkeys=tablerow['pkeys'].keys(),columns=columns).fetch()
        result = Bag()
        for r in f:
            result.setItem(r['pkey'],None,_pkey=r['pkey'],db_caption=tblobj.recordCaption(record=r),_customClasses='mover_db')
        if movername:
            indexbag = Bag(self.page.site.getStaticPath('site:movers',movername,'index.xml'))
            tablecode = tablerow['table'].replace('.','_')
            moverrows = indexbag.getItem('records.%s' %tablecode)
            for pkey in pkeys:
                rownode = moverrows.getNode(pkey)
                if rownode:
                    xml_caption=rownode.attr['caption']
                    if not pkey in result:
                        result.setItem(pkey,None,_pkey=pkey,xml_caption=xml_caption,_customClasses='mover_xml')
                    else:
                        result.getNode(pkey).attr.update(xml_caption=xml_caption,_customClasses='mover_both')
        return result

    @public_method
    def loadMover(self,movername=None):
        result = Bag(self.page.site.getStaticPath('site:movers',movername,'index.xml'))
        tablesbag = result['tables']
        for n in result['records']:
            tablesbag.getNode(n.label).attr.update(pkeys=dict([(pkey,True) for pkey in n.value.keys()]))
        return tablesbag
    
    @public_method
    def saveMover(self,movername=None,data=None):
        assert data and movername,'data and movername are mandatory'
        moversfolder = self.page.site.getStaticPath('site:movers')
        moverpath = os.path.join(moversfolder,movername)
        indexpath = os.path.join(moverpath,'index.xml')
        indexbag = Bag()
        if not os.path.isdir(moverpath):
            os.mkdir(moverpath)
        for table,pkeys in data.digest('#a.table,#a.pkeys'):
            pkeys = pkeys.keys()
            tablecode = table.replace('.','_')
            databag = self.db.table(table).toXml(pkeys=pkeys,rowcaption=True,
                                                    path=os.path.join(moverpath,'data','%s.xml' %tablecode))
            indexbag.setItem('tables.%s' %tablecode,None,table=table,count=len(pkeys))
            for n in databag:
                indexbag.setItem('records.%s.%s' %(tablecode,n.label),None,pkey=n.attr['pkey'],caption=n.attr.get('caption'))            
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