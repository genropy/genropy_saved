# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import random

class AppPref(object):
    def permission_adm(self,**kwargs):
        return 'admin'

    def prefpane_adm(self,tc,**kwargs):
        tc = tc.tabContainer(**kwargs)
        tab_logo = tc.contentPane(title='!!Logo')
        fb = tab_logo.formbuilder(cols=2, border_spacing='4px')
        fb.numberTextBox(value='^.personal',lbl='!!Personal info')
        logobox = tab_logo.div(height='135px',width='135px',
                                    margin_left='3em',margin_top='40px',
                                padding='0px',background_color='white')
        logobox.img(style='width: 135px;',src='^aux.app.logoPath',_fired='^uploaded')

        tab_logo.button('!!Upload logo',action='FIRE aux.app.uploadLogo;',
                    margin_left='6em',margin_top='4ex',width='135px')
        
        tab_logo.dataRpc('aux.app.logoPath','logoUrl',_onStart=True,_fired='^aux.app.uploaded')
        tab_logo.dataController('genro.dlg.upload(msg,"uploadLogo","imgPath",{},label,cancel,send,fireOnSend)',
                               msg='!!Choose file',cancel='!!Cancel',label='!!Browse...',
                               send='!!Send', fired='^aux.app.uploadLogo',fireOnSend='aux.app.uploaded')
        self.printTemplateTab(tc)
    
    def printTemplateTab(self,parentTc):
        bc = parentTc.borderContainer(title='!!Print elements',nodeId='elemBc')
        gridBc = bc.borderContainer(region='left',width='200px')
        self.ajaxContent('printLayout',bc ,design='^aux.adm.design')

        pane = gridBc.contentPane(region='bottom',_class='pbl_roundedGroupBottom')
        pane.data('aux.adm.zoomFactor',0.3)
        def cb_bottom(bc,**kwargs):
            bottom = bc.contentPane(**kwargs)
            bottom.button('!!Close',baseClass='bottom_btn',float='right',margin='1px',fire='.close')
        self.simpleDialog(pane,height='300px',width='700px',dlgId='editorDialog',cb_bottom=cb_bottom,
                            cb_center=self.templateEditorPane,datapath='aux.adm.editDialog')

        pane.horizontalSlider(value='^aux.adm.zoomFactor', minimum=0, maximum=1,
                              intermediateChanges=True)
                              
        iv = self.includedViewBox(gridBc.borderContainer(region='center'),
                                label='!!Template name',nodeId='printTemplateGrid',
                                storepath='#adm.templates', 
                                selected_design='aux.adm.design',
                                struct=self.template_name_struct(),
                                autoWidth=True,add_action=True,del_action=True)
        gridEditor = iv.gridEditor()
        gridEditor.textbox(gridcell='name')
        gridEditor.filteringSelect(gridcell='design',values='sidebar:Sidebar,headline:Headline')
    
    def templateEditorPane(self,parentBc,**kwargs):
        bc = parentBc.borderContainer(datapath='^currentEditedArea',**kwargs)
        self.RichTextEditor(bc, value='^.html', contentPars=dict(region='center'),
                            nodeId='htmlEditor',editorHeight='200px')
        
    def remote_printLayout(self,parentBc,design=None,**kwargs):
        bc = parentBc.borderContainer(region='center',overflow='auto'
                     ).borderContainer(region='center',width='200mm',
                                        height='280mm',
                                        border='1px solid gray',style="""
                                                                    background-color:white;
                                                                    -moz-box-shadow:8px 8px 15px gray;
	                                                                -webkit-box-shadow:8px 8px 15px gray;
                                                                    """,
                                        zoomFactor='^aux.adm.zoomFactor',margin='5px'
                                        ).borderContainer(region='center',margin='10mm',
                                                            connect_ondblclick="""
                                                                        var clickedNode = dijit.getEnclosingWidget($1.originalTarget).sourceNode;
                                                                        SET currentEditedArea = clickedNode.absDatapath();
                                                                        FIRE #editorDialog.open;
                                                                        """,
                                                            _class='hideSplitter',
                                        regions='^aux.adm.template.dimensions',datapath='.template.layout',
                                        design=design)
        bc.css('.printRegion','margin:.5mm;border:.3mm dotted silver;cursor:pointer;')


        if design=='sidebar':
            self._sidebarRegions(bc.borderContainer(region='left',width='50mm',splitter=True,datapath='.left',
                                                _class='hideSplitter',regions='^aux.adm.template.sideleft'),'50mm')
            self._sidebarRegions(bc.borderContainer(region='right',datapath='.right',width='50mm',splitter=True,_class='hideSplitter',
                                                        regions='^aux.adm.template.sideright'),'50mm')
            self._sidebarRegions(bc.borderContainer(region='center',datapath='^.center',_class='hideSplitter'),'25mm')
        else:
            self._headlineRegions(bc.borderContainer(region='top',height='50mm',splitter=True,
                                                    _class='hideSplitter',datapath='.top',
                                                    regions='^aux.adm.template.header'),'50mm')
            self._headlineRegions(bc.borderContainer(region='bottom',datapath='.bottom',height='50mm',
                                                        splitter=True,_class='hideSplitter',regions='^aux.adm.template.footer'),'50mm')
            self._headlineRegions(bc.borderContainer(region='center',_class='hideSplitter',datapath='.center'),'25mm')
            
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

        
    def template_name_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('name', name='!!Name', width='12em')
        r.cell('design', name='!!Design', width='6em')
        return struct


    def rpc_logoUrl(self):
        return '%s?nocache=%i'%(self.app_logo_url(),random.randint(1,1000))

    def rpc_uploadLogo(self,fileHandle=None,ext=None,**kwargs):
        f=fileHandle.file
        content=f.read()
        current_logo = self.custom_logo_path()
        if current_logo:
            if os.path.isfile(current_logo):
                os.remove(current_logo)
        filename='custom_logo%s' % ext
        old_umask = os.umask(2)
        path=self.site.site_static_path('_resources','images','logo',filename)
        dirname=os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        outfile=file(path, 'w')
        outfile.write(content)
        outfile.close()
        os.umask(old_umask)
        result=self.app_logo_url()
        return "<html><body><textarea>%s</textarea></body></html>" % (str(result))