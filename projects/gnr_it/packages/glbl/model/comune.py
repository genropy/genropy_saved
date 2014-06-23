#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('comune', pkey='id', name_long='Comune', name_plural='!!Comuni',caption_field='denominazione',rowcaption='denominazione')
        self.sysFields(tbl)
        tbl.column('codice_regione',name_long='!!Codice Regione')
        tbl.column('codice_provincia',name_long='!!Codice Provincia')
        tbl.column('sigla_provincia',name_long='!!Sigla Provincia').relation('glbl.provincia.sigla',relation_name='comuni',mode='foreignkey')
        tbl.column('codice_comune',name_long='!!Codice Comune')
        tbl.column('denominazione',name_long='!!Denominazione')
        tbl.column('denominazione_tedesca',name_long='!!Denominazione tedesca')
        tbl.column('capoluogo','B',name_long='!!Capoluogo')
        tbl.column('zona_altimetrica','I',name_long='!!Zona altimetrica')
        tbl.column('altitudine','I',name_long='!!Altitudine (m)')
        tbl.column('litoraneo',dtype='B',name_long='!!Comune litoraneo',name_short='Litoraneo')
        tbl.column('comune_montano',name_long='!!Comune montano')
        tbl.column('csl','I',name_long='!!Codice sistema lavoro (2001)')
        tbl.column('superficie','I',name_long='!!Superficie (kmq)')
        tbl.column('popolazione_residente','I',name_long='!!Popolazione residente (2010)')


    @public_method
    def pkeyFromCaption(self,caption=None):
        return self.readColumns(where='$denominazione ILIKE :comune_denominazione',comune_denominazione=caption,columns='$id')