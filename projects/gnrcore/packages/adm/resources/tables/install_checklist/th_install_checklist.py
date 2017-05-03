#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('description')
        r.fieldcell('pkg')
        r.fieldcell('check_ts')
        r.fieldcell('check_user')
        r.fieldcell('annotations')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')

class ViewChecklist(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__syscode',name='!!Code')
        r.fieldcell('name',width='15em')
        r.fieldcell('description',width='30em')
        r.fieldcell('annotations',width='30em')
        r.checkboxcolumn(field='checked',remoteUpdate=True,name='Done',width='5em')

    def th_sections_onpkg(self):
        result =[dict(code='_all_',caption='!!All')]
        for pkg in self.db.application.packages.keys():
            result.append(dict(code=pkg,caption=pkg,condition='$pkg=:cpkgid',condition_cpkgid=pkg))
        return result

    def th_sections_todo(self):
        return [dict(code='_all_',caption='!!All'),dict(code='_todo_',
                        caption='!!To do',condition="$checked IS NOT TRUE"),
                        dict(code='done',caption='!!Done',condition="$checked IS TRUE")]

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@onpkg,10,sections@todo')

    def th_order(self):
        return '__sysrecord'


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('description')
        fb.field('pkg')
        fb.field('check_ts')
        fb.field('check_user')
        fb.field('annotations')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
