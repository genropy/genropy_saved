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

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs,public_method
from gnr.core.gnrdict import dictExtract

from gnr.core.gnrbag import Bag

class TableHandlerStats(BaseComponent):

    @struct_method
    def th_statsTableHandler(self,pane,field=None):
        bc = pane.borderContainer()
        self._statsTableHandlerLeft(bc.tabContainer(region='left',width='230px',margin='2px',
                                                    drawer=True,splitter=True))
        self._statsTableHandlerCenter(bc.framePane(region='center'))



    def _statsTableHandlerLeft(self,tc):
        pass
        

    def _statsTableHandlerCenter(self,frame):

        sc = frame.center.stackContainer()
        iframe = self._statsTableHandlerCenterHtml(sc.contentPane(title='Html'))

        #tc = center.tabContainer()
       # grid = tc.contentPane(title='Griglia').quickGrid('^.pivot_grid')
        #grid.tools('export')
        bar = center.top.slotToolbar('2,stackButtons,*,printStats,exportStats,5')
        bar.printStats.slotButton('!!Print',action="genro.dom.iFramePrint(_iframe)",iconClass='iconbox print',
                                _iframe=iframe.js_domNode)
        bar.exportStats.slotButton('!!Export',iconClass='iconbox export',fire_xls='.run_pivot')
        

    
    def dettaglioTotali(self,bc):
        bc.dataController("""
            this.watch('totalizzatore_visibile',function(){
                return genro.dom.isVisible(bcNode);
            },function(){
                bcNode.fireEvent('.calcola_pivot',true);
            });
        """,_fired='^#FORM.controller.loaded',
            filtri_causali='^.causali',
            filtri_anni_mesi='^.anni_mesi',
            filtri_depositi_pkeys='^.depositi_pkeys',
            stat_rows='^.raggruppamenti.store.rows',
            stat_values='^.raggruppamenti.store.values',
            stat_columns='^.raggruppamenti.store.columns',
            bcNode=bc)
        
        bc.data('.filtri',self.db.table('erpy_mag.articolo_totale').filtriTotalizzazione())
        bc.dataRpc(None,self.db.table('erpy_mag.articolo_totale').getPivotTable,
                    filtri_causali='=.causali',
                    filtri_anni_mesi='=.anni_mesi',
                    filtri_depositi_pkeys='=.depositi_pkeys',
                    stat_rows='=.raggruppamenti.store.rows',
                    stat_values='=.raggruppamenti.store.values',
                    stat_columns='=.raggruppamenti.store.columns',
                    articolo_id='=#FORM.pkey',
                    outmode='^.calcola_pivot',
                    _onResult="""
                        result = result || new gnr.GnrBag();
                        //SET .pivot_grid = result.popNode('pivot_grid')
                        SET .pivot_html = result.getItem('pivot_html')
                        if(result.getItem('xls_url')){
                            genro.download(result.getItem('xls_url'));
                        }
                    """)
        self.dettaglioTotaliParametri(bc.tabContainer(region='left',width='250px',drawer=True,margin='2px'))
        center = bc.roundedGroupFrame(title='Totalizzazioni',region='center')
        iframe = self.dettaglioTotaliHtml(center.contentPane())

        #tc = center.tabContainer()
       # grid = tc.contentPane(title='Griglia').quickGrid('^.pivot_grid')
        #grid.tools('export')
        bar = center.top.bar.replaceSlots('#','#,printStats,exportStats,5')
        bar.printStats.slotButton('!!Print',action="genro.dom.iFramePrint(_iframe)",iconClass='iconbox print',
                                _iframe=iframe.js_domNode)
        bar.exportStats.slotButton('!!Export',iconClass='iconbox export',fire_xls='.calcola_pivot')
        

        #center.top.bar.replaceSlots('#','#,export,5')
    

    
    def _statsTableHandlerCenterHtml(self,pane,**kwargs):
        iframe = pane.div(_class='scroll-wrapper').htmliframe(height='100%',width='100%',border=0)
        pane.dataController("""var cw = _iframe.contentWindow;
                        var cw_body = cw.document.body;
                        if(genro.isMobile){
                            cw_body.classList.add('touchDevice');
                        }
                        var e = cw.document.createElement("link");
                        e.href = styleurl;
                        e.type = "text/css";
                        e.rel = "stylesheet";
                        //e.media = "screen";
                        cw.document.getElementsByTagName("head")[0].appendChild(e);
                        cw_body.classList.add('bodySize_'+genro.deviceScreenSize);
                        cw_body.classList.add('report_content');
                        cw_body.innerHTML = htmlcontent;
                    """ ,
                    _if='htmlcontent',
                    _else="""_iframe.contentWindow.document.body.innerHTML ="<div class='document'>Vuoto</div>" """,
                    _iframe=iframe.js_domNode,styleurl=self.getResourceUri('js_plugins/statspane/report.css', add_mtime=True),
                    htmlcontent='^.pivot_html')
        return iframe

    def dettaglioTotaliParametri(self,tc):
        self.dettaglioTotaliRaggruppamenti(tc.framePane(title='Raggruppamenti'))
        self.dettaglioTotaliParametriFiltri(tc.contentPane(title='Filtri',overflow='auto'))

    def dettaglioTotaliRaggruppamenti(self,frame):
        bar = frame.bottom.slotToolbar('*,calcola,5')
        frame.data('.raggruppamenti.store',self.db.table('erpy_mag.articolo_totale').configPivotTree())
        frame.center.contentPane(overflow='auto'
                        ).tree(storepath='.raggruppamenti.store',margin='5px',
                                 _class="branchtree noIcon",
                                labelAttribute='caption',hideValues=True,
                                draggable=True,dragClass='draggedItem',
                                dropTarget=True,
                                nodeId='raggruppamenti_stats_articolo_%s' %id(frame),
                                getLabelClass="""if (!node.attr.field){return "statfolder"}
                                        return node.attr.stat_type;""",
                               dropTargetCb="""
                                    if(!dropInfo.selfdrop){
                                        return false;
                                    }
                                    return true;
                                """,
                                onDrag='dragValues["selfdrag_path"]= dragValues["treenode"]["relpath"];',
                                onDrop_selfdrag_path=self.onDrop_raggruppamento())
        bar.calcola.slotButton('Calcola',fire='.calcola_pivot')

    def onDrop_raggruppamento(self):
        return """if(!dropInfo.selfdrop){
            return;
        }
        var put_before = dropInfo.modifiers == 'Shift';
        var b = this.widget.storebag();
        var destpath = dropInfo.treeItem.getFullpath(null,b);
        if(destpath==data){
            return;
        }
        var destNode = b.getNode(destpath);
        var destBag;
        var kw = {};
        if(destNode.attr.field){
            destBag = destNode.getParentBag();
            kw._position = (put_before?'<':'>')+destNode.label;
        }else{
            destBag = destNode.getValue();
        }
        var dragNode = b.popNode(data);
        destBag.setItem(dragNode.label,dragNode,null,kw);
    """
    def dettaglioTotaliParametriFiltri(self,tc):
        self.filtroAnnoMese(tc.titlePane(title='Anni/mesi',margin='2px'))
        self.filtroDepositi(tc.titlePane(title='Depositi',margin='2px'))
        self.filtroCausali(tc.titlePane(title='Causali',margin='2px'))

    def filtroAnnoMese(self,pane):
        pane.tree(storepath='.filtri.anni_mesi',
                  checked_anno_mese='.anni_mesi',
                  labelAttribute='caption',hideValues=True,
                  margin='2px')

    def filtroDepositi(self,pane):
        pane.tree(storepath='.filtri.depositi',
                  checked_deposito_id='.depositi_pkeys',
                  labelAttribute='caption',hideValues=True,
                  margin='2px')

    def filtroCausali(self,pane):
        pane.data('.causali','VEND')
        pane.checkBoxText(value='^.causali',
                        values='^.filtri.causali',
                        cols=1,parentForm=False)