#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  index.py


""" index.py """
from gnr.core.gnrdecorator import public_method
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires = """public:Public,th/th:TableHandler"""
    auth_page='admin,superadmin,_DEV_'
    pageOptions={'liveUpdate':True,'userConfig':False}

    def main(self, root,**kwargs):
        self.db.table('adm.install_checklist').createSysRecords()
        frame = root.rootBorderContainer(datapath='main',design='sidebar',title='!![it]Checklist viewer') 
        th = frame.contentPane(region='center').plainTableHandler(table='adm.install_checklist',
                                                            viewResource='ViewChecklist',
                                                            view_store_onStart=True,
                                                            #autoSave=True,
                                                            #configurable=False,
                                                            rowStatusColumn=False)
        th.view.grid.dataController("""SET main.doc_url = null;
                                    var that = this;
                                    setTimeout(function(){
                                        that.setRelativeData('main.doc_url',selectedUrl);
                                    },1);""",selectedUrl='^.selectedId?doc_url')
        frame.contentPane(region='right',width='50%',splitter=True,
                         border_left='1px solid silver').iframe(src='^main.doc_url',height='100%',width='100%',
                                                                              border=0)
        
