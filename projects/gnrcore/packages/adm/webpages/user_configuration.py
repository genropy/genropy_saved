#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  index.py


""" index.py """
from gnr.core.gnrdecorator import public_method
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires = """public:Public,th/th:TableHandler"""
    pageOptions={'openMenu':False,'liveUpdate':True}


    def main(self, root,**kwargs):
        frame = root.rootBorderContainer(datapath='main',design='sidebar',title='!![it]Admin Configurator') 
        top = frame.contentPane(region='top')
        fb = top.formbuilder(cols=4,border_spacing='3px',datapath='.params',nodeId='mainpars')
        fb.dbselect(value='^.user_group',dbtable='adm.group',
                    lbl='User Group',hasDownArrow=True)
        fb.dbselect(value='^.user_id',dbtable='adm.user',lbl='User',
                    condition='$group_code IS NULL OR :ugroup IS NULL OR $group_code=:ugroup',
                    condition_ugroup='=.user_group',hasDownArrow=True)
        fb.dbselect(value='^.pkg',dbtable='adm.pkginfo',lbl='Pkg',hasDownArrow=True)
        fb.dbselect(value='^.tbl',dbtable='adm.tblinfo',lbl='Tbl',condition=':pkginfo IS NULL OR $pkg=:pkginfo',
                    condition_pkginfo='=.pkginfo',hasDownArrow=True)
        frame.contentPane(region='center').inlineTableHandler(table='adm.user_tblinfo',autoSave=False,saveButton=True,
                               semaphore=True,viewResource='ViewFromUserConfigurator',view_store_onStart=True)

   #    tc = frame.tabContainer(region='center',margin='3px')
   #    tblinfo = self.db.table('adm.user_tblinfo')
   #    l = [(k[5:],getattr(tblinfo,k)) for k in dir(tblinfo) if k.startswith('type_') and not k[-1]=='_']
   #    for key,cb in sorted(l,lambda a,b: a[1].order-b[1].order):
   #        getattr(self,'configurator_%s' %key)(tc.contentPane(title=cb.title),
   #                    nodeId=key.lower(),datapath='main.%s' %key,
   #                    viewResource='View_%s' %key,
   #                    pbl_classes=True,margin='2px',
   #                    default_info_type=key,
   #                    view_store_onStart=True)

   #def configurator_AUTH(self,pane,**kwargs):
   #    pane.inlineTableHandler(table='adm.user_tblinfo',autoSave=False,saveButton=True,
   #                            semaphore=True,**kwargs)

   #def configurator_QTREE(self,pane,**kwargs):
   #    pane.inlineTableHandler(table='adm.user_tblinfo',autoSave=False,saveButton=True,
   #                            semaphore=True,**kwargs)

   #def configurator_FTREE(self,pane,**kwargs):
   #    pane.inlineTableHandler(table='adm.user_tblinfo',autoSave=False,saveButton=True,
   #                            semaphore=True,**kwargs)
