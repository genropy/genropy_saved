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
    py_requires='rst_documentation_handler:RstDocumentationHandler,gnrcomponents/dynamicform/dynamicform:DynamicForm'
    css_requires = 'docu'
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        bc.rstHelpDrawer()
        bc.translationController()
        form.htree.customizeTreeOnDrag()
        form.htree.attributes.update(getLabel="""function(node){
                            var l = genro.getData('gnr.language') || genro.locale().split('-')[1];
                            return node && node.attr?node.attr['title_'+l.toLowerCase()] || node.attr.caption:'Documentation';
            }""")
        form.dataController("tree.widget.updateLabels()",_fired='^gnr.language',_delay=1,
                            tree=form.htree)

        self.tutorial_head(bc.contentPane(region='top'))
        frame = bc.framePane(region='center')
        frame.top.slotToolbar('*,stackButtons,*')
        sc = frame.center.stackContainer(region='center',margin='2px')
        docpage = sc.borderContainer(title='!!Documentation')
        rsttc = docpage.tabContainer(margin='2px',region='center',selectedPage='^gnr.language')
        for lang in self.db.table('docu.language').query().fetch():
            rsttc.fullEditorPane(title=lang['name'],lang=lang['code'],pageName=lang['code'])
        if self.isDeveloper():
            self.sourceEditor(docpage.framePane(region='bottom',height='50%',splitter=True,drawer='close',
                            datapath='#FORM.versionsFrame'))

        sc.contentPane(title='!!Parameters',datapath='#FORM').fieldsGrid() #ok



    def browserSource(self,struct):
        r = struct.view().rows()
        r.cell('version', name='Template', width='100%')
        r.cell('url',hidden=True)
        
    def sourceEditor(self,frame):
        bar = frame.top.slotToolbar('5,mbuttons,2,titleAsk,*,delgridrow,addrow_dlg')
        bar.mbuttons.multiButton(value='^#FORM.sourceViewMode',values='rstonly:Source Only,mixed: Mixed view,preview:Preview')
        bar.titleAsk.slotButton('!!Change version name',iconClass='iconbox tag',
                                action="""
                                if(!newname){
                                    return;
                                }
                                n = data.getNode(selectedLabel);
                                if(!n){
                                    return;
                                }
                                n.label = newname;
                                n.getValue().setItem('version',newname);
                                """,
                                data = '=#FORM.record.sourcebag',
                                selectedLabel='=.grid.selectedLabel',
                                ask=dict(title='Change name',fields=[dict(name='newname',lbl='New version name',validate_case='l')]))


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



        bar.addrow_dlg.slotButton('!!Add version',iconClass='iconbox add_row',
                                    version='==(!_currVersions || _currVersions.len()===0)?"_base_":"untitled"',
                                    _currVersions='=#FORM.record.sourcebag',
                                    ask=dict(title='New version',
                                    fields=[dict(name='version',lbl='Version',validate_case='l')]),
                                    action='FIRE #FORM.versionsFrame.newVersion=version;')
        bar.delgridrow.slotButton('!!Delete selected template',iconClass='iconbox delete_row',
                                    action="""grid.publish("delrow");grid.widget.updateRowCount();""",grid=fg.grid)
        fg.dataController("""var currData = this.getRelativeData(editorDatapath);
                              var source = currData.getItem('source');
                              if(!source){
                                 source = defaultsource;
                              }
                             currVersions.setItem(version,new gnr.GnrBag({source:source,version:version}));
                             setTimeout(function(){
                                grid.selection.select(grid.rowCount-1);
                                grid.sourceNode.setRelativeData('.selectedLabel',version);
                             },1)
                                """,
                                defaultsource= self.getDefaultSource(),
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
        pane.dataController("PUT #FORM.versionsFrame.selectedUrl = null;",_fired='^#FORM.controller.saving')

    def tutorial_head(self,pane):
        fb = pane.formbuilder(cols=4, border_spacing='4px')
        fb.field('name',width='12em')
        fb.field('topics',width='12em',tag='checkBoxText',table='docu.topic',popup=True)
        fb.field('publish_date',width='7em')
        fb.field('base_language',width='7em')
        fb.field('doctype',disabled='^.doctype')
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
        return dict(dialog_parentRatio=.9,hierarchical='open',audit=True,tree_excludeRoot=True,
                    tree__class='branchtree noIcon',
                    tree_getLabelClass="return (node.attr.child_count>0?'docfolder':'')+' doclevel_'+node.attr._record.hlevel;",
                    tree_columns="""$id,$name,$hierarchical_name,$hlevel,
                                    $hierarchical_pkey,
                                    $docbag""")
    def getDefaultSource(self):
        return """# -*- coding: UTF-8 -*-
            
class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        pass
    """
    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:        
            parentrecord = record['@parent_id'] 
            if parentrecord:
                record['doctype'] = parentrecord['doctype']

class FormPalette(Form):
    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        self.tutorial_head(bc.contentPane(region='top'))
        tc = bc.tabContainer(region='center',margin='2px',selectedPage='^gnr.language')
        bc.translationController()
        tc.fullEditorPane(title='!!Italiano',lang='it',pageName='IT')
        tc.fullEditorPane(title='!!English',lang='en',pageName='EN')
        tc.contentPane(title='Example sources',pageName='source')

        bc.dataController("""
                this.form.goToRecord(pkey);
            """,subscribe_gnet_article_updateContest=True)

    def th_options(self):
        return dict(dialog_parentRatio=.9,hierarchical=False)
