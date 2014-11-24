# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import metadata

class ViewTestSections(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em',sortable=False)
        r.fieldcell('regione',width='100%')

    def th_order(self):
        return 'nome'

    def th_query(self):
        return dict(column='nome',op='contains', val='')


    def th_sections_zone(self):
        return [dict(code='nord',caption='!!Nord',condition='@regione.zona=:zona',condition_zona='Nord'),
                dict(code='centro',caption='!!Centro',condition='@regione.zona=:zona',condition_zona='Centro'),
                dict(code='sud',caption='!!Sud',condition='@regione.zona=:zona',condition_zona='Sud'),
                dict(code='isole',caption='!!Isole',condition='@regione.zona=:zona',condition_zona='Isole')
                ]

    @metadata(_if='zone == "nord"',_if_zone='^.zone.current')
    def th_sections_nordtest(self):
        return [dict(code='veneto',condition='$regione=:reg',condition_reg='VEN',
                    caption='Veneto',content_color='red'),dict(code='altro',caption='Altro')]


    def th_top_custom(self,top):
        top.bar.replaceSlots('#','searchOn,sections@zone,*,sections@nordtest')

    def th_options(self):
        return dict(virtualStore=False)