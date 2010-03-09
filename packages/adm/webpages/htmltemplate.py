#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='adm.htmltemplate'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Html Templates'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Html Template'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('name',name='!!Name',width='20em')
        r.fieldcell('username',name='!!Username',width='10em')
        r.fieldcell('version',name='!!Version',width='20em')
        return struct

        
    def orderBase(self):
        return 'name'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%')

    def onLoading(self,record,newrecord,loadingParameters,recInfo):
        if newrecord:
            record['username'] = self.user
            record['data'] = Bag()
            record['data.main.page.height'] = 280
            record['data.main.page.width'] = 200
            record['data.main.page.top'] = 5
            record['data.main.page.bottom'] = 5
            record['data.main.page.left'] = 5
            record['data.main.page.right'] = 5
            record['data.main.design'] = 'headline'
            for i in ('top','center','bottom'):
                if i !='center':
                    record['data.layout.regions.%s' %i] = 30
                for j in ('left','right'):
                    path = '%s.regions.%s'  %(i,j)
                    record['data.layout.%s' %path] = 30
                    
############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        bc.css('.printRegion','margin:.5mm;border:.3mm dotted silver;cursor:pointer;')
        bc.data('zoomFactor',.7)
        self.editorDialog(bc)
        self.controllers(bc)
        self.mainInfo(bc.borderContainer(region='left',width='30em',disabled=disabled))
        editorBc = bc.borderContainer(region='center',overflow='auto',datapath='_temp.mockup')
        self.ajaxContent('printLayout',editorBc ,design='^form.record.data.main.design')

    def remote_printLayout(self,parentBc,design=None,**kwargs):
        
        page = parentBc.borderContainer(region='center',
                                        height='^.main.page.height',
                                        width='^.main.page.width',
                                        border='1px solid gray',style="""
                                                                    background-color:white;
                                                                    -moz-box-shadow:8px 8px 15px gray;
	                                                                -webkit-box-shadow:8px 8px 15px gray;
                                                                    """,
                                        zoomFactor='^zoomFactor',margin='10px')   
        bc = page.borderContainer(region='center',
                                    margin_top='^.main.page.top',
                                    margin_bottom='^.main.page.bottom',
                                    margin_left='^.main.page.left',
                                    margin_right='^.main.page.right',
                          connect_ondblclick="""
                                    var clickedNode = dijit.getEnclosingWidget($1.originalTarget).sourceNode;
                                    SET currentEditedArea = clickedNode.absDatapath();
                                    FIRE #editorDialog.open;
                                """,
                          _class='hideSplitter',
                           regions='^.layout.regions',
                          design=design
                          )
        if design=='sidebar':
            self._sidebarRegions(bc.borderContainer(region='left',width='50mm',splitter=True,datapath='.layout.left',
                                                _class='hideSplitter',regions='^.regions'
                                                ),'50mm')
            self._sidebarRegions(bc.borderContainer(region='right',datapath='.layout.right',width='50mm',
                                                    splitter=True,_class='hideSplitter',
                                                       regions='^.regions'
                                                        ),'50mm')
            self._sidebarRegions(bc.borderContainer(region='center',datapath='.layout.center',_class='hideSplitter'),'25mm')
        else:
            self._headlineRegions(bc.borderContainer(region='top',height='^_temp.mockup.layout.regions.top',splitter=True,
                                                    _class='hideSplitter',datapath='.layout.top',
                                                   regions='^.regions'
                                                    ),'50mm')
            self._headlineRegions(bc.borderContainer(region='bottom',datapath='.layout.bottom',
                                                        height='^_temp.mockup.layout.regions.bottom',
                                                        splitter=True,_class='hideSplitter',
                                                        regions='^.regions'
                                                        ),'50mm')
            self._headlineRegions(bc.borderContainer(region='center',_class='hideSplitter',datapath='.layout.center'),'25mm')

    def _sidebarRegions(self,bc,height):
        
        bc.contentPane(region='top',height=height,_class='printRegion sideTop',
                        splitter=True,datapath='.top').div(innerHTML='^.html')
        bc.contentPane(region='bottom',height=height,_class='printRegion sideBottom',
                        splitter=True,datapath='.bottom').div(innerHTML='^.html')
        bc.contentPane(region='center',_class='printRegion sideCenter',
                        datapath='.center').div(innerHTML='^.html')
        
    def _headlineRegions(self,bc,width):
        bc.contentPane(region='left',width=width,_class='printRegion headLeft',splitter=True, 
                        datapath='.left').div(innerHTML='^.html')
        bc.contentPane(region='right',width=width,_class='printRegion headRight',splitter=True,
                        datapath='.right').div(innerHTML='^.html')
        bc.contentPane(region='center',_class='printRegion headCenter',
                        datapath='.center').div(innerHTML='^.html')


    def controllers(self,pane):
        for part in ('height','width','top','bottom','left','right'):
            pane.dataFormula("_temp.mockup.main.page.%s" %part, "part+'mm';",part='^.data.main.page.%s' %part)
        pane.dataFormula("_temp.mockup.main.design", "design",design="^.data.main.design")
            
    def editorDialog(self,pane):
        def cb_bottom(bc,**kwargs):
            bottom = bc.contentPane(**kwargs)
            bottom.button('!!Close',baseClass='bottom_btn',float='right',margin='1px',fire='.close')
        self.simpleDialog(pane,height='300px',width='700px',dlgId='editorDialog',cb_bottom=cb_bottom,
                            cb_center=self.templateEditorPane,datapath='editorDialog')
    def templateEditorPane(self,parentBc,**kwargs):
        bc = parentBc.borderContainer(datapath='^currentEditedArea',**kwargs)
        self.RichTextEditor(bc, value='^.html', contentPars=dict(region='center'),
                            nodeId='htmlEditor',editorHeight='200px')
        
    def mainInfo(self,bc,disabled=False):
        top = bc.contentPane(region='top',height='18ex',margin='5px',_class='pbl_roundedGroup')
        top.div('!!Info',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(cols=1, border_spacing='4px',disabled=disabled)
        fb.field('name',width='15em')
        fb.field('version',width='15em')
        bottom = bc.contentPane(region='bottom',margin='5px',margin_top='0',
                                _class='pbl_roundedGroupBottom')
        bottom.horizontalSlider(value='^zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True,width='15em',float='right') 
        self.layoutMainInfo(bc.borderContainer(region='center',margin='5px',margin_top='0',_class='pbl_roundedGroup',
                                datapath='.data'),disabled=disabled)

    
    def layoutMainInfo(self,bc,disabled=None):
        topTC = bc.tabContainer(region='top',height='50%',selectedPage='^.main.design')
        self.headLineOpt(topTC.contentPane(title='Headline',pageName='headline'))
        self.sideBarOpt(topTC.contentPane(title='Sidebar',pageName='sidebar'))
        
        center = bc.contentPane(region='center',datapath='.main.page')
        fb = center.formbuilder(cols=2, border_spacing='4px',disabled=disabled)
        fb.numbertextBox(value='^.height',lbl='!!Height',width='5em')
        fb.numbertextBox(value='^.width',lbl='!!Width',width='5em')
        fb.numbertextBox(value='^.top',lbl='!!Top',width='5em')
        fb.numbertextBox(value='^.bottom',lbl='!!Bottom',width='5em')
        fb.numbertextBox(value='^.left',lbl='!!Left',width='5em')
        fb.numbertextBox(value='^.right',lbl='!!Right',width='5em')
        
    def headLineOpt(self,pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px',datapath='.layout')
        for i in ('top','center','bottom'):
            if i != 'center':
                fb.numbertextBox(lbl='!!%s height' %i.title(),width='4em')
                fb.dataController("SET _temp.mockup.layout.%s.regions = val+'mm';" %i ,
                                    val="^.regions.%s" %i,
                                    _fired='^gnr.forms.formPane.loaded')
            else:
                fb.div()
            for j in ('left','right'):
                path = '%s.regions.%s'  %(i,j)
                fb.numberTextbox(value='^.%s' %path,
                                lbl='!!%s' %j.title(),
                                width='5em',validate_onAccept="if(userChange){SET _temp.mockup.layout.%s = value+'mm';}" %path)
                fb.dataController("SET _temp.mockup.layout.%s = val+'mm';" %path ,val="=.%s" %path,_if='val',
                                _fired='^gnr.forms.formPane.loaded')
               #fb.dataController("console.log(val);SET .%s = parseFloat(val.slice(0,-2))*.2" %path,
               #                    val="^_temp.mockup.layout.%s" %path,_if='val')
                
    def sideBarOpt(self,pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px',datapath='.layout')
        for i in ('left','center','right'):
            for j in ('top','bottom'):
                fb.numberTextbox(value='^.%s.regions.%s' %(i,j),lbl='!!%s %s'%(i.title(),j.title()),width='5em')

        