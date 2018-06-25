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
                itemspath=None,workspaces=None,channelspath=None,itemIdentifier=None,dashboardIdentifier=None,title=None,**kwargs):
        self.itemIdentifier = itemIdentifier or 'di_%s' %id(pane)
        self.dashboardIdentifier = dashboardIdentifier
        self.workspaces = workspaces or '#%s.dashboards' %dashboardIdentifier if dashboardIdentifier else 'dashboardItems'
        if not workpath:
            workpath = '%s.%s' %(workspaces,self.itemIdentifier)
        self.editMode = editMode
        self.workpath = workpath
        self.itemRunner = '^%s.runItem' %self.workpath
        self.parameters = parameters or Bag()
        self.itemspath = itemspath
        self.channelspath = channelspath
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
        confpane = None
        if self.editMode:
            conftc = bc.tabContainer(margin='2px',datapath='.conf',childname='config',region='center')
            self.configuration(conftc.contentPane(title='!!Configurations'),**kwargs)
            self.configurationSubscriber(conftc.contentPane(title='!!Subscriptions'))
        else:
            self.configuration(bc.contentPane(region='center',datapath='.conf',childname='config'),**kwargs)


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
                        action="""var curtitle = this.getRelativeData(wp+'.current_title');
                                    var that = this;
                                    genro.dlg.ask(_T('Closing item ')+curtitle,
                                            _T('You are going to remove a item '+curtitle),
                                            {confirm:_T('Confirm'),cancel:_T('Cancel')},
                                            {confirm:function(){
                                                genro.dashboards[dashboardIdentifier].emptyTile(that);
                                            }, cancel:function(){}});
                                    """,wp=self.workpath,dashboardIdentifier=self.dashboardIdentifier)
            
        top.lightbutton(_class='menu_white_svg',height='16px',width='16px',
                        position='absolute',top='1px',right='4px',cursor='pointer',
                        action="""
                        if(event.shiftKey){
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
    
    def configurationSubscriber(self,pane):
        frame = pane.bagGrid(storepath='%s.conf_subscriber' %self.storepath,
                        datapath='%s.configurationSubscriber' %self.workpath,
                        struct=self.configurationSubscriberStruct,
                        addrow=False,
                        margin='2px',border='1px solid silver')
        frame.dataController("""
            var conf = genro.getData(confpath);
            var conf_subscribers = genro.getData(subspath) || new gnr.GnrBag();
            conf.getNodes().forEach(function(n){
                if(n.attr.autoTopic){
                    conf_subscribers.setItem(n.attr.autoTopic,new gnr.GnrBag({topic:n.attr.autoTopic,varpath:n.label}));
                }
            })
            var cb = function(){
                var result = new gnr.GnrBag();
                conf.forEach(function(n){
                    if(!n._value){
                        result.setItem(n.label,null,{caption:n.attr.lbl || n.label,default_kw:{varpath:n.label}});
                    }
                });
                return result;
            };
            genro.setData(subspath,conf_subscribers);
            SET .currentParametersMenu = new gnr.GnrBagCbResolver({method:cb});
        """,_onBuilt=True,confpath='%s.conf' %self.storepath,
            subspath='%s.conf_subscriber' %self.storepath)
        frame.dataController("""
        if(!channels){
            channels = new gnr.GnrBag();
            this.setRelativeData(channelspath,channels);
        }
        subscribers.values().forEach(function(v){
            var topic = v.getItem('topic');
            if(!channels.getNode(topic)){
                channels.setItem(topic,new gnr.GnrBag({topic:topic}));
            }
        });
        """,channelspath=self.channelspath,
            channels='=%s' %self.channelspath,
            subscribers='^%s.conf_subscriber' %self.storepath,
            _delay=100)
        bar = frame.top.bar.replaceSlots('delrow','delrow,addrow',addrow_defaults='.currentParametersMenu')
    
    def configurationSubscriberStruct(self,struct):
        r=struct.view().rows()
        r.cell('varpath',name='!!Parameter',width='20em')
        r.cell('topic',name='!!Topic',width='20em',
                            edit=dict(tag='comboBox',
                                        values='=%s?=#v.keys().join(",")' %self.channelspath))

    def __getattr__(self, fname): 
        return getattr(self,fname) if fname in self.__dict__ else getattr(self.page,fname)
        