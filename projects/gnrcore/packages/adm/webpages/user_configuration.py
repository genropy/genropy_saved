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
        fb.dbselect(value='^.username',dbtable='adm.user',lbl='User',alternatePkey='username',
                    condition='$group_code IS NULL OR :ugroup IS NULL OR $group_code=:ugroup',
                    condition_ugroup='=.user_group',hasDownArrow=True)
        fb.dbselect(value='^.pkgid',dbtable='adm.pkginfo',lbl='Pkg',hasDownArrow=True)
        fb.dbselect(value='^.tblid',dbtable='adm.tblinfo',lbl='Tbl',condition=':pkgid IS NULL OR $pkgid=:pkgid',
                    condition_pkgid='=.pkgid',hasDownArrow=True)
        th = frame.contentPane(region='center').dialogTableHandler(table='adm.user_config',
                                                            view_store_onStart=True)
        bar = th.view.top.bar.replaceSlots('addrow','newrule')
        self.newRuleButton(bar)
        rpc = bar.dataRpc(None,self.db.table('adm.user_config').newConfigRule,subscribe_new_config_rule=True)
        rpc.addCallBack("""
            frm.goToRecord(result);
            """,frm=th.form.js_form)

    def newRuleButton(self,bar):
        bar.newrule.slotButton('!!Add rule',ask=dict(title='Rule',fields=[dict(lbl='User Group',hasDownArrow=True,
                                                                    name='user_group',tag='dbselect',dbtable='adm.group'),
                                                                dict(lbl='User',hasDownArrow=True,
                                                                    name='username',tag='dbselect',dbtable='adm.user',
                                                                    alternatePkey='username',
                                                                    condition='$user_group IS NULL OR $user_group=:ugroup',
                                                                    condition_ugroup='=.user_group'), 
                                                                dict(lbl='Pkg',hasDownArrow=True,
                                                                    name='pkgid',tag='dbselect',dbtable='adm.pkginfo'),
                                                                dict(lbl='Table',
                                                                    name='tblid',tag='dbselect',dbtable='adm.tblinfo',
                                                                    condition=':pkgid IS NULL OR $pkgid=:pkgid',
                                                                    condition_pkgid='=.pkgid',hasDownArrow=True)],
                                                               ),
                                action="""
                                PUBLISH new_config_rule = {user_group:user_group,username:username,pkgid:pkgid,tblid:tblid};
        """)



