#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import datetime
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

class GnrWebDebugger(GnrBaseProxy):
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
        self._debug_calls.addItem('%03i Table:%s' % (len(self._debug_calls), dbtable.replace('.', '_')), value,
                                  **kwargs)

    def event_onCollectDatachanges(self):
        page = self.page
        if page.debugopt and self._debug_calls:
            path = 'gnr.debugger.main.c_%s' % self.page.callcounter
            page.setInClientData(path, self._debug_calls)

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