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
        self._debug_calls=Bag()
    
    def right_pane(self, pane):
        pane.dataController("SET _clientCtx.mainBC.right?show=false;",_init=True)
        pane.dataController("if(show){genro.nodeById('gnr_debugger').updateContent();}",show='^_clientCtx.mainBC.right?show')
        debugAc = pane.accordionContainer(width='20%',region='right',splitter=True, nodeId='gnr_debugger',_class='gnrdebugger')
        debugAc.remote('debugger.debuggerContent', cacheTime=-1)
    
    def bottom_pane(self, pane):
        pane.dataController("SET _clientCtx.mainBC.bottom?show=false;",_init=True)
        pane.dataController("if(show){genro.nodeById('gnr_bottomHelper').updateContent();}",show='^_clientCtx.mainBC.bottom?show',_class='gnrdebugger')
        bottomHelperTc = pane.stackContainer(height='30%',region='bottom',splitter=True, nodeId='gnr_bottomHelper')
        bottomHelperTc.remote('bottomHelperContent', cacheTime=-1)
        
    def rpc_debuggerContent(self):
        src = self.page.domSrcFactory.makeRoot(self)
        src.dataRemote('_dev.dbstruct','app.dbStructure')
        src.accordionPane(title='Datasource').tree(storepath='*D',persist=False,inspect='shift')
        src.accordionPane(title='Database').tree(storepath='_dev.dbstruct',persist=False,inspect='shift')
        src.accordionPane(title='Page source').tree(storepath='*S', label="Source inspector",
                                                   inspect='shift',selectedPath='_dev.selectedSourceNode') 
        src.dataController('genro.src.highlightNode(fpath)',fpath='^_dev.selectedSourceNode')
        dbmnt=src.accordionPane(title='Db Maintenance')
        dbmnt.dataRpc('status', 'tableStatus', _fired='^aux.do_tableStatus')
        dbmnt.dataRpc('status', 'checkDb', _fired='^aux.do_checkDb')
        dbmnt.dataRpc('status', 'applyChangesToDb', _fired='^aux.do_applyChangesToDb')
        dbmnt.dataRpc('status', 'resetApp', _fired='^aux.do_resetApp')
        bc=dbmnt.borderContainer(height='100%')
        top=bc.contentPane(region='top',font_size='.9em',height='10ex')
        center=bc.tabContainer(region='center',font_size='.9em')
        center.contentPane(title='test')
        top.button('tableStatus', fire='aux.do_tableStatus',)
        top.button('CheckDb', fire='aux.do_checkDb')
        top.button('applyChangesToDb', fire='aux.do_applyChangesToDb')
        top.button('resetApp', fire='aux.do_resetApp')
        for k,x in enumerate(self.db.packages.items()):
            pkgname, pkg = x
            pane=center.contentPane(title=pkgname,height='100%')
            pane.button('test')
        return src
       
    def output(self,debugtype,**kwargs):
        page =self.page
        if self.debug or page.isDeveloper():
            debugopt=getattr(page,'debugopt','') or ''
            if debugopt and debugtype in debugopt:
                getattr(self,'output_%s' % debugtype)(page,**kwargs)

    def output_sql(self, page, sql=None, sqlargs=None,dbtable=None, error=None):
        b=Bag()
        dbtable=dbtable or ''
        b['dbtable']=dbtable 
        b['sql']="innerHTML:<div style='white-space: pre;font-size: x-small;background-color:#ffede7;padding:2px;'>%s</div>" % sql
        b['sqlargs']=Bag(sqlargs)
        if error:
            b['error']=str(error)
        self._debug_calls.addItem('%03i SQL:%s'%(len(self._debug_calls),dbtable.replace('.','_')),b,debugtype='sql')

    def output_py(self, page, _frame=None, **kwargs):
        b=Bag(kwargs)
        if  _frame:
            import inspect
            m=inspect.getmodule(_frame)
            lines,start=inspect.getsourcelines(_frame)
            code=''.join(['%05i %s'%(n+start,l)for n,l in enumerate(lines)])
            b['module']=m.__name__
            b['line_number']=_frame.f_lineno
            b['locals']=Bag(_frame.f_locals)
            b['code']="innerHTML:<div style='white-space: pre;font-size: x-small;background-color:#e0ffec;padding:2px;'>%s</div>" % code       
            label='%s line:%i' %(m.__name__.replace('.','_'),_frame.f_lineno)
        self._debug_calls.addItem('%03i PY:%s'%(len(self._debug_calls),label),b,debugtype='py')
        
    def event_onCollectDataChanges(self):
        page = self.page
        if page.debugopt and self._debug_calls:
            changeSet = Bag()
            changeSet.setItem('debugger_main',self._debug_calls,_client_path='debugger.main.c_%s'%self.page.callcounter)
            page.setLocalClientDataChanges(changeSet)
        
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