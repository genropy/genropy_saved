# -*- coding: UTF-8 -*-

# th_lib.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrclasses import GnrMixinError

class TableHandlerCommon(BaseComponent):
    def _th_relationExpand(self,pane,relation=None,condition=None,condition_kwargs=None,default_kwargs=None,**kwargs):
        maintable=kwargs.get('maintable') or pane.getInheritedAttributes().get('table') or self.maintable
        if default_kwargs is None:
            default_kwargs = dict()
        relation_attr = self.db.table(maintable).model.getRelation(relation)
        many = relation_attr['many'].split('.')
        fkey = many.pop()
        table = str('.'.join(many))
        fkey = str(fkey)
        condition_kwargs['fkey'] = '^#FORM.pkey'
        basecondition = '$%s=:fkey' %fkey       
        condition = basecondition if not condition else '(%s) AND (%s)' %(basecondition,condition)  
        default_kwargs['default_%s' %fkey] = '=#FORM/parent/#FORM.pkey'
        return table,condition 
        
    def _th_getResourceName(self,name=None,defaultModule=None,defaultClass=None):
        if not name:
            return '%s:%s' %(defaultModule,defaultClass)
        if not ':' in name:
            return '%s:%s' %(name,defaultClass)
        if name.startswith(':'):
            return '%s%s' %(defaultModule,name)
        return name
        
    def _th_mixinResource(self,rootCode=None,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        try:
            self.mixinComponent(self.package.name,'tables','_packages',pkg,tablename,resourceName,mangling_th=rootCode)
        except GnrMixinError:
            self.mixinComponent(pkg,'tables',tablename,resourceName,mangling_th=rootCode)
            
    
    def _th_getResClass(self,table=None,resourceName=None,defaultClass=None):
        pkg,tablename = table.split('.')
        defaultModule = 'th_%s' %tablename
        resourceName = self._th_getResourceName(resourceName,defaultModule,defaultClass)
        return self.importTableResource(table,resourceName,pkg=pkg)
        
    def _th_hook(self,method,mangler=None,asDict=False,dflt=None):
        if isinstance(mangler,Bag):
            mangler = mangler.getInheritedAttributes().get('th_root')
        if hasattr(self,'legacy_dict'):
            method=self.legacy_dict.get(method,method)
        if asDict:
            prefix='%s_%s_'% (mangler,method)
            return dict([(fname,getattr(self,fname)) for fname in dir(self) 
                                     if fname.startswith(prefix) and fname != prefix])
        if hasattr(self,'legacy_dict'):
            return getattr(self,method)          
        def emptyCb(*args,**kwargs):
            return dflt
        return getattr(self,'%s_%s' %(mangler.replace('.','_'),method),emptyCb) 

#####################################OLDSTUFF#####################
    def userCanWrite(self):
        return self.application.checkResourcePermission(self.tableWriteTags(), self.userTags)

    def userCanDelete(self):
        return self.application.checkResourcePermission(self.tableDeleteTags(), self.userTags)

    def tableWriteTags(self):
        return 'superadmin'

    def tableDeleteTags(self):
        return 'superadmin'

    def rpc_onLoadingSelection(self, selection):
        """ovverride if you need"""
        pass

    def rowsPerPage(self):
        return 25

    def hiddencolumnsBase(self):
        return

    def hierarchicalViewConf(self):
        return None

    def hierarchicalEdit(self):
        return None

    def formTitleBase(self, pane):
        pane.data('form.title', self.tblobj.attributes.get('name_long', 'Record'))
        
    def onSavingFormBase(self):
        """JS ONCALLING OF RPCSAVING PROCESS
           params inside js:
           data: what you send
           form: the formBase js object
           if you return false the rpc is not called;
        """
        return None

class QueryHelper(BaseComponent):
    def query_helper_main(self, pane):
        pane.dataController(""" var row = genro.getDataNode('list.query.where.'+queryrow);
                                var attrs = row.getAttr();
                                var op = attrs['op'];
                                var col_caption = attrs['column_caption'];
                                var op_caption = attrs['op_caption'];
                                if(op=='in'){
                                    FIRE #helper_in_dlg.open = {row:queryrow,title:col_caption+' '+op_caption};
                                }else if(op=='tagged'){
                                    FIRE #helper_tag_dlg.open = {row:queryrow,call_mode:'helper'};
                                }""",
                            queryrow="^list.helper.queryrow")
        self.helper_in_dlg(pane)
        self.helper_tag_dlg(pane)

    def helper_in_dlg(self, pane):
        def cb_center(parentBC, **kwargs):
            bc = parentBC.borderContainer(**kwargs)
            top = bc.contentPane(region='top', margin_bottom='0', padding='2px',
                                 datapath='.#parent', height='25px', overflow='hidden')
            top = top.toolbar(height='24px')
            top.div('!!Enter a list of values:', float='left', margin='3px')
            menubag = Bag()
            menubag.setItem('save', None, label='!!Save', action='FIRE .saveAsUserObject;')
            menubag.setItem('save_as', None, label='!!Save as', action='FIRE .saveAsUserObject = "new";')
            menubag.setItem('delete', None, label='!!Delete ', action='FIRE .deleteCurrSaved;')
            menubag.setItem('-', None)
            top.data('.menu', menubag)
            top.dataRemote('.menu.load', 'getObjListIn', cacheTime=10,
                           sync=True, label='!!Load',
                           action='FIRE .loadUserObject = $1.pkey;')
            ddb = top.dropDownButton('!!Command', float='right')
            ddb.menu(storepath='.menu', _class='smallmenu')
            center = bc.contentPane(region='center', margin='5px', margin_top=0)
            center.simpleTextArea(value='^.items', height='90%', width='95%', margin='5px')

        dialogBc = self.formDialog(pane, title='^.opener.title', loadsync=True,
                                   datapath='list.helper.op_in', centerOn='_pageRoot',
                                   height='300px', width='300px',
                                   formId='helper_in', cb_center=cb_center)
        dialogBc.dataController("""var val =genro._('list.query.where.'+queryrow);
                                   if(val){
                                       SET .data.items = val.replace(/,+/g,'\\n');                                       
                                   }else{
                                        SET .data = null;
                                   }
                                   """,
                                nodeId="helper_in_loader", queryrow='=.opener.row')

        dialogBc.dataController("""
                                var splitPattern=/\s*[\\n\\,]+\s*/g;
                                var cleanPattern=/(^\\s*[\\n\\,]*\\s*|\\s*[\\n\\,]*\\s*$)/g;
                                items=items.replace(cleanPattern,'').split(splitPattern).join(',');
                                genro.setData('list.query.where.'+queryrow,items);
                                FIRE .saved;""",
                                items='=.data.items', queryrow='=.opener.row',
                                nodeId="helper_in_saver")
        dialogBc.dataController("""
                                  data = data.replace(/\s+/g,',').replace(/,+$/g,'');
                                  var pars = new gnr.GnrBag({data:new gnr.GnrBag({values:data}),title:title,objtype:objtype});
                                  SET #userobject_dlg.pars = pars;
                                  if(command=='new'){
                                       current = "*newrecord*"
                                  }
                                  FIRE #userobject_dlg.pkey = current || '*newrecord*';""",
                                command="^.saveAsUserObject", current='=.currentUserObject',
                                data='=.data.items', title='!!Save list',
                                objtype='list_in')
        dialogBc.dataRpc('dummy', 'loadUserObject',
                         tbl=self.maintable, id='^.loadUserObject', _if='id',
                         _onResult='SET .currentUserObject = $2.id; SET .data.items = $1.getValue().getItem("values");')
        dialogBc.dataController("SET .currentUserObject=pkey", _fired="^#userobject_dlg.saved",
                                pkey='=#userobject_dlg.savedPkey',
                                objtype='=#userobject_dlg.pars.objtype',
                                _if='objtype=="list_in"')
        dialogBc.dataController("""SET #deleteUserObject.pars = new gnr.GnrBag({title:title,pkey:current,objtype:"list_in"}); 
                                   FIRE #deleteUserObject.open;""", _fired="^.deleteCurrSaved",
                                title='!!Delete list of values', current='=.currentUserObject', _if='current')
        dialogBc.dataController("SET .data.items = null; SET .currentUserObject=null;",
                                _fired="^#deleteUserObject.deleted", objtype='=#deleteUserObject.pars.objtype',
                                _if='objtype=="list_in"')

    def rpc_getObjListIn(self, **kwargs):
        result = self.rpc_listUserObject(objtype='list_in', tbl=self.maintable, **kwargs)
        return result

    def helper_tag_dlg(self, pane):
        def cb_center(parentBC, **kwargs):
            parentBC.contentPane(**kwargs).remote('getFormTags_query', queryColumn='=.#parent.queryColumn',
                                                  queryValues='^.#parent.queryValues', call_mode='helper')

        dialogBc = self.formDialog(pane, title='!!Helper TAG', loadsync=False,
                                   datapath='list.helper.op_tag', centerOn='_pageRoot',
                                   height='300px', width='510px', allowNoChanges=False,
                                   formId='helper_tag', cb_center=cb_center)
        dialogBc.dataController("""
                                   SET .data = null;
                                   var rowNode = genro.getDataNode('list.query.where.'+queryrow);
                                   SET .queryColumn  = rowNode.attr.column;
                                   FIRE .queryValues = rowNode.getValue();
                                   FIRE .loaded;
                                """,
                                nodeId="helper_tag_loader", queryrow='=.opener.row')

        dialogBc.dataController("""
                                var tagged = [];
                                var tagged_not = [];
                                var cb = function(node){
                                    var selectedTag = node.attr['selectedTag'];
                                    if (selectedTag){
                                        if (selectedTag[0]=='!'){
                                            tagged_not.push(selectedTag.slice(1));
                                        }else{
                                            tagged.push(selectedTag);
                                        }
                                    }
                                }
                                tagbag.forEach(cb);
                                var result = tagged.join(',')+'!'+tagged_not.join(',');
                                genro.setData('list.query.where.'+queryrow,result);
                                FIRE .saved;""",
                                tagbag='=.data.tagbag', queryrow='=.opener.row',
                                nodeId="helper_tag_saver")
