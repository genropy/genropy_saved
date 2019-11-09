# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from past.builtins import basestring
from gnr.web.gnrwebpage import BaseComponent
from redbaron import RedBaron
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrstring import boolean,flatten
from gnr.core.gnrbag import Bag
from collections import OrderedDict
from datetime import datetime
import os

SYSFIELDS_DEFAULT = OrderedDict([('id',True), ('ins',True), ('upd',True), 
                                    ('ldel',True), ('user_ins',False), 
                                    ('user_upd',False), 
                                    ('draftField',False), 
                                    ('counter',None),
                                    ('hierarchical',None),
                                    ('df',False)])


class TableModuleWriter(BaseComponent):
    def bagToArgString(self,arguments,prefix=','):
        if not arguments:
            return ''
        atlst = []
        for k,v in list(arguments.items()):
            if v in ('',None):
                continue
            if isinstance(v,basestring):
                v = ("'%s'" if not "'" in v else 'u"%s"') %v
            elif isinstance(v, Bag):
                v = "dict(%s)" %self.bagToArgString(v,prefix='')
            atlst.append("%s=%s" %(k,v))
        return '%s%s' %(prefix,','.join(atlst))

    def get_redbaron(self,filepath):
        if os.path.exists(filepath):

            with open(filepath, "r") as f:
                source_code = f.read()
        else:
            source_code = """# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        pass
""" 
        red = RedBaron(source_code)
        return red
            
    def makeOneTable(self,filepath=None,table_data=None):
        red = self.get_redbaron(filepath)
        config_db_node = red.find('def','config_db')
        table = table_data.pop('name')
        table_data['name_long'] = table_data['name_long'] or table
        table_data['name_plural'] = table_data['name_plural'] or table
        table_data['caption_field'] = table_data['caption_field'] or table_data['pkey']
        sysFields = table_data.pop('_sysFields')
        columns = table_data.pop('_columns') or Bag()
        config_db_node.replace("""def config_db(self,pkg):\n        tbl =  pkg.table('%s'%s)""" %(table,self.bagToArgString(table_data)))
        if sysFields and sysFields.pop('_enabled'):
            config_db_node.append('self.sysFields(tbl%s)' %self.bagToArgString(self._sysFieldsArguments(sysFields)))
        for col in list(columns.values()):
            relation = col.pop('_relation')
            s = self._columnPythonCode(col,relation)
            config_db_node.append(s)
        with open(filepath,'w') as f:
            f.write(red.dumps())

    def _sysFieldsArguments(self,sysFields):
        counter = sysFields.pop('counter')
        arguments = OrderedDict()
        for k,v in list(sysFields.items()):
            if v is None:
                continue
            if k == 'hierarchical' and v=='True':
                v = True
            if k in SYSFIELDS_DEFAULT and SYSFIELDS_DEFAULT[k] != v: 
                arguments[k] = v     
        if counter:
            if counter == 'True':
                counter = True
            if isinstance(counter,basestring) and ',' in counter:
                for c in counter.split(','):
                    arguments['counter_%s' %c] = c   
            else:
                arguments['counter'] = counter     
        return arguments

    def _columnPythonCode(self,c,relation=None):
        attributes = Bag()
        col = c.deepcopy()
        name = flatten(col.pop('name'))
        dtype = col.pop('dtype')
        size = col.pop('size')
        name_long = col.pop('name_long')
        name_short = col.pop('name_short')
        tag = col.pop('tag') #column,formulaColumn,aliasColumn,pyColumn
        if dtype and dtype not in ('A','T','C'):
            attributes['dtype'] = dtype
        if size:
            attributes['size'] = size
        attributes.setItem('name_long', name_long or name,localized=True)
        if name_short:
            attributes.setItem('name_short', name_short,localized=True)
        attributes.update(col)
        relationCode = ''
        if relation and relation['relation']:
            relationCode = '.%s' %self._relationPythonCode(relation)
        coltype = 'column'
        if attributes['sql_formula'] or attributes['select'] or attributes['exists']:
            coltype = 'formulaColumn'
        elif attributes['relation_path']:
            coltype = 'aliasColumn'
        elif attributes['pymethod']:
            coltype = 'pyColumn'
        return "tbl.%s('%s'%s)%s" % (coltype,name, self.bagToArgString(attributes),relationCode)

    def _relationPythonCode(self,relation):
        relpath = relation.pop('relation')
        r = relpath.split('.')
        if len(r)==3:
            pkg,table,id = r
            if pkg == 'main':
                relpath = '%s.%s' %(table,id)
        relation_name = relation.pop('relation_name')
        foreignkey = relation.pop('foreignkey')
        attributes = Bag()
        if relation_name:
            attributes['relation_name'] = relation_name
        if foreignkey:
            attributes['mode'] = 'foreignkey'
        for k, v in list(relation.items()):
            if v is not None:
                attributes[k] = v
        atlst = []
        for k,v in list(attributes.items()):
            if v == 'True':
                v = True
            if isinstance(v,basestring):
                if "'" in v:
                    v = '"%s"' %v
                else:
                    v = "'%s'" %v
            atlst.append("%s=%s" %(k,v))
        return """relation('%s',%s)"""  %(relpath,', '.join(atlst))


class TableModuleEditor(BaseComponent):
    py_requires='package_editor/model_editor:TableModuleWriter'
    def handleSysFields(self,red=None):
        sysFieldBaronNode = red.find('name','sysFields') if red else None
        result = Bag(list(SYSFIELDS_DEFAULT.items()))
        if not sysFieldBaronNode:
            result['_enabled'] = False
            return result
         #counter_kwargs=None
        result['_enabled'] = True
        args,kwargs = self.parsBaronNodeCall(sysFieldBaronNode.parent[2])
        counters = []
        for k,v in list(kwargs.items()):
            if k in ('hierarchical','counter'):
                if v is True:
                    v = 'True'
            if k.startswith('counter_'):
                counters.append(v)
            else:
                result[k] = v
        if counters:
            result['counter'] = ','.join(counters)
        return result

    def _getColBag(self,node,firstArg=None,firstArgDefault=None):
        cbag = Bag()
        p = node.parent
        cargs,ckwargs = self.parsBaronNodeCall(p[2])
        colname = cargs[0]
        cbag = Bag()
        cbag['name'] = colname
        if len(cargs)>1:
            fval = cargs[1]
        else:
            fval = ckwargs.pop(firstArg,firstArgDefault)
        cbag[firstArg] = fval
        for k,v in list(ckwargs.items()):
            cbag[k] = v
        return cbag

    def parsBaronNodeCall(self,node):
        args = []
        kwargs = OrderedDict()
        for argNode in node.find_all('call_argument'):
            key = argNode.target.value if argNode.target else None
            value = argNode.value.value
            argtype = argNode.value.type
            if argtype=='string':
                value = value.strip("'") if "'" in value else value.strip('"')
            elif value in ('True','False'):
                value = boolean(value)
            elif hasattr(value,'value'):
                value = Bag(self.parsBaronNodeCall(value)[1])
            if not key:
                args.append(value)
            else:
                kwargs[key] = value
        return args,kwargs

    def _loadColumnBag(self,colNode,aliasColumn=False):
        cbag = self._getColBag(colNode,'dtype','T')
        p = colNode.parent
        if p.find('name','relation'):
            _relation = Bag()
            rargs,rkwargs = self.parsBaronNodeCall(p[4])
            mode = rkwargs.pop('mode',None)
            _relation['relation'] = rargs[0]
            _relation['foreignkey'] = mode=='foreignkey'
            for k,v in list(rkwargs.items()):
                _relation[k] = v
            cbag['_relation'] = _relation
        return cbag

    def _columnVal(self,colname,colobj):
        cbag = Bag()
        cattr = dict(colobj.attributes)
        _sysfield = cattr.pop('_sysfield',None)
        if _sysfield:
            return
        cbag['name'] = colname
        for attrname,attrvalue in list(cattr.items()):
            if attrname in ('name','dtype','size','group','name_long','name_short','indexed','unique'):
                cbag[attrname] = cattr.pop(attrname)
        return cbag

    def relationEditorDialog(self,bc,grid):
        dlg = bc.dialog(title='Relation',
                        subscribe_edit_relation="""this.widget.show()
                                                   this.setRelativeData('.data',$1.relation);
                                                   this.setRelativeData('.rowIndex',$1.rowIndex)
                                                """,datapath='#FORM.relationEditor')
        frame = dlg.framePane(height='300px',width='600px')
        bc = frame.center.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=2,datapath='.data')
        fb.textbox(value='^.relation',lbl='Relation')
        fb.textbox(value='^.relation_name',lbl='Relation name')
        fb.checkbox(value='^.foreignkey',label='Foreignkey')
        fb.filteringSelect(value='^.onDelete',lbl='onDelete',values='raise,cascade,setnull')
        fb.filteringSelect(value='^.onDelete_sql',lbl='onDelete(sql)',values='raise,cascade,setnull')
        fb.filteringSelect(value='^.onUpdate',lbl='onUpdate',values='cascade,raise')
        fb.filteringSelect(value='^.onUpdate_sql',lbl='onUpdate(sql)',values='cascade,raise')
        fb.textbox(value='^.one_name',lbl='One name')
        fb.textbox(value='^.many_name',lbl='Many name')
        fb.checkbox(value='^.deferred',label='Deferred')
        fb.filteringSelect(value='^.one_one',lbl='One one',values='True,*')
        fb.comboBox(value='^.meta_thmode',lbl='Tablehandler',values='dialog,plain,border')
        bc.contentPane(region='center').multiValueEditor(value='^#FORM.relationEditor.data',
                    exclude='relation,relation_name,foreignkey,onDelete,onDelete_sql,onUpdate,onUpdate_sql,one_name,many_name,deferred,one_one')
        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""grid.gridEditor.setCellValue(rowIndex,'_relation',data.deepCopy());
                                                    dlg.hide();
                                                    """,
                                        dlg=dlg.js_widget,
                                        grid=grid.js_widget,
                                        rowIndex='=.rowIndex',
                                        data='=.data')

    def columns_struct(self,struct):
        r = struct.view().rows()
        r.cell('name',width='10em',name='Name',edit=True)

    def tables_viewer_struct(self,struct):
        r = struct.view().rows()
        r.cell('name',width='15em',name='Name')
        r.cell('model_change_ts',dtype='DH',width='10em',name='Mod. Update')
        r.cell('resource_change_ts',dtype='DH',width='10em',name='Res. Update')

    def tablesModulesEditor(self,pane,storepath=None,datapath='.tablesFrame',project=None,package=None):
        
        tablesframe = pane.bagGrid(frameCode='tablesModulesEditor',title='Tables',
                                                storepath=storepath,
                                                datapath=datapath,
                                                struct=self.tables_viewer_struct,
                                                #pbl_classes=True,
                                                #grid_multiSelect=False,
                                                margin='2px',

                                                addrow=True,delrow=True,
                                                store_deleteRows="""
                                                PUBLISH deleteSelectedPackageTables ={tables:pkeys}
                                                """,
                                                store_data='^#FORM._loadedPackageTables',
                                                store_selfUpdate=True)
        pane.dataRpc('dummy',self.table_editor_deletePackageTables,_if='tables',
                    package=package.replace('^','='),project=project.replace('^','='),
                    subscribe_deleteSelectedPackageTables=True,
                    _onResult="PUBLISH reloadTableModules;")

        tablesframe.grid.dataController("""var selectedIndex = grid.getSelectedRowidx();
                                            var selectedPkeys = grid.getSelectedPkeys();
                                            SET #FORM.selectedTables = selectedPkeys;
                                            if(selectedIndex.length>1){
                                                SET #FORM.currenModelModule = null;
                                                SET #FORM.currenResourceModule = null;
                                            }else{
                                                var selectedRow = grid.rowByIndex(selectedIndex[0]);
                                                SET #FORM.currenModelModule = selectedRow['_modulepath'];
                                                SET #FORM.currenResourceModule = selectedRow['_thresourcepath'];
                                            }
                                            """,
                                        selectedId='^.selectedId',grid=tablesframe.grid.js_widget)
        topbar = tablesframe.top.bar.replaceSlots('delrow','export,5,fileimporter,5,searchOn,delrow')
        bar = tablesframe.bottom.slotToolbar('*,makerRes,5,makerMenu,5,importLegacy,*')
        bar.makerRes.slotButton('Make Resources',
                            action='FIRE #FORM.instanceAction= event.shiftKey? "make_resources_force":"make_resources"')
        bar.makerMenu.slotButton('Make Menu',
                            action='FIRE #FORM.instanceAction= "make_menu"')
        bar.importLegacy.slotButton('Import Legacy',fire_import_legacy='#FORM.instanceAction')
        topbar.fileimporter.PaletteImporter(paletteCode='filexlscsv_importer' ,
                            dockButton_iconClass='iconbox inbox',title='!!Table from csv/xls',
                            importButton_label='Create model',
                            importButton_action="""genro.publish('model_from_importfile',{
                                    colsbag:this.getRelativeData('.match'),
                                    filepath:this.getRelativeData('.imported_file_path'),
                                    tblname:tblname
                                });""",
                            importButton_ask=dict(title='Table name',fields=[dict(name='tblname',lbl='Name')]))

        pane.dataRpc('dummy',self.moduleFromImportfile,subscribe_model_from_importfile=True,
                    package=package.replace('^','='),project=project.replace('^','='),
                    _onResult='PUBLISH reloadTableModules;')
        pane.dataRpc('#FORM._loadedPackageTables',self.table_editor_loadPackageTables,
                package=package,project=project,_if='project&&package',_else='return new gnr.GnrBag();',
                subscribe_reloadTableModules=True,
                _onCalling="""
                SET #FORM.currenModelModule = null;
                SET #FORM.currenResourceModule = null; 
                """)
        form = tablesframe.grid.linkedForm(frameCode='tableModule',
                                 datapath='.tableForm',loadEvent='onRowDblClick',
                                 dialog_height='550px',dialog_width='1100px',
                                 dialog_title='^#FORM.tableForm.pkey',handlerType='dialog',
                                 childname='form',attachTo=pane,store=True,
                                 store_pkeyField='_pkey')
        self.tablesForm(form)

    def tablesForm(self,form):
        saverpc = form.store.handler('save',rpcmethod=self.saveTableModule,
                            fullRecord=True,package='=.record?package',project='=.record?project')
        saverpc.addCallback("genro.publish('reloadTableModules')")
        form.store.handler('load',rpcmethod=self.loadTableModule,
                            project='=#FORM/parent/#FORM.record.project_name',
                            package='=#FORM/parent/#FORM.record.package_name')
        form.top.slotToolbar('2,navigation,*,form_add,form_revert,form_save,semaphore,2')
        form.dataController("this.form.setLocked(true)",_onStart=True)
        form.dataController("genro.dlg.alert('Wrong info','Table has wrong data');",save_failed='^#FORM.controller.save_failed')
        bc = form.center.borderContainer()
        left = bc.borderContainer(datapath='.record',region='left',width='300px')
        tc = left.tabContainer(region='top',height='50%',margin='2px')
        tablepane = tc.contentPane(title='Table attributes')
        self.sysFieldPane(tc.contentPane(title='Sysfields'))
        fb = tablepane.div(margin='5px').formbuilder(cols=1)
        fb.dataFormula('#FORM.columnsValues',"""columns.values().map(function(v){return v.getItem('name')}).join(',')""",
                        columns='^._columns',_if='columns && columns.len()',_else='null')
        fb.textbox(value='^.name',lbl='Name',validate_notnull=True,validate_case='l')
        fb.comboBox(value='^.pkey',lbl='Pkey',validate_notnull=True,values='^#FORM.columnsValues')
        fb.textbox(value='^.name_long',lbl='Name Long',colspan=2,width='100%')
        fb.textbox(value='^.name_plural',lbl='Name Plural',colspan=2,width='100%')
        fb.comboBox(value='^.caption_field',lbl='Caption field',values='^#FORM.columnsValues')       
        fb.checkbox(value='^.lookup',label='Lookup')
        left.contentPane(region='center',overflow='hidden').multiValueEditor(value='^#FORM.record',
                                            exclude='%s,_columns,_sysFields' %','.join(fb.fbuilder.field_list))
        centerbc = bc.borderContainer(region='center')
        bottom = centerbc.contentPane(region='bottom',height='150px',splitter=True,overflow='hidden')
        columnsframe = centerbc.contentPane(region='center').bagGrid(frameCode='columns',title='Columns',
                                                        datapath='#FORM.columnsGrid',
                                                    storepath='#FORM.record._columns',
                                                    struct=self.columns_struct,
                                                    structpath='#FORM.moduleColumnsStruct',
                                                    #pbl_classes=True,
                                                    margin='2px',
                                                    grid_selfDragRows=True,
                                                    grid_selfsubscribe_onSelectedRow="""
                                                                if($1.selectedId){
                                                                    genro.publish('mve_moreattr_setSource','#FORM.record._columns.'+$1.selectedId);
                                                                }
                                                                """,
                                                    addrow=True,delrow=True,export=True)
        bottom.dataFormula('#FORM.columnsExcludedMoreAttr',"struct.getItem('#0.#0').digest('#a.field').join(',')+',_newrecord'",
                                struct='^#FORM.moduleColumnsStruct')
        bottom.multiValueEditor(exclude='^#FORM.columnsExcludedMoreAttr',nodeId='mve_moreattr')
        columnsframe.top.bar.replaceSlots('delrow','searchOn,2,delrow')
        bar = columnsframe.top.bar.replaceSlots('vtitle','columnspicker')
        box = bar.columnspicker.div()
        box.div('Columns',cursor='pointer',font_weight='bold')
        cp = box.tooltipPane().div(padding='10px')
        cp.dataFormula('#FORM.currentCheckedColumns','tableModuleEditor.getCheckableCols();',_onStart=True)
        cp.checkboxText(value='^#FORM.currentCheckedColumns',
                        values='^#FORM.checkableCols',
                        cols=2)

        cp.dataFormula('#FORM.checkableCols',"tableModuleEditor.getCheckableCols(columns)",columns='^#FORM.record._columns')
        cp.dataController("""tableModuleEditor.setCurrentStruct(this,currentCheckedColumns)""",
                        currentCheckedColumns='^#FORM.currentCheckedColumns',_delay=1)
        self.relationEditorDialog(bc,grid=columnsframe.grid)

    def sysFieldPane(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=2,border_spacing='3px',datapath='._sysFields',fld_disabled='^._enabled?=!#v')
        fb.checkbox(value='^._enabled',label='Sysfields enabled',disabled=False,colspan=2)
        fb.checkbox(value='^.id',label='Id')
        fb.checkbox(value='^.ins',label='ins')
        fb.checkbox(value='^.upd',label='upd')
        fb.checkbox(value='^.ldel',label='ldel',tooltip='Logica delete field')
        fb.checkbox(value='^.user_upd',label='user_upd')
        fb.checkbox(value='^.draftField',label='draftField')
        fb.checkbox(value='^.df',label='df',tooltip='DynamicFields management')
        fb.br()
        fb.comboBox(value='^.hierarchical',values='True',lbl='hierarchical',tooltip='True or the columns you need hierarchical version',colspan=2)
        fb.comboBox(value='^.counter',lbl='counter',values='True',
                    tooltip="""Sorting counter for records.<br/> True means absolute order.<br/> One or many foreignkey columns means different counter columns for different sorting""",
                    colspan=2)
        fb.dataController("""
                    if(_enabled){
                        if(pkey && pkey!='id'){
                           SET .id = false;
                        }else{
                           SET  #FORM.record.pkey = 'id';
                        }
                    }
                    """,pkey='^#FORM.record.pkey',_enabled='^._enabled',id='^.id',_delay=100)

    @public_method
    def moduleFromImportfile(self,colsbag=None,filepath=None,tblname=None,project=None,package=None,**kwargs):
        filepath = os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %tblname))
        table_data = Bag()
        table_data['name'] = tblname
        columns_bag = Bag()
        table_data['_columns'] = columns_bag
        for c in list(colsbag.values()):
            legacy_name = c['source_field']
            colname = c['dest_field'] or legacy_name
            b = Bag(dict(name=colname,legacy_name=legacy_name,
                        name_long=None,dtype=c['dtype']))
            columns_bag.setItem(colname,b)
        self.makeOneTable(filepath,table_data=table_data)


    @public_method
    def saveTableModule(self,data=None,package=None,project=None,**kwargs):
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
    def loadTableModule(self,pkey=None,project=None,package=None,**kwargs):
        if pkey=='*newrecord*':
            record = Bag()
            record['_sysFields'] = self.handleSysFields()
            resultAttr = dict(_pkey=pkey,_newrecord=True,project=project,package=package)
            return record,resultAttr
        table = pkey
        red = self.get_redbaron(os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %table)))
        resultAttr = dict(_pkey=pkey,_newrecord=False,project=project,package=package)
        record = Bag()
        record['name'] = table
        record['_sysFields'] = self.handleSysFields(red)
        config_db = red.find('def','config_db')
        if config_db:
            targs,tkwargs = self.parsBaronNodeCall(config_db.find('name','table').parent[2])
            record.update(tkwargs)
            columnsvalue = Bag()
            for colNode in red.find_all('name','column'):
                cbag = self._loadColumnBag(colNode)
                cbag['tag'] = 'column'
                columnsvalue[cbag['name']] = cbag
            for colNode in red.find_all('name','aliasColumn'):
                cbag = self._getColBag(colNode,'relation_path')
                cbag['tag'] = 'aliasColumn'
                columnsvalue.setItem(cbag['name'],cbag,_customClasses='aliasColumnRow')
            for colNode in red.find_all('name','formulaColumn'):
                cbag = self._getColBag(colNode,'sql_formula')
                cbag['tag'] = 'formulaColumn'
                columnsvalue.setItem(cbag['name'],cbag,_customClasses='formulaColumnRow')
            for colNode in red.find_all('name','pyColumn'):
                cbag = self._getColBag(colNode,'py_method')
                cbag['tag'] = 'pyColumn'
                columnsvalue.setItem(cbag['name'],cbag,_customClasses='pyColumnRow')
            record.setItem('_columns',columnsvalue,_sendback=True)
        return record,resultAttr


    @public_method
    def table_editor_deletePackageTables(self,tables=None,package=None,project=None):
        packagepath = self.getPackagePath(project,package)
        th_resource_basepath = os.path.join(packagepath,'resources','tables')
        models_path = os.path.join(packagepath,'model')
        for tablename in tables:
            modulepath = os.path.join(models_path,'%s.py' %tablename)
            if os.path.exists(modulepath):
                os.remove(modulepath)
            thresourcepath = os.path.join(th_resource_basepath,tablename,'th_%s.py' %tablename)
            if os.path.exists(thresourcepath):
                os.remove(thresourcepath)

    @public_method
    def table_editor_loadPackageTables(self,package=None,project=None):
        result = Bag()
        packagepath = self.getPackagePath(project,package)
        th_resource_basepath = os.path.join(packagepath,'resources','tables')
        models_path = os.path.join(packagepath,'model')
        for m in os.listdir(models_path):
            tablename,ext = os.path.splitext(m)
            if ext!='.py':
                continue
            modulepath = os.path.join(models_path,m)
            resourcepath = os.path.join(th_resource_basepath,tablename,'th_%s.py' %tablename)
            
            tablevalue = Bag()
            tablevalue['name'] = tablename
            tablevalue['_pkey'] = tablename
            tablevalue['_modulepath'] = modulepath
            tablevalue['_thresourcepath'] = resourcepath
            tablevalue['model_change_ts'] =  datetime.fromtimestamp(os.path.getmtime(modulepath))
            if os.path.exists(resourcepath):
                tablevalue['resource_change_ts'] =  datetime.fromtimestamp(os.path.getmtime(resourcepath))

            result[tablename] = tablevalue
        return result

