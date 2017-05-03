#!/usr/bin/env python
# encoding: utf-8

from gnrpkg.adm.decorators import checklist

class Table(object):
   @checklist(name='Import dati',pkg='glbl',code=2,subcode=5)
   def verifica_caricamento_dati(self):
       """Verifica importazione dati: vai nelle preferenze di glbl"""