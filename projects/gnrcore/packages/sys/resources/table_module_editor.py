# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from redbaron import RedBaron
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrstring import boolean
from gnr.core.gnrbag import Bag
from collections import OrderedDict
import os
SYSFIELDS_DEFAULT = OrderedDict(id=True, ins=True, upd=True, 
                                    ldel=True, user_ins=False, 
                                    user_upd=False, 
                                    draftField=False, 
                                    counter=False,
                                    hierarchical=False,
                                    df=False)

MORE_ATTRIBUTES = 'cell_,format,validate_notnull,validate_case'

class TableModuleEditor(BaseComponent):
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

    def bagToArglist(self,arguments):
        if not arguments:
            return ''
        atlst = []
        for k,v in arguments.items():
            if isinstance(v,basestring):
                v = ("'%s'" if not "'" in v else '"%s"') %v
                atlst.append("%s=%s" %(k,v))
        return ',%s' %','.join(atlst)
            
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
            arguments = OrderedDict()
            for k,v in sysFields.items():
                if SYSFIELDS_DEFAULT.get(k) == v:
                    arguments[k] = v                
            config_db_node.append('sysFields(tbl%s)' %self.bagToArglist(arguments))
        for col in columns.values():
            relation = col.pop('_relation')
            s = self._columnPythonCode(col,relation)
            config_db_node.append(s)
        with open(filepath,'w') as f:
            f.write(red.dumps())
            
    
    def _columnPythonCode(self,col,relation=None):
        attributes = Bag()
        col = col.deepcopy()
        name = col.pop('name')
        dtype = col.pop('dtype')
        size = col.pop('size')
        name_long = col.pop('name_long')
        name_short = col.pop('name_short')
        more_attributes = col.pop('_more_attributes')
        tag = col.pop('tag') #column,formulaColumn,aliasColumn,pyColumn
        if dtype and dtype not in ('A','T','C'):
            attributes['dtype'] = dtype
        if size:
            attributes['size'] = size
        attributes.setItem('name_long', name_long or name,localized=True)
        if name_short:
            attributes.setItem('name_short', name_short,localized=True)
        attributes.update(col)
        if more_attributes:
            for key,dtype,value in more_attributes.digest('#v.attribute_key,#v.attribute_dtype,#v.attribute_value'):
                dtype = dtype or 'T'
                if value not in (None,''):
                    attributes[key] = self.catalog.fromText(value,dtype)
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

    def handleSysFields(self,red):
        sysFieldBaronNode = red.find('name','sysFields')
        if not sysFieldBaronNode:
            return Bag()
        result = Bag(SYSFIELDS_DEFAULT) #counter_kwargs=None
        result['_enabled'] = True
        args,kwargs = self.parsBaronNodeCall(sysFieldBaronNode.parent[2])
        for k,v in kwargs.items():
            result[k] = v
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
        more_attributes = Bag()
        for attrname,attrvalue in cattr.items():
            more_attributes[attrname] = Bag(dict(attribute_key=attrname,attribute_value=attrvalue,dtype=self.catalog.names[type(attrvalue)]))
        cbag['_more_attributes'] = more_attributes
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
        def struct(struct):
            r = struct.view().rows()
            r.cell('attribute_key',name='Key',edit=dict(tag='ComboBox',values=MORE_ATTRIBUTES),width='10em')
            r.cell('attribute_dtype',name='Dtype',edit=dict(tag='filteringSelect',
                                                            values='T:Text,B:Bool,I:Int,N:Decimal'),width='10em')
            r.cell('attribute_value',name='Value',edit=True,width='10em')

        frame = dlg.bagGrid(height='200px',width='400px',storepath='#FORM.moreAttributes.data',struct=struct)
        
        bar = frame.bottom.slotBar('*,cancel,10,confirm,2',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.cancel.slotButton('Cancel',action="dlg.hide()",dlg=dlg.js_widget)
        bar.confirm.slotButton('Confirm',action="""griddata.setItem('#'+rowIndex+'._more_attributes',data.deepCopy());
                                                    dlg.hide()
                                                    """,
                                        dlg=dlg.js_widget,
                                        griddata='=#FORM.record._columns',
                                        rowIndex='=.rowIndex',
                                        data='=.data')

    def columns_struct(self,struct):
        r = struct.view().rows()
        r.cell('legacy_name',width='10em',name='Legacy Name',hidden='^main.connectionTpl?=!#v')
        r.cell('name',width='10em',name='Name',edit=True)
        r.cell('dtype',width='5em',name='Dtype',edit=dict(tag='filteringSelect',values='T:Text,I:Int,N:Decimal,B:Bool,D:Date,DH:Timestamp,X:Bag'))
        r.cell('size',width='5em',name='Size',edit=True)
        r.cell('group',width='5em',name='Group',edit=True)
        r.cell('name_long',width='20em',name='Name long',edit=True)
        r.cell('name_short',width='10em',name='Name short',edit=True)
        r.cell('indexed',width='5em',name='Indexed',edit=True,dtype='B')
        r.cell('unique',width='5em',name='Unique',edit=True,dtype='B')
        r.cell('_more_attributes',width='20em',name='More attributes',edit=True,editOnOpening=""" 
                                        var more_attributes = rowData.getItem(field);
                                        genro.publish('edit_more_attributes',{more_attributes:more_attributes,rowIndex:rowIndex})
                                        return false;
                                    """)

        r.cell('_relation',width='20em',name='Relation',edit=True,
                     editOnOpening="""var relation = rowData.getItem(field);
                                    if(relation){
                                        relation = relation.deepCopy();
                                    }
                                    genro.publish('edit_relation',{relation:relation,rowIndex:rowIndex})
                                    return false;
                                    """)
    def tablesForm(self,form):
        form.top.slotToolbar('2,navigation,*,form_delete,form_add,form_revert,form_save,semaphore,2')
        form.store.attributes.update(autoSave=True)
        form.dataController("this.form.setLocked(true)",_onStart=True)
        form.dataController("genro.dlg.alert('Wrong info','Table has wrong data');",save_failed='^#FORM.controller.save_failed')
        bc = form.center.borderContainer()
        self.moreAttributesDialog(bc)
        top = bc.contentPane(datapath='.record',region='top')
        fb = top.formbuilder(cols=3)
        fb.dataFormula('#FORM.columnsValues',"""columns.values().map(function(v){return v.getItem('name')}).join(',')""",
                        columns='^._columns',_if='columns && columns.len()',_else='null')
        fb.textbox(value='^.name',lbl='Name',validate_notnull=True,validate_case='l')
        fb.textbox(value='^.name_long',lbl='Name Long')
        fb.textbox(value='^.name_plural',lbl='Name Plural')
        fb.comboBox(value='^.pkey',lbl='Pkey',validate_notnull=True,values='^#FORM.columnsValues')
        fb.comboBox(value='^.caption_field',lbl='Caption field',values='^#FORM.columnsValues')       
        fb.checkbox(value='^.lookup',lbl='Lookup')
        fb.button('Handle Sysfields') 
        columnsframe = bc.contentPane(region='center').bagGrid(frameCode='columns',title='Columns',
                                                        datapath='#FORM.columnsGrid',
                                                    storepath='#FORM.record._columns',
                                                    struct=self.columns_struct,
                                                    pbl_classes=True,margin='2px',
                                                    grid_selfDragRows=True,
                                                    addrow=True,delrow=True)
        self.relationEditorDialog(bc,grid=columnsframe.grid)


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

           #tablevalue['_sysFields'] =self.handleSysFields(red)
           #columnsvalue = Bag()
           #tablevalue.setItem('_columns',columnsvalue,_sendback=True)
           #for colNode in red.find_all('name','column'):
           #    cbag = self._loadColumnBag(colNode)
           #    cbag['tag'] = 'column'
           #    columnsvalue[cbag['name']] = cbag
           #for colNode in red.find_all('name','aliasColumn'):
           #    cbag = self._getColBag(colNode,'relation_path')
           #    cbag['tag'] = 'aliasColumn'
           #    columnsvalue[cbag['name']] = cbag
           #for colNode in red.find_all('name','formulaColumn'):
           #    cbag = self._getColBag(colNode,'sql_formula')
           #    cbag['tag'] = 'formulaColumn'
           #    columnsvalue[cbag['name']] = cbag
           #for colNode in red.find_all('name','pyColumn'):
           #    cbag = self._getColBag(colNode,'py_method')
           #    cbag['tag'] = 'pyColumn'
           #    columnsvalue[cbag['name']] = cbag
