# -*- coding: utf-8 -*-

# th_handbook.py
# Created by Saverio Porcari.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name', name='!!Name', width='20em')
        r.fieldcell('title', name='!!Title', width='20em')
        r.fieldcell('docroot_id', name='!!Doc root', width='20em')
        r.fieldcell('language', name='!!Language', width='5')
        r.fieldcell('version', name='!!Version', width='20em')
        r.fieldcell('last_exp_ts')
        
    def th_order(self):
        return 'name'
        
    def th_query(self):
        return dict(column='title',op='contains', val='')

class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.div(margin='10px',margin_right='20px').formbuilder(cols=2,border_spacing='6px',
                                                    fld_width='100%',
                                                    max_width='1000px',
                                                    width='100%',colswidth='auto')
        fb.field('name')
        fb.br()
        fb.field('title')
        fb.field('docroot_id', hasDownArrow=True, validate_notnull=True, tag='hdbselect', folderSelectable=True)
        fb.checkBoxText(value='^.toc_roots',
                        table='docu.documentation', popup=True, cols=4,lbl='TOC roots',
                        condition='$parent_id = :docroot_id', condition_docroot_id='^.docroot_id' )


        fb.field('language')
        fb.field('version')
        fb.field('author')
        themesSn = self.site.storageNode('rsrc:pkg_docu','sphinx_env','themes')
        if themesSn.exists:
            themes = ','.join([s.basename for s in themesSn.children() if s.isdir and not s.basename.startswith('.')])
            fb.field('theme', values=themes, tag='filteringSelect')
        fb.field('sphinx_path')

        fb.field('custom_styles',tag='simpleTextArea',colspan=2,height='300px')
        example_pars_fb = top.div(margin='10px',margin_right='20px').formbuilder(cols=2,border_spacing='6px',
                                                    fld_width='100%',
                                                    max_width='700px',
                                                    width='100%',colswidth='auto',
                                                    datapath='.examples_pars',hidden='^#FORM.record.examples_site?=!#v')
    
        example_pars_fb.numberTextBox('^.default_height',width='4em',lbl='Default height')
        example_pars_fb.numberTextBox('^.default_width',width='4em',lbl='Default width')
        example_pars_fb.filteringSelect('^.source_region',width='6em',lbl='Source position',
                    values='stack:Stack Demo/Source,stack_f:Stack Source/Demo,top:Top,left:Left,bottom:Bottom,right:Right')
        example_pars_fb.textbox('^.source_theme',width='6em',lbl='Source theme')

    def th_top_exportButton(self, top):
        bar = top.bar.replaceSlots('*','*,export_button')
        bar.export_button.slotButton('Exp.To Sphinx',
                                    action="""genro.publish("table_script_run",{table:"docu.handbook",
                                                                               res_type:'action',
                                                                               resource:'export_to_sphinx',
                                                                               handbook_id: pkey});""",
                                                                               pkey='=#FORM.pkey')

    
        
               