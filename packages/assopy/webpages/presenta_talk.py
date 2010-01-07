#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" presenta_talk """
import time
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
        return '!!Assopy Presentazione talk'
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin,candidatoOratore'

    def main(self, root, newtalk=False, **kwargs):
        top, pages = self.publicPagedPane(root, '!!Proposta talk', selected='selectedPage')
        anagrafica_id=self.anagraficaRecord('id')
        if not anagrafica_id:
            self.pageNoAnag(pages)
        else:
            self.pageForm(pages, newtalk)
            self.pageSaving(pages)
            self.pageSaved(pages)

    def pageForm(self,pages,newtalk):
        client, bottom = self.publicPage(pages, datapath='form')
        client.dataScript('.isValid',"return true",dummy='^form.doSave',data='=.tabs',
                                     _if='genro.dataValidate(data)',
                                    _else="genro.focusOnError(data); return false;")  
                                                         
        client.dataScript('dummy','SET selectedPage=1;', isValid='^.isValid', _if='isValid')
        
        client.dataRpc('.saveResponse','save', data='=.tabs', _POST=True,
                           isValid='^.isValid' , _if='isValid', _onResult='SET selectedPage=2;')                           
        tc=client.tabContainer(margin='2px', selected='^.selectedTab', datapath='.tabs')
        oratore_id=self.oratoreRecord('id')
        talks=[]
        if oratore_id:
            talks=self.userTalks(correnti=True).fetch()
        self.oratorePane(tc,
                         datapath='.oratore',
                         title='!!Dati oratore',
                         oratore_id=oratore_id)
        
        for j,t in enumerate(talks):
            self.talkPane(tc, datapath='.talks.talk_%i'% j, talkcode=t['codice'], talk_id=t['id'], oratore_id=oratore_id,pane_number=j)
        newtalk=newtalk or (len(talks)==0) 
        if newtalk:
            j=len(talks)
            self.talkPane(tc, datapath='.talks.talk_%i'% j, talkcode='!!Nuovo talk', talk_id=None, oratore_id=oratore_id, newtalk=newtalk,pane_number=j)
        else:
            bottom.div('!!Nuovo talk',connect_onclick='genro.pageReload({newtalk:true})',_class='pbl_button',float='left')
            
        bottom.div('!!Registra', connect_onclick='FIRE form.doSave=true',_class='pbl_button pbl_confirm',float='right')
        bottom.div(u'!!Torna al menù',connect_onclick='genro.gotoURL("index.py")',_class='pbl_button',float='right')
        
    def oratorePane(self, pane, datapath, title, oratore_id):
        lc=pane.layoutContainer(title=title, datapath=datapath)
        right=lc.contentPane(layoutAlign='right',width='160px')
        lc=lc.layoutContainer(layoutAlign='client')
        pane=lc.contentPane(layoutAlign='top',height='100px')
        fb=pane.formbuilder(cols=1, datapath='.record')
        if oratore_id:
            fb.dataRecord('', 'assopy.oratore', pkey=oratore_id, _init=True,sync=True)
            pane.data('speakerImagePath',self.imageUrl())
            pane.dataScript('dummy',"genro.dlg.message(msg,genro.domById('speakerimg_btn'))",
                                          msg=u"!!L'immagine è stata salvata.", fired='^speakerImagePath')
            right.img(_class='speakerimg',src='^speakerImagePath',float='right')
            
            right.dataScript('dummy','genro.dlg.upload(msg,"uploadImg","speakerImagePath",{username:username},label,cancel,send)',
                                   msg='!!Scegli immagine',cancel='!!Annulla',label='!!Sfoglia...',label='!!Sfoglia...',
                                   username='=_pbl.user_record.username',
                                   send='!!Invia', fired='^invioImmagine')
            right.button('!!Scegli immagine',nodeId='speakerimg_btn',margin_left='17px',fire='invioImmagine')
        fb.dbCombobox(width='210px', lbl=u'!!Attività',value = '^.attivita',
                               dbtable='assopy.attivita',columns='descrizione')
        fb.dbCombobox(width='210px', lbl=u'!!Settore',value = '^.settore',
                               dbtable='assopy.settore',columns='descrizione')
        fb.field('assopy.oratore.www',width='440px', lbl='Homepage')
        pane=lc.tabContainer(layoutAlign='client',datapath='.record',margin='5px')
        c1=pane.contentPane(title='!!Presentazione Italiano')
        c1.textarea(value='^.presentazione', _class='pres_oratore')
        c2=pane.contentPane(title='!!Presentazione Inglese')
        c2.textarea(value='^.presentazione_en', _class='pres_oratore')
    
    def talkPane(self, pane, datapath, talkcode, talk_id ,oratore_id,newtalk=False,pane_number=None):
        title=talkcode
        lc=pane.layoutContainer(title=title, datapath=datapath, selected=(newtalk and oratore_id ), height='100%')
        top=lc.layoutContainer(layoutAlign='top',height='90px',border_bottom='1px solid silver')
        right=top.contentPane(layoutAlign='right',width='270px',border_left='1px solid silver')
        fb = right.formbuilder(cols=1,border_spacing='4px',margin_top='2px',margin_left='6px')
        fb.filteringSelect(value='^.record.durata',lbl='!!Durata',
                           values='!!30:30 minuti,45:45 minuti,60:60 minuti,90:90 minuti',default=60)
        fb.field('assopy.talk.oratore2_id',lbl='!!Con',value='^.record.oratore2_id')
        pane=top.contentPane(layoutAlign='client')
        client=lc.contentPane(layoutAlign='client',background_color='whitesmoke')
        fb = pane.formbuilder(cols=2, datapath='.record',border_spacing='6px',margin_top='2px')
        if talk_id:
            fb.dataRecord('', 'assopy.talk', pkey=talk_id, _init=True,sync=True)            
        fb.field('assopy.talk.codice', width='100px', disabled=(not newtalk),lbl='!!Nome breve',
        promptMessage=u'!!Usare un nome breve. Una volta salvato non sarà modificabile.')
        fb.field('assopy.talk.track_id',lbl='Track')

        fb.field('assopy.talk.titolo',required=True,width='360px', colspan=2)
        fb.field('assopy.talk.argomento',width='360px',colspan=2,lbl='Keywords')
        tc=client.tabContainer(height='100%')
        c1=tc.contentPane(title='!! Abstract Italiano')
        #ci.div('!!Abstract',_class='pbl_largemessage',margin='auto',margin_top='2px',margin_bottom='3px')
        c1.textarea(lbl_valign='top', lbl='Abstract', 
                     value='^.record.abstract',_class='talk_abstract', colspan=2)
        
        c2=tc.contentPane(title='!! Abstract Inglese')
        #ci.div('!!Abstract',_class='pbl_largemessage',margin='auto',margin_top='2px',margin_bottom='3px')
        c2.textarea(value='^.record.abstract_en',_class='talk_abstract', colspan=2)
        if newtalk:
            right.div(u'!!Scegli un nome breve per il tuo talk. Ricorda che non sarà modificabile.',_class='pbl_largemessage',
                                                 text_align='center',font_size='X-small')
            right.div(u'!!Dopo aver salvato il talk potrai inviare un allegato preferibilmente in PDF o HTML',_class='pbl_largemessage',
                                                 text_align='center',font_size='X-small')
        else:
            fire='attach_fire_%i' % pane_number
            btn='attach_btn_%i' % pane_number
            ldr='attach_ldr_%i' % pane_number
            pth='attach_pth_%i' % pane_number
            talkFileUrl = self.talkfileUrl(talkcode)
            pane.data(pth, talkFileUrl)
            pane.dataScript('dummy',"genro.dlg.message(msg,genro.domById('%s'))" %  btn, msg=u"L'allegato è stato salvato.", fired='^%s' % pth)
            #tt = right.dropdownbutton('!!Invia allegato', nodeId=drp, margin_top=' 5px',float='right',margin_right='10px').tooltipDialog(nodeId=dlg).div(background_color='grey',padding='3px')
           # tt.fileInput(width='27em', height='1.4em', margin_top='1px', label='!!Sfoglia...', cancel='!!Annulla',
                                 #remote_username=self.user, remote_talkcode=talkcode, method='uploadTalk', nodeId=ldr, onUpload="genro.setData('%s', $1)" % pth )
            #tt.button("!!Invio",margin_top='5px', action="genro.nodeById('%s').widget.onCancel();genro.nodeById('%s').widget.uploadFile()" % (dlg, ldr))
            
            
            
            right.dataScript('dummy','genro.dlg.upload(msg,"uploadTalk",pth,{username:username,talkcode:talkcode},label,cancel,send)',
                                   msg='!!Invia allegato',cancel='!!Annulla',label='!!Sfoglia...',label='!!Sfoglia...',
                                   username='=_pbl.user_record.username',
                                   talkcode='=.record.codice',
                                   pth=pth,
                                   send='!!Invia', fired='^%s' % fire)
            right.button('!!Invia allegato',nodeId=btn,margin_top=' 5px',float='right',margin_right='10px',fire=fire)
            
            right.dataScript('dummy', 'genro.openWindow(fileurl)', fileurl='=%s' % pth, fired='^.%s_fire'%pth)
            right.button('!!Mostra allegato',margin_top='5px', margin_left='10px',float='left', fire='.%s_fire'%pth,visible='^%s'%pth)

    def imageUrl(self):
        imgpath= self.talkFilePath('_speakerimg') 
        if not imgpath:
            imgpath=self.utils.siteFolder('data', 'speakers','_speakerimg.gif',relative=True)
        else:
            imgpath=self.utils.siteFolder(imgpath,relative=True)
        return imgpath
        
    def talkfileUrl(self,talkcode=None,**kwargs):
        talkfile= self.talkFilePath(talkcode)
        if talkfile:
            return self.utils.rootFolder(talkfile,relative=True)
            
    def talkFilePath(self,talk):
        userfolder=os.path.join(self.siteFolder, 'data', 'speakers',self.user)
        try:
            files=os.listdir(userfolder)
            talkfiles=[x for x in files if (x.startswith('%s.'%talk)) or (x==talk)]
            
            if talkfiles:
                return os.path.join(userfolder, talkfiles[0])
        except:
            pass
    
        
    def pageSaving(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio in corso...", _class='pbl_largemessage', margin_top='1em',margin_right='3em',margin_left='3em')

    def pageSaved(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio completato",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Rivedi Pagina', connect_onclick='genro.pageReload({})',_class='pbl_button',float='right')
        bottom.div(u'!!Torna al menù', connect_onclick='genro.gotoURL("index.py")',_class='pbl_button',float='right')
        
    
    def pageNoAnag(self,pages):
        client,bottom=self.publicPage(pages)
        client.div(u"!!Per proporre un talk è necessario completare il proprio profilo",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Completa il profilo',width='14em' ,connect_onclick='genro.gotoURL("modifica_utente.py")',_class='pbl_button',float='right')
        bottom.div(u'!!Torna al menù',width='14em', connect_onclick='genro.gotoURL("index.py")',_class='pbl_button',float='right')
    
    def rpc_save(self,data=None,**kwargs):
        tbl_oratore = self.db.table('assopy.oratore')
        oratore=data['oratore.record']
        if not oratore['id']:
            oratore['id']=tbl_oratore.newPkeyValue()
            oratore['anagrafica_id']=self.anagraficaRecord('id')
            tbl_oratore.insert(oratore)
        else:
            tbl_oratore.update(oratore)
        tbl_talk = self.db.table('assopy.talk')
        for talk in data['talks'].values():
            talk=talk['record']
            talk['oratore_id']=oratore['id']
            talk['evento_id']=self.eventoRecord('id')
            tbl_talk.insertOrUpdate(talk)
        self.db.commit()
        return 'ok'
        
    def rpc_uploadImg(self,username='',ext='',**kwargs):
        form=self.request.form
        f=form['fileHandle'].file
        content=f.read()
        imgfile=self.talkFilePath('_speakerimg')
        if imgfile and os.path.isfile(imgfile):
            os.remove(imgfile)
        filename='_speakerimg%s' % ext
        old_umask = os.umask(2)
        
        outfile=self.createFileInData('speakers',username,filename)
        outfile.write(content)
        outfile.close()
        os.umask(old_umask)
        
        result=self.imageUrl()
        return "<html><body><textarea>%s</textarea></body></html>" % (str(result))

        
    def rpc_uploadTalk(self,username='',talkcode='',ext='',**kwargs):
        old_umask = os.umask(2)

        form=self.request.form
        talkcode=talkcode.strip()
        f=form['fileHandle'].file
        content=f.read() 
        talkfile=self.talkFilePath(talkcode)
        if talkfile and os.path.isfile(talkfile):
            os.remove(talkfile)
        filename='%s%s' %(talkcode,ext)
        outfile=self.createFileInData('speakers',username,filename)
        outfile.write(content)
        outfile.close()
        result=self.utils.rootFolder(self.talkFilePath(talkcode),relative=True)
        
        os.umask(old_umask)
        
        return "<html><body><textarea>%s</textarea></body></html>" % (str(result))
        
    def rpc_talkfile(self,talkcode=None):
        return self.talkFilePath(talkcode)
        

