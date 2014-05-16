# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name', name='!!Name', width='20em')
        r.fieldcell('username', name='!!Username', width='10em')
        r.fieldcell('version', name='!!Version', width='20em')        
        
    def th_order(self):
        return 'name'
        
    def th_query(self):
        return dict(column='name',op='contains', val='')

class Form(BaseComponent):
    py_requires = "gnrcomponents/attachmanager/attachmanager:AttachManager"
    def th_form(self, form):
        bc = form.center.borderContainer()
        bc.css('.printRegion', 'margin:.5mm;border:.3mm dotted silver;cursor:pointer;')
        bc.data('zoomFactor', .5)
        #self.editorDialog(bc)
        self.htmltemplate_controllers(bc)
        self.htmltemplate_mainInfo(bc.borderContainer(region='left', width='55em', splitter=True,datapath='.record'))
        bc.borderContainer(region='center', overflow='auto', datapath='#FORM._temp.data').remote(self.htmltemplate_printLayout,
                                                                                           design='^#FORM.record.data.main.design')


    @public_method
    def htmltemplate_printLayout(self, parentBc, design=None, **kwargs):
        page = parentBc.borderContainer(region='center',
                                        height='^.main.page.height',
                                        width='^.main.page.width',
                                        border='1px solid gray', style="""
                                                                    background-color:white;
                                                                    -moz-box-shadow:8px 8px 15px gray;
                                                                    -webkit-box-shadow:8px 8px 15px gray;
                                                                    """,
                                        zoom='^zoomFactor', margin='10px')
        layers = page.contentPane(region='center',overflow='hidden')
        layers.div('^#FORM.backgroundLetterhead',position='absolute',top=0,left=0,right=0,bottom=0,
                    _class='backgroundLetterhead',visible='^#FORM.showBackground')
        layer_1 = layers.div(position='absolute',top=0,left=0,right=0,bottom=0,z_index=1)

        bc = layer_1.borderContainer(position='absolute',
                                  top='^.main.page.top',
                                  bottom='^.main.page.bottom',
                                  left='^.main.page.left',
                                  right='^.main.page.right',
                                  connect_onclick="""
                                    var clickedNode = dijit.getEnclosingWidget($1.target).sourceNode;
                                    if(clickedNode){
                                        SET #FORM.currentEditedArea = clickedNode.absDatapath();
                                    }
                                """,
                                  #_class='hideSplitter',
                                  regions='^#FORM._temp.data.layout.regions',
                                  design=design
                                  )
        regions = dict(headline=('top', 'bottom', 'center'), sidebar=('left', 'right', 'center'))
        for region in regions[design]:
            self._htmltemplate_subRegions(bc, region=region, design=design)


    def _htmltemplate_subRegions(self, parentBc, region=None, design=None):
        subregions = dict(sidebar=('top', 'bottom', 'center'), headline=('left', 'right', 'center'))
        bc = parentBc.borderContainer(region=region, splitter=(region != 'center'),
                                      _class='hideSplitter', datapath='.layout.%s' % region,
                                      regions='^.regions')
        for subregion in subregions[design]:
            bc.contentPane(region=subregion, _class='printRegion', splitter=(subregion != 'center'),
                           datapath='#FORM.record.data.layout.%s.%s' % (region, subregion)).div(innerHTML='^.html')

    def htmltemplate_controllers(self, pane):
        for part in ('height', 'width', 'top', 'bottom', 'left', 'right'):
            pane.dataFormula("#FORM._temp.data.main.page.%s" % part, "part+'mm';", part='^#FORM.record.data.main.page.%s' % part)
        pane.dataFormula("#FORM._temp.data.main.design", "design", design="^#FORM.record.data.main.design")
        pane.dataFormula('#FORM.record.center_height',"Math.floor(page_height-page_margin_top-page_margin_bottom-header_height-footer_height)",
                            page_height='^.main.page.height',
                            page_margin_top='^.main.page.top',
                            page_margin_bottom='^.main.page.bottom',
                            header_height='^.layout.top?height',
                            footer_height='^.layout.bottom?height',
                            datapath='#FORM.record.data')

        pane.dataFormula('#FORM.record.center_width',"Math.floor(page_width-page_margin_left-page_margin_right-side_left-side_right)",
                            page_width='^.main.page.width',
                            page_margin_left='^.main.page.left',
                            page_margin_right='^.main.page.right',
                            side_left='^.layout.left?width',
                            side_right='^.layout.left?width',
                            datapath='#FORM.record.data')

    def htmltemplate_mainInfo(self, bc):
        self.htmltemplate_form(bc.borderContainer(region='top', height='230px',splitter=True))
        
        center = bc.roundedGroupFrame(region='center',datapath='^#FORM.currentEditedArea',overflow='hidden')
        center.center.contentPane(overflow='hidden').ckEditor(value='^.html',nodeId='htmlEditor',toolbar='standard')
        bottom = center.bottom
        bar = bottom.slotBar('picker_flib,5,atcPalette,*,5,showBackground,5,zoomfactor,5',_class='pbl_roundedGroupBottom')
        bar.showBackground.div(margin_top='1px').checkbox(value='^#FORM.showBackground',label='Background letterheads',default=True)
        if 'flib' in self.db.packages:
            self.mixinComponent('flib:FlibPicker')
            bar.picker_flib.flibPicker(dockButton=dict(label='Files'),viewResource=':ImagesView')
        else:
            bar.picker_flib.div()
        bar.atcPalette.palettePane(paletteCode='atcPalette',title='Attachments',dockButton=dict(label='Attachments'),
                                height='800px',width='500px').attachmentPane(mode='headline',pbl_classes='*',
                                viewResource='gnrcomponents/attachmanager/attachmanager:AttachManagerViewBase')
        bar.zoomfactor.horizontalSlider(value='^zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True, width='15em', float='right')

    def htmltemplate_form(self,bc):
        left = bc.borderContainer(region='left', width='23em')
        self.htmltemplate_tplInfo(left.roundedGroup(region='top',title='!!Info',height='115px'))        
        self.htmltemplate_basePageParams(left.roundedGroup(region='center', datapath='.data.main.page',title='!!Page sizing'))
        tc = bc.tabContainer(region='center', selectedPage='^.data.main.design',margin='2px')
        self.htmltemplate_headLineOpt(tc.contentPane(title='Headline', pageName='headline'))
        self.htmltemplate_sideBarOpt(tc.contentPane(title='Sidebar', pageName='sidebar'))
        

    def htmltemplate_tplInfo(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        fb.field('name', width='12em',colspan=2)
        fb.field('based_on', width='12em',hasDownArrow=True,colspan=2,lbl='Based on')
        fb.dataRpc('#FORM.backgroundLetterhead',self.loadBasedOn,letterhead_id='^.based_on',_if='letterhead_id',_else='return "";')
        fb.field('type_code', width='7em',hasDownArrow=True,lbl='Type')
        fb.field('version', width='3em',lbl='V.')
        fb.field('next_letterhead_id', width='12em',hasDownArrow=True,lbl='Follow on',colspan=2)

    @public_method
    def loadBasedOn(self,letterhead_id=None,**kwargs):
        letterheadtbl = self.db.table('adm.htmltemplate')
        base = letterheadtbl.getHtmlBuilder(letterhead_pkeys=letterhead_id)
        base.finalize(base.body)
        basehtml = base.root.getItem('#0.#1').toXml(omitRoot=True,autocreate=True,forcedTagAttr='tag',docHeader=' ',
                                        addBagTypeAttr=False, typeattrs=False, 
                                        self_closed_tags=['meta', 'br', 'img'])
        return basehtml


    def htmltemplate_basePageParams(self, pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.numbertextBox(value='^.height', lbl='!!Height', width='5em')
        fb.numbertextBox(value='^.width', lbl='!!Width', width='5em')
        fb.numbertextBox(value='^.top', lbl='!!Top', width='5em')
        fb.numbertextBox(value='^.bottom', lbl='!!Bottom', width='5em')
        fb.numbertextBox(value='^.left', lbl='!!Left', width='5em')
        fb.numbertextBox(value='^.right', lbl='!!Right', width='5em')

    def htmltemplate_headLineOpt(self, pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px', datapath='.data.layout')
        for i in ('top', 'center', 'bottom'):
            if i != 'center':
                fb.numbertextBox(value='^.%s?height' % i, lbl='!!%s height' % i.title(),
                                 width='4em')
                fb.dataController("""this.setRelativeData("#FORM._temp.data.layout.regions.%s",
                                                      parseInt((val||0)*3.779527559)+'px',
                                                      {show:val!=0});""" % i,
                                  val="^.%s?height" % i)
                fb.dataController(
                        "if(_triggerpars.kw.reason!=true){SET .%s?height = dojo.number.round(parseFloat(heightpx.slice(0,-2))/3.779527559,2);}" % i
                        ,
                        heightpx="^#FORM._temp.data.layout.regions.%s" % i)
            else:
                fb.div()
            for j in ('left', 'right'):
                data_path = '%s.%s?width' % (i, j)
                temp_path = '%s.regions.%s' % (i, j)
                fb.numberTextbox(value='^.%s' % data_path,
                                 lbl='!!%s' % j.title(),
                                 width='5em')
                fb.dataController("""this.setRelativeData('#FORM._temp.data.layout.%s',
                                                    parseInt((val||0)*3.779527559)+'px',
                                                    {show:val!=0});""" % temp_path,
                                  val="^.%s" % data_path)
                fb.dataController(
                        "if(_triggerpars.kw.reason!=true){SET .%s = dojo.number.round(parseFloat(val.slice(0,-2))/3.779527559,2);}" % data_path
                        ,
                        val="^#FORM._temp.data.layout.%s" % temp_path)
        fb.numbertextBox(value='^#FORM.record.center_height', lbl='!!Center height', width='5em',readOnly=True)
        fb.br()
        fb.numbertextBox(value='^#FORM.record.center_width', lbl='!!Center width', width='5em',readOnly=True)


    def htmltemplate_sideBarOpt(self, pane):
        fb = pane.formbuilder(cols=3, border_spacing='4px', datapath='.data.layout')
        for i in ('left', 'center', 'right'):
            if i != 'center':
                fb.numbertextBox(value='^.%s?width' % i, lbl='!!%s width' % i.title(),
                                 width='4em')
                fb.dataController("""this.setRelativeData("#FORM._temp.data.layout.regions.%s",
                                                      parseInt((val||0)*3.779527559)+'px',
                                                      {show:val!=0});""" % i,
                                  val="^.%s?width" % i)
                fb.dataController(
                        "if(_triggerpars.kw.reason!=true){SET .%s?width = dojo.number.round(parseFloat(heightpx.slice(0,-2))/3.779527559,2);}" % i
                        ,
                        heightpx="^#FORM._temp.data.layout.regions.%s" % i)
            else:
                fb.div()
            for j in ('top', 'bottom'):
                data_path = '%s.%s?height' % (i, j)
                temp_path = '%s.regions.%s' % (i, j)
                fb.numberTextbox(value='^.%s' % data_path,
                                 lbl='!!%s' % j.title(),
                                 width='5em')
                fb.dataController("""this.setRelativeData('#FORM._temp.data.layout.%s',
                                                    parseInt((val||0)*3.779527559)+'px',
                                                    {show:val!=0});""" % temp_path,
                                  val="^.%s" % data_path)
                fb.dataController(
                        "if(_triggerpars.kw.reason!=true){SET .%s = dojo.number.round(parseFloat(val.slice(0,-2))/3.779527559,2);}" % data_path
                        ,
                        val="^#FORM._temp.data.layout.%s" % temp_path)
        fb.numbertextBox(value='^#FORM.record.center_height', lbl='!!Center height', width='5em',readOnly=True)
        fb.br()
        fb.numbertextBox(value='^#FORM.record.center_width', lbl='!!Center width', width='5em',readOnly=True)

    
    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['username'] = self.user
            record['data'] = Bag()
            record['data.main.page.height'] = 297
            record['data.main.page.width'] = 210
            record['data.main.page.top'] = 0
            record['data.main.page.bottom'] = 0
            record['data.main.page.left'] = 0
            record['data.main.page.right'] = 0
            record['data.main.design'] = 'headline'
            for i in ('top', 'center', 'bottom'):
                if i != 'center':
                    record.setItem('data.layout.%s' % i, None, height=30)
                for j in ('left', 'right'):
                    path = '%s.%s' % (i, j)
                    record.setItem('data.layout.%s' % path, None, width=30)

            for i in ('left', 'center', 'right'):
                if i != 'center':
                    record.setItem('data.layout.%s' % i, None, width=30)
                for j in ('top', 'bottom'):
                    path = '%s.%s' % (i, j)
                    record.setItem('data.layout.%s' % path, None, height=30)

    def th_options(self):
        return dict(dialog_height='630px',dialog_width='1100px',duplicate=True)
                          