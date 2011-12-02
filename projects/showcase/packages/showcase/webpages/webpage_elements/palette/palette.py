# -*- coding: UTF-8 -*-
"""palette"""

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    maintable = 'genrotit.h_tipo_titolo'
    py_requires="""public:Public, th/th:TableHandler,
                   gnrcomponents/htablehandler:HTableHandler"""
                   
    def main(self, root, **kwargs):
        frame = root.rootBorderContainer('Tipi titolo')
        self.htableHandler(frame, table='genrotit.h_tipo_titolo', nodeId='inputArea',
                           datapath='h_tipo_titolo', editMode='bc')
                           
    def inputArea_form(self, pane, table=None, **kwargs):
        bc = pane.borderContainer()
        top = bc.contentPane(region='top', margin='2px', _class='pbl_roundedGroup')
        top.div('Informazioni Tipo Titolo', _class='pbl_roundedGroupLabel')
        fb = top.div(padding='10px').formbuilder(cols=2, lbl_width='6em',datapath='.record')
        fb.field('child_code', lbl='!!Codice', width='10em')
        fb.field('description', lbl='!!Descrizione', width='30em')
        center = bc.borderContainer(region='center', datapath='#FORM',_class='pbl_roundedGroup',margin='2px')
        
        group = center.paletteGroup('griglie_campi', title='Griglie Campi', dockTo='dummyDock', width='450px')
        self.prepara_griglia_campi(center.contentPane(margin='2px',region='left',width='33%'),paletteGroup=group,
                                   classificazione = 'T', paletteTitle='Campi Anagrafica')
        self.prepara_griglia_campi(center.contentPane(margin='2px',region='center'),paletteGroup=group,
                                   classificazione = 'M', paletteTitle='Campi Movimento')
        self.prepara_griglia_campi(center.contentPane(margin='2px',region='right',width='33%'),paletteGroup=group,
                                   classificazione = 'V', paletteTitle='Campi Valutazione')
        
    def prepara_griglia_campi(self, pane, paletteGroup=None, classificazione=None, paletteTitle=None, **kwargs):
        nodeId = 'tipo_titolo_campo_%s' %classificazione
        th = pane.plainTableHandler(nodeId=nodeId, datapath='.%s' %nodeId, relation='@campi',
                                    condition="@campo_id.classificazione =:classificazione",
                                    condition_classificazione=classificazione,
                                    viewResource=':ViewFromTipoTitoloCampo', configurable=False, **kwargs)
        viewbar = th.view.top.bar
        th.view.attributes.update(border='1px solid silver',rounded=6,margin='2px')
        grid = th.view.grid
        viewbar.replaceSlots('searchOn','delrow,picker')
        viewbar.replaceSlots('vtitle','vcaption',vcaption=paletteTitle)
        viewbar.picker.slotButton(label='Mostra palette', iconClass='iconbox app',
                                  action="""var palette = genro.wdgById("griglie_campi_floating");
                                            palette.show();
                                            palette.bringToTop();""")
        paletteCode = 'campi_%s' %classificazione
        paletteGroup.paletteGrid(paletteCode, title=paletteTitle, dockButton=True,
                                 struct=self.struct_campi,
                                 grid_filteringGrid=grid, # grid_filteringGrid = th.view.grid
                                 grid_filteringColumn='id:campo_id' # grid_filteringColumn Consente la sincronizzazione
                                                                    # fra campi già inseriti e campi non ancora inseriti
                                 ).selectionStore(table='genrotit.campo',
                                                  where='$classificazione=:c',c=classificazione) # E' lo store della griglia: senza
                                                                                                 # la griglia sarebbe vuota!!
        
        grid.dragAndDrop(paletteCode)
        grid.dataRpc('dummy', self.aggiungiCampi,
                      data='^.dropped_%s' %paletteCode,
                      tipo_titolo_id='=#FORM.pkey')
                      
        grid.attributes.update(selfDragRows=True)
                      
    def struct_campi(self, struct):
        r = struct.view().rows()
        r.fieldcell('id',hidden=True)
        r.fieldcell('descrizione', width='100%')
        
    @public_method
    def aggiungiCampi(self, data=None, tipo_titolo_id=None):
        tbl = self.db.table('genrotit.tipo_titolo_campo')
        for row in data:
            campo_id = row.get('id')
            tbl.insert(dict(tipo_titolo_id=tipo_titolo_id,campo_id=campo_id))
        self.db.commit()
