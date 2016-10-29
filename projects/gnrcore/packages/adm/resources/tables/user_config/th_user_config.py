#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class ViewFromUserConfigurator(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',edit=True,hidden='^#mainpars.user_group',width='6em')
        r.fieldcell('user_id',edit=True,hidden='^#mainpars.user_id',width='7em')
        r.fieldcell('pkg',edit=True,hidden='^#mainpars.pkg',width='4em')
        r.fieldcell('tbl',edit=dict(condition='$pkg=:p',condition_p='=.pkg'),hidden='^#mainpars.tbl',width='8em')
        r.fieldcell('entity',edit=True,width='5em')


        r.fieldcell('qtree',edit=dict(tag='remoteSelect',auxColumns='code,description',
                        method='_table.adm.user_config.getCustomCodes',condition_tbl='=.tbl',
                        condition_item_type='QTREE',
                        hasDownArrow=True),
                        _customGetter=self.valgetter('QTREE'),width='6em')

        r.fieldcell('ftree',edit=dict(tag='remoteSelect',auxColumns='code,description',
                        method='_table.adm.user_config.getCustomCodes',condition_tbl='=.tbl',
                        condition_item_type='FTREE',
                        hasDownArrow=True),
                        _customGetter=self.valgetter('FTREE'),width='6em')
        r.fieldcell('tbl_permission',edit=dict(tag='checkBoxText',values='hidden,readonly,/,ins,upd,del',cols=3),
                    width='12em',name='!!Permission')
        r.fieldcell('forbidden_columns',edit=dict(tag='checkBoxText',remoteValues='_table.adm.tblinfo.getTblInfoCols',condition_tbl='=.tbl'),
                        width='25em',editDisabled='=#ROW.tbl?=!#v')
        r.fieldcell('readonly_columns',edit=dict(tag='checkBoxText',remoteValues='_table.adm.tblinfo.getTblInfoCols',condition_tbl='=.tbl'),
                        width='25em',editDisabled='=#ROW.tbl?=!#v')

    def th_options(self):
        return dict(default_user_group='=#mainpars.user_group',default_user_id='=#mainpars.user_id',
                    default_pkg='=#mainpars.pkg',default_tbl='=#mainpars.tbl')

    def th_view(self,view):
        view.dataController("""
                if(_node.label=='tbl_permission'){
                    var v = _triggerpars.kw.value;
                    var reason = _triggerpars.kw.reason;
                    if(!v || reason=='reset_hidden_readonly'){
                        return;
                    }
                    if(v.indexOf('hidden')>=0 || v.indexOf('readonly')>=0){
                        setTimeout(function(){
                            _node.getParentBag().setItem('tbl_permission',v.indexOf('hidden')>=0?'hidden':'readonly',null,{doTrigger:'reset_hidden_readonly'});
                        },1);
                    }
                }

            """,store='^.store')

    def th_hiddencolumns(self):
        return '$rank'

    def valgetter(self,type=None):
        t = type.lower()
        return """function(row){var p = objectFromString('%s');
                                return p[row['%s']] || row['%s']}""" % (getattr(self.db.table('adm.user_config'),'type_%s' %type)(),t,t)

    def th_order(self):
        return 'rank:a'

    def th_condition(self):
        return dict(condition="""(:ugroup IS NULL OR $user_group=:ugroup) AND
                                (:uid IS NULL OR $user_id=:uid) AND
                                (:pkginfo IS NULL OR $pkg=:pkginfo) AND
                                (:tblinfo IS NULL OR $tbl=:tblinfo)
                            """,condition_ugroup='^#mainpars.user_group',
                                 condition_uid='^#mainpars.user_id',
                                 condition_tblinfo='^#mainpars.tbl',
                                 condition_pkginfo='^#mainpars.pkg'
                                 )

class View_QTREE(ViewFromUserConfigurator):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',edit=True,hidden='^#mainpars.user_group')
        r.fieldcell('user_id',edit=True,hidden='^#mainpars.user_id')
        r.fieldcell('pkg',edit=True,hidden='^#mainpars.pkg')
        r.fieldcell('tbl',edit=dict(condition='$pkg=:p',condition_p='=.pkg'),hidden='^#mainpars.tbl')
        r.fieldcell(self.typetree().lower(),edit=dict(tag='remoteSelect',auxColumns='code,description',
                        method='_table.adm.user_config.getCustomCodes',condition_tbl='=.tbl',
                        condition_item_type=self.typetree(),
                        hasDownArrow=True),
                        _customGetter=self.valgetter())

    def th_options(self):
        return dict(default_user_group='=#mainpars.user_group',default_user_id='=#mainpars.user_id',
                    default_pkg='=#mainpars.pkg',default_tbl='=#mainpars.tbl')

    def typetree(self):
        return 'QTREE'

class View_FTREE(View_QTREE):
    def typetree(self):
        return 'FTREE'


class View_AUTH(View_QTREE):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group',edit=True,hidden='^#mainpars.user_group')
        r.fieldcell('user_id',edit=True,hidden='^#mainpars.user_id')
        r.fieldcell('pkg',edit=True,hidden='^#mainpars.pkg')
        r.fieldcell('tbl',edit=dict(condition='$pkg=:p',condition_p='=.pkg'),hidden='^#mainpars.tbl')
        r.fieldcell('data',hidden=True)
        r.cell('view_permissions',rowTemplate="$data",width='20em',#cellClasses='tplcell',
                    edit=dict(contentCb="""function(pane,kw){
                            pane._('checkbox',{value:'^.data.view_read',label:'Read'})
                            pane._('br')
                            pane._('checkbox',{value:'^.data.view_add',label:'Add'})
                            pane._('br')
                            pane._('checkbox',{value:'^.data.view_del',label:'Del'})
                        }

                        """),
                    calculated=True)


       #r.checkboxcell('data.view_read',name='VRead',threestate=True)
       #r.checkboxcell('data.view_add',name='VAdd',threestate=True)
       #r.checkboxcell('data.view_del',name='VDel',threestate=True)
       #r.checkboxcell('data.form_read',name='FRead',threestate=True)
       #r.checkboxcell('data.form_add',name='FAdd',threestate=True)
       #r.checkboxcell('data.form_del',name='FDel',threestate=True)
       #r.checkboxcell('data.form_upd',name='FUpd',threestate=True)
       #r.checkboxcell('data.column_read',name='CRead',threestate=True)
       #r.checkboxcell('data.column_upd',name='CUpd',threestate=True)

    def typetree(self):
        return 'AUTH'




class QTreeViewFromUserRO(View_QTREE):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_group')
        r.fieldcell('pkg')
        r.fieldcell('tbl')
        r.fieldcell('value',_customGetter="""function(row){return objectFromString('%s')[row['value']] || row['value']}""" %self.db.table('adm.user_config').type_QTREE()
                        )


class QTreeViewFromUser(View_QTREE):
    def th_hiddencolumns(self):
        return '$rank'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('pkg',edit=True)
        r.fieldcell('tbl',edit=dict(condition='$pkg=:p',condition_p='=.pkg'))
        r.fieldcell('value',edit=dict(tag='remoteSelect',auxColumns='code,description',
                        method='_table.adm.user_config.getCustomCodes',condition_tbl='=.tbl',condition_item_type='QTREE',
                        hasDownArrow=True),
                        _customGetter="""function(row){return objectFromString('%s')[row['value']] || row['value']}""" %self.db.table('adm.user_config').type_QTREE()
                        )

    def th_order(self):
        return 'rank:a'

class Form_AUTH(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer(data='.record')
        fb = bc.contentPane(region='left',width='50%').formbuilder(cols=2, border_spacing='4px')
        fb.checkbox(value='^.data.view_read',label='!!View Read')
        fb.checkbox(value='^.data.view_add',label='!!View Add')
        fb.checkbox(value='^.data.view_del',label='!!View Del')
        fb.checkbox(value='^.data.form_read',label='!!Form Read')
        fb.checkbox(value='^.data.form_add',label='!!Form Add')
        fb.checkbox(value='^.data.form_del',label='!!Form Del')
        fb.checkbox(value='^.data.form_upd',label='!!Form Update')
        self.column_config(bc.contentPane(region='center'))

    def _columnsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname', width='14em', name='!!Field')
        r.cell('datatype', width='8em', name='!!Datatype')
        r.cell('name_long', width='15em', name='!!Name long')
        r.cell('read', width='5em', name='!!Read',edit=True,dtype='B')
        r.cell('write', width='5em', name='!!Write',edit=True,dtype='B',editDisabled='=#ROW.virtual_column')


    def column_config(self,pane):
        pane.css('.virtualCol','color:green')
        frame = pane.bagGrid(frameCode='columnsGrid',title='Columns',struct=self._columnsgrid_struct,
                        storepath='#FORM.record.data.columns_configuraton',
                        datapath='#FORM.column_config_grid',
                        pbl_classes=True,
                        margin='2px',_class='pbl_roundedGroup',
                        addrow=False,delrow=False)


    def getColumnConfig(self,table=None):
        tblobj = self.db.table(table)
        result = Bag()
        for field,colobj in tblobj.model.columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T')),
                            read=True,write=True))

        for field,colobj in tblobj.model.virtual_columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T'),auth_tags=None,
                                            read=True,write=False,virtual_column=True)),_customClasses='virtualCol')

        return result


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        currentColumnConfig = record['data.columns_configuraton']
        cconf = self.getColumnConfig(record['tbl'])
        if currentColumnConfig:
            cconf.update(currentColumnConfig)
        record['data'] = record['data'] or Bag()
        record['data.columns_configuraton'] = cconf



    def th_options(self):
        return dict(default_user_group='=#mainpars.user_group',default_user_id='=#mainpars.user_id',
                    default_pkg='=#mainpars.pkg',default_tbl='=#mainpars.tbl')

