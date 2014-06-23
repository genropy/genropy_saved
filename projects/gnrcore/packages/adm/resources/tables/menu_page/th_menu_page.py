#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('label')
        r.fieldcell('filepath')
        r.fieldcell('tbl')
        r.fieldcell('pkg')

        r.fieldcell('metadata')

    def th_order(self):
        return 'label'

    def th_query(self):
        return dict(column='label', op='contains', val='')


class PagePickerView(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('label',width='100%')

    def th_sections_pkgsel(self):
        result = []
        f = self.db.table('adm.menu_page').query(columns='$pkg',distinct=True).fetch()
        if f:
            for r in f:
                pkgId = r['pkg']
                result.append(dict(code=pkgId,caption=pkgId,condition='$pkg=:cpkg',condition_cpkg=pkgId))
        else:
            result.append(dict(code='all',caption='All'))
        return result

    def th_top_upperslotbar(self,top):
        top.bar.replaceSlots('vtitle','sections@pkgsel')

class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('label')
        fb.field('filepath')
        fb.field('tbl')
        fb.field('pkg')

       #fb.textbox(value='^metadata.formResource',lbl='FormResource')
       #fb.textbox(value='^metadata.viewResource',lbl='ViewResource')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
