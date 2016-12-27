# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import metadata,public_method


class TestViewVotoRadio(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('denominazione', width='20em'#,edit=True
            )
        r.fieldcell('popolazione_residente', width='10em',#,edit=True,
            name='Popolazione')
        r.checkboxcolumn('voto_si',#radioButton=True,
            remoteUpdate=True,
            columnset='voto',name=u'Sì',width='4em')
        r.checkboxcolumn('voto_no',#radioButton=True,
            columnset='voto',name='No',width='4em',
            remoteUpdate=True)
        r.checkboxcolumn('voto_astenuto',#radioButton=True,
            columnset='voto',name='Ast.',width='4em',
            remoteUpdate=True)

    def th_order(self):
        return 'denominazione'
    def th_options(self):
        return dict(columnset_voto='Votazione')
