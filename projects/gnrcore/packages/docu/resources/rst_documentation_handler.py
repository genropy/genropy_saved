# -*- coding: utf-8 -*-

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
            var url = '%s/'+hname;
            var txt = dragValues['text/plain'];
            dragValues['text/plain'] = '`'+txt+' <'+url+'>`_'
            """ % self.db.package('docu').htmlProcessorName())

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
        bc.roundedGroupFrame(title='Snippet',region='center',overflow='hidden').codemirror(value='^.snippet',
                                    height='100%',config_lineNumbers=True,
                                config_mode='rst',config_keyMap='softTab',
                                config_addon='search')
        bar = form.bottom.slotBar('revertbtn,*,cancel,savebtn',margin_bottom='2px',_class='slotbar_dialog_footer')
        bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
        bar.cancel.button('!!Cancel',action='this.form.abort();')
        bar.savebtn.button('!!Save',iconClass='fh_semaphore',action='this.form.publish("save",{destPkey:"*dismiss*"})')

    def rst_imageTab(self,pane):
        th = pane.attachmentGrid(pbl_classes=True,screenshot=True,design='headline')
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
    
        template_link= """ `$description <$fileurl ?download=1>`_"""
        th.view.grid.attributes.update(onDrag_rstimage="""
                                    var rowset = dragValues.gridrow.rowset;
                                    var result = [];
                                    var url = dragValues.gridrow.rowdata.fileurl;
                                    var ext = url.slice(url.lastIndexOf('.'));
                                    var tpl;
                                    if(!['.jpg','.jpag','.png','.svg','.tiff'].includes(ext)){
                                        tpl = '_tpl_link';
                                    }else{
                                        tpl = dragInfo.modifier=='Shift' ? '_tpl_figure':'_tpl_image';
                                    }
                                    tpl = dragInfo.sourceNode.attr[tpl];
                                    rowset.forEach(function(row){
                                        if(row.fileurl){
                                            result.push(dataTemplate(tpl,row));
                                        }
                                    });
                                    dragValues['text/plain'] = result.join(_lf+_lf)
                                """ ,_tpl_image=template_image,_tpl_link=template_link,
                                    _tpl_figure=template_figure)



    @struct_method
    def rst_rstHelpDrawer(self,parent,closable='close',region='right',width='300px',margin='2px',**kwargs):
        tc = parent.tabContainer(overflow='hidden',
                       closable=closable,
                       splitter=True,datapath='#FORM',region='right',width=width,**kwargs)
        self.rst_snippetTab(tc.contentPane(title='Snippet',overflow='hidden'),path=self.getResource('rst_snippets.xml',pkg='docu'))
        self.rst_imageTab(tc.contentPane(title='Attachments',overflow='hidden'))

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
        bar.lineWrapping.checkbox(value='^#FORM.lineWrapping',label='!!Line wrapping',parentForm=False)
        center = frame.center.borderContainer()
        cm = center.contentPane(region='center',overflow='hidden').codemirror(value='^.rst',
                                config_lineNumbers=True,height='100%',
                                config_mode='rst',config_keyMap='softTab',
                                lineWrapping='^#FORM.lineWrapping',
                                parentForm=True,
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
    def documentationViewer(self,pane,startpath=None,**kwargs):
        table = 'docu.documentation'
        datapath = 'docviewer_%s' %table.replace('.','_')
        pane.attributes.update(overflow='hidden')
        bc = pane.borderContainer(datapath=datapath,_anchor=True,**kwargs)
        self.dc_content(bc.framePane(region='center'))
        self.dc_left_toc(bc.contentPane(region='left',width='180px' if self.deviceScreenSize == 'phone' else '250px',splitter=True,
                            border_right='1px solid #020F20',drawer='close' if startpath else True),startpath=startpath)

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
        bar = frame.top.slotBar('doccaption,*,editrst,nav_up,nav_down,3,nav_left,nav_right,10,searchSelect,5',height='24px',
                                border_bottom='1px solid #3A4D65',toolbar=True,background='#DBDBDB')
        bar.dataController("""
            var n = tocroot.getNode(hierarchical_pkey.replace(/\//g, '.'));   
            var next_sibling_hname,prev_sibling_hname,parent_hname,first_child_hname;
            var parentNode = n.getParentNode();
            if(parentNode){
                var parentrec = parentNode.attr._record || {};
                var parentBag = parentNode.getValue('static');
                next_sibling_hname = (parentBag.getItem('#'+(parentBag.index(n.label)+1)+'?_record') || {}).hierarchical_name;
                prev_sibling_hname = (parentBag.getItem('#'+(parentBag.index(n.label)-1)+'?_record') || {}).hierarchical_name;
                parent_hname = parentrec.hierarchical_name;
            }
            if(n.attr.child_count>0){
                first_child_hname = (n.getValue().getItem('#0?_record') || {}).hierarchical_name;
            }
            SET .next_sibling_hname = next_sibling_hname;
            SET .prev_sibling_hname = prev_sibling_hname;
            SET .parent_hname = parent_hname;
            SET .first_child_hname = first_child_hname;

            """,hierarchical_pkey='^.record.hierarchical_pkey',tocroot='=.toc.root')

        bar.nav_up.slotButton('!!Parent',iconClass='iconbox arrow_up',
                            disabled='==!parent_hname',
                            action="SET .hierarchical_name=parent_hname;",
                            parent_hname='^.parent_hname')
        bar.nav_down.slotButton('!!First child',iconClass='iconbox arrow_down',
                                disabled='==!first_child_hname',
                                action='SET .hierarchical_name=first_child_hname',
                                first_child_hname='^.first_child_hname')

        bar.nav_left.slotButton('!!Prev',iconClass='iconbox arrow_left',
                                action='SET .hierarchical_name= prev_hhname || parent_hname',
                                parent_hname='^.parent_hname',
                                prev_hhname='^.prev_sibling_hname',
                                disabled='==!(prev_hhname || parent_hname)'
                                )
        bar.nav_right.slotButton('!!Next',iconClass='iconbox arrow_right',
                                action='SET .hierarchical_name = next_hhname || first_child_hname',
                                first_child_hname='^.first_child_hname',
                                next_hhname='^.next_sibling_hname',
                                disabled='==!(next_hhname || first_child_hname)')

        bar.searchSelect.textbox(value='^.searchKey',
                                    rounded=8,width='12em',placeholder='!!Search',padding='2px',padding_left='4px',
                                    onEnter=True,
                                    validate_onAccept="""if(!value){
                                        return;
                                    }
                                    var url = '/docu/index/search';
                                    var selected_language = GET gnr.language;
                                    SET .docurl = genro.addParamsToUrl(url,{text:value,selected_language:selected_language})
                                    SET .searchKey = null;""")
        bar.doccaption.lightButton('^.doccaption',hidden='^.doccaption?=!#v',
                    _class='rst_breadcrumb',
                    action="""var url;
                    if(event.shiftKey){
                        url = genro.addParamsToUrl('/docu/viewer/',{startpath:_hierarchical_name});
                    }else{
                        if(_sourcebag && _sourcebag.len()){
                            url = '/docu/viewer/'
                        }else{
                            url = '/docu/index/rst/';
                        }
                        url+=_hierarchical_name;
                    }
                    genro.openBrowserTab(url);
                    """,
                    _sourcebag='=.record.sourcebag',
                    _hierarchical_name='=.record.hierarchical_name',
                    cursor='pointer',margin_top='2px')
        bar.editrst.div().lightButton(_class='iconbox edit',_tags='_DEV_,author',
                                    action='FIRE .edit_current_record;',margin='2px')
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
                                  border_left='1px solid #3A4D65',
                                  closable=True,
                                    closable_top='20px',
                                    closable_background='transparent',
                                    closable_onclick='SET .localIframeUrl = null',
                                  closable_label='<div class="delete iconbox">&nbsp</div>',
                       closable_width='20px',closable_left='8px',closable_height='21px',
                       closable_border='0px',)
        bc.dataController("bc.setRegionVisible('right',localIframeUrl!=null)",
                bc=bc.js_widget,localIframeUrl='^.localIframeUrl',_onBuilt=True)
        pane.dataRecord('.record',table,pkey='^.pkey',
                        applymethod=self.db.table('docu.documentation').checkSourceBagModules)
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
        visitor_identifier = self.rootenv['user'] or self.rootenv['visitor_identifier']
        if visitor_identifier:
            self.dc_visitor_pane(bc.contentPane(region='bottom',closable='close',height='40px',background_color='#efefef'),visitor_identifier=visitor_identifier)
    
    def dc_visitor_pane(self,pane,visitor_identifier=None):
        pane.dataRecord('.visitor_record','docu.documentation_visit',
                        visitor_identifier=visitor_identifier,
                        documentation_id='^.pkey',ignoreMissing=True)
        pane.dataRpc(None,self.dc_updateVisitRecord,visit_record='^.visitor_record',
                    documentation_id='=.pkey',_if='documentation_id && _reason=="child"')
        fb = pane.formbuilder(datapath='.visitor_record',cols=1,float='right')
        fb.filteringSelect(value='^.visit_level',values='!!01:Quick view,02:Have questions,09:Okay',lbl='Visit')
        #fb.textbox(value='^.notes',lbl='Notes',width='20em')
    
    @public_method
    def dc_updateVisitRecord(self,visit_record=None,documentation_id=None,**kwargs):
        visitor_identifier = self.rootenv['user'] or self.rootenv['visitor_identifier']
        visit_record['visitor_identifier'] = visitor_identifier
        visit_record['documentation_id'] = documentation_id
        with self.db.table('docu.documentation_visit').recordToUpdate(visitor_identifier=visitor_identifier,
                                                                    documentation_id=documentation_id,
                                                                    insertMissing=True) as rec:
            rec['visitor_identifier'] = visitor_identifier
            rec['documentation_id'] = documentation_id
            rec['notes'] = visit_record['notes']
            rec['visit_level'] = visit_record['visit_level']
        self.db.commit()




    

            

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

    def dc_left_toc(self, pane,startpath=None):
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
        if startpath:
            treebox.dataController("SET .hierarchical_name=startpath;",_onStart=True,startpath=startpath)
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


