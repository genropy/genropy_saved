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
        fb.dbselect(value='^.pkgid',dbtable='adm.pkginfo',lbl='Pkg',hasDownArrow=True)
        fb.dbselect(value='^.tblid',dbtable='adm.tblinfo',lbl='Tbl',condition=':pkgid IS NULL OR $pkgid=:pkgid',
                    condition_pkgid='=.pkgid',hasDownArrow=True)
        frame.contentPane(region='center').dialogTableHandler(table='adm.user_config',view_store_onStart=True)


