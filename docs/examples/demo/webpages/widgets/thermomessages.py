#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os

from gnr.core.gnrlang import getUuid

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root,cols='3', **kwargs):
        root = self.rootLayoutContainer(root)
        
        lc = root.layoutContainer(height='100%')
        top = lc.contentPane(layoutAlign='top', height='10em', background_color='whitesmoke')
        main = lc.contentPane(layoutAlign='client', background_color='white')
        bottom = lc.contentPane(gnrId='bottom', layoutAlign='bottom', height='10em', background_color='green')
        
        self.thermo(bottom, thermoid='untermometro', title='Termometro inutile', thermolines=3)
        
        
        trmbtn = top.button("Thermo Start", gnrId='trmbtn', action="""
        genro.setData('start_operazioneLunga', null);
        genro.publish('start_untermometro');
        """)
        
        trmbtn.dataRpc('operazioneLunga', 'operazioneLunga', upd='^start_operazioneLunga')
        top.div('^operazioneLunga')
        
        
        
        bottom.progressBar(width='300px', gnrId='trm', indeterminate='^trm.indet', maximum='^trm.max', places='^trm.places', progress='^trm.progress')
        
        bottom.data('trm.max', 20)
        bottom.data('trm.progress', 5)
        
    def thermo(self, where, thermoid='thermo', title='', thermolines=1):
        kwargs = {}
        kwargs['subscribe_start_%s' % thermoid] = """
            this.refreshThermo = function(){
                genro.setData('_thermo._trigger.%s', null);
                var prog = genro.getData('_thermo.%s.t1.progress');
                if ((this.lastprog != null) && (prog == null)){
                    this.hide();
                }
                this.lastprog = prog;
                if(this.open){
                    setTimeout(dojo.hitch(this, 'refreshThermo'), 1000);
                }
            }
            this.lastprog = null;
            setTimeout(dojo.hitch(this, 'refreshThermo'), 1000);
            this.show(); 
            """ % (thermoid, thermoid)
        
        d = where.dialog(title=title, width='27em', datapath='_thermo.%s' % thermoid, closable=False, **kwargs)
        
        for x in range(thermolines):
            tl = d.div(datapath='.t%i' % (x+1, ))
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', 
                          places='^.places', progress='^.progress')
            tl.div('^.message', height='1em')
        
        
        d.dataRpc('_thermo.%s' % thermoid, 'thermoProgress', thermoid=thermoid,
                                                             stop='^_thermo._trigger.%s' % thermoid)
        d.button('Stop', action="genro.setData('_thermo._trigger.%s', true);" % thermoid)
        
        
    def rpc_thermoProgress(self, thermoid, stop=None):
        try:
            thermoBag = Bag(self.pageLocalDocument('thermo_%s' % thermoid))
            if stop: 
                thermoBag['stop'] = True
                thermoBag.toXml(self.pageLocalDocument('thermo_%s' % thermoid), autocreate=True)
            return thermoBag
        except:
            pass
        
        
    def setThermo(self, thermoid, progress_1=None, message_1=None, maximum_1=None, indeterminate_1=None, stop=None, end=None, **kwargs):
        try:
            thermoBag = Bag(self.pageLocalDocument('thermo_%s' % thermoid))
        except:
            thermoBag = Bag()
            
        max = maximum_1 or thermoBag['t1.maximum']
        prog = progress_1 or thermoBag['t1.maximum']
        if max and prog > max:
            end = True
        if end:
            thermoBag = Bag()
        else:
            params = dict(progress_1=progress_1, message_1=message_1, maximum_1=maximum_1, indeterminate_1=indeterminate_1)
            params.update(kwargs)
            for k,v in params.items():
                if v is not None:
                    key, thermo = k.split('_')
                    thermoBag['t%s.%s' % (thermo, key)] = v
                    if key == 'progress':
                        if not kwargs.get('indeterminate_%s' % thermo):
                            thermoBag.pop('indeterminate_%s' % thermo)
                            
        thermoBag.toXml(self.pageLocalDocument('thermo_%s' % thermoid), autocreate=True)
        return thermoBag['stop']
        
    def rpc_operazioneLunga(self):
        import time
        self.setThermo('untermometro', 0, 'messaggio bello' , maximum_1=10, maximum_2=10, maximum_3=10)
        
        for x in range(10):
            stop = self.setThermo('untermometro', x, 'messaggio bello %i' % x)
            if stop: 
                self.setThermo('untermometro', end=True)
                return "stopped"
            
            for y in range(10):
                self.setThermo('untermometro', progress_2=y, message_2='messaggio medio %i' % y)
                for z in range(10):
                    self.setThermo('untermometro', progress_3=z, message_3='messaggio brutto %i' % z)
                    
                    time.sleep(0.1)
                    
                    
                    
        self.setThermo('untermometro', end=True)
        return "finito"
        
    def rpc_getMessages(self):
        msgbag = Bag()
        msgfolder = self.pageLocalDocument(os.path.join('_messages'))
        if os.path.exists(msgfolder):
            files = [(os.stat(os.path.join(msgfolder, f)).st_mtime, f) for f in os.listdir(msgfolder)]
            files.sort()
            for f in files:
                if not f.startswith('.'):
                    fname = os.path.join(msgfolder, f)
                    b = Bag(fname)
                    msgbag.update(b)
                    os.remove(fname)
        return msgbag
            
        
    def sendMessage(self, target='page', package=None, topic=None, msg=None):
        msgbag = Bag()
        if target == 'page':
            msgbag['page'] = msg
            fname = self.pageLocalDocument(os.path.join('_messages', '%s.xml' % getUuid()))
            msg.toXml(fname)
        elif target == 'connection':
            msgbag['connection'] = msg
            msgid = '%s.xml' % getUuid()
            for page in os.listdir(self.connectionFolder):
                pagedir = os.path.join(self.connectionFolder, page)
                if os.isdir(pagedir):
                    msg.toXml(os.path.join(pagedir, '_messages', msgid))
                    
        elif target == 'all':
            pass
    
