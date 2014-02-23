# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/framegrid:FrameGrid'
    css_requires = 'public'
    
    @classmethod
    def getMainPackage(cls,request_args=None,request_kwargs=None):
        return request_kwargs.get('th_from_package') or request_args[0]
        
    @property
    def maintable(self):
        callArgs = self.getCallArgs('conf_pkg','conf_table')
        return '%(conf_pkg)s.%(conf_table)s' %callArgs

    @property
    def pagename(self):
        callArgs = self.getCallArgs('conf_pkg','conf_table')  
        return 'tableconf_%(conf_pkg)s_%(conf_table)s' %callArgs

    def main(self,root,th_pkey=None,**kwargs):
        tc = root.tabContainer(margin='2px',datapath='main')
        self.column_config(tc.contentPane(title='!!Column configuration',datapath='.column_config'))
        self.ftree_config(tc.framePane(title='!!Fieldstree',datapath='.ftree_config'))


    def _columnsgrid_struct(self,struct):
        r = struct.view().rows()
        r.cell('fieldname', width='14em', name='Field')
        r.cell('datatype', width='8em', name='Datatype')
        r.cell('name_long', width='15em', name='Name long')
        r.cell('auth_tags', width='15em', name='Auth tags',edit=True)


    def column_config(self,pane):
        pane.css('.virtualCol','color:green')
        frame = pane.bagGrid(frameCode='columnsGrid',title='Columns',struct=self._columnsgrid_struct,
                        storepath='.store',
                        datapath='.grid',pbl_classes=True,margin='2px',_class='pbl_roundedGroup',addrow=False,delrow=False)
        #frame.grid.data('.sorted','fname:d')
        frame.dataRpc('.store',self.getColumnConfig,table=self.maintable,_onStart=True)

    def ftree_config(self,frame):

        frame.left.slotBar('10,fieldsTree,*',width='200px',closable=True,fieldsTree_table=self.maintable,
                            fieldsTree_height='100%',splitter=True,border_left='1px solid silver')
        menudata,metadata = self.db.table(self.maintable).getCustomFieldsMenu()
        frame.data('.menu.store._root',menudata or Bag(),caption='Fields')
        if metadata:
            frame.data('.menu.pkey',metadata['pkey'])
        tree_kw = dict()
        dropCode = 'gnrdbfld_%s' %self.maintable.replace('.','_')
        tree_kw['tree_onDrop_%s' %dropCode] = """ 
                                        var storebag = this.getRelativeData(this.attr.storepath);

                                          var p = dropInfo.treeItem.getFullpath(null,storebag) || '_root';
                                          var branch = storebag.getItem(p);
                                          if(!branch){
                                             branch = new gnr.GnrBag();
                                             storebag.setItem(p,branch);
                                          }

                                          var nodelabel = objectPop(data,'_nodelabel');
                                          var fullpath = objectPop(data,'_fullpath');
                                          if(fullpath){
                                            storebag.popNode(fullpath);
                                          }
                                          var kw = objectExtract(data,'fieldpath,caption,dtype,maintable')
                                          branch.setItem(nodelabel,null,kw);"""
        tree_kw['tree_dropCode'] = dropCode
        tree_kw['tree_dropTargetCb'] = "return dropInfo.treeItem.attr.dtype==null;"
        tree_kw['tree_draggable'] = True
        tree_kw['tree_onDrag'] = """
            var sn = dragInfo.sourceNode;
            var storebag = sn.getRelativeData(sn.attr.storepath);
            var fldinfo = objectUpdate({}, treeItem.attr);
            fldinfo._nodelabel = treeItem.label;
            fldinfo._fullpath = treeItem.getFullpath(null,storebag);
            dragValues['text/plain'] = treeItem.attr.fieldpath;
            dragValues['%s'] = fldinfo;

        """ %dropCode

        tree_kw['tree_dropTarget'] = True
        #tree_kw['tree_dropTargetCb'] = 'return true'
        frame.contentPane(overflow='hidden').bagEditor(storepath='.menu.store',labelAttribute='caption',addrow=True,**tree_kw)
        frame.bottom.slotBar('*,saveBtn,3',_class='slotbar_dialog_footer').saveBtn.button('Save',fire='.saveMenuUserObject')
        frame.dataRpc('dummy',self.saveMenuUserObject,_fired='^.saveMenuUserObject',
                        data='=.menu.store._root',pkey='=.menu.pkey',_onResult='SET .menu.pkey=result')

    @public_method
    def saveMenuUserObject(self,data=None,pkey=None,**kwargs):
        metadata = Bag()
        metadata['pkey'] = pkey
        metadata['code'] = '%s_fieldstree' %self.maintable.replace('.','_')
        pkey,record = self.db.table('adm.userobject').saveUserObject(table=self.maintable,objtype='fieldsmenu',data=data,metadata=metadata)
        return pkey

    @public_method
    def getColumnConfig(self,table=None):
        tblobj = self.db.table(table)
        result = Bag()
        for field,colobj in tblobj.model.columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T')),auth_tags=None))

        for field,colobj in tblobj.model.virtual_columns.items():
            colattr = colobj.attributes
            result.setItem(field,Bag(dict(fieldname=field,name_long=colattr.get('name_long'),datatype=colattr.get('dtype','T'),auth_tags=None)),_customClasses='virtualCol')

        return result





