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
        frame.bagEditor(storepath='.menu.store',
                        **{str('onDrop_gnrdbfld_%s' %self.maintable.replace('.','_')):"genro.bp(true)"})




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





