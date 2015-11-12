#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
import os

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('topics')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')


class Form(BaseComponent):
    py_requires='rst_documentation_handler:RstDocumentationHandler'
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        bc.rstHelpDrawer()
        form.htree.customizeTreeOnDrag()
        form.htree.attributes.update(getLabel="""function(node){
                            var l = genro.getData('gnr.language') || genro.locale().split('-')[1];
                            return node && node.attr?node.attr['title_'+l.toLowerCase()] || node.attr.caption:'Documentation';
            }""")
        form.dataController("tree.widget.updateLabels()",_fired='^gnr.language',_delay=1,
                            tree=form.htree)

        self.tutorial_head(bc.contentPane(region='top'))
        tc = bc.tabContainer(region='center',margin='2px',selectedPage='^gnr.language')
        tc.dataRpc('dummy',self.getTranslation,subscribe_doTranslation=True,
                    _onResult="""if(result){
                        this.setRelativeData('.content_rst_'+result.language,result.docbody);
                        this.setRelativeData('.title_'+result.language,result.doctitle);
                    }""")
        bc.translationController()
        tc.fullEditorPane(title='!!Italiano',lang='it',pageName='IT')
        tc.fullEditorPane(title='!!English',lang='en',pageName='EN')
        self.sourceEditor(bc.framePane(region='bottom',height='50%',splitter=True,drawer='open',
                            datapath='#FORM.versionsFrame'))


    def browserSource(self,struct):
        r = struct.view().rows()
        r.cell('version', name='Template', width='100%')
        r.cell('url',hidden=True)
        
    def sourceEditor(self,frame):
        bar = frame.top.slotToolbar('5,mbuttons,*,delgridrow,addrow_dlg')
        bar.mbuttons.multiButton(value='^#FORM.sourceViewMode',values='rstonly:Source Only,mixed: Mixed view,preview:Preview')
        bc = frame.center.borderContainer(design='sidebar')
        fg = bc.frameGrid(region='left',width='120px',splitter=True,margin='5px',
                            storepath='#FORM.record.sourcebag',datamode='bag',
                            struct=self.browserSource,
                            grid_selectedLabel='.selectedLabel',
                            grid_autoSelect=True,
                            grid_selected_url='#FORM.versionsFrame.selectedUrl',
                            grid_draggable_row=True,
                            grid_onDrag_versionLink="""
                            var version = dragValues.gridrow.rowdata['version'];
                            var v = "`"+version+" <javascript:localIframe('version:"+version+"')>`_";
                            dragValues['text/plain'] = v;
                            """,
                            _class='noheader buttons_grid no_over')
        fg.dataController("""
                            var l = url.split(':');
                            if(l[0]!='version'){
                                return;
                            }
                            var index = data.index(l[1]);
                            if(index>=0){
                                grid.selection.select(index);
                            }
                            """,
                            subscribe_setInLocalIframe=True,grid=fg.grid.js_widget,
                            data='=#FORM.record.sourcebag')

        center = bc.borderContainer(region='center')
        center_right = center.contentPane(region='right',overflow='hidden',splitter=True,border_left='1px solid silver',background='white')
        self.sourcePreviewIframe(center_right)
        bc.dataController("""var width = 0;
                            status = status || 'rstonly';
                             if(status=='mixed'){
                                width = '50%';
                             }else if(status=='preview'){
                                width = '100%'
                             }
                             right.style.width = width;
                             bc.setRegionVisible('right',width!=0);
                             """,
                         bc=center.js_widget,
                         status='^#FORM.sourceViewMode',
                         right=center_right.js_domNode,_onStart=True)



        bar.addrow_dlg.slotButton('!!Add custom template',iconClass='iconbox add_row',
                                    version='untitled',
                                    ask=dict(title='New version',
                                    fields=[dict(name='version',lbl='Version',validate_case='l')]),
                                    action='FIRE #FORM.versionsFrame.newVersion=version;')
        bar.delgridrow.slotButton('!!Delete selected template',iconClass='iconbox delete_row',
                                    action="""grid.publish("delrow");grid.widget.updateRowCount();""",grid=fg.grid)
        fg.dataController("""var currData = this.getRelativeData(editorDatapath);
                             currVersions.setItem(version,new gnr.GnrBag({source:currData.getItem('source'),version:version}));
                             setTimeout(function(){
                                grid.selection.select(grid.rowCount-1);
                             },1)
                                """,

                         version="^#FORM.versionsFrame.newVersion",
                          currVersions='=#FORM.record.sourcebag',
                          editorDatapath='=#FORM.versionsFrame._editorDatapath',
                          grid=fg.grid.js_widget)
        fg.grid.dataFormula("#FORM.versionsFrame._editorDatapath", "'#FORM.record.sourcebag.'+selectedLabel;",
        selectedLabel="^.selectedLabel",_if='selectedLabel',_else='"#FORM.versionsFrame.dummypath"')
        center_center = center.contentPane(region='center',datapath='^#FORM.versionsFrame._editorDatapath',margin_left='6px',margin='3px')
        center_center.codemirror(value='^.source',
                          config_mode='python',config_lineNumbers=True,
                          config_indentUnit=4,config_keyMap='softTab',
                          height='100%')
        
    def sourcePreviewIframe(self,pane):
        pane.iframe(src='^#FORM.versionsFrame.selectedUrl',height='100%',
                    width='100%',border=0)

    def tutorial_head(self,pane):
        fb = pane.formbuilder(cols=5, border_spacing='4px')
        fb.field('name',width='12em')
        fb.field('topics',width='12em',tag='checkBoxText',table='gnet.article_topic',popup=True)
        fb.field('publish_date',width='7em')
        
        fb.button('Graceful reload',action='FIRE #FORM.gracefulReload;')
        fb.dataRpc('dummy',self.gracefulReload,_fired='^#FORM.gracefulReload')
        fb.div('Old html',hidden='^.old_html?=!#v').tooltipPane().div(height='150px',width='200px',overflow='auto',_class='selectable').div('^.old_html')

    @public_method
    def gracefulReload(self):
        path = os.path.join(self.site.site_path,'root.py')
        with open(path,'r') as f:
            t = f.read()
        with open(path,'w') as f:
            f.write(t)

    def th_options(self):
        return dict(dialog_parentRatio=.9,hierarchical=True,
                    tree_columns="""$id,$name,$hierarchical_name,
                                    $hierarchical_pkey,
                                    $docbag""")


class FormPalette(Form):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.tutorial_head(bc.contentPane(region='top'))
        tc = bc.tabContainer(region='center',margin='2px',selectedPage='^gnr.language')
        tc.dataRpc('dummy',self.getTranslation,subscribe_doTranslation=True,
                    _onResult="""if(result){
                        this.setRelativeData('.content_rst_'+result.language,result.docbody);
                        this.setRelativeData('.title_'+result.language,result.doctitle);
                    }""")
        bc.translationController()
        tc.fullEditorPane(title='!!Italiano',lang='it',pageName='IT')
        tc.fullEditorPane(title='!!English',lang='en',pageName='EN')
        tc.contentPane(title='Example sources',pageName='source')

        bc.dataController("""
                this.form.goToRecord(pkey);
            """,subscribe_gnet_article_updateContest=True)

    def th_options(self):
        return dict(dialog_parentRatio=.9,hierarchical=False)
