# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent



class TestDyinCheckbox(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome')
        r.fieldcell('province_principali_sigla')


class TestEditInlineCheckbox(BaseComponent):
    def th_struct(self,struct):

        r = struct.view().rows()
        r.fieldcell('sigla',hidden=True)
        r.fieldcell('nome')
        r.fieldcell('province_principali_sigla',edit=dict(tag='checkBoxText',table='glbl.provincia',
                                                          condition='$regione=:reg',condition_reg='^.sigla'))

    def th_options(self):
        return dict(tags=None)


class TestDyinCheckboxForm(BaseComponent):
    def th_form(self,form):
        fb = form.record.formbuilder(cols=1,border_spacing='3px')
        #fb.field('province_principali_sigla')
        fb.checkBoxText(value='^.province_principali_sigla',#values='MI:Milano,CO:Como,SO:Sondrio')
                        table='glbl.provincia',
                        condition='$regione=:reg',condition_reg='^.sigla'
                        )
