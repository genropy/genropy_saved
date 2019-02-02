#!/usr/bin/python
# -*- coding: utf-8 -*-

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
    def th_hiddencolumns(self):
        return '$__syscode,$name,$description,$annotations,$doc_url,$pkg'
    def th_struct(self,struct):
        r = struct.view().rows()
        r.checkboxcolumn(field='checked',remoteUpdate=True,name='Done',width='5em')
        r.cell('tpl',rowTemplate="""<div style="font-weight:bold">$pkg: $name</div>
                                    <div style="font-size:.9em;">$description</div>
                                    <div style="font-size:.9em;color:red;">$annotations</div>""",
                                    width='30em',cellClasses='tplcell',
                                    #edit=dict(fields=[dict(field='annotations',tag='simpleTextArea',height='40px')]),
                                    calculated=True)

    def th_sections_onpkg(self):
        result =[dict(code='_all_',caption='!!All')]
        f = self.db.table('adm.install_checklist').query(columns='$pkg',addPkeyColumn=False,distinct=True).fetch()
        f = [r['pkg'] for r in f]
        for pkg in list(self.db.application.packages.keys()):
            if pkg in f:
                result.append(dict(code=pkg,caption=pkg,condition='$pkg=:cpkgid',condition_cpkgid=pkg))
        return result

    def th_sections_todo(self):
        return [dict(code='_all_',caption='!!All'),dict(code='_todo_',
                        caption='!!To do',condition="$checked IS NOT TRUE"),
                        dict(code='done',caption='!!Done',condition="$checked IS TRUE")]

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@onpkg,10,sections@todo')

    def th_order(self):
        return '__syscode'


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
