#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import hashlib
import inspect
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

class GnrWebDebugger(GnrBaseProxy):
    def init(self, **kwargs):
        self.db = self.page.db
        self.debug = getattr(self.page, 'debug', False)
        self._debug_calls = Bag()

    def bottom_pane(self, parentBC):
        parentBC.data("_clientCtx.mainBC.bottom?show", False)
        parentBC.dataController("if(show){genro.nodeById('gnr_bottomHelper').updateRemoteContent();}",
                                show='^_clientCtx.mainBC.bottom?show', _class='gnrdebugger')
        bottomHelperSC = parentBC.stackContainer(height='30%', region='bottom', splitter=True,
                                                 nodeId='gnr_bottomHelper')
        bottomHelperSC.remote('bottomHelperContent', cacheTime=-1)


    def output(self, debugtype, **kwargs):
        page = self.page
        debugopt = getattr(page, 'debugopt', '') or ''
        if debugopt and debugtype in debugopt:
            getattr(self, 'output_%s' % debugtype)(page, **kwargs)

    def output_sql(self, page, sql=None, sqlargs=None, dbtable=None, error=None):
        b = Bag()
        dbtable = dbtable or ''
        b['dbtable'] = dbtable
        b[
        'sql'] = "innerHTML:<div style='white-space: pre;font-size: x-small;background-color:#ffede7;padding:2px;'>%s</div>" % sql
        b['sqlargs'] = Bag(sqlargs)
        if error:
            b['error'] = str(error)
        self._debug_calls.addItem('%03i SQL:%s' % (len(self._debug_calls), dbtable.replace('.', '_')), b,
                                  debugtype='sql')

    def output_py(self, page, _frame=None, **kwargs):
        b = Bag(kwargs)
        if  _frame:
            import inspect

            m = inspect.getmodule(_frame)
            lines, start = inspect.getsourcelines(_frame)
            code = ''.join(['%05i %s' % (n + start, l)for n, l in enumerate(lines)])
            b['module'] = m.__name__
            b['line_number'] = _frame.f_lineno
            b['locals'] = Bag(_frame.f_locals)
            b[
            'code'] = "innerHTML:<div style='white-space: pre;font-size: x-small;background-color:#e0ffec;padding:2px;'>%s</div>" % code
            label = '%s line:%i' % (m.__name__.replace('.', '_'), _frame.f_lineno)
        self._debug_calls.addItem('%03i PY:%s' % (len(self._debug_calls), label), b, debugtype='py')

    def event_onCollectDatachanges(self):
        page = self.page
        if page.debugopt and self._debug_calls:
            path = 'debugger.main.c_%s' % self.page.callcounter
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