# -*- coding: UTF-8 -*-

"""
examplehandler.py
Created by Giovanni Porcari on 2010-08-09.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class RstDocumentationHandler(BaseComponent):
    py_requires='gnrcomponents/attachmanager/attachmanager:AttachManager'
    @struct_method
    def rst_customizeTreeOnDrag(self,tree):
        tree.attributes.update(onDrag_linkPrepare="""
            var hname = treeItem.attr._record['hierarchical_name'];
            var url = '/docu/index/rst/'+hname;
            var txt = dragValues['text/plain'];
            dragValues['text/plain'] = '`'+txt+' <'+url+'>`_'
            """ )

    def rst_snippetTab(self,pane,path=None):
        pane.data('#FORM.snippetEditor.data',Bag(path))
        def struct(struct):
            r = struct.view().rows()
            r.cell('name',width='15em',name='Name')
            r.cell('snippet',hidden=True)
        slots='2,vtitle,*,searchOn,5,delrow,addrow,10' if self.isDeveloper() else '2,vtitle,*,searchOn,2'
        view = pane.bagGrid(frameCode='snippetEditor',
                            storepath='#FORM.snippetEditor.data',datapath='#FORM.snippetEditor',struct=struct,
                            grid_draggable_row=True,
                            grid_onDrag_snippet="""
                                    var rowset = dragValues.gridrow.rowset;
                                    var result = [];
                                    rowset.forEach(function(row){
                                                                if(row.snippet){
                                                                    result.push(row.snippet);
                                                                }
                                                          });
                                    dragValues['text/plain'] = result.join(_lf+_lf)
                                """,
                        pbl_classes='*',slots=slots,
                        title='Snippets',
                        margin='2px')
        if self.isDeveloper():
            form = view.grid.linkedForm(frameCode='snippetEditor_form',
                                 datapath='#FORM.snippetEditor.form',loadEvent='onRowDblClick',
                                 dialog_height='300px',dialog_width='400px',
                                 dialog_title='Snippet',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='memory',store_pkeyField='snippet_code')
            self.rst_snipped_form(form)
            pane.dataRpc('dummy',self.rst_updateRstSnippets,newdata='^#FORM.snippetEditor.data',snippetpath=path,_delay=500)
        return view

    @public_method
    def rst_updateRstSnippets(self,newdata=None,snippetpath=None):
        newdata.walk(lambda n: n.setAttr({}))
        newdata.toXml(snippetpath,typevalue=False,pretty=True)


    def rst_snipped_form(self,form,folders=None):
        bc = form.center.borderContainer(datapath='.record')
        bc.dataFormula('.snippet_code',"name?flattenString(name,['.',' ','(',')','=','%']).toLowerCase():null",name='^.name')
        fb = bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Name',validate_notnull=True)
        bc.roundedGroupFrame(title='Snippet',region='center',overflow='hidden').codemirror(value='^.snippet',lbl='Snippet',
                                    height='100%',config_lineNumbers=True,
                                config_mode='rst',config_keyMap='softTab',
                                config_addon='search')
        bar = form.bottom.slotBar('revertbtn,*,cancel,savebtn',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
        bar.cancel.button('!!Cancel',action='this.form.abort();')
        bar.savebtn.button('!!Save',iconClass='fh_semaphore',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def rst_imageTab(self,pane):
        th = pane.attachmentGrid(pbl_classes=True,screenshot=True,
                                                                    design='headline')
        template_image = """.. image:: $fileurl
    :width: 100px
    :align: center
    :height: 100px"""
        template_figure= """.. figure:: stars.jpg
    :width: 200px
    :align: center
    :height: 100px
    :figclass: align-center

    $description"""
        th.view.grid.attributes.update(onDrag_rstimage="""
                                                          var rowset = dragValues.gridrow.rowset;
                                                          var result = [];
                                                          var tpl = dragInfo.sourceNode.attr[dragInfo.modifier=='Shift' ? '_tpl_figure':'_tpl_image'];
                                                          rowset.forEach(function(row){
                                                                if(row.fileurl){
                                                                    result.push(dataTemplate(tpl,row));
                                                                }
                                                          });
                                                          dragValues['text/plain'] = result.join(_lf+_lf)
                                                        """ ,_tpl_image=template_image,
                                                            _tpl_figure=template_figure)



    @struct_method
    def rst_rstHelpDrawer(self,parent,drawer='close',region='right',width='300px',margin='2px',**kwargs):
        tc = parent.tabContainer(overflow='hidden',
                       drawer='close',
                       splitter=True,datapath='#FORM',region='right',width=width,**kwargs)
        self.rst_snippetTab(tc.contentPane(title='Snippet',overflow='hidden'),path=self.getResource('rst_snippets.xml'))
        self.rst_imageTab(tc.contentPane(title='Images',overflow='hidden'))

    @struct_method
    def rst_translationController(self,pane):
        pane.dataRpc('dummy',self.rst_getTranslation,subscribe_doTranslation=True,
                    base_language='=#FORM.record.base_language',
                    _onResult="""if(result){
                        this.setRelativeData('#FORM.record.docbag.'+result.language+'.rst',result.docbody);
                        this.setRelativeData('#FORM.record.docbag.'+result.language+'.title',result.doctitle);
                    }""")



    @struct_method
    def rst_fullEditorPane(self,parent,lang=None,datapath=None,**kwargs):
        lang = lang.lower()
        bc = parent.borderContainer(datapath='#FORM.record.docbag.%s' %lang,**kwargs)
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.textbox('^.title',width='30em',lbl='!!Title')
        bc.editorFrame(region='center',lang=lang)

    @struct_method
    def rst_editorFrame(self,pane,lang=None,**kwargs):
        lang = lang.lower()
        frame = pane.framePane('content_%s' %lang,**kwargs)
        bar = frame.top.slotToolbar('5,rstdocbuttons,30,quoteMenu,3,lineWrapping,*,autotranslate,5')
        bar.rstdocbuttons.multiButton(value='^#FORM.docbuttons_%s' %lang,values='rstonly:RST Only,mixed: Mixed view,preview:Preview')
        bar.autotranslate.slotButton('=="Translate from "+(_base_language || "it");',_base_language='=#FORM.record.base_language',
            action="""_base_language = _base_language || 'it';
                        var docbody = this.getRelativeData('#FORM.record.docbag.'+_base_language+'.rst');
                        var doctitle = this.getRelativeData('#FORM.record.docbag.'+_base_language+'.title');
                        PUBLISH doTranslation = {to_language:to_language,docbody:docbody,doctitle:doctitle};""", 
                        to_language=lang,
            hidden='^.rst')
        bar.lineWrapping.checkbox(value='^#FORM.lineWrapping',label='!!Line wrapping')
        center = frame.center.borderContainer()
        cm = center.contentPane(region='center',overflow='hidden').codemirror(value='^.rst',
                                config_lineNumbers=True,height='100%',
                                config_mode='rst',config_keyMap='softTab',
                                lineWrapping='^#FORM.lineWrapping',
                                config_addon='search')
        menu = bar.quoteMenu.dropDownButton('!!Quote').menu()
        menu.menuLine('[tr-off]text[tr-on]',action='this.getAttributeFromDatasource("cm").externalWidget.gnr_quoteSelection("[tr-off]","[tr-on]");',cm=cm)
        menu.menuLine('``text``',action='this.getAttributeFromDatasource("cm").externalWidget.gnr_quoteSelection("``","``");',cm=cm)
        menu.menuLine('*text*',action='this.getAttributeFromDatasource("cm").externalWidget.gnr_quoteSelection("*","*");',cm=cm)
        menu.menuLine('**text**',action='this.getAttributeFromDatasource("cm").externalWidget.gnr_quoteSelection("**","**");',cm=cm)

        right = center.contentPane(region='right',overflow='hidden',splitter=True,border_left='1px solid silver',background='white')
        pane.dataController("""var width = 0;
                            status = status || 'rstonly';
                             if(status=='mixed'){
                                width = '50%';
                             }else if(status=='preview'){
                                width = '100%'
                             }
                             right.style.width = width;
                             bc.setRegionVisible('right',width!=0);
                             """,
                         bc=center.js_widget,status='^#FORM.docbuttons_%s' %lang,right=right.js_domNode,_onStart=True)
        right.renderedIframe(value='^.rst',height='100%',width='100%',border=0)
        return frame

    @struct_method
    def rst_renderedIframe(self,pane,value=None,**kwargs):
        iframe = pane.div(_class='scroll-wrapper').htmliframe(**kwargs)
        js_script_url = self.site.getStaticUrl('rsrc:common','localiframe.js',nocache=True)
        pane.dataRpc('dummy',self.getPreviewRst2html,
                    rstdoc=value,
                    _delay=500,
                    _if='rstdoc',
                    _else=""" _iframe.contentWindow.document.body.innerHTML ="<div class='document'>To do...</div>" """,
                    _onResult="""
                        var cw = kwargs._iframe.contentWindow;
                        var cw_body = cw.document.body;

                        var s = cw.document.createElement("script");
                        s.type = "text/javascript";
                        s.src = '%s';
                        cw.document.getElementsByTagName("head")[0].appendChild(s);
                        if(genro.isMobile){
                            cw_body.classList.add('touchDevice');
                        }
                        cw_body.classList.add('bodySize_'+genro.deviceScreenSize);

                        cw_body.innerHTML = result;
                    """ %js_script_url,
                    _iframe=iframe.js_domNode)

    @public_method
    def getPreviewRst2html(self,rstdoc=None,**kwargs):
        if rstdoc:
            return self.site.getService('rst2html')(rstdoc,**kwargs)
        return ''

    @public_method
    def rst_getTranslation(self,docbody=None,doctitle=None,to_language=None,base_language=None,**kwargs):
        if docbody or doctitle:
            tr = self.getService('translation')
            base_language = base_language or 'it'
            docbody = docbody or doctitle
            return dict(docbody=tr.translate(docbody,to_language=to_language,from_language=base_language) if docbody else None,
                        doctitle=tr.translate(doctitle,to_language=to_language,from_language=base_language) if doctitle else None,
                        language=to_language)


class DocumentationViewer(BaseComponent):
    py_requires = 'th/th:TableHandler,rst_documentation_handler:RstDocumentationHandler'
    css_requires = 'docu'
    @public_method
    def documentationViewer(self,pane,**kwargs):
        table = 'docu.documentation'
        datapath = 'docviewer_%s' %table.replace('.','_')
        pane.attributes.update(overflow='hidden')
        bc = pane.borderContainer(datapath=datapath,_anchor=True,**kwargs)
        self.dc_content(bc.framePane(region='center'))
        self.dc_left_toc(bc.contentPane(region='left',width='180px' if self.deviceScreenSize == 'phone' else '250px',splitter=True,
                            border_right='1px solid #020F20',drawer=True))

    def dc_content(self,frame):
        table = 'docu.documentation'
        frame.dataController("""var lang = language?language.toLowerCase():'en';
                            SET .doccaption = lang=='it'? hierarchical_title_it:hierarchical_title_en;
                            SET .docurl = '/docu/index/rst/'+hierarchical_name+'?selected_language='+language;
                            """ , 
                            hierarchical_name='^.hierarchical_name',
                            hierarchical_title_it='^.hierarchical_title.it',
                            hierarchical_title_en='^.hierarchical_title.en',
                            language='^gnr.language',
                            _delay=1)
        bar = frame.top.slotBar('doccaption,*,editrst,5',height='18px',
                                border_bottom='1px solid #3A4D65')
        bar.doccaption.lightButton('^.doccaption',hidden='^.doccaption?=!#v',
                    _class='rst_breadcrumb',
                    action="""var url;
                    if(_sourcebag && _sourcebag.len()){
                        url = '/docu/viewer/'
                    }else{
                        url = '/docu/index/rst/';
                    }
                    url+=_hierarchical_name;
                    genro.openWindow(url);""",
                    _sourcebag='=.record.sourcebag',
                    _hierarchical_name='=.record.hierarchical_name',
                    cursor='pointer')
        bar.editrst.div().lightButton(_class='iconbox edit',_tags='_DEV_,author',
                                    action='FIRE .edit_current_record;')
        bc = frame.center.borderContainer()
        wrapper = bc.contentPane(overflow='hidden',region='center').div(_class='scroll-wrapper')
        wrapper.data('.docurl','')
        wrapper.htmliframe(src='^.docurl',height='100%',width='100%',border=0,
                            connect_onload="""
                            var cw = this.domNode.contentWindow;
                            if(genro.isMobile){
                                cw.document.body.classList.add('touchDevice');
                            }
                            cw.document.body.classList.add('bodySize_'+genro.deviceScreenSize);
                            if(this.domNode.getAttribute('src')=='null'){
                                //emptylink
                                return;
                            }
                            SET .loadedUrl = this.domNode.contentWindow.location.pathname;""")
        pane = bc.contentPane(region='right',width='50%',splitter=True,
                                  overflow='hidden',
                                  border_left='1px solid #3A4D65')
        bc.dataController("bc.setRegionVisible('right',localIframeUrl!=null)",
                bc=bc.js_widget,localIframeUrl='^.localIframeUrl',_onBuilt=True)
        pane.dataRecord('.record',table,pkey='^.pkey',applymethod=self.db.table('docu.documentation').checkSourceBagModules)
        pane.dataFormula('.localIframeUrl','sourcebag.len()==1?sourcebag.getItem("_base_.url"):null',
                    sourcebag='^.record.sourcebag')
        pane.dataController("""
                        var l = url.split(':');
                        var urlToSet;
                        if(l[0]=='version'){
                            var versionRow = data.getItem(l[1]);
                            if(versionRow){
                                urlToSet = versionRow.getItem('url');
                            }else{
                                urlToSet = null;
                            }

                        }else{
                            urlToSet = l[1];
                        }
                        SET .localIframeUrl = urlToSet;
                        """,
                        subscribe_setInLocalIframe=True,
                        data='=.record.sourcebag')
        pane.iframe(src='^.localIframeUrl',src__source_viewer=True,height='100%',width='100%',border=0)

    @public_method
    def dc_path_hierarchical_name(self,hierarchical_name=None,**kwargs):
        if hierarchical_name:
            hierarchical_name = hierarchical_name.strip('/')
        else:
            return
        hierarchical_pkey =  self.db.table('docu.documentation').readColumns(columns='$hierarchical_pkey',where='$hierarchical_name=:hname',
                    hname=hierarchical_name)
        path = hierarchical_pkey.replace('/','.') if hierarchical_pkey else 'root'
        return path 

    def dc_left_toc(self, pane):
        table = 'docu.documentation'
        treebox = pane.div(margin_top='10px',margin_left='2px')
        tree = treebox.hTableTree(storepath='.toc', hideValues=True, 
                inspect='shift',table=table,
                condition='$is_published',
                store__onBuilt=True,
                openOnClick='*',
                isTree=False,excludeRoot=True, 
                draggable=self.application.checkResourcePermission('_DEV_,author', self.userTags),
                selected_pkey='.pkey',
                columns="""$id,$name,$hierarchical_name,
                            $hierarchical_pkey,
                            $docbag,$hlevel""",
                selfsubscribe_onSelected="""
                  var n = $1.item;
                  var rec = $1.item.attr._record;
                  SET .hierarchical_name = rec.hierarchical_name;
                  var htitles= {};
                  var tdict,curchunk;
                  while(n){
                     tdict = objectExtract(n.attr,'title_*',true);
                     for(var t in tdict){
                        curchunk = tdict[t] || n.attr.caption
                        htitles[t] = htitles[t]?curchunk+'/'+htitles[t]:curchunk;
                     }
                     n = n.getParentNode();
                  }
                  var that = this;
                  for(var t in htitles){
                    that.setRelativeData('.hierarchical_title.'+t,htitles[t]);
                  }
                """,
                selectedLabelClass='branchtree_selected',
                getLabelClass="return (node.attr.child_count>0?'docfolder':'')+' doclevel_'+node.attr._record.hlevel;",
                _class="branchtree docuTree treeLongLabels noIcon",
                      getLabel="""function(node){
                          var l = genro.getData('gnr.language') || genro.locale().split('-')[1];
                          return node.attr['title_'+l.toLowerCase()] || node.attr.caption;
                      }""",
                      font_size='12px',color='#666',line_height='15px',
                moveTreeNode=False,margin_left='5px')
        tree.customizeTreeOnDrag()
        first_selected = self.db.table(table).query(limit=1).fetch()
        treebox.dataController("""var startpath = first_selected.replace(/\//g,'.');
                                tree.widget.setSelectedPath(null,{value:startpath});""",first_selected=first_selected[0]['hierarchical_pkey'],tree=tree,_onBuilt=1)
        treebox.dataController("""
                PUT .docurl = loadedUrl;
                var loaded_hierarchical_name = loadedUrl.replace('/docu/index/rst/','');
                var path = genro.serverCall(rpcmethod,{hierarchical_name:loaded_hierarchical_name});
                tree.widget.setSelectedPath(null,{value:path});
            """,
            loadedUrl='^.loadedUrl',
            docurl='=.docurl',
            _if='loadedUrl!=docurl',
            rpcmethod=self.dc_path_hierarchical_name,
            tree=tree)
        treebox.dataController("tree.widget.updateLabels()",_fired='^gnr.language',_delay=1,tree=tree)
        treebox.dataController("""
            var that = this;
            var onSavedCb = function(){
                that.setRelativeData('.docurl',null);
                that.setRelativeData('.docurl',currurl);
            };
            genro.dlg.zoomPalette({height:'600px',width:'700px',table:table,pkey:pkey,
                                      formResource:'FormPalette',main_call:'main_form',
                                      onSavedCb:onSavedCb,top:'30px',right:'40px'});
            """,table=table,edit_current_record='^.edit_current_record',
                                pkey='=.pkey',currurl='=.docurl')
        treebox.dataController("""
                            genro.publish({topic:tablecode+'_updateContest',iframe:'*'},{pkey:pkey});""",
                            pkey='^.pkey',tablecode=table.replace('.','_'))


