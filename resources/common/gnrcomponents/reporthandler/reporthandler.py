# -*- coding: utf-8 -*-
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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrbag import Bag


class ReportHandler(BaseComponent):
    py_requires='th/th:TableHandler'
    js_requires='gnrcomponents/reporthandler/reporthandler'
    @extract_kwargs(condition=dict(slice_prefix=False))
    @struct_method
    def rh_reportHandler(self,pane,table=None,condition=None,condition_kwargs=None,nodeId=None,
                            reportIdentifier=None,**kwargs):
        nodeId = nodeId or 'rh_%s' %table.replace('.','_')
        bc = pane.borderContainer(datapath='.%s' %nodeId,_anchor=True,**kwargs)
        bc.child('_reportHandlerLayout',region='center',
                            table=table,nodeId=nodeId,
                            userObjectId=reportIdentifier,**kwargs)
        bc.dataController("""
            if(autorun){
                var that = this;
                genro.callAfter(function(){
                    that.fireEvent('.getReportBag',true);
                },2000,this,'rh_run');
            }
            """,
            conf_group_by='^.conf.group_by',
            conf_order_by='^.conf.order_by',
            conf_values='^.conf.values',
            conf_query='^.conf.query',
            autorun='=.conf.autorun',
            #_delay=2000,
            bcNode=bc)
     
        bc.dataRpc('.result',self.rh_reportBag,
                    table=table,
                    condition=condition,
                    group_by='=.conf.group_by',
                    values='=.conf.values',
                    query='=.conf.query',
                    _lockScreen=dict(thermo=True),
                    _onCalling="""
                        if(!genro.dom.isVisible(_bcNode)){
                            return false;
                        }
                    """,
                    _fired='^.getReportBag',
                    _bcNode=bc,**condition_kwargs)
    
    @public_method
    def rh_reportBag(self,table=None,query=None,condition=None,values=None,group_by=None,**kwargs):
        if not group_by:
            return
        columns_list = list()
        group_list = list()
        def getfield(v):
            col = v['field']
            if not col.startswith('@'):
                col = '$%s' %col
            return col
        for v in list(group_by.values()):
            col = getfield(v)
            group_list.append(col)
            if v['field']!= v['name']:
                col = '%s AS %s' %(col,v['name'])
            columns_list.append(col)
        for v in list(values.values()):
            col = getfield(v)
            aggregator = v['aggregator']
            if not aggregator:
                if v['dtype'] in ('N','L','F','I'):
                    aggregator = 'sum'
            col = '%s(%s) AS %s' %(aggregator,col,v['name'])
            columns_list.append(col)
        tblobj = self.db.table(table)
        where = query.pop('where')
        order_by = query.pop('order_by') or group_list[0]
        limit = query.pop('limit')
        querykw = {'limit':limit,'order_by':order_by,'columns':','.join(columns_list),
                    'group_by':','.join(group_list)}
        querykw.update(kwargs)
        where, querykw = self.app._decodeWhereBag(tblobj, where, querykw)
        if condition:
            where = ' ( %s ) AND ( %s )' %(where,condition) if where else condition
        return tblobj.query(where=where,**querykw).selection().output('baglist')
            


    @public_method
    def _rh_viewer(self,pane,table=None,rootId=None,confPaletteCode=None,**kwargs):
        frame = pane.framePane(frameCode='%s_viewer' %rootId)
        bar = frame.top.slotToolbar('2,confBtn,*,getRepBtn,2')
        bar.confBtn.slotButton('!!Configuration',iconClass='iconbox gear',
                                action="genro.publish(confPaletteCode+'_show');",
                                confPaletteCode=confPaletteCode)
        bar.getRepBtn.slotButton('Run',action='FIRE #ANCHOR.getReportBag')
        
        frame.center.quickGrid(value='^#ANCHOR.result')

    @public_method
    def _rh_configurator(self,pane,table=None,rootId=None,**kwargs):
        tc = pane.tabContainer()
        self._rh_conf_columns(tc,title='Fields',rootId=rootId,table=table)
        self._rh_conf_query(tc,title='Query',rootId=rootId,table=table)
    
    def _rh_conf_columns(self,parent,rootId=None,table=None,**kwargs):
        bc = parent.borderContainer(design='sidebar',**kwargs)
        bc.contentPane(region='left',width='200px',border_right='1px solid silver').fieldsTree(
            table=table,dragCode='fieldvars')
        self._rh_conf_columns_grid(bc,frameCode='%s_conf_group_by' %rootId,
                                    datapath='#ANCHOR.grids.group_by',title='!!Group by',
                                storepath='=#ANCHOR.conf.group_by',
                                struct=self._rh_groupby_struct,
                                    region='top',height='50%')
        self._rh_conf_columns_grid(bc,frameCode='%s_conf_values' %rootId,
                                    datapath='#ANCHOR.grids.values',title='!!Values',
                                storepath='=#ANCHOR.conf.values',
                                struct=self._rh_value_struct,region='center')

    def _rh_conf_columns_grid(self,parent,table=None,**kwargs):
        frame = parent.bagGrid(parentForm=False,addrow=False,delrow=True,
                                grid_gridplugins=False,
                                **kwargs)
        grid = frame.grid
        grid.data('.table',table)
        grid.dragAndDrop(dropCodes='fieldvars')
        grid.dataController("""var caption = data.fullcaption;
                                var field = data.fieldpath;
                                var pkey = field.replace(/\W/g,'_');
                                var dtype = data.dtype;
                                grid.gridEditor.addNewRows([{'field':field,
                                                            value:field,
                                                            dtype:dtype,
                                                            caption:caption,
                                                            pkey:pkey,
                                                            name:pkey,
                                                            required_columns:data.required_columns}]);
                                                            """,
                                data="^.dropped_fieldvars",grid=grid.js_widget) 


    def _rh_groupby_struct(self,struct):
        r = struct.view().rows()
        r.cell('name', name='Name', width='15em',edit=dict(validate_notnull=True))
        r.cell('caption', name='Caption', width='15em',edit=True)
        r.cell('dtype', name='Dtype', width='4em',edit=dict(tag='filteringSelect',values='T,N,L,D,DH,H'))
        r.cell('sqlformat',name='Sql format',width='12em',edit=True)


    def _rh_value_struct(self,struct):
        """array_agg(expression)	any	array of the argument type	input values, including nulls, concatenated into an array
            avg(expression)	smallint, int, bigint, real, double precision, numeric, or interval	numeric for any integer-type argument, double precision for a floating-point argument, otherwise the same as the argument data type	the average (arithmetic mean) of all input values
            bit_and(expression)	smallint, int, bigint, or bit	same as argument data type	the bitwise AND of all non-null input values, or null if none
            bit_or(expression)	smallint, int, bigint, or bit	same as argument data type	the bitwise OR of all non-null input values, or null if none
            bool_and(expression)	bool	bool	true if all input values are true, otherwise false
            bool_or(expression)	bool	bool	true if at least one input value is true, otherwise false
            count(*)	 	bigint	number of input rows
            count(expression)	any	bigint	number of input rows for which the value of expression is not null
            every(expression)	bool	bool	equivalent to bool_and
            max(expression)	any array, numeric, string, or date/time type	same as argument type	maximum value of expression across all input values
            min(expression)	any array, numeric, string, or date/time type	same as argument type	minimum value of expression across all input values
            string_agg(expression, delimiter)	text, text	text	input values concatenated into a string, separated by delimiter
            sum(expression)	smallint, int, bigint, real, double precision, numeric, interval, or money	bigint for smallint or int arguments, numeric for bigint arguments, otherwise the same as the argument data type	sum of expression across all input values
        """
        r = struct.view().rows()
        r.cell('name', name='Name', width='15em',edit=dict(validate_notnull=True))
        r.cell('caption', name='Caption', width='15em',edit=True)
        r.cell('dtype', name='Dtype', width='4em',edit=dict(tag='filteringSelect',values='T,N,L,D,DH,H'))
        r.cell('aggregator',name='Aggregator',width='10em',
                edit=dict(tag='filteringSelect',values='sum,avg,count,max,min'))

    def _rh_conf_query(self,parent,rootId=None,table=None,**kwargs):
        bc = parent.borderContainer(datapath='#ANCHOR.conf.query',**kwargs)
        bc.contentPane(onCreated="""
                this.querymanager = new gnr.FakeTableHandler(this);
            """,datapath='#ANCHOR.conf',
            nodeId='%s_query' %rootId,
            query_table=table,margin='2px',region='center')

