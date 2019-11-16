# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint
from gnr.core.gnrbag import Bag

tags='user'
caption = '!!Print grid'
description='!!Print grid'

def _cleanWhere(where):
    if not where:
        return
    wrongLinesPathlist = []
    def cb(node,_pathlist=None):
        attr = node.attr
        if not (attr.get('op') and attr.get('column')):
            if not isinstance(node.value,Bag):
                wrongLinesPathlist.append('.'.join(_pathlist+[node.label]))
    where.walk(cb,_pathlist=[])
    for path in wrongLinesPathlist:
        where.popNode(path)

class Main(BaseResourcePrint):
    batch_prefix = 'pr_grid'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = 'print'
    batch_title = 'Print grid'
    print_mode = 'pdf'
    html_res = 'html_res/print_gridres'

    def pre_process(self):
        self.htmlMaker.row_table = getattr(self,'maintable',None)
        
    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,**kwargs):
        pane = pane.div(min_height='60px')        
        fb = pane.formbuilder(cols=1,fld_width='20em',border_spacing='4px')
        userobject = extra_parameters['userobject']
        where = None
        printParams = {}
        if userobject:
            data,metadata = self.db.table('adm.userobject'
                                ).loadUserObject(userObjectIdOrCode=userobject,
                                                table=self.tblobj.fullname)
            struct =  data['struct']
            query = data['query']
            queryPars = data['queryPars']
            printParams = data['printParams'] or Bag()
            for k,v in printParams.items():
                fb.data('.{}'.format(k),v)

            fb.data('.currentGridStruct',struct)
            fb.data('.currentQuery',query) 
            where = query['where']
            if queryPars:
                fb.div('!!Query',font_weight='bold',color='#444')
                for code,pars in queryPars.digest('#k,#a'):
                    field = pars['field']
                    tblobj = self.db.table(self.tblobj.fullname)
                    rc = tblobj.column(field).relatedColumn()
                    wherepath = pars['relpath']
                    colobj = tblobj.column(field)
                    tblcol = colobj.table
                    wdgvalue = '^.wherepars.{wherepath}'.format(wherepath=wherepath)
                    if colobj.name==tblcol.pkey:
                        wdg = fb.dbSelect(value=wdgvalue,lbl=pars['lbl'],
                                            dbtable=self.tblobj.fullname)
                    elif pars['op'] == 'equal' and rc is not None:
                        wdg = fb.dbSelect(value=wdgvalue,lbl=pars['lbl'],
                                            dbtable=rc.table.fullname)
                    else:
                        wdg = fb.textbox(value=wdgvalue,lbl=pars['lbl'])
                fb.div('!!Print parameters',font_weight='bold',color='#444')
        else:
            fb.dataController("""
                        var grid = genro.wdgById(gridId);
                        SET .grid_datamode = grid.datamode;
                        SET .currentGridStruct = grid.getExportStruct();""",
                        _onBuilt=True,gridId=extra_parameters['gridId'])
        fb.textbox(value='^.print_title',lbl='!!Title')
        fb.filteringSelect(value='^.orientation',lbl='!!Orientation',values='H:Horizontal,V:Vertical')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',lbl='!!Letterhead',hasDownArrow=True)
        fb.filteringSelect(value='^.totalize_mode', lbl='!!Totalize',values='doc:Document,page:Page')
        fb.textbox(value='^.totalize_carry',lbl='!!Carry caption',hidden='^.totalize_mode?=#v!="page"')
        fb.textbox(value='^.totalize_footer',lbl='!!Totals caption',hidden='^.totalize_mode?=!#v')
        _cleanWhere(where)
        where = where or Bag()
        fb.data('.use_current_selection',len(where) is 0)
        if len(where) > 0 and not printParams.get('allow_only_saved_query'):
            fb.checkbox(value='^.use_current_selection',label='!!Use current selection')
        if record_count==1:
            fb.checkbox(value='^.allrows',
                        label='!!Use all selection rows',
                        hidden='^.use_current_selection?=!#v')

        