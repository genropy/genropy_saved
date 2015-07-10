# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from redbaron import RedBaron
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrstring import boolean
from gnr.core.gnrlang import uniquify
from gnr.core.gnrbag import Bag
from collections import OrderedDict
import os

SYSFIELDS_DEFAULT = OrderedDict([('id',True), ('ins',True), ('upd',True), 
                                    ('ldel',True), ('user_ins',False), 
                                    ('user_upd',False), 
                                    ('draftField',False), 
                                    ('counter',None),
                                    ('hierarchical',None),
                                    ('df',False)])


class TableModuleWriter(BaseComponent):
    def bagToArglist(self,arguments):
        if not arguments:
            return ''
        atlst = []
        for k,v in arguments.items():
            if isinstance(v,basestring):
                v = ("'%s'" if not "'" in v else '"%s"') %v
            atlst.append("%s=%s" %(k,v))
        return ',%s' %','.join(atlst)

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
        columns = table_data.pop('_columns')
        config_db_node.replace("""def config_db(self,pkg):\n         tbl =  pkg.table('%s'%s)""" %(table,self.bagToArglist(table_data)))
        if sysFields and sysFields.pop('_enabled'):
            config_db_node.append('self.sysFields(tbl%s)' %self.bagToArglist(self._sysFieldsArguments(sysFields)))
        for col in columns.values():
            relation = col.pop('_relation')
            s = self._columnPythonCode(col,relation)
            config_db_node.append(s)
        with open(filepath,'w') as f:
            f.write(red.dumps())

    def _sysFieldsArguments(self,sysFields):
        counter = sysFields.pop('counter')
        arguments = OrderedDict()
        for k,v in sysFields.items():
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

    def _columnPythonCode(self,col,relation=None):
        attributes = Bag()
        col = col.deepcopy()
        name = col.pop('name')
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
        atlst = []
        for k,v,localized in attributes.digest('#k,#v,#a.localized'):
            if v in (None,''):
                continue
            if isinstance(v,basestring):
                v = ("'%s'" if not "'" in v else '"%s"') %v
            atlst.append("%s=%s" %(k,v))
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

        return "tbl.%s('%s', %s)%s" % (coltype,name, ', '.join(atlst),relationCode)
        

    def _relationPythonCode(self,relation):
        relpath = relation.pop('relation')
        r = relpath.split('.')
        if len(r)==3:
            pkg,table,id = r
            if pkg == 'main':
                relpath = '%s.%s' %(table,id)
        relation_name = relation.pop('relation_name')
        one_one = relation.pop('one_one')
        foreignkey = relation.pop('foreignkey')

        attributes = Bag()
        if relation_name:
            attributes['relation_name'] = relation_name
        if foreignkey:
            attributes['mode'] = 'foreignkey'
        if one_one:
            attributes['one_one'] = '*' if not relation_name else True
        for k, v in relation.items():
            if v is not None:
                attributes[k] = v
        atlst = []
        for k,v in attributes.items():
            if isinstance(v,basestring):
                if "'" in v:
                    v = '"%s"' %v
                else:
                    v = "'%s'" %v
            atlst.append("%s=%s" %(k,v))
        return """relation('%s',%s)"""  %(relpath,', '.join(atlst))


class TableModuleEditor(BaseComponent):
    py_requires='table_module_editor:TableModuleWriter'
    js_requires ='table_module_editor'


    def handleSysFields(self,red):
        sysFieldBaronNode = red.find('name','sysFields')
        result = Bag(SYSFIELDS_DEFAULT.items())
        if not sysFieldBaronNode:
            result['_enabled'] = False
            return result
         #counter_kwargs=None
        result['_enabled'] = True
        args,kwargs = self.parsBaronNodeCall(sysFieldBaronNode.parent[2])
        counters = []
        for k,v in kwargs.items():
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
        for k,v in ckwargs.items():
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
            for k,v in rkwargs.items():
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
        for attrname,attrvalue in cattr.items():
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
        pane = frame.center.contentPane()
        fb = pane.formbuilder(cols=2,datapath='.data')
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
        fb.checkbox(value='^.one_one',label='One one')
        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""grid.gridEditor.setCellValue(rowIndex,'_relation',data.deepCopy());
                                                    dlg.hide();
                                                    """,
                                        dlg=dlg.js_widget,
                                        grid=grid.js_widget,
                                        rowIndex='=.rowIndex',
                                        data='=.data')


    def moreAttributesDialog(self,bc):
        dlg = bc.dialog(title='More attributes',
                        subscribe_edit_more_attributes="""this.widget.show()
                                                   this.setRelativeData('.data',$1.more_attributes);
                                                   this.setRelativeData('.rowIndex',$1.rowIndex)
                                                """,datapath='#FORM.moreAttributes')
       #def struct(struct):
       #    r = struct.view().rows()
       #    r.cell('attribute_key',name='Key',edit=dict(tag='ComboBox',values=MORE_ATTRIBUTES),width='10em')
       #    r.cell('attribute_dtype',name='Dtype',edit=dict(tag='filteringSelect',
       #                                                    values='T:Text,B:Bool,I:Int,N:Decimal'),width='10em')
       #    r.cell('attribute_value',name='Value',edit=True,width='10em')

       #frame = dlg.bagGrid(height='200px',width='400px',storepath='#FORM.moreAttributes.data',struct=struct)
       #
      # frame = dlg.framPane()
      # bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
      # bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
      # bar.confirm.slotButton('Confirm',action="""griddata.setItem('#'+rowIndex+'._more_attributes',data.deepCopy());
      #                                             dlg.hide()
      #                                             """,
      #                                 dlg=dlg.js_widget,
      #                                 griddata='=#FORM.record._columns',
      #                                 rowIndex='=.rowIndex',
       #                                 data='=.data')

    def columns_struct(self,struct):
        r = struct.view().rows()
        r.cell('name',width='10em',name='Name',edit=True)
        #r.cell('dtype',width='5em',name='Dtype',edit=dict(tag='filteringSelect',values='T:Text,I:Int,N:Decimal,B:Bool,D:Date,DH:Timestamp,X:Bag'))
        #r.cell('size',width='5em',name='Size',edit=True)
        #r.cell('group',width='5em',name='Group',edit=True)
        #r.cell('name_long',width='20em',name='Name long',edit=True)
        #r.cell('name_short',width='10em',name='Name short',edit=True)
        #r.cell('indexed',width='5em',name='Indexed',edit=True,dtype='B')
        #r.cell('unique',width='5em',name='Unique',edit=True,dtype='B')
        #r.cell('_more_attributes',width='20em',name='More attributes',edit=True,editOnOpening=""" 
        #                                var more_attributes = rowData.getItem(field);
        #                                genro.publish('edit_more_attributes',{more_attributes:more_attributes,rowIndex:rowIndex})
        #                                return false;
        #                            """)
#
        #r.cell('_relation',width='20em',name='Relation',edit=True,
        #             editOnOpening="""var relation = rowData.getItem(field);
        #                            if(relation){
        #                                relation = relation.deepCopy();
        #                            }
        #                            genro.publish('edit_relation',{relation:relation,rowIndex:rowIndex})
        #                            return false;
        #                            """)

    def tablesModulesEditor(self,pane,storepath=None,datapath='.tablesFrame',project=None,package=None):
        tablesframe = pane.bagGrid(frameCode='tablesModulesEditor',title='Tables',
                                                storepath=storepath,
                                                datapath=datapath,
                                                struct=self.tables_struct,
                                                grid_multiSelect=False,
                                                pbl_classes=True,margin='2px',
                                                addrow=True,delrow=True)
        pane.dataRpc(storepath,self.table_editor_loadPackageTables,package=package,project=project,
                _if='project&&package',_else='return new gnr.GnrBag();',
                subscribe_tableModuleWritten=True)

        form = tablesframe.grid.linkedForm(frameCode='tableModule',
                                 datapath='.tableForm',loadEvent='onRowDblClick',
                                 dialog_height='550px',dialog_width='1100px',
                                 dialog_title='^.form.record.name',handlerType='dialog',
                                 childname='form',attachTo=pane,store=True,
                                 store_pkeyField='_pkey')
        self.tablesForm(form)

    def tablesForm(self,form):
        saverpc = form.store.handler('save',rpcmethod=self.saveTableModule,fullRecord=True)
        saverpc.addCallback("genro.publish('tableModuleWritten')")
        form.store.handler('load',rpcmethod=self.loadTableModule,
                            default_project='=#FORM/parent/#FORM.record.project_name',
                            default_package='=#FORM/parent/#FORM.record.package_name')
        form.top.slotToolbar('2,navigation,*,form_delete,form_add,form_revert,form_save,semaphore,2')
        form.dataController("this.form.setLocked(true)",_onStart=True)
        form.dataController("genro.dlg.alert('Wrong info','Table has wrong data');",save_failed='^#FORM.controller.save_failed')
        bc = form.center.borderContainer()
        top = bc.borderContainer(datapath='.record',region='top',height='150px')
        tc = top.tabContainer(region='left',width='600px',margin='2px')
        tablepane = tc.contentPane(title='Table attributes')
        self.sysFieldPane(tc.contentPane(title='Sysfields'))
        fb = tablepane.div(margin='5px').formbuilder(cols=2)
        fb.dataFormula('#FORM.columnsValues',"""columns.values().map(function(v){return v.getItem('name')}).join(',')""",
                        columns='^._columns',_if='columns && columns.len()',_else='null')
        fb.textbox(value='^.name',lbl='Name',validate_notnull=True,validate_case='l')
        fb.comboBox(value='^.pkey',lbl='Pkey',validate_notnull=True,values='^#FORM.columnsValues')
        fb.textbox(value='^.name_long',lbl='Name Long',colspan=2,width='100%')
        fb.textbox(value='^.name_plural',lbl='Name Plural',colspan=2,width='100%')
        fb.comboBox(value='^.caption_field',lbl='Caption field',values='^#FORM.columnsValues')       
        fb.checkbox(value='^.lookup',label='Lookup')
        centerbc = bc.borderContainer(region='center')
        rightpane = centerbc.contentPane(region='right',width='250px',splitter=True,drawer=True,overflow='hidden')
        columnsframe = centerbc.contentPane(region='center').bagGrid(frameCode='columns',title='Columns',
                                                        datapath='#FORM.columnsGrid',
                                                    storepath='#FORM.record._columns',
                                                    struct=self.columns_struct,
                                                    structpath='#FORM.moduleColumnsStruct',
                                                    pbl_classes=True,margin='2px',
                                                    grid_selfDragRows=True,
                                                    grid_selfsubscribe_onSelectedRow="""
                                                                genro.publish('mve_moreattr_setSource','#FORM.record._columns.'+$1.selectedId)""",
                                                    addrow=True,delrow=True)
        rightpane.dataFormula('#FORM.columnsExcludedMoreAttr',"currentCheckedColumns?'name,'+currentCheckedColumns:null",
                                currentCheckedColumns='^#FORM.currentCheckedColumns',_onStart=True)
        rightpane.multiValueEditor(exclude='^#FORM.columnsExcludedMoreAttr',nodeId='mve_moreattr')
        columnsframe.top.bar.replaceSlots('addrow','addrow,5,searchOn,2')
        bar = columnsframe.top.bar.replaceSlots('vtitle','columnspicker')
        box = bar.columnspicker.div()
        box.div('Columns',cursor='pointer',font_weight='bold')
        cp = box.tooltipPane().div(padding='10px')
        cp.data('#FORM.currentCheckedColumns','name_long,size')
        cp.checkboxText(value='^#FORM.currentCheckedColumns',
                        values='^#FORM.record._columns?_columnsValues',cols=2)

        cp.dataController("""if(_reason=='setCurrentStruct'){
                return;
            }
            tableModuleEditor.setCurrentStruct(this,currentCheckedColumns,columnsValues)""",
                        currentCheckedColumns='^#FORM.currentCheckedColumns',
                        columnsValues='^#FORM.record._columns?_columnsValues',_delay=1,_onStart=True)

        top.contentPane(region='center',overflow='hidden').multiValueEditor(value='^#FORM.record',
                                            exclude='%s,_columns,_sysFields' %','.join(fb.fbuilder.field_list))
        self.relationEditorDialog(bc,grid=columnsframe.grid)

    def sysFieldPane(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=4,border_spacing='3px',datapath='._sysFields',fld_disabled='^._enabled?=!#v')
        fb.checkbox(value='^._enabled',label='Sysfields enabled',disabled=False,colspan=4)
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
    def saveTableModule(self,data=None,**kwargs):
        recordNode = data.getNode('record')
        record = recordNode.value
        recInfo = recordNode.attr
        oldpath = None
        resultAttr = dict()
        if recInfo['_newrecord']:
            table = record['name']
            package = recInfo['package']
            project = recInfo['project']
        else:
            project,package,old_table = recInfo['_pkey'].split('.')
            table = record['name']
            if table!=old_table:
                oldpath = os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %old_table))
        filepath = os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %table))    
        newPkey = '%s.%s.%s' %(project,package,table)
        self.makeOneTable(filepath=filepath,table_data=record)
        if oldpath and os.path.exists(oldpath):
            os.remove(oldpath)
        return (newPkey, resultAttr)

        

    @public_method
    def loadTableModule(self,pkey=None,default_project=None,default_package=None,**kwargs):
        if pkey=='*newrecord*':
            record = Bag()
            resultAttr = dict(_pkey=pkey,_newrecord=True,project=default_project,package=default_package)
            return record,resultAttr
        project,package,table = pkey.split('.')
        red = self.get_redbaron(os.path.join(os.path.join(self.getPackagePath(project,package),'model','%s.py' %table)))
        config_db = red.find('def','config_db')
        targs,tkwargs = self.parsBaronNodeCall(config_db.find('name','table').parent[2])
        resultAttr = dict(_pkey=pkey,_newrecord=False,project=project,package=package)
        record = Bag(tkwargs)
        record['name'] = table
        record['_sysFields'] = self.handleSysFields(red)
        columnsvalue = Bag()
        allcallattrs = []
        for colNode in red.find_all('name','column'):
            cbag = self._loadColumnBag(colNode)
            cbag['tag'] = 'column'
            columnsvalue[cbag['name']] = cbag
            allcallattrs.extend(cbag.keys())
        for colNode in red.find_all('name','aliasColumn'):
            cbag = self._getColBag(colNode,'relation_path')
            cbag['tag'] = 'aliasColumn'
            columnsvalue[cbag['name']] = cbag
            allcallattrs.extend(cbag.keys())
        for colNode in red.find_all('name','formulaColumn'):
            cbag = self._getColBag(colNode,'sql_formula')
            cbag['tag'] = 'formulaColumn'
            allcallattrs.extend(cbag.keys())
        for colNode in red.find_all('name','pyColumn'):
            cbag = self._getColBag(colNode,'py_method')
            cbag['tag'] = 'pyColumn'
            columnsvalue[cbag['name']] = cbag
            allcallattrs.extend(cbag.keys())
        allcallattrs = uniquify(allcallattrs)
        allcallattrs.remove('name')
        record.setItem('_columns',columnsvalue,_sendback=True,_columnsValues=','.join(allcallattrs))

        return record,resultAttr

    @public_method
    def table_editor_loadPackageTables(self,package=None,project=None):
        result = Bag()
        models_path = os.path.join(self.getPackagePath(project,package),'model')
        for m in os.listdir(models_path):
            tablename,ext = os.path.splitext(m)
            if ext!='.py':
                continue
            red = self.get_redbaron(os.path.join(models_path,m))
            config_db = red.find('def','config_db')
            targs,tkwargs = self.parsBaronNodeCall(config_db.find('name','table').parent[2])
            tablevalue = Bag(tkwargs)
            tablevalue['name'] = tablename
            tablevalue['_pkey'] = '%s.%s.%s' %(project,package,tablename)
            result[tablename] = tablevalue
        return result

