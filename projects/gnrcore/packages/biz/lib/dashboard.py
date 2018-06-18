#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module dashboard : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os,sys
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrbag import Bag



class BaseDashboardItem(object):
    item_name=''
    run_onbuilt = 1
    run_timer = None
    title_template = '$title'
    linked_item = None
    py_requires = None
    css_requires = None
    js_requires = None

    def __init__(self, page=None, resource_table=None, **kwargs):
        self.page = page
        self.db = page.db
        self.tblobj = resource_table


    @extract_kwargs(itempar=True)
    def __call__(self,pane,editMode=None,workpath=None,parameters=None,itempar_kwargs=None,
                itemspath=None,workspaces=None,itemIdentifier=None,title=None,**kwargs):
        self.itemIdentifier = itemIdentifier or 'di_%s' %id(pane)
        self.workspaces = workspaces or 'dashboards'
        if not workpath:
            workpath = '%s.%s' %(workspaces,self.itemIdentifier)
        self.editMode = editMode
        self.workpath = workpath
        self.itemRunner = '^%s.runItem' %self.workpath
        self.parameters = parameters or Bag()
        self.itemspath = itemspath
        self.title = title or itempar_kwargs.pop('title',None) or self.item_name
        self.storepath = '%s.%s' %(itemspath,self.itemIdentifier) if itemspath and self.itemIdentifier else ''
        bc = pane.borderContainer()
        self.itembar(bc.contentPane(region='top',min_height='20px'))
        sc = bc.stackContainer(region='center',datapath=self.storepath,selectedPage='^%s._dashboardPageSelected' %workpath)
        self.item_centerstack = sc
        kwargs.update(itempar_kwargs)
        kwargs.update(self.parameters.asDict(ascii=True))
        pane = sc.contentPane(pageName='content',childname='content')
        self.content(pane,**kwargs)
        bc = sc.borderContainer(pageName='conf')
        bc.dataController("""FIRE .runItem;""",
                        _onBuilt=self.run_onbuilt,
                        datapath=workpath,_timing='=.runTimer')
        bc.dataController("""if(runRequired){
            SET .runRequired = false;
            FIRE .runItem;
        }""",
        changedConfig='^.configuration_changed',runRequired='=.runRequired',datapath=self.workpath)
        self.configuration(bc.contentPane(region='center',datapath='.conf',childname='config'),**kwargs)
       #bottom = bc.contentPane(region='bottom',_class='slotbar_dialog_footer')
       #bottom.button('!!Ok',top='2px',right='2px',action="""sc.switchPage(0);
       #                                                    FIRE %s.configuration_changed;
       #                                                """ %(workpath or ''),sc=sc.js_widget)
        

    def itembar(self,pane):
        top = pane.div(height='20px',_class='dashboard_item_top',onDrag="""dragValues['itemIdentifier'] = '%s';
                                               """ %self.itemIdentifier,draggable=self.itemIdentifier is not None)
        self.item_topbar = top
        top.div('^.current_title',text_align='center',datapath=self.workpath,padding_top='3px',
                connect_ondblclick="""
                var store = genro.getData('%s');
                var dflt = store.getItem('title');
                genro.dlg.prompt(_T('Change title'),{lbl:_T('Title'),dflt:dflt,action:function(newtitle){store.setItem('title',newtitle);}});
                """ %self.storepath)
        top.dataFormula('%s.current_title' %self.workpath,"dataTemplate(tpl,itemaData)",tpl=self.title_template,
                        itemaData='^%s' %self.storepath,_onBuilt=True)
        if self.editMode:
            top.lightbutton(_class='close_svg',height='16px',
                        width='16px',top='1px',position='absolute',
                        left='4px',cursor='pointer',
                        action="""var curtitle = this.getRelativeData('%s.current_title');
                                    var that = this;
                                    genro.dlg.ask(_T('Closing item ')+curtitle,
                                            _T('You are going to remove a item '+curtitle),
                                            {confirm:_T('Confirm'),cancel:_T('Cancel')},
                                            {confirm:function(){
                                                genro.dashboards.emptyTile(that);
                                            }, cancel:function(){}});
                                    """ %self.workpath)
            
        top.lightbutton(_class='menu_white_svg',height='16px',width='16px',
                        position='absolute',top='1px',right='4px',cursor='pointer',
                        action="""
                        if(event.shiftKey){
                            console.log('publish',itemIdentifier+'_parameters_open')
                            genro.publish(itemIdentifier+'_parameters_open');
                        }else{
                            if(_dashboardPageSelected=='conf'){
                                SET ._dashboardPageSelected = 'content';
                                FIRE .configuration_changed;
                            }else{
                                SET ._dashboardPageSelected = 'conf';
                            } 
                        }
                        """ ,datapath=self.workpath,
                        itemIdentifier=self.itemIdentifier,
                        _dashboardPageSelected='=._dashboardPageSelected')
        if self.editMode and self.linked_item:
            box = top.div(position='absolute',top='1px',right='40px',height='16px',width='20px')
            box.div(draggable=True,cursor='move',display='inline-block',
                            workpath=self.workpath,storepath=self.storepath,
                            height='15px',width='15px',**self.linked_item)


    def content(self,pane,**kwargs):
        pass

    def configuration(self,pane,**kwargs):
        pass
        
    def __getattr__(self, fname): 
        return getattr(self,fname) if fname in self.__dict__ else getattr(self.page,fname)
        