# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for dialogs:
"""
from gnr.web.gnrbaseclasses import BaseComponent

class Dialogs(BaseComponent):
    css_requires = 'dialogs'
    def hiddenTooltipDialog(self, pane, height='20ex',width='30em',title=None, 
                            close_action=None, dlgId=None, nodeId=None,
                            bottom_left=None,bottom_left_action=None,
                            bottom_right=None,bottom_right_action=None,
                            fired=None, datapath=None, onOpen=None, onEnter=None):
        onOpen = onOpen or ''
        dlgId = dlgId or nodeId or self.getUuid()
        bcId = '%s_bc' % dlgId
        btnId = '%s_btn' % dlgId
        dlg = pane.dropdownbutton('', hidden=True, nodeId=btnId, datapath=datapath)

        dlg=dlg.tooltipdialog(nodeId=dlgId, connect_onOpen='genro.wdgById("%s").resize();%s' % (bcId, onOpen),
                              connect_onClose=close_action)
        pane.dataController("""genro.wdgById(btnId)._openDropDown(genro._firingNode.getDomNode());""", 
                                btnId=btnId, fired=fired) 
        container=dlg.borderContainer(height=height,width=width,nodeId=bcId, onEnter=onEnter)
        top = container.contentPane(region='top',_class='dijitDialogTitleBar',height='18px')
        if close_action:
            top.div(_class='icnTabClose',float='right',margin='2px',connect_onclick=close_action)
        top.div(title)        
        bottom = container.contentPane(region='bottom',height='18px')
        if bottom_left:
            bottom.button(bottom_left,baseClass='bottom_btn',
                       connect_onclick=bottom_left_action,float='right',margin_right='5px')
        if bottom_right:
            bottom.button(bottom_right,baseClass='bottom_btn',
                       connect_onclick=bottom_right_action,float='right',margin_right='5px')
        center=container.borderContainer(region='center')
        return center
        
    def confirm(self, pane, dlgId=None, title='!!Confirm',msg='!!Are you sure ?',
                    width='30em', height='20ex', fired=None, 
                    btn_ok='!!Confirm', action_ok=None, btn_cancel='!!Cancel', action_cancel=None, **kwargs):
        dlgId = dlgId or self.getUuid()
        
        pane.dataController('genro.wdgById(dlgId).show()', dlgId=dlgId, fired=fired)
        dlg = pane.dialog(title=title, nodeId=dlgId).borderContainer(width=width, height=height)
        bottom = dlg.contentPane(region='bottom', height='27px', font_size='.9em', background_color='silver',
                                    connect_onclick="""if($1.target != this.widget.domNode){genro.wdgById('%s').hide()}""" % dlgId)
        center = dlg.contentPane(region='center')
        center.div(msg, _class='dlg_msgbox')
        bottom.button(btn_ok, action=action_ok, float='right')
        bottom.button(btn_cancel, action=action_cancel, float='right')
        for btn, action in [(kwargs[k], kwargs.get('action_%s' % k[4:])) for k in kwargs.keys() if k.startswith('btn_')]:
            bottom.button(btn, action=action, float='left')
        

    def thermoDialog(self, pane, thermoid='thermo', title='', thermolines=1, fired=None, alertResult=False):
        dlgid = 'dlg_%s' % thermoid
        dlg = pane.dialog(nodeId=dlgid, title=title,datapath='_thermo.%s.result' % thermoid,
                        closable='ask', close_msg='!!Stop the batch execution ?', close_confirm='Stop', close_cancel='Continue', 
                        close_action='FIRE ^_thermo.%s.flag = "stop"' % thermoid,
                        connect_show='this.intervalRef = setInterval(function(){genro.fireEvent("_thermo.%s.flag")}, 500)' % thermoid,
                        connect_hide='clearInterval(this.intervalRef);')
                        #onAskCancel
        bc=dlg.borderContainer(width='330px', height='%ipx' %(100+thermolines*40) )
        footer=bc.contentPane(region='bottom', _class='dialog_bottom')
        body=bc.contentPane(region='center')
        for x in range(thermolines):
            tl = body.div(datapath='.t%i' % (x+1, ), border_bottom='1px solid gray', margin_bottom='3px')
            tl.div('^.message', height='1em', text_align='center')
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum', 
                          places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')
                          
        footer.button('Stop', baseClass='bottom_btn',
                action='genro.wdgById("%s").onAskCancel();' % dlgid)
        pane.dataController('console.log("open thermo %s");genro.wdgById("%s").show()' %(dlgid,dlgid), fired=fired)
        pane.dataController('genro.wdgById(dlgid).hide();', dlgid=dlgid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        if alertResult:
            pane.dataFormula('gnr.alert', 'msg', msg='=_thermo.%s.result.message' % thermoid, 
                            status='^_thermo.%s.result.status' % thermoid, _if='(status=="stopped" || status=="end")')
        
        pane.dataRpc('_thermo.%s.result' % thermoid, 'app.getThermo', thermoid=thermoid,
                                                             flag='^_thermo.%s.flag' % thermoid)
                                                             
class DialogForm(BaseComponent):
    def dialog_form(self,parent,title='',formId='',height='',width='',datapath='',
                cb_center=None,cb_bottom='*',loadsync=False,confirm_btn=None,
                allowNoChanges=True,**kwargs):
        def cb_bottom_standard(bc,confirm_btn=None,**kwargs):
            bottom = bc.contentPane(**kwargs)
            confirm_btn = confirm_btn or '!!Confirm'
            bottom.button(confirm_btn,baseClass='bottom_btn',float='right',margin='1px',
                            fire_always='.save',disabled='^.disable_button')
            bottom.button('!!Cancel',baseClass='bottom_btn',float='right',margin='1px',fire='.hide')

            bottom.dataFormula(".disable_button", "!valid||(!changed||allowNoChanges)||saving",valid="^.form.valid",
                                changed="^.form.changed",saving='^.form.saving',
                                allowNoChanges=allowNoChanges)
        if cb_bottom=='*':
            cb_bottom=cb_bottom_standard
        dlgId='%s_dlg'%formId
        dialog = parent.dialog(title=title,nodeId=dlgId,datapath=datapath,**kwargs)
        bc=dialog.borderContainer(height=height,width=width)
        if cb_bottom:
            cb_bottom(bc,region='bottom',_class='dialog_bottom',confirm_btn=confirm_btn)
        if cb_center:
            cb_center(bc,region='center',datapath='.data',_class='pbl_dialog_center', 
                     formId=formId,dlgId=dlgId)
        
        bc.dataController('genro.wdgById(dlgId).show();',dlgId=dlgId,_fired="^.show" )
        bc.dataController('genro.wdgById(dlgId).hide();',dlgId=dlgId,_fired="^.hide" )
        bc.dataController("FIRE .show; console.log(formId); genro.formById(formId).load(loadsync)" ,
                        formId=formId,loadsync=loadsync,_fired="^.open" )

        bc.dataController('genro.formById("%s").save(always=="always"?true:false);' %formId,
                          always="^.save" )
        bc.dataController('genro.formById("%s").saved(); FIRE .hide;' %formId,
                         _fired="^.saved" )
        bc.dataController('genro.formById("%s").loaded();' %formId,_fired="^.loaded" )
        return bc                                      
