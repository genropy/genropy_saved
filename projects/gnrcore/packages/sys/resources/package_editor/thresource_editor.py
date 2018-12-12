# -*- coding: utf-8 -*-

# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from redbaron import RedBaron
from gnr.core.gnrbag import Bag
import os 
from gnr.core.gnrdecorator import public_method

class THResourceEditor(BaseComponent):

    def thres_dialogNewView(self,pane):
        dlg = pane.dialog(title='!!New ViewResource',
                            subscribe_form_newThView_onLoading='this.widget.show();',
                            subscribe_form_newThView_onDismissed='this.widget.show();')
        form = dlg.frameForm(formId='newThView',datapath='#FORM.newThView',
                            height='400px',width='600px',store=True)
        saverpc = form.store.handler('save',rpcmethod=self.thres_saveTHViewClass)
        saverpc.addCallback("genro.publish('reloadTableModules')")
        form.store.handler('load',rpcmethod=self.thres_loadTHViewClass)
        bc = form.center.borderContainer()
        self.thres_structMakerPane(bc.contentPane(region='center'))
        self.thres_viewOptionsPane(bc.contentPane(region='bottom'))
        bar = form.bottom.slotBar('*,cancel,confirm,10',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton("!!Cancel",action="this.form.abort();")
        bar.cancel.slotButton("!!Confirm",action="this.form.save({destPkey:'*dismiss*'});")

    def thres_viewOptionsPane(self,pane):
        fb = pane.formbuilder(cols=3,border_spacing='3px')
        fb.textbox(value='^.th_hiddencolumns',lbl='th_hiddencolumns',colspan=3)
        fb.comboBox(value='^.th_order',lbl='th_order',colspan=3,values='#FORM.currentColumns')
        fb.comboBox(value='^.th_query.column',lbl='th_query: column',values='#FORM.currentColumns')
        fb.filteringSelect(value='^.th_query.op',lbl='op',values='equal,contains,startswith,contains,greater')
        fb.textbox(value='^.th_query.val',lbl='val')

    def thres_structMakerPane(self,pane):
        pane.bagGrid(frameCode='structMaker',title='structMaker',
                    datapath='#FORM.columnsGrid',
                    storepath='#FORM.record._columns',
                    struct=self.thres_structMakerStruct,
                    pbl_classes=True,margin='2px',
                    grid_selfDragRows=True,
                   #grid_selfsubscribe_onSelectedRow="""
                   #                                if($1.selectedId){
                   #                            genro.publish('mve_moreattr_setSource','#FORM.record._columns.'+$1.selectedId);
                   #                                            }
                   #                                            """,
                    addrow=True,delrow=True)

    def thres_structMakerStruct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname',width='20em',name='Field',edit=True)
        r.cell('width',width='10em',name='Width',edit=True)
        r.cell('format',width='10em',name='Format',edit=True)


    @public_method
    def thres_saveTHViewClass(self,data=None,package=None,project=None,**kwargs):
        recordNode = data.getNode('record')
        record = recordNode.value
        recInfo = recordNode.attr
        oldpath = None
        resultAttr = dict()
        if recInfo['_newrecord']:
            table = record['name']
        else:
            old_table = recInfo['_pkey']
            table = record['name']
            if table!=old_table:
                oldpath = os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %old_table))
        filepath = os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %table))    
        self.makeOneTable(filepath=filepath,table_data=record)
        if oldpath and os.path.exists(oldpath):
            os.remove(oldpath)
        return (table, resultAttr)

    @public_method
    def thres_loadTHViewClass(self,pkey=None,**kwargs):
        tablepath,viewResource = pkey.split(':')
        project,package,tablename = tablepath.split('.')
        packagepath = self.getPackagePath(project,package)
        th_resource_basepath = os.path.join(packagepath,'resources','tables')
        respath = os.path.join(th_resource_basepath,tablename,'th_%s.py' %tablename)
       #table = pkey
       #red = self.get_redbaron(os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %table)))
       #resultAttr = dict(_pkey=pkey,_newrecord=False,project=project,package=package)
       #record = Bag()
       #record['name'] = table
       #record['_sysFields'] = self.handleSysFields(red)
       #config_db = red.find('def','config_db')
       #if config_db:
       #    targs,tkwargs = self.parsBaronNodeCall(config_db.find('name','table').parent[2])
       #    record.update(tkwargs)
       #    columnsvalue = Bag()
       #    for colNode in red.find_all('name','column'):
       #        cbag = self._loadColumnBag(colNode)
       #        cbag['tag'] = 'column'
       #        columnsvalue[cbag['name']] = cbag
       #    for colNode in red.find_all('name','aliasColumn'):
       #        cbag = self._getColBag(colNode,'relation_path')
       #        cbag['tag'] = 'aliasColumn'
       #        columnsvalue.setItem(cbag['name'],cbag,_customClasses='aliasColumnRow')
       #    for colNode in red.find_all('name','formulaColumn'):
       #        cbag = self._getColBag(colNode,'sql_formula')
       #        cbag['tag'] = 'formulaColumn'
       #        columnsvalue.setItem(cbag['name'],cbag,_customClasses='formulaColumnRow')
       #    for colNode in red.find_all('name','pyColumn'):
       #        cbag = self._getColBag(colNode,'py_method')
       #        cbag['tag'] = 'pyColumn'
       #        columnsvalue.setItem(cbag['name'],cbag,_customClasses='pyColumnRow')
       #    record.setItem('_columns',columnsvalue,_sendback=True)
        #return record,resultAttr
