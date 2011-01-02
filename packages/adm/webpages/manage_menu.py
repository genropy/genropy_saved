#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" menu manager"""

#from gnr.core.gnrbag import Bag
from gnr.core.gnrdate import decodeOneDate
import hashlib

class GnrCustomWebPage(object):
    maintable = 'adm.menu'
    py_requires = 'public:Public,public:IncludedView,public:RecordHandler'#we need to pass the name of components

    #public is used for the skin 
    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'user'

    def windowTitle(self):
        return '!!Menu lines'#the !! is used to have a localised string

    def pageAuthTags(self, method=None, **kwargs):#this defines who can use the page
        return 'user'


    def main(self, root, **kwargs):
        center, top, bottom = self.pbl_rootBorderContainer(root,
                                                           title='Menu manager')
        linesView = center.borderContainer(region='top', height='380px')
        treeView = center.borderContainer(region='center')
        buttons = center.contentPane(region='bottom', height='32px')
        self.menulinesView(linesView)
        self.bottomButtons(buttons)

    def bottomButtons(self, pane):
        pane.button('Import from XML', action='FIRE importFromXml')
        pane.button('Update menu', action='FIRE updateMenuBag')
        pane.dataRpc('dummy', 'importFromXml', _fired='^importFromXml', _onResult='FIRE #menulinesView.reload')
        pane.dataRpc('dummy', 'updateMenuBag', _fired='^updateMenuBag')

    def menulinesView(self, bc):
        iv = self.includedViewBox(bc,
                                  table='adm.menu',
                                  datapath='menulines',
                                  connect_onRowDblClick="""var selid= GET .selectedId;
                                                           FIRE .firedPkey = selid;
                                    """,
                                  multiSelect=False,
                                  #sortedBy='code',
                                  label=u'!!Menu lines',
                                  autoWidth=True,
                                  struct=self.menulinesView_struct,
                                  add_action='FIRE .firedPkey;',
                                  del_action='FIRE .deletingRecord;',
                                  nodeId='menulinesView',
                                  selectionPars=dict(order_by='$code'))

        self.recordDialog('adm.menu', firedPkey='^menulines.firedPkey',
                          width='660px', height='380px',
                          formCb=self.menuForm)

        bc.dataController("""FIRE #menulinesView.reload """, _onStart=True)

    def menulinesView_struct(self, struct):
        r = struct.view().rows()
        r.fieldcell('code', width='26em')
        r.fieldcell('label', width='14em')
        r.fieldcell('file', width='18em')
        r.fieldcell('parameters', width='10em')
        r.fieldcell('level', width='5em', dtype='L')
        r.fieldcell('position', width='5em')
        return struct

    def menuForm(self, recordBC, **kwargs):
        pane = recordBC.contentPane(_class='pbl_roundedGroup', **kwargs)
        fb = pane.formbuilder(cols=1, margin_left='1em', border_spacing='5px', width='550px')
        fb.field('adm.menu.code', autospan=1)
        fb.field('adm.menu.label', autospan=1)
        fb.field('adm.menu.description', autospan=1)
        fb.field('adm.menu.file', autospan=1)
        fb.field('adm.menu.basepath', autospan=1)
        fb.field('adm.menu.tags', autospan=1)
        fb.field('adm.menu.parameters', autospan=1)

    def rpc_importFromXml(self):
        menubag = self.application.config['menu']
        self.db.table('adm.menu').importFromBag(menubag)
        self.db.commit()
        return

    def rpc_createMenuBag(self):
        menubag = self.db.table('adm.menu').createMenuBag(menubag)
        return
        
       