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

"""Component for dialogs"""

from gnr.web.gnrbaseclasses import BaseComponent

class Dialogs(BaseComponent):
    """A class that handles the dialog :ref:`components <component>`"""
    css_requires = 'dialogs'

    def simpleDialog(self, parent, title='', dlgId=None, height='', width='', datapath='',
                     cb_center=None, cb_bottom='*', confirm_btn=None, **kwargs):
        """A simple dialog layout"""
        bc = self._innerDialog(parent, title=title, dlgId=dlgId, height=height, width=width, datapath=datapath,
                               cb_center=cb_center, cb_bottom=cb_bottom, confirm_btn=confirm_btn, **kwargs)
        bc.dataController("""FIRE ._setOpener = opener;
                             FIRE ._openSimpleDialog; 
                             """, opener="^.open")
        bc.dataController("FIRE ._closeSimpleDialog;", _fired="^.close")
        return bc

    def _innerDialog(self, parent, title='', dlgId=None, datapath='', height='', width='',
                     cb_center=None, cb_bottom='*', confirm_btn=None,
                     formId=None,formDatapath=None,pkeyPath=None,controllerPath=None, **kwargs):
        """Internal method used by dialogs micro components"""
        dialog = parent.dialog(title=title, nodeId=dlgId, datapath=datapath, **kwargs)
        dialog.dataController("""if(typeof(opener)=='object'){
                                if (opener.dialogPage){
                                    SET .page = objectPop(opener,'dialogPage');
                                }
                                opener = new gnr.GnrBag(opener);
                             }else if(opener==true){
                                 opener = new gnr.GnrBag();
                             }
                             SET .opener = opener;""", opener="^._setOpener")
        dialog.dataController('genro.wdgById(dlgId).show();SET .isOpen=true;',
                              dlgId=dlgId, _fired="^._openSimpleDialog")
        dialog.dataController('genro.wdgById(dlgId).hide();SET .isOpen=false;',
                              dlgId=dlgId, _fired="^._closeSimpleDialog")

        sc = dialog.stackContainer(height=height, width=width, selectedPage='^.selected_stack_page')
        sc.dataController("SET .selected_stack_page = %s_page[0];" % dlgId, **{'subscribe_%s_page' % dlgId: True})
        bc = sc.borderContainer(pageName='main',formId=formId,formDatapath=formDatapath,pkeyPath=pkeyPath,controllerPath=controllerPath)
        bc.mainStack = sc
        cb_bottom = cb_bottom or getattr(self, '%s_bottom' % dlgId, None)
        cb_center = cb_center or getattr(self, '%s_center' % dlgId, None)
        if cb_bottom == '*':
            cb_bottom = self.formDialog_bottom
        if cb_bottom:
            cb_bottom(bc, region='bottom', _class='dialog_bottom', confirm_btn=confirm_btn)
        if cb_center:
            cb_center(bc, region='center', _class='pbl_dialog_center', dlgId=dlgId, **kwargs)
        return bc

    def formDialog(self, parent, title='', formId='', height='', width='', datapath='', pkeyPath=None,
                   cb_center=None, cb_bottom='*', loadsync=False, confirm_btn=None,
                   allowNoChanges=True, **kwargs):
        """A dialog that use a form object"""
        dlgId = '%s_dlg' % formId
        bc = self._innerDialog(parent, title=title, dlgId=dlgId, datapath=datapath,
                                formDatapath='.data',controllerPath='.form', 
                                formId=formId,pkeyPath=pkeyPath,
                                height=height, width=width, cb_bottom=cb_bottom,
                               confirm_btn=confirm_btn)
        bc.dataFormula(".disable_button", "!valid||(!changed && !allowNoChanges)||saving", valid="^.form.valid",
                       changed="^.form.changed", saving='^.form.saving', allowNoChanges=allowNoChanges,
                       _formId=formId, _if='_formId')
        if cb_center:
            cb_center(bc, region='center', datapath='.data', _class='pbl_dialog_center',
                      
                       **kwargs)
            #only in form mode
        bc.dataController("""
                             FIRE ._setOpener = opener;
                             FIRE ._openSimpleDialog; 
                             FIRE .load;
                             """, opener="^.open")
        bc.dataController("FIRE ._closeSimpleDialog;", _fired="^.close")
        bc.dataController("genro.formById(_formId).load({sync:loadsync});",
                          _fired="^.load", _delay=1, _formId=formId, _if='_formId',
                          loadsync=loadsync)
        bc.dataController('genro.formById(_formId).save(always=="always"?true:false);',
                          always="^.save", _formId=formId, _if='_formId')
        bc.dataController('genro.formById(_formId).saved(); FIRE .close;', _formId=formId,
                          _fired="^.saved", _if='_formId')
        bc.dataController('genro.formById(_formId).loaded();', _formId=formId,
                          _if='_formId', _fired="^.loaded")
        return bc

    def formDialog_bottom(self, bc, confirm_btn=None, **kwargs):
        """Standard bottom callback used by :ref:`simpledialog` and :ref:`formdialog`"""
        bottom = bc.contentPane(**kwargs)
        confirm_btn = confirm_btn or '!!Confirm'
        bottom.button(confirm_btn, baseClass='bottom_btn', float='right', margin='1px',
                      fire_always='.save', disabled='^.disable_button')
        bottom.button('!!Cancel', baseClass='bottom_btn', float='right', margin='1px', fire='.close')
        return bottom

    def iframeDialog(self, parent, title='', dlgId='', height='', width='', src='', datapath='',
                     confirm_btn=None, allowNoChanges=True, cb_bottom=None, **kwargs):
        """A :ref:`simpledialog` with an :ref:`iframe` inside"""
        def cb_center(parentBC, **kwargs):
            pane = parentBC.contentPane(**kwargs)
            pane.iframe(order='0px', height='100%', width='100%',
                        border=0, nodeId='%s_frame' % dlgId,
                        src=src, condition_function='return value;',
                        condition_value='^.isOpen')
                        
        dlg = self.simpleDialog(parent, title=title, datapath=datapath,
                                dlgId=dlgId, height=height, width=width,
                                cb_center=cb_center, cb_bottom=cb_bottom, **kwargs)

    ############ OLD ##############################################################
    def hiddenTooltipDialog(self, pane, height='20ex', width='30em', title=None,
                            close_action=None, dlgId=None, nodeId=None,
                            bottom_left=None, bottom_left_action=None,
                            bottom_right=None, bottom_right_action=None,
                            fired=None, datapath=None, onOpen=None, onEnter=None):
        """.. warning:: deprecated since version 0.7
        
        A tooltipdialog box opened by \"_fired\""""
        onOpen = onOpen or ''
        dlgId = dlgId or nodeId or self.getUuid()
        bcId = '%s_bc' % dlgId
        btnId = '%s_btn' % dlgId
        dlg = pane.dropdownbutton('', hidden=True, nodeId=btnId, datapath=datapath)

        dlg = dlg.tooltipdialog(nodeId=dlgId, connect_onOpen='genro.wdgById("%s").resize();%s' % (bcId, onOpen),
                                connect_onClose=close_action)
        pane.dataController(""" 
                                var aroundNode = typeof(fired)=='string' ? genro.nodeById(fired) : genro._firingNode;
                                if(_reason=='container'){
                                    return;
                                }
                                genro.wdgById(btnId)._openDropDown(aroundNode.getDomNode());""",
                            btnId=btnId, fired=fired)
        container = dlg.borderContainer(height=height, width=width, nodeId=bcId, onEnter=onEnter,
                                        _class='pbl_dialog_center')
        if title is not False:
            top = container.contentPane(region='top', _class='dijitDialogTitleBar', height='18px')
            if close_action:
                top.div(_class='icnTabClose', float='right', margin='2px', connect_onclick=close_action)
            top.div(title)
        if bottom_left or bottom_right:
            bottom = container.contentPane(region='bottom', height='18px', _class='pbl_roundedGroupBottom')
            if bottom_left:
                bottom.button(bottom_left, baseClass='bottom_btn',
                              connect_onclick=bottom_left_action, float='right', margin_right='5px')
            if bottom_right:
                bottom.button(bottom_right, baseClass='bottom_btn',
                              connect_onclick=bottom_right_action, float='right', margin_right='5px')
        center = container.borderContainer(region='center')
        return center

    def confirm(self, pane, dlgId=None, title='!!Confirm', msg='!!Are you sure?',
                width='30em', height='20ex', fired=None,
                btn_ok='!!Confirm', action_ok=None, btn_cancel='!!Cancel', action_cancel=None, **kwargs):
        """.. warning:: deprecated since version 0.7
        
        A confirm dialog"""
        dlgId = dlgId or self.getUuid()

        pane.dataController('genro.wdgById(dlgId).show()', dlgId=dlgId, fired=fired)
        dlg = pane.dialog(title=title, nodeId=dlgId).borderContainer(width=width, height=height)
        bottom = dlg.contentPane(region='bottom', height='27px', font_size='.9em', background_color='silver',
                                 connect_onclick="""if($1.target != this.widget.domNode){genro.wdgById('%s').hide()}""" % dlgId)
        center = dlg.contentPane(region='center')
        center.div(msg, _class='dlg_msgbox')
        bottom.button(btn_ok, action=action_ok, float='right')
        bottom.button(btn_cancel, action=action_cancel, float='right')
        for btn, action in [(kwargs[k], kwargs.get('action_%s' % k[4:])) for k in kwargs.keys() if
                            k.startswith('btn_')]:
            bottom.button(btn, action=action, float='left')                           