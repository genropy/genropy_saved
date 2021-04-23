#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag

class Page(BaseComponent):
    pageOptions={'openMenu':False}
    
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

        self.tutorial_head(bc.contentPane(region='top', height='70px', splitter=True))
        frame = bc.framePane(region='center')
        frame.top.slotToolbar('*,stackButtons,*')
        sc = frame.center.stackContainer(region='center',margin='2px')
        docpage = sc.borderContainer(title='!!Documentation')
        rsttc = docpage.tabContainer(margin='2px',region='center',selectedPage='^gnr.language')
        for lang in self.db.table('docu.language').query().fetch():
            rsttc.fullEditorPane(title=lang['name'],lang=lang['code'],pageName=lang['code'])
        if self.isDeveloper():
            source_footer = docpage.contentPane(region='bottom',height='50%',splitter=True,closable='close')
            self.sourceEditor(source_footer.framePane(datapath='#FORM.versionsFrame'))

        sc.contentPane(title='!!Parameters',datapath='#FORM').fieldsGrid() #ok

    
    def browserSource(self,struct):
        r = struct.view().rows()
        r.cell('version', name='Template', width='100%')
        r.cell('url',hidden=True)
        
    @extract_kwargs(source=True,preview=True)
    def sourceEditor(self,frame,theme=None,source_kwargs=None,preview_kwargs=None):
        bar = frame.top.slotToolbar('5,mbuttons,2,titleAsk,2,fbmeta,*,delgridrow,addrow_dlg')
        bar.mbuttons.multiButton(value='^#FORM.sourceViewMode',values='rstonly:Source Only,mixed: Mixed view,preview:Preview')
        bar.titleAsk.slotButton('!!Change version name',iconClass='iconbox tag',
                                action="""
 
                                n = data.getNode(selectedLabel);
                                if(!n){
                                    return;
                                }
                                if(newname){
                                    n.label = newname;
                                    n.getValue().setItem('version',newname);;
                                }
                                if(newdesc){
                                    n.getValue().setItem('description',newdesc);
                                }
                                """,
                                data = '=#FORM.record.sourcebag',
                                selectedLabel='=.grid.selectedLabel',
                                ask=dict(title='Change name',fields=[dict(name='newname',lbl='New version name',validate_case='l'),
                                                                        dict(name='newdesc',lbl='New version description')]))

        bar.dataFormula('#FORM.sourceMetaCurrentDatapath',"selectedLabel?this.absDatapath('#FORM.record.sourcebag.'+selectedLabel):'nosourcelabel';",
                        selectedLabel='^.grid.selectedLabel',sbag='=#FORM.record.sourcebag')
        bar.dataFormula(".grid.selectedLabel","null",_fired='^#FORM.controller.loading')
        bar.dataFormula(".grid.selectedLabel","sbag && sbag.len()?sbag.getNode('#0').label:null",_fired='^#FORM.controller.loaded',
                    sbag='=#FORM.record.sourcebag')

        fb = bar.fbmeta.formbuilder(cols=4,border_spacing='0',datapath='^#FORM.sourceMetaCurrentDatapath')
        fb.numberTextBox(value='^.iframe_height',width='3em',lbl='Height(px)')
        fb.numberTextBox(value='^.iframe_width',width='3em',lbl='Width(px)')
        fb.filteringSelect(value='^.source_region',width='10em',lbl='Source',
                            values='stack:Stack Demo/Source,stack_f:Stack Source/Demo,top:Top,left:Left,bottom:Bottom,right:Right')
        fb.checkbox(value='^.source_inspector',label='inspector')

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

        center = bc.borderContainer(region='center',_class='hideSplitter',border='1px solid silver',margin='4px')
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
                         right=self.sourcePreviewIframe(center).js_domNode,_onStart=True)

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
        cm = self.sourceViewerCM(center) 

    def sourceViewerCM(self,parent):
        bc = parent.borderContainer(region='center',datapath='^#FORM.versionsFrame._editorDatapath',margin_left='6px')
        cm = bc.contentPane(region='center').codemirror(value='^.source',parentForm=True,config_theme='twilight',
                          config_mode='python',config_lineNumbers=True,
                          config_indentUnit=4,config_keyMap='softTab',
                          height='100%')
        return cm
        
    def sourcePreviewIframe(self,parent):
        bc = parent.borderContainer(region='right',splitter=True,border_left='1px solid silver',background='white')
        bc.contentPane(region='center',overflow='hidden').iframe(src='^#FORM.versionsFrame.selectedUrl',src__avoid_module_cache=True,height='100%',
                    width='100%',border=0,margin='3px')
        bc.dataController("PUT #FORM.versionsFrame.selectedUrl = null;",_fired='^#FORM.controller.saving')
        return bc

    def tutorial_head(self,pane):
        fb = pane.formbuilder(cols=4, border_spacing='4px')
        fb.field('name',width='20em', colspan=2)
        fb.field('topics',width='12em',tag='checkBoxText',table='docu.topic',popup=True)
        fb.field('publish_date',width='7em')

        fb.field('base_language',width='4em')
        fb.field('revision', width='7em')
        fb.field('author', width='10em')
        fb.field('sphinx_toc')
        #fb.div('Old html',hidden='^.old_html?=!#v').tooltipPane().div(height='150px',width='200px',overflow='auto',_class='selectable').div('^.old_html')

    def th_options(self):
        return dict(dialog_parentRatio=.9,hierarchical='open',audit=True,tree_excludeRoot=True,
                    tree__class='branchtree noIcon',
                    tree_getLabelClass="return (node.attr.child_count>0?'docfolder':'')+' doclevel_'+node.attr._record.hlevel;",
                    tree_columns="""$id,$name,$hierarchical_name,$hlevel,
                                    $hierarchical_pkey,
                                    $docbag""")
    def getDefaultSource(self):
        return """# -*- coding: utf-8 -*-
            
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
        else:
            self.db.table('docu.documentation').checkSourceBagModules(record)


class GifMaker(Form):
    def sourceViewerCM(self,parent):
        pattr = parent.attributes
        pattr['border'] = None
        top = parent.contentPane(region='top',datapath='^#FORM.versionsFrame._editorDatapath',height='55px')
        fb = top.formbuilder(cols=4)
        fb.slotButton('!!Empty',action="""SET #FORM.versionsFrame.lastSelected = selectedUrl;
                                                 SET #FORM.versionsFrame.selectedUrl = null;
                                                 var lastSource = this.getRelativeData(editorDatapath+'.source');
                                                 SET #FORM.versionsFrame.lastSource = lastSource;
                                                 this.setRelativeData(editorDatapath+'.source',null);
                                                 """,
                            selectedUrl='=#FORM.versionsFrame.selectedUrl',
                            editorDatapath='=#FORM.versionsFrame._editorDatapath')
        fb.slotButton('!!Movie',fire='#FORM.sourceMovie')
        fb.slotButton('!!Run',action="""SET #FORM.versionsFrame.selectedUrl = lastSelected;""",
                                lastSelected='=#FORM.versionsFrame.lastSelected')
        fb.numberTextBox(value='^#FORM.sleepTime',width='3em',default=10,lbl='Freq.')

        
        bc = parent.borderContainer(region='center',datapath='^#FORM.versionsFrame._editorDatapath',margin_left='6px')
        cm = bc.contentPane(region='center',margin='5px',
                        ).codemirror(value='^.source',parentForm=True,config_theme='night',
                          config_mode='python',config_lineNumbers=True,
                          config_indentUnit=4,config_keyMap='softTab',
                          font_size='1.2em',
                          height='100%')
        bc.dataController("""
        var that = this;
        source = source || currSource;
        source = source.split('');
        sleepTime = sleepTime || 80;
        var currtext = [];
        this.watch('writing',function(){
            if(source.length==0){
                return true;
            }
            currtext.push(source.shift());
            cm.externalWidget.setValue(currtext.join(''));
        },function(){
            that.setRelativeData('#FORM.versionsFrame.selectedUrl',lastSelected);
            return;
        },sleepTime);
        """,source='=#FORM.versionsFrame.lastSource',_fired='^#FORM.sourceMovie',
        cm=cm,sleepTime='=#FORM.sleepTime',currSource='=.source',
        lastSelected='=#FORM.versionsFrame.lastSelected')

        return cm

    def sourcePreviewIframe(self,parent):
        bc = parent.borderContainer(region='right',width='50%')
        bc.contentPane(region='center',overflow='hidden',margin='5px',background='white').iframe(src='^#FORM.versionsFrame.selectedUrl',src__avoid_module_cache=True,height='100%',
                    width='100%',border=0,margin='3px')
        bc.dataController("PUT #FORM.versionsFrame.selectedUrl = null;",_fired='^#FORM.controller.saving')
        return bc

    def th_form(self,form):
        bc = form.center.borderContainer()
        bc.contentPane(region='center',background='RGBA(30, 48, 85, 1.00)')
        self.sourceEditor(bc.contentPane(region='bottom',height='440px',
                                        splitter=True).framePane(margin_top='5px'))


    def th_options(self):
        return dict(hierarchical=False)

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