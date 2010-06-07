#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    saveAlways=True
    maintable='adm.htmltemplate'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView,foundation/macrowidgets:RichTextEditor'

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
                    record.setItem('data.layout.%s' %i,None,height=30)
                for j in ('left','right'):
                    path = '%s.%s'  %(i,j)
                    record.setItem('data.layout.%s' %path,None,width= 30)
                    
            for i in ('left','center','right'):
                if i !='center':
                    record.setItem('data.layout.%s' %i,None,width=30)
                for j in ('top','bottom'):
                    path = '%s.%s'  %(i,j)
                    record.setItem('data.layout.%s' %path,None,height= 30)
                    
############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        bc.css('.printRegion','margin:.5mm;border:.3mm dotted silver;cursor:pointer;')
        bc.data('zoomFactor',.5)
        #self.editorDialog(bc)
        self.controllers(bc)
        self.mainInfo(bc.borderContainer(region='left',width='50em',splitter=True,disabled=disabled))
        bc.borderContainer(region='center',overflow='auto',datapath='_temp.data').remote('printLayout',
                                                                                            design='^form.record.data.main.design',
                                                                                            lazy=False)

    def remote_printLayout(self,parentBc,design=None,**kwargs):
        design = design or 'headline'
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
                          connect_onclick="""
                                    var clickedNode = dijit.getEnclosingWidget($1.target).sourceNode;
                                    SET currentEditedArea = clickedNode.absDatapath();
                                """,
                          _class='hideSplitter',
                           regions='^_temp.data.layout.regions',
                          design=design
                          )
        regions=dict(headline=('top','bottom','center'),sidebar=('left','right','center'))
        for region in regions[design]:
            self._subRegions(bc,region=region,design=design,)

    def _subRegions(self,parentBc,region=None,design=None):
        subregions=dict(sidebar=('top','bottom','center'),headline=('left','right','center'))
        bc = parentBc.borderContainer(region=region,splitter=(region!='center'),
                            _class='hideSplitter',datapath='.layout.%s' %region,
                            regions='^.regions')
        for subregion in subregions[design]:
            bc.contentPane(region=subregion,_class='printRegion',splitter=(subregion!='center'),
                            datapath='form.record.data.layout.%s.%s'%(region,subregion)).div(innerHTML='^.html')

    def controllers(self,pane):
        for part in ('height','width','top','bottom','left','right'):
            pane.dataFormula("_temp.data.main.page.%s" %part, "part+'mm';",part='^.data.main.page.%s' %part)
        pane.dataFormula("_temp.data.main.design", "design",design="^.data.main.design")
       
    def mainInfo(self,bc,disabled=False):
        editorPane = bc.borderContainer(datapath='^currentEditedArea',region='bottom',height='320px')
        self.RichTextEditor(editorPane, value='^.html', contentPars=dict(region='center'),
                            nodeId='htmlEditor',editorHeight='200px',toolbar=self.rte_toolbar_standard())
                            
        mainBc = bc.borderContainer(region='center',margin='5px',_class='pbl_roundedGroup',)
        topleft = mainBc.borderContainer(region='left',width='20em')
        self.tplInfo(topleft.contentPane(region='top'),disabled=disabled)
        bottom = mainBc.contentPane(region='bottom',margin='5px',margin_top='0',
                                _class='pbl_roundedGroupBottom')
        bottom.horizontalSlider(value='^zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True,width='15em',float='right')
        self.basePageParams(topleft.contentPane(region='center',datapath='.data.main.page'),disabled=disabled)
        topTC = mainBc.tabContainer(region='center',selectedPage='^.data.main.design')
        self.headLineOpt(topTC.contentPane(title='Headline',pageName='headline'))
        self.sideBarOpt(topTC.contentPane(title='Sidebar',pageName='sidebar'))

        
    def tplInfo(self,pane,disabled=None):
        pane.div('!!Info',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, border_spacing='4px',disabled=disabled)
        fb.field('name',width='15em')
        fb.field('version',width='15em')
 
    def basePageParams(self,pane,disabled=None):
        fb = pane.formbuilder(cols=2, border_spacing='4px',disabled=disabled)
        fb.numbertextBox(value='^.height',lbl='!!Height',width='5em')
        fb.numbertextBox(value='^.width',lbl='!!Width',width='5em')
        fb.numbertextBox(value='^.top',lbl='!!Top',width='5em')
        fb.numbertextBox(value='^.bottom',lbl='!!Bottom',width='5em')
        fb.numbertextBox(value='^.left',lbl='!!Left',width='5em')
        fb.numbertextBox(value='^.right',lbl='!!Right',width='5em')
        
    def headLineOpt(self,pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px',datapath='.data.layout')
        for i in ('top','center','bottom'):
            if i != 'center':
                fb.numbertextBox(value='^.%s?height' %i,lbl='!!%s height' %i.title(),
                                width='4em')
                fb.dataController("""genro.setData("_temp.data.layout.regions.%s",
                                                      parseInt((val||0)*3.779527559)+'px',
                                                      {show:val!=0});"""%i,
                                    val="^.%s?height" %i)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s?height = dojo.number.round(parseFloat(heightpx.slice(0,-2))/3.779527559,2);}" %i,
                                    heightpx="^_temp.data.layout.regions.%s" %i)
            else:
                fb.div()
            for j in ('left','right'):
                data_path = '%s.%s?width' %(i,j)
                temp_path = '%s.regions.%s'  %(i,j)
                fb.numberTextbox(value='^.%s' %data_path,
                                lbl='!!%s' %j.title(),
                                width='5em')
                fb.dataController("""genro.setData('_temp.data.layout.%s',
                                                    parseInt((val||0)*3.779527559)+'px',
                                                    {show:val!=0});""" %temp_path ,
                                  val="^.%s" %data_path)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s = dojo.number.round(parseFloat(val.slice(0,-2))/3.779527559,2);}" %data_path,
                                    val="^_temp.data.layout.%s" %temp_path)
    
    def sideBarOpt____(self,pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px',datapath='.layout')
        for i in ('left','center','right'):
            if i != 'center':
                fb.numbertextBox(value='^.%s?width' %i,lbl='!!%s width' %i.title(),
                                width='4em')
                fb.dataController("""
                                     SET _temp.data.layout.regions.%s = parseInt((val||0)*3.779527559)+'px';
                                    """%i,
                                    val="^.%s?width" %i)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s?width = dojo.number.round(parseFloat(heightpx.slice(0,-2))/3.779527559,2);}" %i,
                                    heightpx="^_temp.data.layout.regions.%s" %i)
            else:
                fb.div()
            for j in ('top','bottom'):
                data_path = '%s.%s?height' %(i,j)
                temp_path = '%s.regions.%s'  %(i,j)
                fb.numberTextbox(value='^.%s' %data_path,
                                lbl='!!%s' %j.title(),
                                width='5em')
                fb.dataController("SET _temp.data.layout.%s = parseInt((val||0)*3.779527559)+'px';" %temp_path ,
                                  val="^.%s" %data_path)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s = dojo.number.round(parseFloat(val.slice(0,-2))/3.779527559,2);}" %data_path,
                                    val="^_temp.data.layout.%s" %temp_path)
    def sideBarOpt(self,pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px',datapath='.data.layout')
        for i in ('left','center','right'):
            if i != 'center':
                fb.numbertextBox(value='^.%s?width' %i,lbl='!!%s width' %i.title(),
                                width='4em')
                fb.dataController("""genro.setData("_temp.data.layout.regions.%s",
                                                      parseInt((val||0)*3.779527559)+'px',
                                                      {show:val!=0});"""%i,
                                    val="^.%s?width" %i)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s?width = dojo.number.round(parseFloat(heightpx.slice(0,-2))/3.779527559,2);}" %i,
                                    heightpx="^_temp.data.layout.regions.%s" %i)
            else:
                fb.div()
            for j in ('top','bottom'):
                data_path = '%s.%s?height' %(i,j)
                temp_path = '%s.regions.%s'  %(i,j)
                fb.numberTextbox(value='^.%s' %data_path,
                                lbl='!!%s' %j.title(),
                                width='5em')
                fb.dataController("""genro.setData('_temp.data.layout.%s',
                                                    parseInt((val||0)*3.779527559)+'px',
                                                    {show:val!=0});""" %temp_path ,
                                  val="^.%s" %data_path)
                fb.dataController("if(_triggerpars.kw.reason!=true){SET .%s = dojo.number.round(parseFloat(val.slice(0,-2))/3.779527559,2);}" %data_path,
                                    val="^_temp.data.layout.%s" %temp_path)
    