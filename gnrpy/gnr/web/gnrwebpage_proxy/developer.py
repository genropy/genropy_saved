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
                result.setItem('r_%i',None,caption=d,mover=d)
        result.setItem('__newmover__',None,caption='!!New Mover',mover='')
        return result

    @public_method
    def getMoverTableRows(self,tablerow=None,**kwargs):
        if not tablerow:
            return Bag()
        tblobj = self.db.table(tablerow['table'])
        columns,mask = tblobj.rowcaptionDecode(tblobj.rowcaption)
        result = Bag()
        if columns:
            columns = ','.join(columns)
        f = tblobj.query(where='$pkey IN :pkeys',pkeys=tablerow['pkeys'].keys(),columns=columns).fetch()
        for r in f:
            result.setItem(r['pkey'],Bag(dict(_pkey=r['pkey'],rowcaption=tblobj.recordCaption(record=r))))
        return result

    @public_method
    def loadMover(self,movername=None):
        if not movername:
            return Bag()
        return Bag(self.page.site.getStaticPath('site:movers',movername,'index.xml'))
    
    @public_method
    def saveMover(self,movername=None,data=None):
        assert data and movername,'data and movername are mandatory'
        moversfolder = self.page.site.getStaticPath('site:movers')
        if not os.path.isdir(moversfolder):
            os.mkdir(moversfolder)
        moverpath = os.path.join(moversfolder,movername)
        indexpath = os.path.join(moverpath,'index.xml')
        if not os.path.isdir(moverpath):
            os.mkdir(moverpath)
        indexbag = Bag(indexpath) if os.path.isfile(indexpath) else Bag()
        indexbag.update(data)
        for k,v in indexbag.items():
            self.db.table(v.getItem("table")).toXml(pkeys=v.getItem('pkeys').keys(),
                                                    path=os.path.join(moverpath,'data','%s.xml' %k))
        indexbag.toXml(indexpath)
        
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