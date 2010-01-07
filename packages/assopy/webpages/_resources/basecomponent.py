#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Season """
import os
from gnr.core.gnrbag import Bag

from gnr.core.gnrstring import templateReplace


class Public(object):
    def __onmixin__(self):
        self.css_requires.append('public')
        self.css_requires.append('assopy')
        
    def get_paypal_site(self, test_ipn=None):
        if test_ipn:
            pp = 'sandbox'
        else:
            pp = 'pycon'
        return self.application.config.getAttr('packages.assopy.paypal.%s' % pp, 'url')
        
    def get_paypal_business(self, test_ipn=None):
        if test_ipn:
            pp = 'sandbox'
        else:
            pp = 'pycon'
        return self.application.config.getAttr('packages.assopy.paypal.%s' % pp, 'business')
    
        
    def cancel_url(self):
        return "genro.pageBack()"

    def publicPane(self, root, title=None,height=None,datapath=None,**kwargs):
        """
        return top, client, bottom elements of a the public page layout of this package
        """
        lc,top=self.publicRoot(root, title=title,height=height)
        bottom=lc.contentPane(layoutAlign='bottom', _class='pbl_formContainerBottom')
        client=lc.contentPane(layoutAlign='client', _class='pbl_formContainerClient',datapath=datapath, **kwargs)
        return (top,client,bottom)

    def publicPagedPane(self, root, title=None,height=None, selected='_pbl.selectedPage',**kwargs):
        """
        return a header and a stack container
        """
        lc,top = self.publicRoot(root, title=title, height=height)
        pages = lc.stackContainer(layoutAlign='client', _class='pbl_formContainerStack', selected='^%s'%selected, **kwargs)
        return (top, pages)

    def publicTabbedPane(self, root, title=None,height=None,**kwargs):
        """
        return a header and a tab container
        """
        lc,top = self.publicRoot(root, title=title, height=height)
        pages = lc.tabContainer(layoutAlign='client', _class='pbl_formContainerTab', **kwargs)
        return (top, pages)

    def publicPage(self, pages,datapath=None, **kwargs):
        lc=pages.layoutContainer(**kwargs)

        bottom=lc.contentPane(layoutAlign='bottom', _class='pbl_formContainerBottom')
        client=lc.contentPane(layoutAlign='client', _class='pbl_formContainerClient',datapath=datapath)
        return (client,bottom)
        
    def publicTbarPage(self, pages,datapath='.client',tbar_height='24px',tbar_datapath='.toolbar', **kwargs):
        lc=pages.layoutContainer(**kwargs)
        tbar=lc.contentPane(layoutAlign='top',height=top_height,datapath=tbar_datapath).toolbar()
        client=lc.contentPane(layoutAlign='client', _class='pbl_formContainerClient',datapath=datapath)
        return (client,tbar)
        
    def publicRoot(self, root, title=None, height=None):
        if self.user:
            root.dataRecord('_pbl.user_record','assopy.utente', username=self.user, _init=True)
        root.data('gnr.workdate', self.workdate)        
        height = height or '97%'
        lc=root.layoutContainer(_class='pbl_formContainer', height=height,gnrId='rootwidget')
        top=lc.layoutContainer(layoutAlign='top', _class='pbl_formContainerTitle')
        topleft = top.contentPane(layoutAlign='left',width='130px',tooltip='!!Applicativo web realizzato con <b>Genropy</b>')
        topright = top.contentPane(layoutAlign='right', width='130px',margin_top='3px').div()
        topcli = top.contentPane(layoutAlign='client',margin_top='3px')
        if title:
            topcli.div(title)
        topright.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
        topright.dataScript('dummy', 'genro.pageReload()', fired='^aux.locale_ok')
        if self.user:
            topright.a(connect_onclick="genro.logout()", 
                  tooltip="!!Esci dall'applicativo Assopy",
                  href='#', _class='logout', content='&nbsp;')
        topright.dataScript('gnr.localizerClass',"""return 'localizer_'+status""",status='^gnr.localizerStatus',_init=True,_else="return 'localizer_hidden'")
        topright.div(connect_onclick='genro.pageBack()', _class='goback',tooltip='!!Torna alla pagina precedente')
        topright.a(connect_onclick='FIRE aux.locale = "it"', href='#', _class='it_flag', content='&nbsp;')
        topright.a(connect_onclick='FIRE aux.locale = "en"', href='#', _class='en_flag', content='&nbsp;')
        topright.div(connect_onclick='genro.dev.openLocalizer()', _class='^gnr.localizerClass',float='right')
        
        #topleft.div(_class='logout',width='20px',float='left').menu(action="function(attributes){genro.gotoURL(attributes.href)}").remote('menu_browse',cacheTime=60)
        topleft.div('Genropy',_class='genrologo',float='left')
        return lc,topcli

    def userRecord(self,path=None):
        if not hasattr(self,'_userRecord' ):
            user = self.pageArgs.get('_user_')
            if not user or not( 'passpartout' in self.userTags):
                user =  self.user
            self._userRecord=self.db.table('assopy.utente').record(username=user).output('bag')
        return self._userRecord[path]

    def anagraficaRecord(self,path=None):
        return self.userRecord()['@assopy_anagrafica_utente_id'][path]

    def oratoreRecord(self,path=None):
        return self.anagraficaRecord()['@assopy_oratore_anagrafica_id'][path]

    def socioRecord(self,path=None):
        return self.anagraficaRecord()['@assopy_socio_anagrafica_id'][path]

    def userOrdini(self,correnti=True):
        id_anagrafica=self.anagraficaRecord('id')
        id_evento = self.eventoRecord('id')
        where='$anagrafica_id=:id_anagrafica'
        if correnti:
            where='%s AND $evento_id=:id_evento' % where
        return self.db.query('assopy.ordini', where=where, id_anagrafica=id_anagrafica,id_evento=id_evento)

    def userTalks(self,correnti=True):
        id_oratore=self.oratoreRecord('id')
        id_evento = self.eventoRecord('id')
        where='$oratore_id=:id_oratore'
        if correnti:
             where='%s AND $evento_id=:id_evento' % where
        return self.db.query('assopy.talk', where=where, id_oratore=id_oratore,id_evento=id_evento)

    def eventoCorrente(self):
        return self.package.attributes['evento_corrente']

    def eventoRecord(self,path=None):
        if not hasattr(self,'_eventoRecord'):
            evento = self.eventoCorrente()
            self._eventoRecord= self.db.table('assopy.evento').record(codice=evento).output('bag')
        return self._eventoRecord[path]

    def inviaLinkDocumento(self, ordine_id):
        ordine = self.db.table('assopy.ordine').record(ordine_id).output('bag')
        ordine['link'] = self.externalUrl('assopy/stampa_ordine.py/stampa', ordine_id=ordine_id, locale=ordine['@anagrafica_id.@utente_id.locale'])
        return self.sendMailTemplate('invoice_link.xml', ordine['@anagrafica_id.@utente_id.email'], ordine)
        
    
    def menuButton(self,lbl,url):
        if url=='BACK':
            onclick='genro.pageBack'
        elif url=='LOGOUT':
            onclick='genro.logout()'
        elif url=='HOME':
            onclick='genro.gotoHome()'
        elif self.checkPermission(url):
            onclick= "genro.gotoURL('%s')"%url
        else:
            return
        if not self.currTbl:
            tbl=self.clientPane.table(border="0", _class='pbl_index')
            self.currTbl=tbl.tbody()
            self.currCol=2
        self.currCol=self.currCol+1
        if self.currCol>2:
            self.currCol=1
            self.currRow=self.currTbl.tr()
        self.currRow.td(lbl,connect_onclick=onclick)