#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('comune', pkey='id', name_long='Comune', name_plural='!![it]Comuni',caption_field='denominazione',rowcaption='denominazione')
        self.sysFields(tbl)
        tbl.column('codice_regione',name_long='!![it]Codice Regione')
        tbl.column('codice_provincia',name_long='!![it]Codice Provincia')
        tbl.column('sigla_provincia', size='2', name_long='!![it]Sigla Provincia').relation('glbl.provincia.sigla',relation_name='comuni',mode='foreignkey')
        tbl.column('codice_comune',name_long='!![it]Codice Comune')
        tbl.column('denominazione',name_long='!![it]Denominazione')
        tbl.column('denominazione_tedesca',name_long='!![it]Denominazione tedesca')
        tbl.column('capoluogo','B',name_long='!![it]Capoluogo')
        tbl.column('zona_altimetrica','I',name_long='!![it]Zona altimetrica')
        tbl.column('altitudine','I',name_long='!![it]Altitudine (m)')
        tbl.column('litoraneo',dtype='B',name_long='!![it]Comune litoraneo',name_short='Litoraneo')
        tbl.column('comune_montano',name_long='!![it]Comune montano')
        tbl.column('csl','I',name_long='!![it]Codice sistema lavoro (2001)')
        tbl.column('superficie','I',name_long='!![it]Superficie (kmq)')
        tbl.column('popolazione_residente','I',name_long='!![it]Popolazione residente (2010)')


    @public_method
    def pkeyFromCaption(self,caption=None, **kwargs):
        return self.readColumns(where='$denominazione ILIKE :comune_denominazione',comune_denominazione=caption,columns='$id')